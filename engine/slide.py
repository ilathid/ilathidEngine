import pygame
import pygame.locals
from FilePath import FilePath
from GLTexture import GLTexture
from GLManager import GLManager
from Geometry import Geometry2d, img2scr
from CursorManager import CursorManager
from Parameters import Parameters
from Grabber import Grabber, Grabbable
from Hotspot import EngineHotspot

class Slide(Grabbable):
    dragging = False
    grabbing = False
    drag_pos = (0,0)
    
    active_objects = None

    callbacks = None

    def __init__(self, name, stype, filepath):
        assert not isinstance(filepath, list)
        self.type = stype
        self.name = name
        self.slide_tex_files = [filepath] # all surfaces for drawing 2d/3d slide
        self._setInitialValues()
        self.grabber = Grabber()
        self.active_objects = []
        self.callbacks = {}
    
    def getImageSize(self):
        if self.isLoaded:
            return self.tex.size
        else:
            self.makeBuffers()
            return self.tex.size
                            
    def getType(self):
        """ type should be either '3d' or '2d' """
        return self.type
        
    def makeBuffers(self):
        """ Loads any needed data into memory """
        if self.isLoaded: return
        # assert not self.isLoaded
        # Load contained objects
        print "loading " + self.name
        self.active_objects = []
        for obj in self.slide_objects:
            # if obj.checkCondition():
            obj.makeBuffers()
            #    self.active_objects.append(obj)
            #else:
            #    print "skip " + obj
        
        # Turn the file into data
        tex_file = self.slide_tex_files[0]
        file_io = tex_file.getFile()
        self.tex = GLTexture()
        self.tex.imageTexture(file_io, alpha=None)

        # Do an intelligent centering of geom by uv
        (w,h) = self.tex.size
        # TODO: Resize texture to fit window, but image coords are still based on Parameters.slide_size_2d
        geom = Geometry2d(img2scr([(0,0),(0,h),(w,h),(w,0)]))
         
        #geom = Geometry2d((x1,y1),(x1, y2), (x2,y2), (x2,y1))
        file_io.close()
        self.slide_textures.append((self.tex, geom))
        
        self.isLoaded = True
    
    def _setInitialValues(self):
        self.slide_textures = []  
        self.slide_objects = []
        self.active_objects = []
        self.delay = 0 #??
        self.isLoaded = False
        # What about pausing timers?
        
    def getName(self):
        return self.name
    def setDelay(self, delay):
        self.delay = delay
    def getDelay(self):
        return self.delay

    #Attached objects
    def hasObject(self, obj):
        return obj in self.slide_objects

    def attachObject(self, obj):
        if obj not in self.slide_objects:
            self.slide_objects.append(obj)

    def exit(self):
        for obj in self.slide_objects:
            obj._slide_exit()
        if 'exit' in self.callbacks:
            self.callbacks['exit'](self)
    
    def entry(self):
        for obj in self.slide_objects:
            obj._slide_entry()
        #if self.onenterfn is not None:
        #    self.onenterfn()
        # print "Slide " + self.name + " clallbacks " + str(self.callbacks)
        if 'entry' in self.callbacks:
            print "Calling entry"
            self.callbacks['entry'](self)

    #Clear all buffers for memory management
    def clearBuffers(self):
        if not self.isLoaded: return
        print "unloading " + self.name
        # assert self.isLoaded
        # Free textures
        for tex in self.slide_textures:
            del tex
            
        # Free contained objects
        for obj in self.slide_objects:
            obj.clearBuffers()

        self.isLoaded = False

    def __del__(self):
        if self.isLoaded:
            self.clearBuffers()
        for obj in self.slide_objects:
            del obj

    # Draws slide to screen buffer
    def render(self):
        if not self.isLoaded:
            raise Exception("Slide (" + self.name + ") is not in memory!")
        
        for tex, geom in self.slide_textures:
            geom.renderTexture(tex)
        
        for obj in self.slide_objects:
            #if obj.checkCondition():
            obj.render()

    def doEvents(self, events, dt):        
        for obj in self.slide_objects:
            #if obj.checkCondition():
            obj.doEvents(events, dt)
                
        return events
    
    def getLinks(self):
        links = []
        links.append(self.getName())
        for obj in self.slide_objects:
            if isinstance(obj, EngineHotspot):
                dest = obj.getDest()
                if dest is not None and not dest in links:
                    links.append(dest)
        print "Links:" + str(links)
        return links

class Slide2d(Slide):
    pass
