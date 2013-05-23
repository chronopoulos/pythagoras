import pyo, liblo
import interfaces as ix
import instruments as inst
import samplepacks as smp
import scales, synths
import sys
from blist import sortedset

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

   def __init__(self, bpm=120, tonality=None):
      self.OSCserver = liblo.Server(8000)
      self.OSCserver.add_method(None, None, self.routeByName)
      self.players = {} # name:player dictionary
      if jack:
         self.AudioServer = pyo.Server(audio='jack').boot()
      else:
         self.AudioServer = pyo.Server().boot()
      self.AudioServer.start()
      self.metro = pyo.Metro(time=15./bpm).play()
      self.tonality = tonality

   def routeByName(self, pathstr, arg, typestr, server, usrData):
      if debug: print 'JamServer, routeByName: ', pathstr, arg
      pathlist = pathstr.split('/')
      if pathlist[0]=='mixer':
         self.handleMixer(pathlist, arg)
      else:
         try:
            self.players[pathlist[0]].handleMsg(pathlist, arg)
         except KeyError:
            print 'JamServer, routeByName: ', pathlist[0], ' Player not found!!'
      
   def updateMetro(self, bpm):
      self.metro.setTime(15./bpm)

   def addPlayer(self, player):
      player.interface.followMetro(self.metro)
      player.interface.setTonality(self.tonality)
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

class Tonality():

   def __init__(self, scale):
      self.scale = sortedset(scale)
      self.m=len(self.scale)
      self.nad = sortedset(range(self.m))
      self.n = len(self.nad)
      self.degree = 0

   def cycleScale(self,i):
      j=i%self.m
      k=i//self.m
      return k*12 + self.scale[j]

   def cycleNad(self,i):
      j=i%self.n
      k=i//self.n
      return k*self.m + self.nad[j]

   def request(self, i):
      return self.cycleScale(self.degree+self.cycleNad(i))

   def updateScale(self, index, onoff):
      if onoff==1:
         self.scale.add(index)
      else:
         self.scale.remove(index)
      self.m=len(self.scale)

   def updateNad(self, index, onoff):
      if onoff==1:
         self.nad.add(index)
      else:
         self.nad.remove(index)
      self.n = len(self.nad)

   def updateDegree(self, degree):
      self.degree = degree
   

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

   broadcast = liblo.Address(9002)
   #broadcast = liblo.Address('192.168.1.137', 9002)

   # distribute global variables
   for module in modules:
      module.debug = debug
      module.jack = jack
      module.verbose = verbose
      module.broadcast = broadcast


   jamserver = JamServer(bpm=120, tonality=Tonality([0,2,4,5,7,9,11]))
   jamserver.addPlayer(Player('dpad', ix.DirectNotePlayer(inst.Sampler(smp.tr707), dpVol=0.15)))
   jamserver.addPlayer(Player('tr909', ix.Sequencer(inst.Sampler(smp.tr909), seqVol=0.15)))
   jamserver.addPlayer(Player('rx21Latin', ix.Sequencer(inst.Sampler(smp.rx21Latin), seqVol=0.15)))
   jamserver.addPlayer(Player('dundunba', ix.Sequencer(inst.Sampler(smp.dundunba), seqVol=0.15, nnotes=4)))
   jamserver.addPlayer(Player('FM_hi', ix.Sequencer(inst.PolySynth(voice=synths.FM, key=60), seqVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('FM_lo', ix.Sequencer(inst.PolySynth(voice=synths.FM, key=24), seqVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('additive_hi', ix.Sequencer(inst.PolySynth(voice=synths.Additive, key=60), seqVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('additive_lo', ix.Sequencer(inst.PolySynth(voice=synths.Additive, key=36), seqVol=0.25, nnotes=16)))
   jamserver.addPlayer(Player('puddle', ix.Sequencer(inst.PolySynth(voice=synths.Sine, key=48), seqVol=0.25, nnotes=24)))
   jamserver.addPlayer(Player('drone', ix.DroneFace(36, verbose=verbose)))
   jamserver.addPlayer(Player('toner', ix.Toner()))


   print ''
   print 'Setup successful! Now listening for messages...'
   while True:
      jamserver.OSCserver.recv(1) # 1 ms refresh rate

