import serial, pyo, sys
from instruments import *
from poly import Poly
from tonality import Tonality
from synths import *
from samplepacks import *

if 'debug' in sys.argv:
    debug = True
else:
    debug = False


s = pyo.Server().boot()
s.start()


if 'cuttlefish' in sys.argv:
    print 'SETTING CUTTLEFISH MODE'
    instrument = PolySynth(FM, order=24)
    #instrument.setTonality(Tonality([0,2,4,5,7,9,11]))
    instrument.setTonality(Tonality(range(12)))

    mapping = {'a':0,
               'b':1,
               'c':2,
               'd':3,
               'e':4,
               'f':5,
               'g':6,
               'h':7,
               'i':8,
               'j':9,
               'k':10,
               'l':11,
               'm':12,
               'n':13,
               'o':14,
               'p':15,
               'q':16,
               'r':17,
               's':18,
               't':19,
               'u':20,
               'v':21,
               'w':22,
               'x':23}
elif 'dundunba' in sys.argv:
    instrument = Sampler(dundunba)
    mapping = {'a':0,
                'b':1,
                'c':2,
                'd':3}

###

arduino = serial.Serial('/dev/ttyACM3', 9600)
while True:
    msg = arduino.readline()
    print msg
    if msg[0]=='K':
        try:
            instrument.play(mapping[msg[1]], 0.25)
            print 'played: ', msg[1:]
        except KeyError:
	    #pass
            print 'Unmapped: ', msg
    elif msg[0]=='N':
        instrument.handleKnob(float(msg[1:]))

