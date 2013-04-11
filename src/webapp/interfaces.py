import pyo, liblo
import instruments as inst
import numpy as np
from blist import sortedset


class Sequencer():
   """
   Sequencer class
   """


   def __init__(self, instrument, loop=16, nnotes=6, conway=False, seqVol=0.25):
      self.globalVol = 0.5
      self.instrument = instrument
      self.nx = loop
      self.ny = nnotes
      self.conway = False
      self.seqVol = [seqVol]*2
      self.step = 0
      self.gridState = np.array([0]*self.nx*self.ny).reshape((self.nx,self.ny))
      self.diff = np.array([0]*self.nx*self.ny).reshape((self.nx,self.ny))
      self.stepVol = [1. for i in range(self.nx)]
      self.noteVol = [1. for i in range(self.ny)]
      self.broadcast = liblo.Address(9002)

   def handleGlobalVol(self, pathlist, arg):
      self.globalVol = arg[0]

   def handleXY(self, pathlist, arg):
      if debug: print 'Sequencer, handleXY: ', pathlist, arg
      x = arg[0]
      y = arg[1]
      if pathlist[2]=='thexy':
         self.instrument.handleXY(x,y)

   def handleButton(self, pathlist, arg):
      if debug: print 'Sequencer, handleButton: ', pathlist, arg
      if pathlist[2]=='SEQ':
         step = int(pathlist[3])
         note = int(pathlist[4])
         state = arg[0]
         self.updateGridState(step, note, state)
      elif pathlist[2]=='DFT':
         self.instrument.handleDFT(arg[0])
      elif pathlist[2]=='conway':
         self.conway = (arg[0]==1)
      elif pathlist[2]=='clear':
         if arg[0]==1: self.clear()

   def handleSlider(self, pathlist, arg):
      if debug: print 'Sequencer, handleSlider: ', pathlist, arg
      if pathlist[2]=='V':
         if pathlist[3]=='2':
            slider = int(pathlist[4])
            value = arg[0]
            self.instrument.handleRow2(slider, value)
         elif pathlist[3]=='1':
            step = int(pathlist[4])
            vol = arg[0]
            self.updateStepVol(step, vol)
      elif pathlist[2]=='H':
         note = int(pathlist[3])
         vol = arg[0]
	 if debug:
	   print 'about to update notevol with: ', note, vol
         self.updateNoteVol(note, vol)

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
         amp=[lr*self.globalVol*self.stepVol[self.step]*self.noteVol[note] for lr in self.seqVol]
         self.instrument.play(note, amp)

   def handleMCP(self, pathlist, arg):
      pan = arg[0]
      amp = arg[1]
      mul = [amp*(1.-pan), amp*pan]
      self.seqVol = mul

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
      self.sendDiff_sequential()

   def sendDiff_sequential(self):
      xwhere, ywhere = np.where(self.diff != 0)
      n = len(xwhere)
      if n>0:
         for i in range(n):
            value = int(self.diff[xwhere[i],ywhere[i]]==1)
            liblo.send(self.broadcast, self.name+'/button/SEQ/'+str(xwhere[i])+'/'+str(ywhere[i]), value)

   def sendDiff_bundle(self):
      xwhere, ywhere = np.where(self.diff != 0)
      n = len(xwhere)
      if n>0:
         difflist = []
         for i in range(n):
            value = int(self.diff[xwhere[i],ywhere[i]]==1)
            difflist += [xwhere[i],ywhere[i],value]
         liblo.send(self.broadcast, '/mutation/diff', difflist)

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

   def clear(self):
      if debug: print 'Sequencer, clear '
      self.gridState = np.array([0]*self.nx*self.ny).reshape((self.nx,self.ny))
      # TODO bundle these messages into one
      for i in range(self.nx):
         for j in range(self.ny):
            liblo.send(self.broadcast, self.name+'/button/SEQ/'+str(i)+'/'+str(j), 0)


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

