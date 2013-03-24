"""
These are the monophonic synthesizers.
They can be played as is, via the play() method.
However, they're designed to be used within the Poly object,
as part of a polyphonic synthesizer.
"""

import pyo

class Square():
   """
   Square wave synthesizer.
   """

   def __init__(self):
      self.trig = pyo.Trig()
      decaytable = pyo.LinTable(list=[(0, 1.0), (8191, 0.0)])
      self.env = pyo.TrigEnv(self.trig, table=decaytable, dur=0.6, mul=.25)
      waveform = pyo.SquareTable()
      self.osc = pyo.Osc(waveform, freq=[0.,0.], mul=self.env[0])
      self.output = self.osc.out()

   def setFreq(self, f):
      self.osc.setFreq([f,f])

   def setAmp(self, amp):
      self.env.setMul(amp)

   def setDur(self, dur):
      self.env.setDur(dur)

   def play(self, f, amp, dur=0.5):
      self.setFreq(f)
      self.setAmp(amp)
      self.setDur(dur)
      # TODO: make these setter methods more efficient
      #  they're being called more often than they need to be
      self.trig.play()

class Additive():
   """
   Additive synthesizer.
   """

   def __init__(self):
      self.trig = pyo.Trig()
      decaytable = pyo.LinTable(list=[(0, 1.0), (8191, 0.0)])
      self.env = pyo.TrigEnv(self.trig, table=decaytable, dur=0.6, mul=.25)
      self.spectrum = [1.]+[0.]*15  # 16 total
      self.waveform = pyo.HarmTable(self.spectrum)
      self.osc = pyo.Osc(self.waveform, freq=[0.,0.], mul=self.env[0])
      self.filter = pyo.Biquad(self.osc, freq=[300.,300.], type=2, q=2.)
      self.output = self.filter.out()

   def handleXY(self, x, y):
      if debug: print 'Additive, handleXY: ', x, y
      self.filter.setFreq(x*1500.)
      self.filter.setQ(1.+y*3.)

   def handleRow2(self, slider, value):
      harmonic = slider
      coeff = value
      self.updateSpectrum(harmonic, coeff)

   def handleDFT(self, state):
      if state==1:
         self.updateWaveform()

   def setFreq(self, f):
      self.osc.setFreq([f,f])

   def setAmp(self, amp):
      self.env.setMul(amp)

   def setDur(self, dur):
      self.env.setDur(dur)

   def updateSpectrum(self, harmonic, coeff):
      self.spectrum[harmonic] = coeff

   def updateWaveform(self):
      self.waveform.replace(self.spectrum)

   def play(self, f, amp, dur=0.5):
      self.setFreq(f)
      self.setAmp(amp)
      self.setDur(dur)
      # TODO: make these setter methods more efficient
      #  they're being called more often than they need to be
      self.trig.play()


class FM():
   """
   FM synthesizer.
   """

   def __init__(self):
      self.trig = pyo.Trig()
      self.envTableList = [(i*8192/15,1./(i+1)) for i in range(16)]
      self.envTable = pyo.CurveTable(self.envTableList)
      self.env = pyo.TrigEnv(self.trig, table=self.envTable, dur=0.6, mul=0.)
      self.fm = pyo.FM(carrier=[0.,0.], mul=self.env[0])
      self.output = self.fm.out()

   def setEnvTableList(self, timestep, value):
      self.envTableList[timestep] = (timestep*8192/15,value)

   def updateEnvTable(self):
      self.envTable.replace(self.envTableList)

   def setFreq(self, f):
      self.fm.setCarrier(f)

   def setAmp(self, amp):
      self.env.setMul(amp)

   def setDur(self, dur):
      self.env.setDur(dur)

   def handleXY(self, x, y):
      if debug: print 'FM, handleXY: ', x, y
      ratio = int(x*10)+1
      index = 10*y
      self.fm.setRatio(ratio)
      self.fm.setIndex(index)

   def handleRow2(self, slider, value):
      self.setEnvTableList(slider, value)

   def handleDFT(self, state):
      if state==1:
         self.updateEnvTable()

   def play(self, f, amp, dur=0.5):
      self.setFreq(f)
      self.setAmp(amp)
      self.setDur(dur)
      # TODO: make these setter methods more efficient
      #  they're being called more often than they need to be
      self.trig.play()


