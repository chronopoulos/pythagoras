import pygame, sys, os, time, string, liblo
import numpy as np
from pyo import midiToHz as m2h
from pygame.locals import *

if len(sys.argv)>1:
   sensitivity = float(sys.argv[1])
else:
   sensitivity = 900.
   

# define some colors
white = 255, 255, 255
red =  255, 0, 0
yellow = 255, 255, 0
green = 0, 255, 0
teal = 0, 255, 255
blue = 0, 0, 255
violet = 255, 0, 255
black = 0,0,0
colorTable = [green, violet]

# and the alphabet
alphabet = {}
for i in range(24):
    alphabet[string.lowercase[i]] = i

# and the frequency bins
midiNotes = range(36,84) # 48 bins total
f0 = 44100./4096 # 10.76 hz
allFreqs = f0*np.arange(100) # 100 is the number of frequencies you send across, currently
freqBins = []
for m in midiNotes:
    iwhere = np.where((allFreqs>=m2h(m-0.5)) & (allFreqs<m2h(m+0.5)))
    freqBins.append(iwhere[0])

class RadiatingParticle():

    def __init__(self, appSize, direction, color=green, width=0):
        self.appSize = appSize
        self.xy = np.array([float(dim/2) for dim in self.appSize])
        self.size = 5
        self.color = color
        self.width = width
        self.direction = direction
        self.speed = 5.

    def display(self, screen):
        xy_intuple = (int(self.xy[0]), int(self.xy[1]))
        pygame.draw.circle(screen, self.color, xy_intuple, self.size, self.width)

    def move(self):
        self.xy += self.speed*self.direction

    def isGone(self):
        return (not 0 <= self.xy[0] <= self.appSize[0]) or (not 0 <= self.xy[1] <= self.appSize[1])


class SoundPuddle():

    def __init__(self, size=(600,600)):
        pygame.init()
        pygame.display.set_caption('SoundPuddle Simulator')
        self.size = size
        self.radius = np.sqrt(self.size[0]**2+self.size[1]**2)
        self.screen = pygame.display.set_mode(self.size)
        self.center = self.size[0]/2, self.size[1]/2
        self.spokes = [ np.array([np.cos(2*np.pi*i/24), np.sin(2*np.pi*i/24)]) for i in range(24) ] # unit vectors
        self.particles = []
        ###
        self.drawLines()
        pygame.display.flip()
        self.OSCserver = liblo.Server(8666)
        self.OSCserver.add_method(None, None, self.handleOSC)

    def drawLines(self):
        for i in range(24):
            endpoint =  tuple([int(self.center[j]+self.spokes[i][j]*self.radius) for j in range(2)])
            pygame.draw.line(self.screen, white, self.center, endpoint)

    def handlePyGame(self, events):
        for event in events:
            if event.type == QUIT:
                self.gracefulExit()
            elif event.type == KEYDOWN:
                try:
                    spokeIndex = alphabet[event.dict['unicode']]
                    self.launch(self.spokes[spokeIndex], color=green)
                except KeyError:
                    print 'Key unbound'
            else:
                pass

    def handleOSC(self, pathstr, arg, typestr, server, usrData):
        for i in range(len(freqBins)):
            total = 0.
            for j in freqBins[i]:
                total += arg[j]                
            if total >= sensitivity:
                print 'Launching: ', i
                colorIndex = i//24
                spokeIndex = i%24
                self.launch(self.spokes[spokeIndex], color=colorTable[colorIndex])

    def takeStep(self):
        for particle in self.particles:
            particle.move()

    def clean(self):
        gone = []
        for particle in self.particles:
            if particle.isGone():
                gone.append(particle)
        for particle in gone:
            self.particles.remove(particle)

    def mainLoop(self):
        while True:
            self.handlePyGame(pygame.event.get())
            self.OSCserver.recv(46.439909)
            self.screen.fill(black)
            self.drawLines()
            self.takeStep()
            self.clean()
            for particle in self.particles:
                particle.display(self.screen)
            pygame.display.flip()

    def gracefulExit(self):
        pygame.quit()
        sys.exit()

    def launch(self, spoke, color):
        self.particles.append(RadiatingParticle(self.size, spoke, color=color))


if __name__ == '__main__':

    app = SoundPuddle()
    app.mainLoop()



