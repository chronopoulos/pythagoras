import pyo
import instruments as inst
import numpy as np
from blist import sortedset
import random
from voices import FM
import scales
from poly import Poly

class Melodizer():
   """
   Arpeggiator class
   """

   def __init__(self, globalMetro, key=60, scale=scales.major):
      self.voices = []
      for i in range(4):
         self.voices.append(FM())
      self.poly = Poly(self.voices)
      self.key = key
      self.scale = scale
      self.callback = pyo.TrigFunc(globalMetro, self.playNext)
      self.last = 0
      self.jump = [-2,-1,0,1,2]

   def playNext(self):
      current = self.last + random.choice(self.jump)
      freq = pyo.midiToHz(self.key+self.scale(current))
      self.play(freq, 0.25)
      self.last = current

   def play(self, freq, amp):
      vn = self.poly.request()
      self.voices[vn].play(freq, amp)

   def handleFader2(self, value):
      if debug: print 'Arpeggiator, handleFader2: ', value
      chord = int(value*8)
      print chord
      self.chord = chord

   def handleXY(self, x, y):
      if debug: print 'PolySynth, handleXY: ', x, y
      for voice in self.voices:
         voice.handleXY(x,y)


class RandomTick():
   def __init__(self, globalMetro):
      self.callback = pyo.TrigFunc(globalMetro, self.maybeplay)
      self.sample = pyo.SfPlayer('../../samples/drums/acetone/PERC6.WAV', speed=[1,1], mul=0.1)

   def maybeplay(self):
      if random.random()>0.5:
         self.sample.out()

class Drone():
   """
   Drone class
   """

   def __init__(self, key, verbose=False):
      fund = pyo.midiToHz(key)
      self.freqs = [i*fund for i in range(1,5)]
      self.ratios = [5,4,2,2]
      self.indices = [0]*4
      self.muls = [0.15, 0.15, 0.30, 0.22]
      self.muls = [mul/2 for mul in self.muls]
      self.dindices = [0]*4
      self.dmuls = [0]*4
      self.homewardBound = [False]*4
      self.voices = []
      for i in range(4):
         j=i+1
         voice=pyo.FM(carrier=[self.freqs[i],self.freqs[i]]).out()
         voice.setRatio(self.ratios[i])
         voice.setIndex(self.indices[i])
         voice.setMul(self.muls[i])
         self.voices.append(voice)
      self.ticker = 0
      self.jspeed=1./50
      self.dspeed=1./100
      self.verbose = verbose
      self.pressed = sortedset()
      self.handlers = {
                        'LJLR' : self.handle_LJLR,
                        'LJUD' : self.handle_LJUD,
                        'RJLR' : self.handle_RJLR,
                        'RJUD' : self.handle_RJUD,
                        'L1' : self.handle_L1,
                        'R1' : self.handle_R1,
                        'L2' : self.handle_L2,
                        'R2' : self.handle_R2,
                        'B1' : self.handle_B1,
                        'B2' : self.handle_B2,
                        'B3' : self.handle_B3,
                        'B4' : self.handle_B4,
                        'DPLR' : self.handle_DPLR,
                        'DPUD' : self.handle_DPUD,
                        }

   def followMetro_rhythm(self, metro_rhythm):
      pass

   def followMetro_ctrl(self, metro_ctrl):
      self.callback = pyo.TrigFunc(metro_ctrl, self.automation)

   def automation(self):
      for i in range(4):
         if self.homewardBound[i]:
            self.dindices[i] = -self.indices[i]*self.jspeed
         self.indices[i] += self.dindices[i]
         self.muls[i] += self.dmuls[i]
         self.voices[i].setIndex(self.indices[i])
         self.voices[i].setMul(self.muls[i])
      if self.verbose: print 'Indices, Muls, Ratios: ', self.indices, self.muls, self.ratios

   def handle_LJLR(self, value):
      if debug: print 'Drone, handle_LJLR: ', value
      if value==0:
         self.homewardBound[0] = True
      else:
         self.homewardBound[0] = False
         self.dindices[0] = value*self.jspeed

   def handle_LJUD(self, value):
      if debug: print 'Drone, handle_LJUD: ', value
      if value==0:
         self.homewardBound[1] = True
      else:
         self.homewardBound[1] = False
         self.dindices[1] = value*self.jspeed

   def handle_RJLR(self, value):
      if debug: print 'Drone, handle_RJLR: ', value
      if value==0:
         self.homewardBound[2] = True
      else:
         self.homewardBound[2] = False
         self.dindices[2] = value*self.jspeed

   def handle_RJUD(self, value):
      if debug: print 'Drone, handle_RJUD: ', value
      if value==0:
         self.homewardBound[3] = True
      else:
         self.homewardBound[3] = False
         self.dindices[3] = value*self.jspeed

   def handle_L1(self, *args):
      if debug: print 'Drone, handle_L1', args

   def handle_R1(self, *args):
      if debug: print 'Drone, handle_R1', args

   def handle_L2(self, *args):
      if debug: print 'Drone, handle_L2', args
      self.indices = [0,0]+self.indices[2:]
      for i in range(4):
         self.voices[i].setIndex(self.indices[i])

   def handle_R2(self, *args):
      if debug: print 'Drone, handle_R2', args
      self.indices = self.indices[:2]+[0,0]
      for i in range(4):
         self.voices[i].setIndex(self.indices[i])

   def handle_B1(self, state):
      print 'Keyboard, handlebutton1', state
      if (state==1):
         self.pressed.add(0)
      else:
         self.pressed.remove(0)
      print self.pressed

   def handle_B2(self, state):
      if (state==1):
         self.pressed.add(1)
      else:
         self.pressed.remove(1)
      print self.pressed

   def handle_B3(self, state):
      if (state==1):
         self.pressed.add(2)
      else:
         self.pressed.remove(2)
      print self.pressed

   def handle_B4(self, state):
      if (state==1):
         self.pressed.add(3)
      else:
         self.pressed.remove(3)
      print self.pressed

   def handle_DPLR(self, value):
      if debug: print 'Drone, handle_DPLR: ', value
      for i in self.pressed:
         self.ratios[i] += value
         self.voices[i].setRatio(self.ratios[i])
      print 'New ratios: ', self.ratios

   def handle_DPUD(self, value):
      if debug: print 'Drone, handle_DPUD: ', value
      for i in self.pressed:
         self.dmuls[i] = value*self.dspeed
      


