import pyo
import numpy as np
import scales, synths
from poly import Poly

##########################################################

class Sampler():
   """
   Sampler class
   """

   def __init__(self, pack):
      """
      Pack should simply be a list of filenames.
      pyo.SfPlayer objects are created upon instantiation.
      This way, multiple Sampler instances can have their own bitstreams.
      """
      self.notes = []
      for filename in pack:
         self.notes.append(pyo.SfPlayer(filename, speed=[1,1]))

   def play(self, note, amp):
      self.notes[note].setMul(amp)
      self.notes[note].out()

   def setTonality(self, tonality):
      pass

class PolySynth():
   """
   Polyphonic Synth class
   """

   def __init__(self, voice=synths.Square, order=4, key=60):
      self.voices = []
      for i in range(order):
         self.voices.append(voice())
      self.poly = Poly(self.voices)
      self.key = key

   def setTonality(self, tonality):
      self.tonality = tonality

   def handleXY(self, x, y):
      if debug: print 'PolySynth, handleXY: ', x, y
      for voice in self.voices:
         voice.handleXY(x,y)

   def handleRow2(self, slider, value):
      if debug: print 'PolySynth, handleRow2: ', slider, value
      for voice in self.voices:
         voice.handleRow2(slider, value)

   def handleDFT(self, state):
      if debug: print 'PolySynth, handleDFT: ', state
      for voice in self.voices:
         voice.handleDFT(state)

   def play(self, note, amp):
      f = pyo.midiToHz(self.key+self.tonality.request(note))
      vn = self.poly.request()
      self.voices[vn].play(f, amp)
