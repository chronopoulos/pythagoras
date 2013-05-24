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

if 'jack' in sys.argv:
    s = pyo.Server(audio='jack').boot()
else:
    s = pyo.Server().boot()
s.start()

class SoundFlower():

    def __init__(self):
        self.instruments = []

        self.FMchromatic = inst.BrutePoly(order=24, key=30)
        self.FMchromatic.setTonality(Tonality(range(12)))
        self.instruments.append(self.FMchromatic)

        """
        self.FMpentatonic = inst.BrutePoly(order=6, key=60)
        self.FMpentatonic.setTonality(Tonality([0,2,4,7,9]))
        self.instruments.append(self.FMpentatonic)
        """

        self.tr909 = inst.Sampler(packs.tr909, amp=1.5)
        self.instruments.append(self.tr909)

        self.rhodes = inst.Sampler(packs.rhodes, amp=1.5)
        self.instruments.append(self.rhodes)

        self.koto = inst.Sampler(packs.koto)
        self.instruments.append(self.koto)

        self.chimes = inst.Sampler(packs.chimes)
        self.instruments.append(self.chimes)

        self.tr606 = inst.Sampler(packs.tr606, amp=1.5)
        self.instruments.append(self.tr606)

        self.tr707 = inst.Sampler(packs.tr707, amp=1.5)
        self.instruments.append(self.tr707)

        self.tr808 = inst.Sampler(packs.tr808, amp=1.5)
        self.instruments.append(self.tr808)

        self.myVol = 1.

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

        self.mapping1 = {'a':(1,0),
                       'b':(1,1),
                       'c':(1,2),
                       'd':(1,3),
                       'e':(1,4),
                       'f':(1,5),
                       'g':(2,0),
                       'h':(2,1),
                       'i':(2,2),
                       'j':(2,3),
                       'k':(2,4),
                       'l':(2,5),
                       'm':(3,0),
                       'n':(3,1),
                       'o':(3,2),
                       'p':(3,3),
                       'q':(3,4),
                       'r':(3,5),
                       's':(4,0),
                       't':(4,1),
                       'u':(4,2),
                       'v':(4,3),
                       'w':(4,4),
                       'x':(4,5)}

        self.mapping2 = {'a':(1,0),
                       'b':(1,1),
                       'c':(1,2),
                       'd':(1,3),
                       'e':(1,4),
                       'f':(1,5),
                       'g':(5,0),
                       'h':(5,1),
                       'i':(5,2),
                       'j':(5,3),
                       'k':(5,4),
                       'l':(5,5),
                       'm':(6,0),
                       'n':(6,1),
                       'o':(6,2),
                       'p':(6,3),
                       'q':(6,4),
                       'r':(6,5),
                       's':(7,0),
                       't':(7,1),
                       'u':(7,2),
                       'v':(7,3),
                       'w':(7,4),
                       'x':(7,5)}

        self.mapping = self.mapping1

    def play(self, letter):
        i,n = self.mapping[letter]
        self.instruments[i].play(n, 0.25*self.myVol)

    def handleKnobA(self, value):
        self.FMchromatic.handleKnobA(value)
        #self.FMpentatonic.handleKnobA(value)

    def handleKnobB(self, value):
        self.myVol = value/1000.

    def handleKnobC(self, value):
        pass

    def handleSelector(self, letter):
        if letter=='a':
            self.mapping = self.mapping0
            print 'Mode 0 selected'
        elif letter=='b':
            self.mapping = self.mapping1
            print 'Mode 1 selected'
        elif letter=='c':
            self.mapping = self.mapping2
            print 'Mode 2 selected'
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
    elif msg[0]=='S':
        soundflower.handleSelector(msg[1])

