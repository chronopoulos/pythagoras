import pyo, liblo
import instruments as inst
import numpy as np
from blist import sortedset


class Sequencer():
   """
   Sequencer class
   """

   def __init__(self, port, phoneaddress, instrument, loop=16, nnotes=6, conway=False, maxVol=1.):
      self.port = port
      self.OSCserver = liblo.Server(self.port)
      self.OSCserver.add_method(None, None, self.handleMsg)
      self.phoneaddress = phoneaddress
      self.instrument = instrument
      self.nx = loop
      self.ny = nnotes
      self.conway = conway
      self.maxVol = maxVol
      self.step = 0
      self.gridState = np.array([0]*self.nx*self.ny).reshape((self.nx,self.ny))
      self.diff = np.array([0]*self.nx*self.ny).reshape((self.nx,self.ny))
      self.stepVol = [1. for i in range(self.nx)]
      self.noteVol = [1. for i in range(self.ny)]
      self.bindings = {
         ('1', 'fader1') : self.handleFader1,
         ('1', 'fader2') : self.handleFader2,
         ('1', 'toggle1') : self.handleToggle1,
         ('2', 'multitoggle') : self.handleMultiToggle,
         ('2', 'multifader') : self.handleMultiFader,
         ('3', 'rotary1') : self.handleRotary,
         ('3', 'rotary2') : self.handleRotary,
         ('3', 'rotary3') : self.handleRotary,
         ('3', 'rotary4') : self.handleRotary,
         ('3', 'rotary5') : self.handleRotary,
         ('3', 'rotary6') : self.handleRotary,
         ('4', 'xy') : self.handleXY
         }

   def handleMsg(self, pathstr, arg, typestr, server, usrData):
      if debug: print 'Sequencer, handleMsg: ', pathstr, arg
      pathlist = pathstr.split('/')
      if len(pathlist)>=3:
         try:
            self.bindings[pathlist[1],pathlist[2]](pathlist, arg)
         except:
            pass
      else:
         return

   def handleToggle1(self, pathlist, arg):
      if debug: print 'Sequencer, handleToggle1: ', pathlist, arg
      self.conway = arg[0] == 1

   def handleMultiToggle(self, pathlist, arg):
      if debug: print 'Sequencer, handleMultiToggle: ', pathlist, arg
      step = int(pathlist[4]) - 1
      note = int(pathlist[3]) - 1
      state = arg[0]
      self.gridState[step,note] = state

   def handleMultiFader(self, pathlist, arg):
      if debug: print 'Sequencer, handleMultiFader: ', pathlist, arg
      step = int(pathlist[3]) - 1
      vol = arg[0]
      self.stepVol[step] = vol

   def handleRotary(self, pathlist, arg):
      if debug: print 'Sequencer, handleRotary: ', pathlist, arg
      note = int(pathlist[2][-1])-1
      vol = arg[0]
      self.noteVol[note] = vol

   def handleXY(self, pathlist, arg):
      if debug: print 'Sequencer, handleXY: ', pathlist, arg
      x = arg[1]
      y = arg[0]
      self.instrument.handleXY(x,y)

   def handleFader1(self, pathlist, arg):
      if debug: print 'Sequencer, handleFader1: ', pathlist, arg
      bpm = arg[0]*40+100.
      self.metro.setTime(15./bpm)

   def handleFader2(self, pathlist, arg):
      if debug: print 'Sequencer, handleFader2: ', pathlist, arg
      self.instrument.handleFader2(arg[0])

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
      self.sendDiff()

   def sendDiff(self):
      xwhere, ywhere = np.where(self.diff != 0)
      n = len(xwhere)
      if n>0:
         for i in range(n):
            value = int(self.diff[xwhere[i],ywhere[i]]==1)
            liblo.send(self.phoneaddress, '/2/multitoggle/'+str(ywhere[i]+1)+'/'+str(xwhere[i]+1), value)



class Keyboard():
   """
   Keyboard class
   Requires sortedset from the blist module
   """

   def __init__(self, port, phoneaddress, instrument, maxVol=1.):
      self.port = port
      self.OSCserver = liblo.Server(self.port)
      self.OSCserver.add_method(None, None, self.handleMsg)
      self.phoneaddress = phoneaddress
      self.instrument = instrument
      self.maxVol = maxVol
      self.pressed = sortedset()
      self.note_last = 0
      self.bindings = {
         ('1', 'push1') : self.handleKeyboard1,
         ('1', 'push2') : self.handleKeyboard1,
         ('1', 'push3') : self.handleKeyboard1,
         ('1', 'push4') : self.handleKeyboard1,
         ('1', 'push5') : self.handleKeyboard1,
         ('1', 'push6') : self.handleKeyboard1,
         ('1', 'push7') : self.handleKeyboard1,
         ('1', 'push8') : self.handleKeyboard1,
         ('1', 'push9') : self.handleKeyboard1,
         ('1', 'push10') : self.handleKeyboard1,
         ('1', 'push11') : self.handleKeyboard1,
         ('1', 'push12') : self.handleKeyboard1,
         ('2', 'push1') : self.handleKeyboard2,
         ('2', 'push2') : self.handleKeyboard2,
         ('2', 'push3') : self.handleKeyboard2,
         ('2', 'push4') : self.handleKeyboard2,
         ('2', 'push5') : self.handleKeyboard2,
         ('2', 'push6') : self.handleKeyboard2,
         ('2', 'push7') : self.handleKeyboard2,
         ('2', 'push8') : self.handleKeyboard2,
         ('2', 'push9') : self.handleKeyboard2,
         ('2', 'push10') : self.handleKeyboard2,
         ('2', 'push11') : self.handleKeyboard2,
         ('2', 'push12') : self.handleKeyboard2
         }

   def handleMsg(self, pathstr, arg, typestr, server, usrData):
      if debug: print 'Keyboard, handleMsg: ', pathstr, arg
      pathlist = pathstr.split('/')
      if len(pathlist)>=3:
         try:
            self.bindings[pathlist[1],pathlist[2]](pathlist, arg)
         except:
            pass
      else:
         return

   def handleKeyboard1(self, pathlist, arg):
      if debug: print 'Keyboard, handleKeyboard1: ', pathlist, arg
      note = int(pathlist[2][4:]) - 1
      on = (arg[0]==1.0)
      if on:
         self.pressed.add(note)
      else:
         self.pressed.remove(note)
      if debug: print self.pressed

   def handleKeyboard2(self, pathlist, arg):
      if debug: print 'Keyboard, handleKeyboard2: ', pathlist, arg
      note = int(pathlist[2][4:]) - 1
      if (arg[0]==1.0): self.instrument.play(note, self.maxVol)
 
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