class DroneFace():
   """
   Drone interface class
   """

   def __init__(self, key, verbose=False):
      self.globalVol = 0.5
      fund = pyo.midiToHz(key)
      self.freqs = [i*fund for i in range(1,5)]
      self.ratios = [5,4,2,2]
      self.indices = [0]*4
      self.relativeMuls = [0.15, 0.15, 0.30, 0.22]
      self.muls = [0*rm for rm in self.relativeMuls]
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
      self.speed=1./50
      self.verbose = verbose
      self.pressed = sortedset()
      self.metro_accu = pyo.Metro(time=0.01).play()
      self.callback = pyo.TrigFunc(self.metro_accu, self.update)
      self.automation = [0,0,0,0] # 0 is nothing, 1 is linear, 2 is elliptical, 3 is homewardBound
      self.t = 0.
      self.dt = 0.01
      self.amp = [0,0,0,0]

   def setName(self, name):
      self.name = name

   def followMetro(self, metro):
      pass

   def update(self):
      self.t = (self.t + self.dt)%(2*np.pi)
      for i in range(4):
         if self.automation[i]==0: # no automation
            self.indices[i] += self.dindices[i]
         elif self.automation[i]==1: # linear
            self.indices[i] = self.amp[i]*np.cos(self.t)
         elif self.automation[i]==2: # elliptical
            if (i==0) or (i==2):
               self.indices[i] = self.amp[i]*np.cos(self.t)
            else:
               self.indices[i] = self.amp[i]*np.sin(self.t)
         elif self.automation[i]==3: # homewardBound
            self.dindices[i] = -self.indices[i]*self.speed
            self.indices[i] += self.dindices[i]
         self.voices[i].setIndex(self.indices[i])
      if self.verbose: print 'Indices, Muls, Ratios: ', self.indices, self.automation

   def handleXY(self, pathlist, arg):
      if debug: print 'DroneFace, handleXY: ', pathlist, arg
      x = (arg[0]-0.5)*2
      y = (arg[1]-0.5)*2
      if pathlist[2]=='L':
         self.handleXY_L(x,y)
      elif pathlist[2]=='R':
         self.handleXY_R(x,y)

   def handleXY_L(self, x, y):
      self.automation[:2] = [0, 0]
      if debug: print 'DroneFace, handleXY_L: ', x, y
      self.dindices[0], self.dindices[1] = x*self.speed, y*self.speed

   def handleXY_R(self, x, y):
      self.automation[2:] = [0, 0]
      if debug: print 'DroneFace, handleXY_R: ', x, y
      self.dindices[2], self.dindices[3] = x*self.speed, y*self.speed

   def handleSlider(self, pathlist, arg):
      pass

   def handleButton(self, pathlist, arg):
      if debug: print 'Drone, handleButton: ', pathlist, arg
      if pathlist[2]=='L':
         if pathlist[3]=='0':
            if debug: print '0'
            if arg[0]==1:
               self.automation[:2] = [3, 3]
         if pathlist[3]=='1':
            if arg[0]==1:
               self.amp = self.indices[:]
               self.automation[:2] = [1, 1]
            elif arg[0]==0:
               self.automation[:2] = [0, 0]
         elif pathlist[3]=='2':
            if arg[0]==1:
               self.amp = self.indices[:]
               self.automation[:2] = [2, 2]
            elif arg[0]==0:
               self.automation[:2] = [0, 0]
      elif pathlist[2]=='R':
         if pathlist[3]=='0':
            if debug: print '0'
            if arg[0]==1:
               self.automation[2:] = [3, 3]
         if pathlist[3]=='1':
            if arg[0]==1:
               self.amp = self.indices[:]
               self.automation[2:] = [1, 1]
            elif arg[0]==0:
               self.automation[2:] = [0, 0]
         elif pathlist[3]=='2':
            if arg[0]==1:
               self.amp = self.indices[:]
               self.automation[2:] = [2, 2]
            elif arg[0]==0:
               self.automation[2:] = [0, 0]
      if debug: print 'Automation state: ', self.automation

   def handleGlobalVol(self, pathlist, arg):
      self.globalVol = arg[0]
      for i in range(4):
         self.voices[i].setMul([lr*self.relativeMuls[i]*self.globalVol for lr in self.pan])

   def handleMCP(self, pathlist, arg):
      if debug: print 'DroneFace, handleMCP: ', pathlist, arg
      self.pan = [arg[1]*(1.-arg[0]), arg[1]*arg[0]]
      for i in range(4):
         self.voices[i].setMul([lr*self.relativeMuls[i]*self.globalVol for lr in self.pan])


class ChordExplorer():
   """
   Chord Explorer class
   """

   def __init__(self, scaletomod):
      self.verbose = verbose 
      self.twelvetones = [False, False, False, False, False, False, False, False, False, False, False, False] 
      self.twelvescale = []
      self.twelvedegrees = [False, False, False, False, False, False, False, False, False, False, False, False] 
      self.degrees = []
      self.curtone = 0
      self.scale = scaletomod

   def setName(self, name):
      self.name = name

   def followMetro(self, metro):
      pass

   def update(self):
      pass

   def handleGlobalVol(self, pathlist, arg):
      pass

   def handleXY(self, pathlist, arg):
      pass

   def handleSlider(self, pathlist, arg):
      pass

   def calcScale(self):
     index = 0
     self.twelvescale = []
     for b in self.twelvetones:
       if b:
         self.twelvescale.append(index)
       index = index + 1

   def calcDegrees(self):
     index = 0
     scount = len(self.twelvescale)
     self.degrees = []
     for b in self.twelvedegrees:
       if b:
         self.degrees.append(index)
       index = index + 1
       if index > scount:
         break

   def calcNotes(self):
     self.calcScale()
     self.calcDegrees()
     del self.scale[:]
     count = 0
     for d in self.degrees:
      i = d + self.curtone
      j=i%len(self.twelvescale)
      k=i//len(self.twelvescale)
      self.scale.append(k*12 + self.twelvescale[j])

   def handleButton(self, pathlist, arg):
      if debug: print 'chord explorer, handleButton: ', pathlist, arg
      if (pathlist[2] == "12tones"):
        index = int(pathlist[3])
        self.twelvetones[index] = bool(arg[0])
      if (pathlist[2] == "degrees"):
        index = int(pathlist[3])
	self.twelvedegrees[index] = bool(arg[0])  
      if (pathlist[2] == "curtone"):
        self.curtone = int(pathlist[3])
      self.calcNotes()
      if debug:
        print "twelvescale: ", self.twelvescale
        print "degrees ", self.degrees
        print "curtone ", self.curtone
        print "scale ", self.scale
       

   def handleMCP(self, pathlist, arg):
      pass

