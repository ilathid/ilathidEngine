from GLTexture import GLTexture
from SlideObject import SlideObject
from GLManager import GLManager
import pygame.locals
from Parameters import Parameters
from CursorManager import CursorManager

# The following code is pulled directly from here:
# http://www.ariel.com.au/a/python-point-int-poly.html
# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
def PolyPoint(poly, (x,y)):
    # print "test: " + str((x, y))
    n = len(poly)
    inside =False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside

# Test to see if a point on the screen overlaps a geom.
# The geom is either 2d or 3d, can be polygon.
def TestPoint(geom, point):
    gtype = geom.type
    if gtype == "3d":
        if GLManager.getMode() != GLManager.MODE3D:
            GLManager.setMode3d()
        GLManager.init_pick(point)
        GLManager.drawPolygon3d(geom.getPoints(), filled=True)
        hits = GLManager.end_pick()
        return len(hits)>0
        #p = []
        #for point in geom.getPoints():
        #    p.append(GLManager.project3d(point))

        # Test the points in the resulting polygon
        # return PolyPoint(p, (x,y))
    elif gtype == "2d":
        # TODO: Consider using above method here
        return PolyPoint(geom.getPoints(), point)    
    else:
        raise Exception("Can't test point in geom of type " + gtype)

# Hotspots test for click, enter, leave. Something else has to handle more complicated behavior
class Hotspot(SlideObject):
    _entered = False
    # callbacks={"click":None, "enter":None, "leave":None}
    def __init__(self, geom, click=None, enter = None, leave = None):
        self.geom = geom
        self.click = click
        #self.clickArgs = clickArgs
        self.enter = enter
        #self.enterArgs = enterArgs
        self.leave = leave
        #self.leaveArgs = leaveArgs
        self._entered = False
        # For now, callback can be set by the user to a function, or by the age-creator to a generic function to go to a new slide
    
    # Handle Hotspot Events
    def doEvents(self, events, dt):
        if events is None: return  
        if not self.checkCondition(): return
        for event in events:
            if event.type == pygame.locals.MOUSEBUTTONUP and self.click and event.button == 1 and TestPoint(self.geom, event.pos):
                self.click(event.pos)
                events.remove(event)
            if event.type == pygame.locals.MOUSEMOTION and (self.enter or self.leave):
                self.passMouseMove(event.pos)
    
    def passMouseMove(self, pos):
        if not self._entered and TestPoint(self.geom, pos):
            self._entered = True
            if self.enter:
                self.enter(pos)
        elif self._entered and not TestPoint(self.geom, pos):
            self._entered = False
            if self.leave:
                self.leave(pos)
    
    def render(self):
        if Parameters.draw_hotspots and self.checkCondition():
            self.geom.renderPolygon()

# A hotspot which is tied into the engine
class EngineHotspot(Hotspot):
    def __init__(self, engine, geom, callback=None, dest=None, cursor=None, dest_dir=None):
        self.engine = engine
        self.dest = dest
        self.cursor = cursor
        self.callback = callback
        self.dest_dir=dest_dir
        self.hovering = False

        if (not dest) == (not callback):
            raise Exception("Supply exactly one of dest or callback")
        if dest:
            click = self.destClick
        else:
            click = self.callbackClick
            
        if cursor:
            enter = self.cursorEnter
            leave = self.cursorLeave
        else:
            enter = None
            leave = None
        Hotspot.__init__(self, geom, click=click, enter = enter, leave = leave)
        
    def destClick(self, pos):
        self.engine.gotoSlide(self.dest)
        
        # orient the view
        if self.dest_dir is not None:
            GLManager.viewRotation(*self.dest_dir)
    
    def callbackClick(self, pos):
        self.callback()
     
    def cursorEnter(self, pos):
        self.hovering = True
        #print "Enter"

    def cursorLeave(self, pos):
        self.hovering = False
        #print "Leave"

    def getDest(self):
        return self.dest
        
    def render(self):
        if self.checkCondition():
            if self.hovering:
                CursorManager.setCursor(self.cursor)
            Hotspot.render(self)
