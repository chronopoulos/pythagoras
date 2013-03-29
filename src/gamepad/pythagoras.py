import pyo, os, sys
audioserver = pyo.Server().boot()
audioserver.start()

if 'debug' in sys.argv:
    print 'Setting debug = True'
    debug = True
else:
    print 'Setting debug = False'
    debug = False


class Follower():

    def __init__(self, init, refresh):
        self.value = init
        self.refresh = refresh
        self.step = 0
        self.metro = pyo.Metro(time=refresh).play()
        self.callback = pyo.TrigFunc(self.metro, self.increment)

    def increment(self):
        self.value += self.step
        print 'Current value, increment: ', self.value, self.step

    def updateStep(self, step):
        self.step = step


class Sampler():
    """
    Sampler class
    """

    def __init__(self, pack):
        """
        Pack should simply be a list of filenames.
        pyo.SfPlayer objects are created upon instantiation.
        This way, multiple Sampler instances can have their own bitstreams.
        """
        self.notes = []
        for filename in pack:
            self.notes.append(pyo.SfPlayer(filename, speed=[1,1]))

    def play(self, note, amp):
        self.notes[note].setMul(amp)
        self.notes[note].out()

class Granular():

    def __init__(self):
        self.snd = SndTable('../../samples/vocals/iamavisitor.wav')
        self.env = HannTable()
        self.pos = Phasor(snd.getRate()*.25, 0, snd.getSize())
        self.dur = Noise(.001, .1)
        self.output = Granulator(snd, env, [1, 1.001], pos, dur, 24, mul=.1).out()


def combineBytes(values):
    if values[1] > 127:
        bigpart = values[1] - 255
    else:
        bigpart = values[1]
    return (bigpart * 255 + values[0])/float(2**15)


class Gamepad():
    """
    guided by:
    http://upgrayd.blogspot.com/2011/03/logitech-dual-action-usb-gamepad.html
    """
    def __init__(self):
        self.pipe = open('/dev/input/js1', 'r')
        self.bindings = {
                        (1,0) : self.handle_button1,
                        (1,1) : self.handle_button2,
                        (1,2) : self.handle_button3,
                        (1,3) : self.handle_button4,
                        (2,4) : self.handle_DPadLeftRight,
                        (2,5) : self.handle_DPadUpDown,
                        (2,0) : self.handle_LJoyLeftRight,
                        (2,1) : self.handle_LJoyUpDown,
                        (2,2) : self.handle_RJoyLeftRight,
                        (2,3) : self.handle_RJoyUpDown
                        }


    def handle_button1(self, values):
        if debug: print 'handle_button1: ', values
        if values[0]: sampler.play(0,1.)

    def handle_button2(self, values):
        if debug: print 'handle_button2: ', values
        if values[0]: sampler.play(1,1.)

    def handle_button3(self, values):
        if debug: print 'handle_button3: ', values
        if values[0]: sampler.play(2,1.)

    def handle_button4(self, values):
        if debug: print 'handle_button4: ', values
        if values[0]: sampler.play(3,1.)

    def handle_DPadLeftRight(self, values):
        if debug: print 'handle_DPadLeftRight: ', values

    def handle_DPadUpDown(self, values):
        if debug: print 'handle_DPadUpDown: ', values

    def handle_LJoyLeftRight(self, values):
        if debug: print 'handle_LJoyLeftRight: ', values
        value = combineBytes(values)

    def handle_LJoyUpDown(self, values):
        if debug: print 'handle_LJoyUpDown: ', values
        value = combineBytes(values)
        f.updateStep(value)

    def handle_RJoyLeftRight(self, values):
        if debug: print 'handle_RJoyLeftRight: ', values
        value = combineBytes(values)

    def handle_RJoyUpDown(self, values):
        if debug: print 'handle_RJoyUpDown: ', values
        value = combineBytes(values)

    def listen(self):
        while True:
            msg = self.pipe.read(8)
            if debug: print 'Gamepad, listen: ', [ord(char) for char in msg]
            values = (ord(msg[4]), ord(msg[5]))
            control = (ord(msg[6]), ord(msg[7]))
            try:
                self.bindings[control](values)
            except KeyError:
                print 'Unbound event! Control code is: ', control


if __name__=='__main__':
    
    tr909 = [
    '../../samples/drums/tr909/kick.wav',
    '../../samples/drums/tr909/snare.wav',
    '../../samples/drums/tr909/closedhat.wav',
    '../../samples/drums/tr909/openhat.wav',
    '../../samples/drums/tr909/clap.wav',
    '../../samples/drums/tr909/ride.wav'
    ]

    sampler = Sampler(tr909)

    f = Follower(100,0.01)

    controller = Gamepad()
    controller.listen()

