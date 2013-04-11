This is the version of pythagoras intended for installations and art festivals. Currently we are using video game controllers (Logitech Dual-Action Gamepads) as a physical interface. It is started in the standard way:

$ python pythagoras <debug jack verbose>

Each Gamepad reads its device file in a separate thread via the threading module. Instruments are defined in instruments.py, and bound to controllers by calling the JamServer.addPlayer() in pythagoras.py
