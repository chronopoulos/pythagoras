from pyo import *

s = Server(duplex=0).boot()

son = '/home/chrono/music/samples/zombies_bassline.wav'
info = sndinfo(son)
a = SfPlayer(son, mul=.25)
#a = Noise(.25)

size = 512
m = NewMatrix(width=size, height=info[0]/size)

fin = FFT(a*100, overlaps=1)
# mag should be in dB (log) for a better result
mag = Sqrt(fin["real"]*fin["real"] + fin["imag"]*fin["imag"])
rec = MatrixRec(mag*2-1, m, 0).play()

s.gui(locals()) 
