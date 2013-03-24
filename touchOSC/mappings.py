import liblo

class Phone2Sequencer():

   def __init__(self, phoneIPstring, phonePort, seq, seqPort):
      self.ui = liblo.Address(phoneIPstring, phonePort)
      self.interface = seq
      self.interface.setUI(self.ui)
      self.server = liblo.Server(seqPort)
      self.server.add_method(None, None, self.handleMsg)
      self.bindings = {
         ('1', 'toggle1') : self.interface.updateConway,
         ('2', 'multitoggle') : self.interface.updateGridState,
         ('2', 'multifader') : self.interface.updateStepVol,
         ('3', 'rotary1') : self.interface.updateNoteVol,
         ('3', 'rotary2') : self.interface.updateNoteVol,
         ('3', 'rotary3') : self.interface.updateNoteVol,
         ('3', 'rotary4') : self.interface.updateNoteVol,
         ('3', 'rotary5') : self.interface.updateNoteVol,
         ('3', 'rotary6') : self.interface.updateNoteVol,
         ('4', 'xy') : self.handleXY
         }

   def handleXY(self, pathlist, arg):
      x = arg[1]
      y = arg[0]
      degree = int(x*10)+1
      index = 1000*y
      for voice in self.interface.instrument.voices:
         voice.setDegree(degree)
         voice.setModIndex(index)

   def handleMsg(self, pathstr, arg, typestr, server, usrData):
      if debug: print 'Phone2Sequencer, handleMsg: ', pathstr, arg
      pathlist = pathstr.split('/')
      if len(pathlist)>=3:
         try:
            self.bindings[(pathlist[1],pathlist[2])](pathlist, arg)
         except:
            pass
      else:
         return

class Phone2Keyboard():

   def __init__(self, kb, kbPort):
      self.interface = kb
      self.server = liblo.Server(kbPort)
      self.server.add_method(None, None, self.handleMsg)
      self.bindings = {
         ('1', 'push1') : self.interface.updatePressed,
         ('1', 'push2') : self.interface.updatePressed,
         ('1', 'push3') : self.interface.updatePressed,
         ('1', 'push4') : self.interface.updatePressed,
         ('1', 'push5') : self.interface.updatePressed,
         ('1', 'push6') : self.interface.updatePressed,
         ('1', 'push7') : self.interface.updatePressed,
         ('1', 'push8') : self.interface.updatePressed,
         ('1', 'push9') : self.interface.updatePressed,
         ('1', 'push10') : self.interface.updatePressed,
         ('1', 'push11') : self.interface.updatePressed,
         ('1', 'push12') : self.interface.updatePressed
         }

   def handleMsg(self, pathstr, arg, typestr, server, usrData):
      if debug: print 'Phone2Keyboard, handleMsg: ', pathstr, arg
      pathlist = pathstr.split('/')
      if len(pathlist)>=3:
         try:
            self.bindings[(pathlist[1],pathlist[2])](pathlist, arg)
         except:
            pass
      else:
         return

class WebApp2Sequencer():

   def __init__(self, seq):
      self.interface = seq
      self.bindings = {
         'button' : self.handleButton,
         'slider' : self.handleSlider,
         'xy' : self.handleXY
         }

   def handleXY(self):
      if debug: print 'WebApp2Sequencer, handleXY: ', pathlist, arg

   def handleButton(self, pathlist, arg):
      if debug: print 'WebApp2Sequencer, handleButton: ', pathlist, arg
      if pathlist[2]=='SEQ':
         step = int(pathlist[4])-1
         note = int(pathlist[3])-1
         state = arg[0]
         self.interface.updateGridState(step, note, state)
      elif pathlist[2]=='DFT':
         if arg[0]==1:
            for voice in self.interface.instrument.voices:
               voice.updateWaveform()

   def handleSlider(self, pathlist, arg):
      if debug: print 'WebApp2Sequencer, handleSlider: ', pathlist, arg
      if pathlist[2]=='V':
         if pathlist[3]=='1':
            harmonic = int(pathlist[4])-1
            coeff = arg[0]
            for voice in self.interface.instrument.voices:
               voice.updateSpectrum(harmonic, coeff)
         elif pathlist[3]=='2':
            step = int(pathlist[4])-1
            vol = arg[0]
            self.interface.updateStepVol(step, vol)
      elif pathlist[2]=='H':
         note = int(pathlist[3])-1
         vol = arg[0]
         print 'about to update notevol with: ', note, vol
         self.interface.updateNoteVol(note, vol)

   def handleMsg(self, pathlist, arg):
      if debug: print 'WebApp2Sequencer, handleMsg: ', pathlist, arg
      try:
         self.bindings[pathlist[1]](pathlist, arg)
      except:
         pass

