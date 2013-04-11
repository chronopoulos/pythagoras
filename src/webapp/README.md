This is the webapp version of pythagoras. It is to be used with the Audiocomp web server and layout engine:

https://bitbucket.org/bburdette/audiocomp

To run, start pythagoras as usual:

$ python pythagoras.py <debug, jack>

and then start Audiocomp in a separate terminal:

$ cd audiocomp/layoutctrls
$ ./run

(Make sure you build the javascript, e.g. lein cljsbuild once, before making any requests.)

Now, the controls should be available on localhost:9000
