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
         'button' : self.interface.handleButton,
         'slider' : self.interface.handleSlider,
         'xy' : self.interface.handleXY
         }

   def handleMsg(self, pathlist, arg):
      if debug: print 'Player, handleMsg: ', pathlist, arg
      try:
         self.controlType[pathlist[1]](pathlist, arg)
      except KeyError:
         print 'Player, handleMsg: Unbound control type!'

   def handleXY(self, pathlist, arg):
      if debug: print 'Player, handleXY: ', pathlist, arg
      x = arg[0]
      y = arg[1]
      if pathlist[2]=='L':
         self.interface.handleXY_L(x,y)
      elif pathlist[2]=='R':
         self.interface.handleXY_R(x,y)
      elif pathlist[2]=='thexy':
         self.interface.instrument.handleXY(x,y)

   def handleButton(self, pathlist, arg):
      if debug: print 'Player, handleButton: ', pathlist, arg
      if pathlist[2]=='SEQ':
         step = int(pathlist[3])
         note = int(pathlist[4])
         state = arg[0]
         self.interface.updateGridState(step, note, state)
      elif pathlist[2]=='DFT':
         self.interface.instrument.handleDFT(arg[0])
      elif pathlist[2]=='conway':
         self.interface.conway = (arg[0]==1)
      else:
         self.interface.handleButton(pathlist, arg)

   def handleSlider(self, pathlist, arg):
      if debug: print 'Player, handleSlider: ', pathlist, arg
      if pathlist[2]=='V':
         if pathlist[3]=='2':
            slider = int(pathlist[4])
            value = arg[0]
            self.interface.instrument.handleRow2(slider, value)
         elif pathlist[3]=='1':
            step = int(pathlist[4])
            vol = arg[0]
            self.interface.updateStepVol(step, vol)
      elif pathlist[2]=='H':
         note = int(pathlist[3])
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
      if pathlist[0]=='mixer':
         self.handleMixer(pathlist, arg)
      else:
         try:
            self.players[pathlist[0]].handleMsg(pathlist, arg)
         except KeyError:
            print 'JamServer, routeByName: Player not found!'
      
   def updateMetro(self, bpm):
      self.metro.setTime(15./bpm)

   def addPlayer(self, player):
      player.interface.followMetro(self.metro)
      self.players[player.name] = player

   def handleMixer(self, pathlist, arg):
      if debug: print 'JamServer, handleMCP: ', pathlist, arg
      if pathlist[1]=='xy':
         self.players[pathlist[2]].interface.handleMixer(pathlist, arg)
      elif pathlist[1]=='slider':
         if pathlist[2]=='tempo':
            bpm = 60 + 120*arg[0]
            self.metro.setTime(15./bpm)
         elif pathlist[2]=='volume':
            for player in self.players.values():
               player.interface.handleGlobalVol(pathlist, arg)
   

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

   if 'verbose' in sys.argv:
      print 'Setting verbose = True'
      verbose = True
   else:
      print 'Setting verbose = False'
      verbose = False

   # distribute global variables
   for module in modules:
      module.debug = debug
      module.jack = jack
      module.verbose = verbose


   jamscale=scales.globalscale

   jamserver = JamServer()
   jamserver.addPlayer(Player('tr909', ix.Sequencer(inst.Sampler(smp.tr909), seqVol=0.15)))
   jamserver.addPlayer(Player('rx21Latin', ix.Sequencer(inst.Sampler(smp.rx21Latin), seqVol=0.15)))
   jamserver.addPlayer(Player('dundunba', ix.Sequencer(inst.Sampler(smp.dundunba), seqVol=0.15, nnotes=4)))
   #jamserver.addPlayer(Player('linndrum', ix.Sequencer(inst.Sampler(smp.linndrum), seqVol=0.15)))
   #jamserver.addPlayer(Player('koto', ix.Sequencer(inst.Sampler(smp.koto), seqVol=0.15)))
   #jamserver.addPlayer(Player('rhodes', ix.Sequencer(inst.Sampler(smp.rhodes), seqVol=0.15)))
   #jamserver.addPlayer(Player('chimes', ix.Sequencer(inst.Sampler(smp.chimes), seqVol=0.15)))
   jamserver.addPlayer(Player('FM_hi', ix.Sequencer(inst.PolySynth(voice=synths.FM, key=72, scale=jamscale), seqVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('FM_lo', ix.Sequencer(inst.PolySynth(voice=synths.FM, key=24, scale=jamscale), seqVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('additive_hi', ix.Sequencer(inst.PolySynth(voice=synths.Additive, key=60, scale=jamscale), seqVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('additive_lo', ix.Sequencer(inst.PolySynth(voice=synths.Additive, key=36, scale=jamscale), seqVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('drone', ix.DroneFace(38, verbose=verbose)))
   jamserver.addPlayer(Player('toner', ix.ChordExplorer(scaletomod=scales.globscale)))

   print ''
   print 'Setup successful! Now listening for messages...'
   while True:
      jamserver.OSCserver.recv(1) # 1 ms refresh rate

