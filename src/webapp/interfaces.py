import pyo, liblo
import instruments as inst
import numpy as np


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
      self.stepVol = [0.5 for i in range(self.nx)]
      self.noteVol = [0.5 for i in range(self.ny)]

   def increaseLoop(self):
      pad = np.array([0]*self.ny).reshape(1,self.ny)
      self.gridState = np.concatenate((self.gridState, pad), axis=0)
      self.diff = np.concatenate((self.diff, pad), axis=0)
      self.stepVol.append(0.5)
      self.nx += 1
      liblo.send(broadcast, self.name+'/cmd/loopc', self.nx)
      if debug: print 'Sequencer, increaseLoop, new gridstate: ', self.gridState

   def decreaseLoop(self):
      self.nx -= 1
      self.gridState = self.gridState[:self.nx,:]
      self.diff = self.diff[:self.nx,:]
      self.stepVol = self.stepVol[:self.nx]
      liblo.send(broadcast, self.name+'/cmd/loopc', self.nx)
      if debug: print 'Sequencer, decreaseLoop, new gridstate: ', self.gridState

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
      elif pathlist[2]=='more':
         if arg[0]==1: self.increaseLoop()
      elif pathlist[2]=='fewer':
         if arg[0]==1: self.decreaseLoop()

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

   def setTonality(self, tonality):
      self.instrument.setTonality(tonality)

   def takeStep(self):
      self.advance()
      self.play()

   def play(self):
      notes = np.where(self.gridState[self.step,:]==1)[0]
      for note in notes:
         amp=[lr*self.globalVol*self.stepVol[self.step]*self.noteVol[note] for lr in self.seqVol]
         self.instrument.play(note, amp)

   def handleMixer(self, pathlist, arg):
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
            liblo.send(broadcast, self.name+'/button/SEQ/'+str(xwhere[i])+'/'+str(ywhere[i]), value)

   def sendDiff_bundle(self):
      xwhere, ywhere = np.where(self.diff != 0)
      n = len(xwhere)
      if n>0:
         difflist = []
         for i in range(n):
            value = int(self.diff[xwhere[i],ywhere[i]]==1)
            difflist += [xwhere[i],ywhere[i],value]
         liblo.send(broadcast, '/mutation/diff', difflist)

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
            liblo.send(broadcast, self.name+'/button/SEQ/'+str(i)+'/'+str(j), 0)

class DirectNotePlayer():
   """
   DirectNotePlayer class
   """

   def __init__(self, instrument, dpVol=0.25):
      self.globalVol = 0.5
      self.instrument = instrument
      self.dpVol = [dpVol]*2
      self.broadcast = liblo.Address(9002)

   def handleGlobalVol(self, pathlist, arg):
      self.globalVol = arg[0]

   def handleXY(self, pathlist, arg):
      if debug: print 'DirectNotePlayer, handleXY: ', pathlist, arg
      x = arg[0]
      y = arg[1]
      if pathlist[2]=='thexy':
         self.instrument.handleXY(x,y)

   def handleButton(self, pathlist, arg):
      if debug: print 'DirectNotePlayer, handleButton: ', pathlist, arg
      if pathlist[2]=='note':
         note = int(pathlist[3])
         state = arg[0]
         if (state == 1):
           amp=[lr*self.globalVol for lr in self.dpVol]
           self.instrument.play(note, amp)

   def handleSlider(self, pathlist, arg):
      if debug: print 'DirecNotePlayer, handleSlider: ', pathlist, arg

   def setName(self, name):
      self.name = name

   def followMetro(self, metro):
      pass

   def setTonality(self, tonality):
      self.instrument.setTonality(tonality)

   def takeStep(self):
      pass

   def play(self):
      pass

   def handleMixer(self, pathlist, arg):
      pan = arg[0]
      amp = arg[1]
      mul = [amp*(1.-pan), amp*pan]
      self.dpVol = mul

   def clear(self):
      pass

