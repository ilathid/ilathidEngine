"""
This is just dummy code for the interface elements of the game environment - a menu button on the top of the screen, etc.

This is an example of a library extension.
This one is added to the Engine with E.attatchLayer(i). 

Parameters:
II_height (30)        - height of top interface bar
II_hover_height (10)  - area where mouse causes bar to drop
II_hover_timer (1)    - seconds for hover before menu drops
II_bar_color ((.5,.55,.55, .9))    - rgba color of the bar
"""

from Engine.EngineLayer import EngineLayer
from Engine.GLTexture import GLTexture
from Engine.GLTexture import GLManager
from Engine.Geometry import Geometry2d
from Engine.Parameters import Parameters
from Engine.Logger import Logger

from Engine.Text import Text
from Engine.Archive import Archive
from Engine.Archive import FilePath

import pygame.locals
import time

class topBar():
    def __init__(self):
        pass
        
    def doEvents(self, events, dt):
        return events
    
    def render(self):
        pass

""" Currently, the log bar display just the most recent log message. This is not necessarily helpful. """

class LogBar():
    text = []
    delay = 4

    h = 0  # desired height of log stack
    y = 0  # actual height, ie y-position
    hide = True

    def __init__(self):
        # Poke a hole through to the logger...
        Logger.addCallback(self.getMessage)
        
        # Archive
        self.arch = Archive("Interface", {"type":"file", "file_loc":"Data"})
        self.font_file = FilePath('AC.TTF', self.arch)
#        self.font_file = FilePath('avgardn.ttf', self.arch)
#        self.font_file = FilePath('Ilathidhi01.ttf', self.arch)
        Logger.log("<b>Init: </b> IlathidInterface")
        
    def getMessage(self, text):
        # Make a new geometry object for the text.
        (sw, sh) = Parameters.windowsize
        # self.geom = Geometry2d([(0, 0), (100, 0), (100, -100), (0, -100)], pos=(0,sh))
        
        # Convert text to a renderable-text object
        # te = Text(geom, self.font_file, text)
        
        tex = GLTexture()
        tex.fontTexture(self.font_file, text)

        (w,h) = tex.size
        
        self.y += h
        
        geom = Geometry2d([(0,0),(0,h),(w,h),(w,0)])
        
        self.text.append((text, tex, geom, h, time.time()))
        
    def doEvents(self, events, dt):
        dt = min(dt,.1)
        # drop messages
        t = time.time()
        if len(self.text) > 0:
            (text, tex, geom, h, t_time) = self.text[0]
            # print (text, t - t_time)
            if t - t_time > self.delay:
                del tex, geom
                self.text.pop(0)
                #print "REMOVE"
                #print len(self.text)
        
        #self.h = 0.0
        #for (text, tex, geom, h, t_time) in self.text:
        #    self.h += h
        
        if self.y > 0:
            self.y -= 50*dt
        if self.y < 0:
            self.y = 0            
        
        return events
    
    def render(self):
        (sw,sh) = Parameters.windowsize
        #p1 = (0,sh)
        #p2 = (sw,sh)
        #p3 = (sw, sh-self.y)
        #p4 = (0, sh-self.y)
        #points = [p1, p2, p3, p4]
        #GLManager.drawPolygon2d(points, rgb=(.5,.55,.55, .9), filled=True)

        height = 0.0
        for (text, tex, geom, h, t_time) in self.text[::-1]:
            height += h
            geom.setPosition((0,sh-height+self.y))
            geom.renderPolygon(rgb=(.5,.55,.55, .9), filled=True)
            geom.renderTexture(tex)


class IlathidInterface(EngineLayer):
    def __init__(self):
        # Note: I'm not sure what else to do here...
        #self.height = Parameters.ifSet("II_height", 30)
        #self.height_sens = Parameters.ifSet("II_hover_height", 10)
        #self.hover_timer_max = Parameters.ifSet("II_hover_timer", 1)

        self.logBar = LogBar()
        
    def doEvents(self, events, dt):
        self.logBar.doEvents(events, dt)
        return events
        
    def render(self):
        self.logBar.render()
