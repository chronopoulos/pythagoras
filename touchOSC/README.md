pythagoras
==========

pythagoras is a library for experimentation with musical synthesis and algorithmic composition. It is written in Python, and uses the pyo libary as a sound engine:

https://code.google.com/p/pyo/

It also serves as the audio backend for Audiocomp, a web server and ClojureScript application designed for networking musical collaborations:

https://bitbucket.org/bburdette/audiocomp

Dependencies for pythagoras include:

python-pyo  
python-liblo  
python-numpy  
python-blist  

To run pythagoras, just do:

$ cd src  
$ python pythagoras.py

If you want to run with Jack connectivity, first start jackd, then:

$ python pythagoras.py jack

If you want to use the default sample packs defined in samplepacks.py, they are available here:

https://dl.dropbox.com/u/3020732/samples.tar.gz

____
Chris Chronopoulos, 2013-03-19