class DroneFace():
   """
   Drone interface class
   """

   def __init__(self, key, verbose=False):
      self.globalVol = 0.5
      fund = pyo.midiToHz(key)
      self.freqs = [i*fund for i in range(1,5)]
      self.ratios = [5,4,3,2]
      self.indices = [0.5]*4
      self.relativeMuls = [0.15, 0.15, 0.30, 0.22]
      self.muls = [0*rm for rm in self.relativeMuls]
      self.dindices = [0]*4
      self.voices = []
      for i in range(4):
         j=i+1
         voice=pyo.FM(carrier=[self.freqs[i],self.freqs[i]]).out()
         voice.setRatio(self.ratios[i])
         voice.setIndex(self.indices[i])
         voice.setMul(self.muls[i])
         self.voices.append(voice)
      self.speed=1./50
      self.verbose = verbose
      self.metro_accu = pyo.Metro(time=0.01).play()
      self.callback = pyo.TrigFunc(self.metro_accu, self.update)
      self.automation = [0,0,0,0] # 0 is nothing, 1 is linear, 2 is elliptical, 3 is homewardBound
      self.t = 0.
      self.dt = 0.01
      self.pos = self.indices[:]
      self.broadcast = liblo.Address('192.168.1.133', 9002)

   def setName(self, name):
      self.name = name

   def followMetro(self, metro):
      pass

   def setTonality(self, tonality):
      pass

   def update(self):
      self.t = (self.t + self.dt)%(2*np.pi)
      for i in range(4):
         if self.automation[i]==0: # no automation
            pass
         elif self.automation[i]==1: # linear
            self.indices[i] = (np.sin(self.t)/4+1)*self.pos[i]
         elif self.automation[i]==2: # elliptical
            if (i==0) or (i==2):
               self.indices[i] = (np.cos(self.t)/4+1)*self.pos[i]
            else:
               self.indices[i] = (np.sin(self.t)/4+1)*self.pos[i]
         elif self.automation[i]==3: # homewardBound
            self.indices[i] = self.indices[i]*(1.-self.speed)
         self.voices[i].setIndex(self.indices[i])
      if self.automation[:2] != [0,0]:
         liblo.send(broadcast, self.name+'/xy/L', self.indices[0]/5, self.indices[1]/5)
      if self.automation[2:] != [0,0]:
         liblo.send(broadcast, self.name+'/xy/R', self.indices[2]/5, self.indices[3]/5)

   def handleXY(self, pathlist, arg):
      if debug: print 'DroneFace, handleXY: ', pathlist, arg
      x = arg[0]*5
      y = arg[1]*5
      if pathlist[2]=='L':
         self.handleXY_L(x,y)
      elif pathlist[2]=='R':
         self.handleXY_R(x,y)
      if debug: print 'Automation state: ', self.automation

   def handleXY_L(self, x, y):
      self.automation[:2] = [0, 0]
      if debug: print 'DroneFace, handleXY_L: ', x, y
      self.indices[0], self.indices[1] = x, y
      for i in range(2):
         self.voices[i].setIndex(self.indices[i])

   def handleXY_R(self, x, y):
      self.automation[2:] = [0, 0]
      if debug: print 'DroneFace, handleXY_R: ', x, y
      self.indices[2], self.indices[3] = x, y
      for i in range(2,4):
         self.voices[i].setIndex(self.indices[i])

   def handleSlider(self, pathlist, arg):
      pass

   def handleButton(self, pathlist, arg):
      if debug: print 'Drone, handleButton: ', pathlist, arg
      if pathlist[2]=='L':
         if pathlist[3]=='0':  # homeward bound
            if arg[0]==1:
               self.automation[:2] = [3, 3]
         elif pathlist[3]=='1': # linear
            if arg[0]==1:
               self.pos[:2] = self.indices[:2]
               self.automation[:2] = [1, 1]
         elif pathlist[3]=='2': # circular
            if arg[0]==1:
               self.pos[:2] = self.indices[:2]
               self.automation[:2] = [2, 2]
      elif pathlist[2]=='R':
         if pathlist[3]=='0':  # homeward bound
            if arg[0]==1:
               self.automation[2:] = [3, 3]
         elif pathlist[3]=='1': # linear
            if arg[0]==1:
               self.pos[2:] = self.indices[2:]
               self.automation[2:] = [1, 1]
         elif pathlist[3]=='2': # circular
            if arg[0]==1:
               self.pos[2:] = self.indices[2:]
               self.automation[2:] = [2, 2]
      if debug: print 'Automation state: ', self.automation

   def handleGlobalVol(self, pathlist, arg):
      self.globalVol = arg[0]
      for i in range(4):
         self.voices[i].setMul([lr*self.relativeMuls[i]*self.globalVol for lr in self.pan])

   def handleMixer(self, pathlist, arg):
      if debug: print 'DroneFace, handleMCP: ', pathlist, arg
      self.pan = [arg[1]*(1.-arg[0]), arg[1]*arg[0]]
      for i in range(4):
         self.voices[i].setMul([lr*self.relativeMuls[i]*self.globalVol/5 for lr in self.pan])


class Toner():

   def __init__(self):
      pass

   def handleButton(self, pathlist, arg):
      if debug: print 'Toner, handleButton: ', pathlist, arg
      if (pathlist[2] == "12tones"):
         self.tonality.updateScale(int(pathlist[3]), arg[0])
      elif (pathlist[2] == "degrees"):
         self.tonality.updateNad(int(pathlist[3]), arg[0])
      elif (pathlist[2] == "curtone"):
         if arg[0]==1:
            degree = int(pathlist[3])
            self.tonality.updateDegree(degree)
            for i in range(12):
               if i != degree:
                  liblo.send(broadcast, self.name+'/button/curtone/'+str(i), 0)

   def setName(self, name):
      self.name = name

   def followMetro(self, metro):
      pass

   def setTonality(self, tonality):
      self.tonality = tonality
      for i in self.tonality.scale:
         liblo.send(broadcast, self.name+'/button/12tones/'+str(i), 1)
      for i in self.tonality.nad:
         liblo.send(broadcast, self.name+'/button/degrees/'+str(i), 1)
      liblo.send(broadcast, self.name+'/button/curtone'+str(self.tonality.degree), 1)

   def handleGlobalVol(self, pathlist, arg):
      pass

   def handleXY(self, pathlist, arg):
      pass

   def handleSlider(self, pathlist, arg):
      pass

