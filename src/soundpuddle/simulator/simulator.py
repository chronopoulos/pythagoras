import pygame, sys, os, time, string
import numpy as np
from pygame.locals import *

# define some colors
white = 255, 255, 255
red =  255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
black = 0,0,0

# and the alphabet
alphabet = {}
for i in range(24):
    alphabet[string.lowercase[i]] = i



class RadiatingParticle():

    def __init__(self, appSize, direction, color=green, width=0):
        self.appSize = appSize
        self.xy = np.array([float(dim/2) for dim in self.appSize])
        self.size = 10
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

    def drawLines(self):
        for i in range(24):
            endpoint =  tuple([int(self.center[j]+self.spokes[i][j]*self.radius) for j in range(2)])
            pygame.draw.line(self.screen, white, self.center, endpoint)


    def handle(self, events):
        for event in events:
            if event.type == QUIT:
                self.gracefulExit()
            elif event.type == KEYDOWN:
                try:
                    spokeIndex = alphabet[event.dict['unicode']]
                    self.launch(self.spokes[spokeIndex])
                except KeyError:
                    print 'Key unbound'
            else:
                pass
                #print 'Unbound event:'
                #print event

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
            print 'nparticles = ', len(self.particles)

    def mainLoop(self):
        while True:
            self.handle(pygame.event.get())
            self.screen.fill(black)
            self.drawLines()
            self.takeStep()
            self.clean()
            for particle in self.particles:
                particle.display(self.screen)
            pygame.display.flip()
            time.sleep(0.03)

    def gracefulExit(self):
        pygame.quit()
        sys.exit()


    def launch(self, spoke):
        self.particles.append(RadiatingParticle(self.size, spoke))
        print 'nparticles = ', len(self.particles)



if __name__ == '__main__':

    app = SoundPuddle()
    app.mainLoop()



