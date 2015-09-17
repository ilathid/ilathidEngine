import m_movie_ao

import time

# A = m_movie_ao.m_movie('sample.mpg')
# A = m_movie_ao.m_movie('test.mpg')
A = m_movie_ao.m_movie('365rev.mpg')

A.play(pos=0) # ff00 is left, 00ff is right
a = ''
while a != 'd' :
    a = raw_input("Press a key to start audio")
    if a == 'p':
        A.pause()
A.stop()
