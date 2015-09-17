import pygame
import pygame.locals
from Slide import Slide
from GLTexture import GLTexture
from GLManager import GLManager
from Geometry import Geometry3d, geomFromSide
from CursorManager import CursorManager
from Parameters import Parameters
#TODO: Remove grabber
from Grabber import Grabber

class Slide3d(Slide):
    #_sides3d_order = "NSEWTB"
    _sides3d_order = "NESWTB"
    _sides3d = {'N':(0,0,-1), 'S':(0,0,1),'E':(-1,0,0),'W':(1,0,0),'T':(0,1,0),'B':(0,-1,0)}
    def __init__(self, name, stype, filepaths):
        if len(filepaths) != 6:
            raise Exception("3D Slide needs a list of 6 filepaths, got " + str(len(filepaths)))
        self.name = name      
        self.type = stype
        self.slide_tex_files = filepaths # all surfaces for drawing 2d/3d slide
        self._setInitialValues()
        self.grabber = Grabber()
        self.active_objects = []
        self.callbacks = {}
        
    def makeBuffers(self):
        if self.isLoaded: return
        # Load contained objects
        print "loading " + self.name
        for obj in self.slide_objects:
            if obj.checkCondition():
                obj.makeBuffers()
                self.active_objects.append(obj)
        
        # Load textures
        sidei = iter(self._sides3d_order)
        for tex_file in self.slide_tex_files:
            side = sidei.next()
            # Turn the file into data
            geom = geomFromSide(side)
            
            file_io = tex_file.getFile()
            tex = GLTexture()
            tex.imageTexture(file_io, alpha=None)
            file_io.close()
            self.slide_textures.append((tex, geom))
        self.isLoaded = True
        
    def doEvents(self, events, dt):
        keystate = pygame.key.get_pressed()

        if not self.grabbing:
            if keystate[pygame.locals.K_LEFT]:
                GLManager.viewRotate(0, -200*dt)
            if keystate[pygame.locals.K_RIGHT]:
                GLManager.viewRotate(0, 200*dt)
            if keystate[pygame.locals.K_DOWN]:
                GLManager.viewRotate(-200*dt, 0)
            if keystate[pygame.locals.K_UP]:
                GLManager.viewRotate(200*dt, 0)
        if len(events) == 0:
            return
        
        # Drag Events
        events = self.grabber.doEvents(events)
        
        for obj in self.active_objects:
            obj.doEvents(events, dt )
            
        for event in events:
            if event.type == pygame.locals.MOUSEBUTTONDOWN:
                self.grabber.attatch(self, event.pos)

        # if Parameters.lock_view:
        #     # TODO
        #     self.drag()
                
        return events

    # 3d can grab for rotation
    def isGrabbable(self):
        return Parameters.grab_view
    
    # 3d grab rotation
    def drag(self, pos, grab_pos=None):
        drx = pos[1] - grab_pos[1]
        dry = pos[0] - grab_pos[0]
        # self.drag_pos = pos
        CursorManager.lockPosition(grab_pos)
        GLManager.viewRotate(-drx/3, dry/3)
    
    # 3d grab release
    def release(self, pos):
        CursorManager.unlockPosition()
