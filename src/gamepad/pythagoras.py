import pyo, os, sys
import instruments as inst
import scales, voices

modules = [inst, scales, voices]

#######################

def combineBytes(values, flip=False):
    if values[1] > 127:
        bigpart = values[1] - 255
    else:
        bigpart = values[1]
    if flip:
        return -(bigpart * 255 + values[0])/float(2**15)
    else:
        return (bigpart * 255 + values[0])/float(2**15)

class Gamepad():
    """
    guided by:
    http://upgrayd.blogspot.com/2011/03/logitech-dual-action-usb-gamepad.html
    """
    def __init__(self):
        self.pipe = open('/dev/input/js1', 'r')
        self.bindings = {
                        (1,0) : self.parse_button1,
                        (1,1) : self.parse_button2,
                        (1,2) : self.parse_button3,
                        (1,3) : self.parse_button4,
                        (1,4) : self.parse_L1,
                        (1,5) : self.parse_R1,
                        (1,6) : self.parse_L2,
                        (1,7) : self.parse_R2,
                        (2,4) : self.parse_DPLR,
                        (2,5) : self.parse_DPUD,
                        (2,0) : self.parse_LJLR,
                        (2,1) : self.parse_LJUD,
                        (2,2) : self.parse_RJLR,
                        (2,3) : self.parse_RJUD
                        }


    def parse_button1(self, values):
        if debug: print 'Gamepad, parse_button1: ', values
        try:
            self.callback_button1(values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_button2(self, values):
        if debug: print 'Gamepad, parse_button2: ', values
        try:
            self.callback_button2(values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_button3(self, values):
        if debug: print 'Gamepad, parse_button3: ', values
        try:
            self.callback_button3(values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_button4(self, values):
        if debug: print 'Gamepad, parse_button4: ', values
        try:
            self.callback_button4(values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_L1(self, values):
        if debug: print 'Gamepad, parse_L1: ', values
        try:
            self.callback_L1(values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_R1(self, values):
        if debug: print 'Gamepad, parse_R1: ', values
        try:
            self.callback_R1(values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_L2(self, values):
        if debug: print 'Gamepad, parse_L2: ', values
        try:
            self.callback_L2(values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_R2(self, values):
        if debug: print 'Gamepad, parse_R2: ', values
        try:
            self.callback_R2(values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_DPLR(self, values):
        if debug: print 'Gamepad, parse_DPLR: ', values
        if values==(255,127):
            value=1
        elif values==(0,0):
            value=0
        elif values==(1,128):
            value=-1
        try:
            self.callback_DPLR(value)
        except AttributeError:
            print 'Callback not defined'

    def parse_DPUD(self, values):
        if debug: print 'Gamepad, parse_DPUD: ', values
        if values==(255,127):
            value=-1
        elif values==(0,0):
            value=0
        elif values==(1,128):
            value=1
        try:
            self.callback_DPUD(value)
        except AttributeError:
            print 'Callback not defined'

    def parse_LJLR(self, values):
        if debug: print 'Gamepad, parse_LJLR: ', values
        value = combineBytes(values)
        try:
            self.callback_LJLR(value)
        except AttributeError:
            print 'Callback not defined'

    def parse_LJUD(self, values):
        if debug: print 'Gamepad, parse_LJUD: ', values
        value = combineBytes(values, flip=True)
        try:
            self.callback_LJUD(value)
        except AttributeError:
            print 'Callback not defined'

    def parse_RJLR(self, values):
        if debug: print 'Gamepad, parse_RJLR: ', values
        value = combineBytes(values)
        try:
            self.callback_RJLR(value)
        except AttributeError:
            print 'Callback not defined'

    def parse_RJUD(self, values):
        if debug: print 'Gamepad, parse_RJUD: ', values
        value = combineBytes(values, flip=True)
        try:
            self.callback_RJUD(value)
        except AttributeError:
            print 'Callback not defined'

    def listen(self):
        """
        Blockin infinite loop
        """
        while True:
            msg = self.pipe.read(8)
            if debug: print 'Gamepad, listen: ', [ord(char) for char in msg]
            values = (ord(msg[4]), ord(msg[5]))
            control = (ord(msg[6]), ord(msg[7]))
            try:
                self.bindings[control](values)
            except KeyError:
                print 'Gamepad, Unbound event! Control code is: ', control
            except AttributeError:
                print 'Event bound but callback undefined: ', control

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


#######################

if __name__=='__main__':

    parse_clargs()

    if jack:
        AudioServer = pyo.Server(audio='jack').boot()
    else:
        AudioServer = pyo.Server().boot()
    AudioServer.start()

    ####

    metro_rhythm = pyo.Metro(time=15./120).play()
    metro_accu = pyo.Metro(time=0.01).play()

    controller = Gamepad()

    # Drone instrument
    drone = inst.Drone(27.5, metro_accu, verbose=verbose)
    controller.callback_LJLR = drone.handle_LJLR
    controller.callback_LJUD = drone.handle_LJUD
    controller.callback_RJLR = drone.handle_RJLR
    controller.callback_RJUD = drone.handle_RJUD
    controller.callback_L1 = drone.handle_L1
    controller.callback_R1 = drone.handle_R1
    controller.callback_L2 = drone.handle_L2
    controller.callback_R2 = drone.handle_R2

    controller.callback_button1 = drone.handle_button1
    controller.callback_button2 = drone.handle_button2
    controller.callback_button3 = drone.handle_button3
    controller.callback_button4 = drone.handle_button4

    controller.callback_DPLR = drone.handle_DPLR
    controller.callback_DPUD = drone.handle_DPUD

    # Wub instrument
    """
    wub = inst.Wub(27.5, metro_rhythm)
    controller.callback_RJLR = wub.handle_RJLR
    controller.callback_RJUD = wub.handle_RJUD
    """

    controller.listen()

