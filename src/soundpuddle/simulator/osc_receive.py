import liblo

def handleMsg(pathstr, arg, typestr, server, usrData):
   print 'Message Received:'
   print pathstr, arg

OSCserver = liblo.Server(8000)
OSCserver.add_method(None, None, handleMsg)

while True:
   OSCserver.recv(1) # 1 ms refresh rate
