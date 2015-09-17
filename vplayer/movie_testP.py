import sys
sys.path.append( "../" )
from engine import MoviePlayer

import time

import pygame

class VCallback:
    overlay = None
    def __init__(self, size=0):
        pygame.init()
        pygame.display.set_mode( size, 0 )
        self.overlay = pygame.Overlay( pygame.YV12_OVERLAY, size )
        
    def onVideoReady( self, vfr ):
        self.overlay.display( vfr.data )
# A = MoviePlayer.MovieFile('test.mpg')
# A = MoviePlayer.MovieFile('365rev.mpg')
# A = MoviePlayer.MovieFile('/usr/home/matt/Videos/cans.mpg')

f = open('sample.mpg')
# f = open('test.mpg')
# f = open('/home/matt/Downloads/spline0001-0030.avi')
# f = open('365rev.mpg')
data = f.read()



A = MoviePlayer.MoviePreloaded(data)
callback = VCallback(A.size)
A.setCallback(callback)

options = {'loopstart':2.5, 'loopend':3.5}

# A.seek(1.0)
# time.sleep(3)
# A.play()

# A.play(loopstart = 0.5, loopend = 2, loopseek=True)
A.play()
a = ''
while a != 'q' :
    a = raw_input("Press a key to start audio")
    if a == 'p':
        print "Pause"
        A.pause()
    if a == ' ':
        print "Play"
        A.play()
    if a == 's':
        print "Stop"
        A.stop()
    if a == '1':
        print "Seek 1"
        A.seek(2)
    if a == '2':
        print "Seek 2"
        A.seek(4)
    if a == 'q':
        print "Quit"
        A.stop()
