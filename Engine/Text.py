import os, pygame, re
import pygame.locals
import pygame.surface
import pygame.font
from GLTexture import GLTexture
from Image import Image
from Geometry import Geometry2d

""" Text is an extension of Image, but the image of which is a font-rendered string.
    Note that it may be preferrable, for whatever text you are rendering, to use a 
    texture, with the fontTexture constructor, and then do your rendering with that.
    This class is really only meaningful for text objects on a slide (ie a menu).
    
    You could also place text on a 3d-geom which allows the text to 'map' into a 3d
    environment. IE for writing custom text directly into a 3d slide. But probably
    you just want prerendered textures for that.
    
    Justification not implemented. I am unsure of if the chartable from text.py was needed,
    it was complicated so I left it out for now. I would figure pygame.font can space
    charecters correctly? It was probably only used for word-wrapping, which I'm not sure
    is worth coding for at this stage as I think eventually we want (almost) all prerendered
    text anyway.
    """

#Text class: a rendered peice of text
class Text(Image):
    # fileref : an instance of class FilePath
    def __init__(self, geom, filepath, string, color=(0,0,0), just=0, size=24):
        self.geom_helper = geom
        self.filepath = filepath
        self.string = string
        self.color = color
        self.just = just
        self.size = size
        self.userlineheight = userlineheight
        self.isLoaded = False
        
    def makeBuffers(self):
        if self.isLoaded: return
        
        self.tex = GLTexture()
        self.tex.fontTexure(self.filepath, self.string, self.color, self.just, self.size)

        (w,h) = self.tex.size

        self.geom = Geometry2d([(0,0),(0,h),(w,h),(w,0)], pos=self.geom_helper.getPosition())
        self.isLoaded = True
