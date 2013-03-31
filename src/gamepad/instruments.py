import pyo
import instruments as inst
import numpy as np
from blist import sortedset

class Drone():
   """
   Drone class
   """

   def __init__(self, freq, metro_accu, verbose=False):
      self.freqs = [i*freq for i in range(1,5)]
      self.ratios = [8,4,2,1]
      self.indices = [0]*4
      self.muls = [0.25, 0.15, 0.10, 0.8]
      self.pos = [0]*4
      self.voices = []
      for i in range(4):
         j=i+1
         voice=pyo.FM(carrier=[self.freqs[i],self.freqs[i]]).out()
         voice.setRatio(self.ratios[i])
         voice.setIndex(self.indices[i])
         voice.setMul(self.muls[i])
         self.voices.append(voice)
      self.callback = pyo.TrigFunc(metro_accu, self.update)
      self.ticker = 0
      self.speed=1./50
      self.verbose = verbose
      self.pressed = sortedset()

   def update(self):
      for i in range(4):
         self.indices[i] += self.pos[i]
         self.voices[i].setIndex(self.indices[i])
      if self.verbose: print 'Indices: ', self.indices

   def handle_LJLR(self, value):
      if debug: print 'Drone, handle_LJLR: ', value
      self.pos[0] = value*self.speed

   def handle_LJUD(self, value):
      if debug: print 'Drone, handle_LJUD: ', value
      self.pos[1] = value*self.speed

   def handle_RJLR(self, value):
      if debug: print 'Drone, handle_RJLR: ', value
      self.pos[2] = value*self.speed

   def handle_RJUD(self, value):
      if debug: print 'Drone, handle_RJUD: ', value
      self.pos[3] = value*self.speed

   def handle_L1(self, *args):
      if debug: print 'Drone, handle_L1', args
      for i in range(2):
         self.pos[i] = -self.indices[i]*self.speed

   def handle_R1(self, *args):
      if debug: print 'Drone, handle_R1', args
      for i in range(2,4):
         self.pos[i] = -self.indices[i]*self.speed

   def handle_L2(self, *args):
      if debug: print 'Drone, handle_L2', args
      self.indices = [0,0]+self.indices[2:]
      for i in range(4):
         self.voices[i].setIndex(self.indices[i])

   def handle_R2(self, *args):
      if debug: print 'Drone, handle_L2', args
      self.indices = self.indices[:2]+[0,0]
      for i in range(4):
         self.voices[i].setIndex(self.indices[i])

   def handle_button1(self, state):
      print 'Keyboard, handlebutton1', state
      if (state==1):
         self.pressed.add(0)
      else:
         self.pressed.remove(0)
      print self.pressed

   def handle_button2(self, state):
      if (state==1):
         self.pressed.add(1)
      else:
         self.pressed.remove(1)
      print self.pressed

   def handle_button3(self, state):
      if (state==1):
         self.pressed.add(2)
      else:
         self.pressed.remove(2)
      print self.pressed

   def handle_button4(self, state):
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
         self.muls[i] += value/100.
         self.voices[i].setMul(self.muls[i])
      print 'New muls: ', self.muls
      


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
