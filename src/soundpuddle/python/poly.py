import pyo

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
         self.freeTrigs.append(pyo.Thresh(amplitude, 0.01, dir=1)) # set the threshold lower?
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
