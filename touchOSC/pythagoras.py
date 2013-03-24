import pyo, liblo
import interfaces as ifx
import instruments as inst
import samplepacks as smp
import scales, synths
import sys

modules = [ifx, inst, smp, scales, synths]

class JamServer():

   def __init__(self):
      self.interfaces = []
      if jack:
         self.AudioServer = pyo.Server(audio='jack').boot()
      else:
         self.AudioServer = pyo.Server().boot()
      self.AudioServer.start()
      self.metro = pyo.Metro(time=15./120.).play()
      
   def updateMetro(self, bpm):
      self.metro.setTime(15./bpm)

   def addInterface(self, interface):
      interface.followMetro(self.metro)
      self.interfaces.append(interface)
   

############

if __name__ == '__main__':

   if 'debug' in sys.argv:
      print 'Setting debug = True'
      debug = True
   else:
      print 'Setting debug = False'
      debug = False

   if 'jack' in sys.argv:
      print 'Setting debug = True'
      jack = True
   else:
      print 'Setting debug = False'
      jack = False

   # distribute global variables
   for module in modules:
      module.debug = debug
      module.jack = jack

##############################
# Add players here
##############################

   jamserver = JamServer()
   jamserver.addInterface(ifx.Sequencer(8001, liblo.Address('192.168.1.125',9001), inst.Sampler(smp.linndrum), maxVol=0.2))
   jamserver.addInterface(ifx.Sequencer(8002, liblo.Address('192.168.1.125',9002), inst.PolySynth(voice=synths.FM), maxVol=0.25))
   jamserver.addInterface(ifx.Keyboard(8003, liblo.Address('192.168.1.125',9003), inst.PolySynth(voice=synths.FM, scale=scales.chromatic), maxVol=0.25))


###########

   osc_refresh_rate = 0   # ms
   while True:
      for interface in jamserver.interfaces:
         interface.OSCserver.recv(osc_refresh_rate)

