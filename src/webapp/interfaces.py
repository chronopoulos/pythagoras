import pyo, liblo
import instruments as inst
import numpy as np
from blist import sortedset


class Sequencer():
   """
   Sequencer class
   """


   def __init__(self, instrument, loop=16, nnotes=6, conway=False, maxVol=1.):
      self.instrument = instrument
      self.nx = loop
      self.ny = nnotes
      self.conway = False
      self.maxVol = maxVol
      self.step = 0
      self.gridState = np.array([0]*self.nx*self.ny).reshape((self.nx,self.ny))
      self.diff = np.array([0]*self.nx*self.ny).reshape((self.nx,self.ny))
      self.stepVol = [1. for i in range(self.nx)]
      self.noteVol = [1. for i in range(self.ny)]
      self.webapp = liblo.Address(9002)

   def setName(self, name):
      self.name = name

   def followMetro(self, metro):
      self.metro = metro
      self.callbackMetro = pyo.TrigFunc(self.metro, self.takeStep)

   def takeStep(self):
      self.play()
      self.advance()

   def play(self):
      notes = np.where(self.gridState[self.step,:]==1)[0]
      for note in notes:
         amp=self.maxVol*self.stepVol[self.step]*self.noteVol[note]
         self.instrument.play(note, amp)

   def advance(self):
      self.step = (self.step + 1) % self.nx
      if (self.step==0) and self.conway:
         self.advanceConway()

   def advanceConway(self):
      for i in range(self.nx):
         for j in range(self.ny):
            # count live neighbors
            live_neighbors=0
            for drow in [-1,0,1]:
               for dcol in [-1,0,1]:
                  is_self = (drow==0) and (dcol==0)
                  if (not is_self):
                     live_neighbors += self.gridState[(i+drow)%self.nx,(j+dcol)%self.ny]
            # assign changes
            if (self.gridState[i,j]==1): # if alive
               if (live_neighbors <= 1 or live_neighbors >= 4):
                  self.diff[i,j]=-1 # cell dies
               else:
                  self.diff[i,j]=0  # cell survives
            else: # if dead
               if (live_neighbors==3):
                  self.diff[i,j]=1  # cell is born
               else:
                  self.diff[i,j]=0  # cell remains dead
      # apply changes
      self.gridState += self.diff
      self.sendDiff_sequential(self.webapp)

   def sendDiff_sequential(self, address):
      xwhere, ywhere = np.where(self.diff != 0)
      n = len(xwhere)
      if n>0:
         for i in range(n):
            value = int(self.diff[xwhere[i],ywhere[i]]==1)
            liblo.send(address, self.name+'/button/SEQ/'+str(ywhere[i]+1)+'/'+str(xwhere[i]+1), value)

   def sendDiff_bundle(self):
      xwhere, ywhere = np.where(self.diff != 0)
      n = len(xwhere)
      if n>0:
         difflist = []
         for i in range(n):
            value = int(self.diff[xwhere[i],ywhere[i]]==1)
            difflist += [xwhere[i],ywhere[i],value]
         liblo.send(self.interfaceAddress, '/mutation/diff', difflist)

   def sendDiff_sequential(self):
      xwhere, ywhere = np.where(self.diff != 0)
      n = len(xwhere)
      if n>0:
         difflist = []
         for i in range(n):
            value = int(self.diff[xwhere[i],ywhere[i]]==1)
            liblo.send(self.ui, '/2/multitoggle/'+str(ywhere[i]+1)+'/'+str(xwhere[i]+1), value)

   def updateGridState(self, step, note, state):
      if debug: print 'Sequencer, updateGridState', step, note, state
      self.gridState[step,note] = state # wtf?

   def updateConway(self, pathlist, arg):
      self.conway = arg[0] == 1

   def updateStepVol(self, step, vol):
      if debug: print 'Sequencer, updateStepVol', step, vol
      self.stepVol[step] = vol

   def updateNoteVol(self, note, vol):
      self.noteVol[note] = vol
      if debug: print 'Sequencer, updateNoteVol: updated, with', note, vol


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

   def updatePressed(self, pathlist, arg):
      note = int(pathlist[2][4:]) - 1
      on = (arg[0]==1.0)
      if on:
         self.pressed.add(note)
      else:
         self.pressed.remove(note)
      if debug: print self.pressed

