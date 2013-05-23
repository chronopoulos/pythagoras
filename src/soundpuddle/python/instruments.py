import pyo
import numpy as np
import synths
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

   def handleKnob(self, value):
      pass

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

   def handleKnob(self, value):
      print 'polysynth, handleKnob', value
      for voice in self.voices:
         voice.handleKnob(value)

   def play(self, note, amp):
      f = pyo.midiToHz(self.key+self.tonality.request(note))
      vn = self.poly.request()
      print vn
      self.voices[vn].play(f, amp)

class BrutePoly():

   def __init__(self, voice=synths.FM, order=24, key=60):
      self.voices = []
      for i in range(order):
         self.voices.append(voice())
      self.key = key

   def setTonality(self, tonality):
      self.tonality = tonality

   def handleKnobA(self, value):
      #print 'polysynth, handleKnob', value
      for voice in self.voices:
         voice.handleKnobA(value)

   def handleKnobB(self, value):
      #print 'polysynth, handleKnob', value
      for voice in self.voices:
         voice.handleKnobB(value)

   def handleKnobC(self, value):
      #print 'polysynth, handleKnob', value
      for voice in self.voices:
         voice.handleKnobC(value)

   def play(self, note, amp):
      f = pyo.midiToHz(self.key+self.tonality.request(note))
      self.voices[note].play(f, amp)

