from Parameters import Parameters
from GLTexture import GLTexture
from Geometry import Geometry2d
import pygame.mouse

class CursorManager:
    
    visible = True
    curcursor = None
    cursors = {}
    hotspots = {}
    size = {}
    
    pos = None
    geom = None 
    
    lock = None
    
    @classmethod
    def setDefault(self, cursor):
        CursorManager.default = cursor
    
    @classmethod
    def lockPosition(self, pos):
        CursorManager.lock = pos
    
    @classmethod
    def unlockPosition(self):
        CursorManager.lock = None    
    
    @classmethod
    def setPosition(self, pos):
        pygame.mouse.set_pos(pos)
    
    @classmethod
    def getPosition(self):
        return pygame.mouse.get_pos()
    
    @classmethod
    def addCursor(self, filepath, name, hotspot):
        """ hotspot is position of hotspot in cursor """
        pygame.mouse.set_visible(False)
        fio = filepath.open()
        tex = GLTexture()
        tex.imageTexture(fio, alpha=True) # Passing a file-like object        
        (w,h) = tex.size
        fio.close()
        
        scale = Parameters.cursor_scale
        
        w = w * scale
        h = h * scale

        CursorManager.cursors[name] = tex
        CursorManager.hotspots[name] = (hotspot[0]*scale, hotspot[1]*scale)
        CursorManager.size[name] = (w,h)
        if len(CursorManager.cursors) == 1:
            CursorManager.curcursor = name
            CursorManager.default = name
    
    @classmethod
    def setCursor(self, name):
        if name in CursorManager.cursors:        
            CursorManager.curcursor = name
        else:
            raise Exception("CursorManager: No cursor named " + name)
    
    @classmethod
    def render(self):
        if CursorManager.curcursor is None:
            raise Exception("CursorManager: Must set cursor!")
        if CursorManager.lock is not None:
            pos = CursorManager.lock
            pygame.mouse.set_pos(pos)
        else:
            pos = pygame.mouse.get_pos()
        if CursorManager.visible:
            tex = CursorManager.cursors[CursorManager.curcursor]
            # if CursorManager.pos == pos:
            #     geom = CursorManager.geom
            # else:
            hotspot = CursorManager.hotspots[CursorManager.curcursor]
            size = CursorManager.size[CursorManager.curcursor]
            
            x1 = -hotspot[0]
            x2 = size[0] - hotspot[0]
            y1 = -hotspot[1]
            y2 = size[1] - hotspot[1]
            
            geom = Geometry2d([(x1,y1),(x1,y2),(x2,y2),(x2,y1)], pos=pos)
            CursorManager.pos = pos
            CursorManager.geom = geom
            geom.renderTexture(tex)
        
        # reset each frame
        CursorManager.setCursor(CursorManager.default)
