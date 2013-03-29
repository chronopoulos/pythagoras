import pyo, liblo
import interfaces as ix
import instruments as inst
import samplepacks as smp
import scales, synths
import sys

modules = [ix, inst, smp, scales, synths]

class Player():

   def __init__(self, name, interface):
      self.name = name
      self.interface = interface
      self.interface.setName(self.name)
      self.controlType = {
         'button' : self.handleButton,
         'slider' : self.handleSlider,
         'xy' : self.handleXY
         }

   def handleMsg(self, pathlist, arg):
      if debug: print 'WebApp2Sequencer, handleMsg: ', pathlist, arg
      try:
         self.controlType[pathlist[1]](pathlist, arg)
      except:
         pass

   def handleXY(self, pathlist, arg):
      if debug: print 'WebApp2Sequencer, handleXY: ', pathlist, arg
      x = arg[0]
      y = arg[1]
      self.interface.instrument.handleXY(x,y)

   def handleButton(self, pathlist, arg):
      if debug: print 'WebApp2Sequencer, handleButton: ', pathlist, arg
      if pathlist[2]=='SEQ':
         step = int(pathlist[4])-1
         note = int(pathlist[3])-1
         state = arg[0]
         self.interface.updateGridState(step, note, state)
      elif pathlist[2]=='DFT':
         self.interface.instrument.handleDFT(arg[0])
      elif pathlist[2]=='conway':
         self.interface.conway = (arg[0]==1)

   def handleSlider(self, pathlist, arg):
      if debug: print 'WebApp2Sequencer, handleSlider: ', pathlist, arg
      if pathlist[2]=='V':
         if pathlist[3]=='1':
            slider = int(pathlist[4])-1
            value = arg[0]
            self.interface.instrument.handleRow2(slider, value)

         elif pathlist[3]=='2':
            step = int(pathlist[4])-1
            vol = arg[0]
            self.interface.updateStepVol(step, vol)
      elif pathlist[2]=='H':
         note = int(pathlist[3])-1
         vol = arg[0]
	 if debug:
	   print 'about to update notevol with: ', note, vol
         self.interface.updateNoteVol(note, vol)



class JamServer():

   def __init__(self):
      self.OSCserver = liblo.Server(8000)
      self.OSCserver.add_method(None, None, self.routeByName)
      self.players = {} # name:player dictionary
      if jack:
         self.AudioServer = pyo.Server(audio='jack').boot()
      else:
         self.AudioServer = pyo.Server().boot()
      self.AudioServer.start()
      self.metro = pyo.Metro(time=15./120.).play()

   def routeByName(self, pathstr, arg, typestr, server, usrData):
      if debug: print 'JamServer, routeByName: ', pathstr, arg
      pathlist = pathstr.split('/')
      try:
         self.players[pathlist[0]].handleMsg(pathlist, arg)
      except:
         pass
      
   def updateMetro(self, bpm):
      self.metro.setTime(15./bpm)

   def addPlayer(self, player):
      player.interface.followMetro(self.metro)
      self.players[player.name] = player
   

############

if __name__ == '__main__':

   if 'debug' in sys.argv:
      print 'Setting debug = True'
      debug = True
   else:
      print 'Setting debug = False'
      debug = False

   if 'jack' in sys.argv:
      print 'Setting jack = True'
      jack = True
   else:
      print 'Setting jack = False'
      jack = False

   # distribute global variables
   for module in modules:
      module.debug = debug
      module.jack = jack


   jamserver = JamServer()
   jamserver.addPlayer(Player('tr808', ix.Sequencer(inst.Sampler(smp.tr808), maxVol=0.15)))
   jamserver.addPlayer(Player('rx21Latin', ix.Sequencer(inst.Sampler(smp.rx21Latin), maxVol=0.15)))
   jamserver.addPlayer(Player('linndrum', ix.Sequencer(inst.Sampler(smp.linndrum), maxVol=0.15)))
   jamserver.addPlayer(Player('koto', ix.Sequencer(inst.Sampler(smp.koto), maxVol=0.15)))
   jamserver.addPlayer(Player('rhodes', ix.Sequencer(inst.Sampler(smp.rhodes), maxVol=0.15)))
   jamserver.addPlayer(Player('chimes', ix.Sequencer(inst.Sampler(smp.chimes), maxVol=0.15)))
   jamserver.addPlayer(Player('FM_hi', ix.Sequencer(inst.PolySynth(voice=synths.FM, key=72), maxVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('FM_lo', ix.Sequencer(inst.PolySynth(voice=synths.FM, key=24), maxVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('additive_hi', ix.Sequencer(inst.PolySynth(voice=synths.Additive, key=60), maxVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('additive_lo', ix.Sequencer(inst.PolySynth(voice=synths.Additive, key=36), maxVol=0.25, nnotes=16)))

   print ''
   print 'Setup successful! Now listening for messages...'
   while True:
      jamserver.OSCserver.recv(1) # 1 ms refresh rate

