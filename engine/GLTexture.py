import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import math

def checkGLError(commandname):
    errorcode = glGetError()
    if errorcode != GL_NO_ERROR:
        raise Exception("OpenGL error " + errorcode + " in " + commandname)

class GLTexture:
    
    # image: either a Pygame Surface or a path to a file
    def __init__(self, image, namehint=None, repeat_horizontally=False, repeat_vertically=False):
        
        if isinstance(image, pygame.Surface):
            textureSurface = image
        else:
            if namehint is None:
                textureSurface = pygame.image.load(image)
            else:
                textureSurface = pygame.image.load(image, namehint)
        
        self._width = textureSurface.get_width()
        self._height = textureSurface.get_height()
        
        # Because older GPUs don't support non-power-of-2 textures, some portion of the texture may be unused
        self._content_width = self._width
        self._content_height = self._height
        
        log_w = math.log(self._width, 2)
        log_h = math.log(self._height, 2)
                
        # If the image is not a power-of-two, we need to copy it over to a larger power-of-2 image.
        correctWidth  = int(math.pow( 2, math.ceil(log_w) ))
        correctHeight = int(math.pow( 2, math.ceil(log_h) ))
        
        # FIXME: detect if the GPU/driver supports non-power-of-two textures?
        if self._width != correctWidth or self._height != correctHeight:
            #print "[GLTexture] WARNING: Image", image, "has non-power-of-two size", self._width, "x", self._height, \
            #      ". Size ", correctWidth, "x", correctHeight, " is recommended"
            newsurface = pygame.Surface((correctWidth, correctHeight), pygame.SRCALPHA)
            newsurface.fill(pygame.Color(0, 0, 0, 0)) # fill with transparency
            newsurface.blit(textureSurface, (0,0))
            textureData = pygame.image.tostring(newsurface, "RGBA", False)

            self._max_u = float(self._width) / float(correctWidth) # max texture coordinate
            self._max_v = float(self._height) / float(correctHeight) # max texture coordinate
            self._width = correctWidth
            self._height = correctHeight
        else:
            textureData = pygame.image.tostring(textureSurface, "RGBA", False)
            self._max_u = 1.0
            self._max_v = 1.0

        glGetError() # Clear error flag
        
        self._texture = glGenTextures(1)
        
        checkGLError("glGenTextures")
        
        glBindTexture(GL_TEXTURE_2D, self._texture)
        
        checkGLError("glBindTexture")
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT if repeat_horizontally else GL_CLAMP_TO_EDGE )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT if repeat_vertically else GL_CLAMP_TO_EDGE )
        
        checkGLError("glTexParameter")
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self._width, self._height, 0, GL_RGBA,
            GL_UNSIGNED_BYTE, textureData)
        
        checkGLError("glTexImage2D")
    
    def __del__(self):
        # TODO: implement unloading
        pass
    
    def getWidth(self):
        return self._width
    
    def getHeight(self):
        return self._height
    
    
    def draw(self, x, y):
        self.scaleDraw(x, y, self._content_width, self._content_height)

    
    def scaleDraw(self, x, y, w, h):
        glBindTexture(GL_TEXTURE_2D, self._texture)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f( x, y )
        glTexCoord2f(self._max_u, 0)
        glVertex2f( x + w, y )
        glTexCoord2f(self._max_u, self._max_v)
        glVertex2f( x + w, y + h )
        glTexCoord2f(0, self._max_v)
        glVertex2f( x, y + h )
        glEnd()
        
    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self._texture) 
        