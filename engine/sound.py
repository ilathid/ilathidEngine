#Sound Class and support functions
import pygame
from pygame.locals import *
from filemanager import filemanager

class sound:


    def __init__(self, filename):
        self.file = filename
        self.channel = None
        self.isPaused = 0
        self.volume = 0.5
        
    def playsound(self,loop=0):
        if not pygame.mixer: return    
        self.mysound = pygame.mixer.Sound(filemanager.find_sound(self.file))
        self.loop=loop
        self.channel = self.mysound.play(self.loop)
        if not self.channel:
                self.channel = pygame.mixer.find_channel(1)
                self.channel.play(self.mysound,self.loop)

    def playloopingsound(self,loop=-1):
        self.playsound(loop)

    def playlooppause(self):
        if not self.channel:
            self.playloopingsound()
        elif self.channel.get_busy():
            if self.isPaused:
                self.channel.unpause()
                self.isPaused=0
            else:
                self.channel.pause()
                self.isPaused=1
        
    def stopsound(self):
        self.mysound.stop()
        
    def restartchannel(self):
        self.channel.play(self.mysound,self.loop)
        
    def upsound(self):
        vol=self.mysound.get_volume()
        if vol <= 0.9:
            self.mysound.set_volume(vol+0.1)
    
    def downsound(self):
        vol=self.mysound.get_volume()
        if vol > 0.0:
            self.mysound.set_volume(vol-0.1)
          
    def setvolume(self,vol=0.5):
        self.volume=vol
        self.mysound.set_volume(self.volume)
  
