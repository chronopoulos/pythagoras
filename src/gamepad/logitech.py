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
    def __init__(self, jsfile):
        self.pipe = open(jsfile, 'r')
        self.parsers = {
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
            self.handlers['B1'](values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_button2(self, values):
        if debug: print 'Gamepad, parse_button2: ', values
        try:
            self.handlers['B2'](values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_button3(self, values):
        if debug: print 'Gamepad, parse_button3: ', values
        try:
            self.handlers['B3'](values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_button4(self, values):
        if debug: print 'Gamepad, parse_button4: ', values
        try:
            self.handlers['B4'](values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_L1(self, values):
        if debug: print 'Gamepad, parse_L1: ', values
        try:
            self.handlers['L1'](values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_R1(self, values):
        if debug: print 'Gamepad, parse_R1: ', values
        try:
            self.handlers['R1'](values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_L2(self, values):
        if debug: print 'Gamepad, parse_L2: ', values
        try:
            self.handlers['L2'](values[0])
        except AttributeError:
            print 'Callback not defined'

    def parse_R2(self, values):
        if debug: print 'Gamepad, parse_R2: ', values
        try:
            self.handlers['R2'](values[0])
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
            self.handlers['DPLR'](value)
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
        self.handlers['DPUD'](value)


    def parse_LJLR(self, values):
        if debug: print 'Gamepad, parse_LJLR: ', values
        value = combineBytes(values)
        try:
            self.handlers['LJLR'](value)
        except AttributeError:
            print 'Callback not defined'

    def parse_LJUD(self, values):
        if debug: print 'Gamepad, parse_LJUD: ', values
        value = combineBytes(values, flip=True)
        try:
            self.handlers['LJUD'](value)
        except AttributeError:
            print 'Callback not defined'

    def parse_RJLR(self, values):
        if debug: print 'Gamepad, parse_RJLR: ', values
        value = combineBytes(values)
        try:
            self.handlers['RJLR'](value)
        except AttributeError:
            print 'Callback not defined'

    def parse_RJUD(self, values):
        if debug: print 'Gamepad, parse_RJUD: ', values
        value = combineBytes(values, flip=True)
        try:
            self.handlers['RJUD'](value)
        except AttributeError:
            print 'Callback not defined'

    def listen(self):
        """
        Blocking infinite loop
        """
        while True:
            msg = self.pipe.read(8)
            if debug: print 'Gamepad, listen: ', [ord(char) for char in msg]
            values = (ord(msg[4]), ord(msg[5]))
            control = (ord(msg[6]), ord(msg[7]))
            try:
                self.parsers[control](values)
            except KeyError:
                print 'Gamepad, Unbound event! Control code is: ', control

