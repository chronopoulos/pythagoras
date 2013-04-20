import pyo, os, sys, threading, time
import instruments as inst
import scales, voices
import logitech 
import samplepacks as samp

modules = [inst, scales, voices, logitech]

def parse_clargs():
    global debug, jack, verbose

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
        module.jack = verbose

class Player():

    def __init__(self, name, controller, instrument):
        self.name = name
        self.controller = controller
        self.instrument = instrument
        self.controller.handlers = self.instrument.handlers

    def listen(self):
        self.controller.listen()


class PlayerThread(threading.Thread):

    def __init__(self, player):
        threading.Thread.__init__(self)
        self.player = player

    def run(self):
        self.player.listen()

    def startKingpin(self):
        self.player.listen()
        

class JamServer():

    def __init__(self, bpm=120, refresh=0.01):
        """
        bpm: beats per minute of the global metronome
        refresh: inverse control rate in ms
        """
        if jack:
            self.audioServer = pyo.Server(audio='jack').boot()
        else:
            self.audioServer = pyo.Server().boot()
        self.audioServer.start()
        self.metro_rhythm = pyo.Metro(time=15./bpm).play()
        self.metro_ctrl = pyo.Metro(time=refresh).play()
        self.playerthreads = []

    def addPlayer(self, player):
        player.instrument.followMetro_rhythm(self.metro_rhythm)
        player.instrument.followMetro_ctrl(self.metro_ctrl)
        self.playerthreads.append(PlayerThread(player))

    def start(self):
        """
        All players must be added before calling this method
        """
        for thread in self.playerthreads[1:]:
            thread.setDaemon(True)
            thread.start()
        self.playerthreads[0].startKingpin()


#######################

if __name__=='__main__':

    parse_clargs()

    ####

    jamserver = JamServer(bpm=100)
    jamserver.addPlayer(Player('rhythmbox', logitech.Rainbow('/dev/input/js1'), inst.RhythmBox(inst.Sampler(samp.dundunba))))
    #jamserver.addPlayer(Player('drone', '/dev/input/js1', inst.Drone(36)))
    jamserver.addPlayer(Player('droplets', '/dev/input/js1', inst.Droplets()))
    #jamserver.addPlayer(Player('chris', logitech.Rainbow('/dev/input/js2'), inst.Melodizer()  ))
    jamserver.start()

