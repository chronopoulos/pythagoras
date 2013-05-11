import serial, pyo

s = pyo.Server().boot()
s.start()

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

class Poly():
   """
   Polyphonic voice manager: because pyo.VoiceManager doesn't seem to work?
   Input:
      List of Voices, with output streams in Voice.output
   Methods:
      Poly.request()
      -> Returns the first available Voice.
      -> If no Voices are available, returns the one that was returned longest ago.
   """

   def __init__(self, voices):
      self.voices = voices
      self.nvoices = len(self.voices)
      self.freeVoices = range(self.nvoices)
      self.queue = range(self.nvoices)
      self.freeTrigs = []
      for voice in self.voices:
         amplitude = pyo.Follower(voice.output[0])
         self.freeTrigs.append(pyo.Thresh(amplitude, 0.01, dir=1))
      self.callbacks = []
      for vn in range(self.nvoices):
         self.callbacks.append(pyo.TrigFunc(self.freeTrigs[vn], self.freeVoice, arg=vn))

   def freeVoice(self, voicenum):
      self.freeVoices.append(voicenum)

   def request(self):
      if len(self.freeVoices) > 0:
         voice = self.freeVoices[0]
         self.freeVoices.remove(voice)
         self.queue.remove(voice)
         self.queue.append(voice)
         return voice
      else:
         voice = self.queue[0]
         self.queue.remove(voice)
         self.queue.append(voice)
         return voice

voices = [Square() for i in range(4)]
poly = Poly(voices)

mapping = {'a':pyo.midiToHz(60),
            'b':pyo.midiToHz(62),
            'c':pyo.midiToHz(64),
            'd':pyo.midiToHz(67)}

arduino = serial.Serial('/dev/ttyACM0', 9600)
while True:
    msg = arduino.read(1)
    print msg
    try:
        freq = mapping[msg]
        vn = poly.request()
        voices[vn].play(freq, 0.25)
    except KeyError:
        print 'Unmapped: ', msg

