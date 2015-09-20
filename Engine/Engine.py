import os
import Media
from Hotspot import Hotspot
from SlideManager import SlideManager
from AgeManager import AgeManager
from GLManager import GLManager
from CursorManager import CursorManager
from Archive import Archive,FilePath
from Hotspot import EngineHotspot
from Logger import Logger
from Movie import Movie
import pygame
if os.name == 'nt':
    import pygame._view
import time
from Parameters import Parameters
from pygame.locals import *


class Engine:
    # Create a new hotspot, with callback tied appropriately to the engine
    def Hotspot(self, geom, callback=None, dest=None, cursor=None,dest_dir=None):
        return EngineHotspot(self, geom, callback=callback, dest=dest, cursor=cursor,dest_dir=dest_dir)
    
    # Slide is a string
    def gotoSlide(self, slide):
        Logger.log("Goto <i>" + str(slide) + "</i>")
        s = self.slide_manager.setSlide(slide)
        
    def __init__(self):
        self.age_manager = AgeManager(self)
        self.slide_manager = SlideManager(self.age_manager)
        self.extLayers = []
        
        Media.initialize()
        
        Logger.log("pygame init")
        pygame.init()
        flags = pygame.OPENGL | pygame.DOUBLEBUF
        
        
        #Initailize screen surface and fill with background color
        if Parameters.fullscreen:
            flags |= pygame.FULLSCREEN
            info = pygame.display.Info()    
            ssize = (info.current_w,info.current_h)
            if ssize[0] > 0 and ssize[1] > 0:
                Parameters.windowsize = ssize
                
        
        bestdepth = pygame.display.mode_ok(Parameters.windowsize, flags)
        
        if bestdepth == 0:
            #Exit if display can not be initialized
            sys.exit()
        
        # Create the main screen with Icon and Title
        # (except on OSX because there the better way to set icons is through the app bundle's Info.plist)
        # uname does not work on NT platform
        if os.name != 'nt':
            if os.uname()[0] != 'Darwin':
                iconbitmap = pygame.image.load('ilathid_low.gif') 
                pygame.display.set_icon(iconbitmap) 
        
        pygame.display.set_caption('Ages of Ilathid','Ilathid') 
        pygame.display.set_mode(Parameters.windowsize, flags)
        
        # Init OpenGL
        GLManager.init(Parameters.windowsize)
        
        # Cursors
        arch = Archive("EngineData", {"type":"file", "file_loc":"Data"})
        
        # Add cursors: cursor name, cursor file, click hotspot
        cursors = []
        cursors.append(('forward','fwd.png',(7,2)))
        cursors.append(('grab','grab.png',(7,7)))
        cursors.append(('down','down.png',(5,15)))
        cursors.append(('fist','fist.png',(7,7)))
        cursors.append(('left','left.png',(1,5)))
        cursors.append(('left180','left180.png',(1,5)))
        cursors.append(('right','right.png',(15,5)))
        cursors.append(('right180','right180.png',(15,5)))
        cursors.append(('up','up.png',(10,1)))
        cursors.append(('magnify','magnify.png',(7,7)))
        cursors.append(('minus','minus.png',(7,7)))
        cursors.append(('plus','plus.png',(7,7)))
        cursors.append(('zip','zip.png',(7,7)))
        
        for (cname, cfile, chot) in cursors:
            fp = FilePath('cursors/' + cfile, arch)
            CursorManager.addCursor(fp, cname, chot)
        
    def attatchLayer(self, layer):
        self.extLayers.append(layer)
        
    def run(self):
        self.mainLoop()
        Media.shutdown() #TODO move
        
    def mainLoop(self):
        x = 0
        y = 0
        tl = 0
        dt = 0
        
        last_t = time.time()
        while not pygame.event.peek(pygame.locals.QUIT):
            events = pygame.event.get()
            events = self.doEvents(events, dt)
            
            # Extra Layers
            for l in self.extLayers:
                events = l.doEvents(events, dt)
            
            events = self.slide_manager.getSlide().doEvents(events, dt)
            # Any unhandled events are discarded
           
            # TODO timers need to depend on layers and on slide objects. They may force more frequent time updates
            # One way to do this is that layers can register themselves as affecting the timers
            # Then they can create a kind of timer event, which (opt) calls a callback func and triggers a render
             
            tl = 1.0/Parameters.max_fps + last_t - time.time()
            if tl > 0:
                time.sleep(tl)
            last_t2 = last_t
            last_t = time.time()
            dt = last_t - last_t2
            
            # TODO put render code here
            self.render()
            
        # clean up last slide?
        self.slide_manager.getSlide().clearBuffers()
        self.slide_manager.setSlide(None)

                
    def doEvents(self, events, dt):
        for event in events:
            # Quit
            if event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.locals.QUIT))
                    events.remove(event)
        return events
    
    def render(self):
        GLManager.clear()
        self.slide_manager.getSlide().render()

        # Extra Layers
        for l in self.extLayers:
            l.render()
        
        CursorManager.render()
        
        pygame.display.flip()
