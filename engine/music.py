#Music Class and support functions
import pygame
import parameters
from filemanager import filemanager
from pygame.locals import *
from pygame import *
from pygame.mixer import *

#Pygame Module for Music and Sound
pigmusic = None
currentStdMusic=None
currentMenuMusic=None
currentType = None

def initmusic():
    global pigmusic
    #Init pygame mixer and music
    print "music init GO" 
    try:
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer.init()
        if not pygame.mixer:
            print 'Warning, sound disabled'
        else:
            pigmusic=pygame.mixer.music
    except (pygame.error):
        print 'Warning, unable to init music'
    print "music init OUT ",pigmusic

def upmusic():
    global pigmusic
    if not pigmusic:
        return
    
    vol=pigmusic.get_volume()
    if vol <= 0.9:
        pigmusic.set_volume(vol+0.1)
        
def downmusic():
    global pigmusic
    if not pigmusic:
        return
    
    vol=pigmusic.get_volume()
    if vol > 0.0:
        pigmusic.set_volume(vol-0.1)

def stopmusic():
    global pigmusic
    if not pygame.mixer.get_init():
        return
    if not pigmusic:
        return
    if pigmusic.get_busy():
        pigmusic.stop()

def setvolume(vol):
    global pigmusic
    pigmusic.set_volume(vol)

def getcurrentStdMusic():
    global currentStdMusic
    return currentStdMusic

def getcurrentMenuMusic():
    global currentMenuMusic
    return currentMenuMusic
  
def returtostdmusic():
    #called when we want to force the music to play std music
    cur=currentStdMusic
    cur.playmusic()

    
class Music:

    def __init__(self, name, filename, musictype='std', vol=0.5):
        self._name=name
        self._file=filename
        self._type=musictype
        self._vol=vol
        
    def playmusic(self,loop=-1):
        global pigmusic,currentStdMusic,currentMenuMusic,currentType
        print "music play",self._file
        if not pigmusic: 
            initmusic()
        if self._type == 'std':
            #print "music std type current is ",currentType
            if not currentStdMusic:
                #print "music std no currentStdMusic, we create it with ",self._file
                currentStdMusic=self
            #print "is pigmusic busy ? ",pigmusic.get_busy()
            if pigmusic.get_busy():
                #print "music std, music is busy"
                if currentType == 'std':
                    #print "music std, currentType is std isn't it : ",currentType
                    if currentStdMusic.getfile()==self._file:
                        #print "music std, same music don't do anything"
                        return
                    else:
                        #print "music std, not the same we change, currentStdMusic=",self._file
                        currentStdMusic=self
                #print "is pigmusic busy ? ",pigmusic.get_busy()
                if pigmusic.get_busy():
                    print "    music std, music is busy"
                    if currentType == 'std':
                        print "    music std, currentType is std isn't it : ",currentType
                        if currentStdMusic.getfile()==self._file:
                            print "    music std, same music don't do anything"
                            return
                        else:
                            print "    music std, not the same we change, currentStdMusic=",self._file
                            currentStdMusic=self
                    else:
                        print "    music std, current type is menu isn't it :", currentType ," so we change it to std\n"
                        #we change menu slide to standard slide
                        currentType='std'
                else:
                    #print "music std, current type is menu isn't it :", currentType ," so we change it to std\n"
                    #we change menu slide to standard slide
                    currentType='std'
            else:
                #print "music std, music is not busy we start it"
                currentType='std'
                currentStdMusic=self
        else:
            #print "music menu type current is ",currentType
            if not currentMenuMusic:
                #print "music menu no currentMenuMusic, we create it with ",self._file
                currentMenuMusic=self
            if pigmusic.get_busy():
                #print "music menu, music is busy"
                if currentType == 'menu':
                    #print "music menu, currentType is menu isn't it : ",currentType
                    if currentMenuMusic.getfile()==self._file:
                        #print "music menu, same music don't do anything"
                        #return
                        pass
                    else:
                        #print "music menu, not the same we change, currentMenuMusic=",self._file
                        currentMenuMusic=self
                if pigmusic.get_busy():
                    print "    music menu, music is busy"
                    if currentType == 'menu':
                        print "    music menu, currentType is menu isn't it : ",currentType
                        if currentMenuMusic.getfile()==self._file:
                            print "    music menu, same music don't do anything"
                            return
                        else:
                            print "    music menu, not the same we change, currentMenuMusic=",self._file
                            currentMenuMusic=self
                    else:
                        print "    music menu, current type is std isn't it :", currentType ," so we change it to menu\n"
                        #we change standard slide to menu slide
                        currentType='menu'
                else:
                    #print "music menu, current type is std isn't it :", currentType ," so we change it to menu\n"
                    #we change standard slide to menu slide
                    currentType='menu'
            else:
                #print "music menu ,music is not busy we start it"
                currentType='menu'
                currentMenuMusic=self
        pigmusic.load(filemanager.find_music(self._file))
        pigmusic.set_volume(self._vol)
        pigmusic.play(loop)
        
    def getfile(self):
        return self._file

    def getname(self):
        return self._name

    def stopmusic(self):
        print "we stop music!!!!! ",self._file
        global pigmusic
        if not pigmusic: 
            return
        if pigmusic.get_busy():
            if self._type == 'std':
                if currentStdMusic.getfile()==self._file:
                    pigmusic.stop()
            else:
                if currentMenuMusic.getfile()==self._file:
                    pigmusic.stop()
