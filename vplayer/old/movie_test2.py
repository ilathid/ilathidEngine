import sys
import pymedia
import time
import pygame
from m_player import Player

class VCallback:
    overlay = None
    def onAudioReady( self, afr ):
        return afr
        
    def onVideoReady( self, vfr ):
        # print "vfr"
        if self.overlay is None:
            pygame.init()
            pygame.display.set_mode( vfr.size, 0 )
            self.overlay = pygame.Overlay( pygame.YV12_OVERLAY, vfr.size )
        self.overlay.display( vfr.data )
render = VCallback()

player= Player(render)
player.start()
# player.setLoops(1)
player.startPlayback( 'sample.mpg' )
# player.startPlayback( 'test.mpg' )
# player.startPlayback( '365rev.mpg' )
while player.isPlaying():
    time.sleep( 0.01 )
