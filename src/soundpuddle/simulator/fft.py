import pyo, sys, time

if 'jack' in sys.argv:
   s = pyo.Server(audio='jack').boot()
else:
   s = pyo.Server().boot()

s.start()

audioIn = pyo.Input(chnl=[0,1], mul=0.7)
#a = pyo.Noise(.25).mix(2)
fft = pyo.FFT(audioIn, size=1024, overlaps=4, wintype=2)

#t = ExpTable([(0,0),(3,0),(10,1),(20,0),(30,.8),(50,0),(70,.6),(150,0),(512,0)], size=512)
#amp = TableIndex(t, fin["bin"])
#re = fin["real"] * amp
#im = fin["imag"] * amp
#fout = IFFT(re, im, size=1024, overlaps=4, wintype=2).mix(2).out()

s.gui(locals())
