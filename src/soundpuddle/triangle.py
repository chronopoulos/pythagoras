import pyo, voices

audioServer = pyo.Server().boot()
audioServer.start()

class Triangle():

   def __init__(self):
      self.voices = [voices.Spoke(pyo.midiToHz(60+i)) for i in range(24)]

   def play(self, i):
      self.voices[i].play()

###

triangle = Triangle()

audioServer.gui(locals())
