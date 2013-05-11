import pyo

s = pyo.Server().boot()
s.start()

#audioIn = pyo.Input(chnl=[0,1], mul=0.7)
a = pyo.Noise(.25)

fft = pyo.FFT(a, size=1024, overlaps=1, wintype=2)
re = fft['real']
im = fft['imag']
bin = fft['bin']
mag = pyo.Sqrt(re*re + im*im)
   
magTable = pyo.NewTable(1024)
tablerec = pyo.TableRec(mag, magTable)

refreshTrig = pyo.Select(bin, value=0)
pyo.TrigFunc(refreshTrig, tablerec.play)

value = pyo.TableIndex(magTable, bin)

s.gui(locals())
