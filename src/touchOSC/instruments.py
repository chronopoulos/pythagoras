"""
instrument classes should have the following methods:
   handleMsg(pathstr, arg, typestr, server, player) for handling processed messages
"""

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

   def handleXY(self, x, y):
      if debug: print 'Sampler, handleXY: ', x, y
      print 'nothing here yet'

class PolySynth():
   """
   Polyphonic Synth class
   """

   def __init__(self, voice=synths.Square, order=4, key=60, scale=scales.majorPentatonic):
      self.voices = []
      for i in range(order):
         self.voices.append(voice())
      self.poly = Poly(self.voices)
      self.key = key
      self.scale = scale

   def play(self, note, amp):
      f = pyo.midiToHz(self.key+self.scale(note))
      vn = self.poly.request()
      self.voices[vn].play(f, amp)

   def handleXY(self, x, y):
      if debug: print 'PolySynth, handleXY: ', x, y
      for voice in self.voices:
         voice.handleXY(x,y)

   def handleFader2(self, value):
      if debug: print 'PolySynth, handleFader2: ', value
      print 'nothing here yet'


def triad(i):
   j=i%3
   k=i//3
   notes = [0,2,4]
   return k*7 + notes[j]

class Arpeggiator():
   """
   Arpeggiator class
   """

   def __init__(self, voice=synths.Square, order=4, key=60, scale=scales.major, chord=0):
      self.voices = []
      for i in range(order):
         self.voices.append(voice())
      self.poly = Poly(self.voices)
      self.key = key
      self.scale = scale
      self.chord = chord

   def play(self, note, amp):
      f = pyo.midiToHz(self.key+self.scale(self.chord+triad(note)))
      vn = self.poly.request()
      self.voices[vn].play(f, amp)

   def handleFader2(self, value):
      if debug: print 'Arpeggiator, handleFader2: ', value
      chord = int(value*8)
      print chord
      self.chord = chord

   def handleXY(self, x, y):
      if debug: print 'PolySynth, handleXY: ', x, y
      for voice in self.voices:
         voice.handleXY(x,y)
