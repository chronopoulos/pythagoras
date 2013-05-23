import serial, pyo, sys, os
from poly import Poly
from tonality import Tonality
import instruments as inst
import synths
import samplepacks as packs

# Parse Arguments

try:
    if sys.argv[1][:5]=='/dev/':
        deviceFile = sys.argv[1]
except IndexError:
    deviceFile = '/dev/ttyACM0'

if 'debug' in sys.argv:
    debug = True
else:
    debug = False


# Start Audio Server

s = pyo.Server().boot()
s.start()

class SoundFlower():

    def __init__(self):
        self.instruments = []

        self.brutepoly = inst.BrutePoly(order=6, key=60)
        self.brutepoly.setTonality(Tonality([0,2,4,7,9]))
        self.instruments.append(self.brutepoly)

        self.rhodes = inst.Sampler(packs.rhodes)
        self.instruments.append(self.rhodes)

        self.koto = inst.Sampler(packs.koto)
        self.instruments.append(self.koto)

        self.chimes = inst.Sampler(packs.chimes)
        self.instruments.append(self.chimes)

        self.mapping0 = {'a':(0,0),
                       'b':(0,1),
                       'c':(0,2),
                       'd':(0,3),
                       'e':(0,4),
                       'f':(0,5),
                       'g':(0,6),
                       'h':(0,7),
                       'i':(0,8),
                       'j':(0,9),
                       'k':(0,10),
                       'l':(0,11),
                       'm':(0,12),
                       'n':(0,13),
                       'o':(0,14),
                       'p':(0,15),
                       'q':(0,16),
                       'r':(0,17),
                       's':(0,18),
                       't':(0,19),
                       'u':(0,20),
                       'v':(0,21),
                       'w':(0,22),
                       'x':(0,23)}

        self.mapping1 = {'a':(0,0),
                       'b':(0,1),
                       'c':(0,2),
                       'd':(0,3),
                       'e':(0,4),
                       'f':(0,5),
                       'g':(1,0),
                       'h':(1,1),
                       'i':(1,2),
                       'j':(1,3),
                       'k':(1,4),
                       'l':(1,5),
                       'm':(2,0),
                       'n':(2,1),
                       'o':(2,2),
                       'p':(2,3),
                       'q':(2,4),
                       'r':(2,5),
                       's':(3,0),
                       't':(3,1),
                       'u':(3,2),
                       'v':(3,3),
                       'w':(3,4),
                       'x':(3,5)}

        self.mapping = self.mapping1

    def play(self, letter):
        i,n = self.mapping[letter]
        self.instruments[i].play(n, 0.25)

    def handleKnobA(self, value):
        self.brutepoly.handleKnobA(value)

    def handleKnobB(self, value):
        pass

    def handleKnobC(self, value):
        pass

##

soundflower = SoundFlower()
arduino = serial.Serial(deviceFile, 9600)
while True:
    msg = arduino.readline()
    print msg
    if msg[0]=='K':
        try:
            soundflower.play(msg[1])
        except KeyError:
            pass
            #print 'Unmapped: ', msg
    elif msg[0]=='A':
        soundflower.handleKnobA(float(msg[1:]))
    elif msg[0]=='B':
        soundflower.handleKnobB(float(msg[1:]))
    elif msg[0]=='C':
        soundflower.handleKnobC(float(msg[1:]))

