
import pygame

from engine.filemanager import filemanager
from engine.gametimer import timer
from engine.age import age
from engine.FilePath import FilePath
from engine.SlideManager import SlideManager

def pad(counter):
    val = str(counter)
    while (len(val) < 5):
        val = ('0' + val)

    return val



#Slides Parameters
#pres.onentrance(startpresentationmovie)
#pres.onexit(stoppresentationmovie)


#endpresentation.onentrance(showEndPresentation)



# local variables:
# tab-width: 4

class DniAge(age):
    
    def __init__(self):
        super(DniAge, self).__init__("data/ages/Dni/age.xml", DniAge)
        
        self.towercounter = 0
        self.towertimer = timer(45, lambda: self.toweranim())

        # self.toweranim();
    
        # dni23 = self._slides['dni23']
        # dni23.updatestate('switch', True)

    def starttoweranim(self):
        self.towertimer.start()
    
    def stoptoweranim(self):
        self.towertimer.stop()
    
    def toweranim(self):
        self.towercounter += 1
        if (self.towercounter == 101):
            self.towercounter = 0
        self._images['dni37image'].update( FilePath(('37_' + pad(self.towercounter) + '.png'), "images.zip", 0 ))
        self._images['dni59image'].update( FilePath(('59_' + pad(self.towercounter) + '.png'), "images.zip", 0 ))
        #dni59text.update(string=(('59_' + pad(towercounter)) + '.png'))
        #time.sleep(1)
        return 1
    
    def playfirstmusic(self):
        pygame.mixer.init()
        # self._movies['presentation'].play()
        if not self._slides['dni1'].getstate('musicplayed'):
            #pygame.mixer.pre_init(44100,-16,2, 1024 * 3)        
            self._musics['music1'].playmusic()
            self._slides['dni1'].updatestate('musicplayed', True)
    
    def endpresentationmovie(self):
        # self._movies['presentation'].stop()
        pass
    
    def flipswitch(self):
        dni21 = self._slides['dni21']
        dni23 = self._slides['dni23']
        dni25 = self._slides['dni25']
        dni27 = self._slides['dni27']
        dni28 = self._slides['dni28']
        
        dni21.setfile(0, 'switch-unlocked.jpg') #remplacer avec unlocked
        #Faudra faire dememe avec le slides 20 et 18 pour le unlocked
        #Voire les autres slides du couloir pour la lumiere
        #slide de la porte
        dni23.setfile(0, 'dnichamber23-ouvert.jpg', 'slides.zip')
        dni23.updatestate('switch', True)
        dni25.setfile(0, 'dnichamber25-ouvert.jpg', 'slides.zip')
        dni27.setfile(0, 'dnichamber27-ouvert.jpg', 'slides.zip')
        dni28.setfile(0, 'dnichamber28-ouvert.jpg', 'slides.zip')
        dni25.attachhotspot((148,84,492,403), 'forward', {'dest': "dni29"})
        dni21.updatestate('switch', True)
        dni21.detachhotspot(1)
        pygame.mixer.quit()
        self._movies['switchmovie'].play()
    
    
    #function called after switchmovie in order to go to the dest slide
    def show23(self):
        dni23 = self._slides['dni23']

        dni23.setfile(0, 'dnichamber23-ouvert.jpg', 'slides.zip')
        self._movies['switchmovie'].stop
        SlideManager.replaceTopSlide(dni23)
        
    def playlightmusic(self):
        dni23 = self._slides['dni23']
        if not dni23.getstate('musicplayed'):
            #pygame.mixer.pre_init(44100,-16,2, 1024 * 3)
            pygame.mixer.init()
            self._musics['music23'].playmusic()
            dni23.updatestate('musicplayed', True)
    
    def showEnd(self):
        #endmovie.stop()
        pygame.mixer.init()
        #endpresentation.display()
    
    def showEndPresentation(self):
        #global endmovie
        #endmovie=None
        pass
    
    def runstory(self):
        self.towertimer.stop()
        pygame.mixer.quit()
        self._movies['endmovie'].play()
    
    def startpresentationmovie(self):
        pygame.mixer.quit()
        #presentationmovie.play()
    
    def stoppresentationmovie(self):
        #presentationmovie.stop()
        pass
    
    #def showstart(self):
    #    dni1.display()
