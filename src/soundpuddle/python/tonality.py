from blist import sortedset

class Tonality():

   def __init__(self, scale):
      self.scale = sortedset(scale)
      self.m=len(self.scale)
      self.nad = sortedset(range(self.m))
      self.n = len(self.nad)
      self.degree = 0

   def cycleScale(self,i):
      j=i%self.m
      k=i//self.m
      return k*12 + self.scale[j]

   def cycleNad(self,i):
      j=i%self.n
      k=i//self.n
      return k*self.m + self.nad[j]

   def request(self, i):
      return self.cycleScale(self.degree+self.cycleNad(i))

   def updateScale(self, index, onoff):
      if onoff==1:
         self.scale.add(index)
      else:
         self.scale.remove(index)
      self.m=len(self.scale)

   def updateNad(self, index, onoff):
      if onoff==1:
         self.nad.add(index)
      else:
         self.nad.remove(index)
      self.n = len(self.nad)

   def updateDegree(self, degree):
      self.degree = degree