class Wub():

   def __init__(self, freq, metro_rhythm):
      self.wubfreq = 1/6./metro_rhythm.time
      self.LFO = pyo.Sine(freq=self.wubfreq, mul=2, add=4)
      self.waveform = pyo.FM(carrier=[freq,freq], ratio=8, index=self.LFO, mul=0.5).out()

   def handle_RJLR(self, value):
      if debug: print 'Wub, handle_RJLR: ', value
      self.LFO.setFreq(4*value+4)

   def handle_RJUD(self, value):
      if debug: print 'Wub, handle_RJUD: ', value
      self.LFO.setMul(2*value+2)


class Keyboard():
   """
   Keyboard class
   Requires sortedset from the blist module
   """

   def __init__(self, instrument, maxVol=1.):
      self.instrument = instrument
      self.maxVol = maxVol
      self.pressed = sortedset()
      self.note_last = 0

   def handle_Button1(self, state):
      print 'Keyboard, handlebutton1', state
      if (state==1):
         self.pressed.add(0)
      else:
         self.pressed.remove(0)

   def handle_Button2(self, state):
      if (state==1):
         self.pressed.add(1)
      else:
         self.pressed.remove(1)

   def handle_Button3(self, state):
      if (state==1):
         self.pressed.add(2)
      else:
         self.pressed.remove(2)

   def handle_Button4(self, state):
      if (state==1):
         self.pressed.add(3)
      else:
         self.pressed.remove(3)
 
   def playNext(self):
      if len(self.pressed)==0:
         return
      elif self.note_last >= self.pressed[-1]:
            note_current = self.pressed[0]
            self.instrument.play(note_current, self.maxVol)
            self.note_last = note_current
      else:
            i = 0
            while self.pressed[i] <= self.note_last:
               i += 1
            note_current = self.pressed[i]
            self.instrument.play(note_current, self.maxVol)
            self.note_last = note_current

   def takeStep(self):
      self.playNext()

   def followMetro(self, metro):
      self.metro = metro
      self.callbackMetro = pyo.TrigFunc(self.metro, self.takeStep)
