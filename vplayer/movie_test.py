import sys
sys.path.append( "../" )
from engine import AoIMovie

import time

# A = m_movie.m_movie('sample.mpg')
# A = m_movie.m_movie('test.mpg')
# A = m_movie.m_movie('365rev.mpg')
A = AoIMovie.MovieFile('/usr/home/matt/Videos/cans.mpg')

A.play(pos=20) # ff00 is left, 00ff is right
a = ''
while a != 'd' :
    a = raw_input("Press a key to start audio")
    if a == 'p':
        A.pause()
A.stop()
