from Engine.FilePath import FilePath
from Engine.Movie import Movie
from Engine.Age import Age
from Engine.Gamestate import Gamestate
from Engine.Logger import Logger
from Engine.Geometry import Geometry2d, img2scr

import time

class Dni(Age):
    
    def init(self):
        self.loadXML()

        # TODO: Movie has many todos:
        # - movie can be skipped sometimes
        # - movie can block all user events (cinemetic)
        # - movie needs a onFinish() callback, so that 
        #   things can be done when the movie ends (ie linking after movBook)
        self.starttime = time.time()
        # Try adding a video here?
        # fp = FilePath("movies/rocks.mpg", self.arch)
        # geom = Geometry2d(img2scr([(0,0), (0,600), (800,600), (800,0)]))
        # self.movBook = Movie(geom, fp)

        fp = FilePath("movies/void.mpg", self.arch)
        geom = Geometry2d(img2scr([(0,0), (0,600), (800,600), (800,0)]))
        self.movBook = Movie(geom, fp)
        
        fp = FilePath("movies/video59.mpg", self.arch)
        geom = Geometry2d(img2scr([(391,125), (391,255), (521,255), (521,125)]))
        self.mov59 = Movie(geom, fp)
        
        fp = FilePath("movies/video37.mpg", self.arch)
        geom = Geometry2d(img2scr([(387,241), (387,241+8), (387+24,241+8), (387+24,241)]))
        self.mov37 = Movie(geom, fp)
        
        dni59 = self._slides["dni59"]
        dni37 = self._slides["dni37"]
        
        dni59.attachObject(self.mov59)
        dni59.attachObject(self.movBook)
        dni37.attachObject(self.mov37)
        
        # Try adding a video here?
        fp2 = FilePath("movies/wall.mpg", self.arch)
        geom2 = Geometry2d(img2scr([(0,0), (0,600), (800,600), (800,0)]))
        self.movSwitch = Movie(geom2, fp2)
        
        self.movSwitch.setCondString("not Dni.switch")
        
        dni21 = self._slides["dni21"]
        dni21.attachObject(self.movSwitch)
        Gamestate.setVar('Dni.switch', False)
        
    def flipswitch(self):
        Logger.log("<b>Switch!</b>")
        self.movSwitch.setEndCallback(self.endSwitch)
        self.movSwitch.play(loop=False)
    
    def endSwitch(self):
        Gamestate.setVar('Dni.switch', True)
    
    # What is this: the videos are syncronized using a base time
    # Possible problem: getDuration() may not be accurate
    def dni33_entry(self, slide):
        Logger.log("Entered slide dni33!")
        self.mov37.makeBuffers()
        tim = (time.time() - self.starttime) % self.mov37.getDuration()
        self.mov37.play(loop=True, starttime=tim)
                
    def dni37_entry(self, slide):
        Logger.log("Entered slide dni37!")
        self.mov59.makeBuffers()
        tim = (time.time() - self.starttime) % self.mov37.getDuration()
        tim = tim % self.mov59.getDuration()
        self.mov59.play(loop=True, starttime=tim)
        
    def dni34_entry(self, slide):
        Logger.log("Entered slide dni34!")
        self.mov59.stop()
        self.mov37.stop()
        self.mov59.clearBuffers()
        self.mov37.clearBuffers()
    
    def runstory(self):
        # Gamestate.setVar('Dni.switch', False)
        Logger.log("runstory")
        # self.engine.gotoSlide("ZenGarden.ZenGarden1")
        self.movSwitch.clearBuffers()
        #if Gamestate.getVar('Dni.book_on'):        
            # self.mov59.pause()
            #self.mov59.clearBuffers()
        self.movBook.makeBuffers()
        self.movBook.setEndCallback(self.endVoid)
        self.movBook.play(loop=False)
        #else:

        #    Gamestate.setVar('Dni.book_on', True)
        
    def endVoid(self):
        Logger.log('<b>Warp Complete</b>')
        self.engine.gotoSlide("ZenGarden.ZenGarden1")
