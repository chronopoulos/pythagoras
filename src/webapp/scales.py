"""
Scales are first-order functions that take an index as argument,
and return the distance in semitones from the root.
Modular arithmetic is used, so there is no limit to the index you may request.
"""

def chromatic(i):
   return i

globscale = []

def globalscale(i):
  L = len(globscale)
  if (L == 0):
    return majorPentatonic(i) 
  j=i%L
  k=i//L
  return k*12 + globscale[j]

def major(i):
   j=i%7
   k=i//7
   scale = [0,2,4,5,7,9,11]
   return k*12 + scale[j]

def minor(i):
   # natural minor
   j=i%7
   k=i//7
   scale = [0,2,3,5,7,8,10]
   return k*12 + scale[j]

def harmonicMinor(i):
   j=i%7
   k=i//7
   scale = [0,2,3,5,7,8,11]
   return k*12 + scale[j]

def majorPentatonic(i):
   j=i%5
   k=i//5
   scale = [0,2,4,7,9]
   return k*12 + scale[j]

def minorPentatonic(i):
   j=i%5
   k=i//5
   scale = [0,3,5,7,10]
   return k*12 + scale[j]

def diminished(i):
   j=i%8
   k=i//8
   scale = [0,2,3,5,6,8,9,11]
   return k*12 + scale[j]
