import pygame
import re
from GLManager import GLManager, checkGLError
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
from Parameters import Parameters

"""
GLTexture is used to create and store opengl textures.

GLTexture.tex_id  :  to setup opengl to draw the texture
GLTexture.uv_size :  to know what part of the texture is valid
GLTexture.size    :  to know the original size of the texture region

My intention is that all textures in Ilathid are GLTextures. These textures contain a
rectangular region (uv_size) which is where the valid texture data is. size is the original
pixel-size of the texture data, for the sake of coordinate conversion.

Rendering a texture onto a geom often involes mapping the 4 uv corners of the texture, but other things are possible.

In the end, it seemed desirable that use of the texture be as flexible as possible. Other classes do their own opengl rendering, using a textures .tex_id. That means that this file
is mostly just convenience. You could allocate your own opengl textures if you really wanted to.

"""
class GLTexture:
    tex_id = None
    uv_size = (0,0)
    size = (0,0)
    
    def __init__(self):
        pass
    
    
    def fontTexture(self, filepath, string, color=(0,0,0), just=0, size=24):
        """ Load a texture from a font, by font filename. """
        # Could have passed a font object itself, would this have been a good idea?
        
        fio = filepath.open()
        font = pygame.font.Font(fio, size)

        surfs = []
        
        # parse markup: Make many text surfs in lines
        for line in string.splitlines():
            surf_line = []
            blocks = re.split('(</?[biuBIU]>)', line)
            for block in blocks:
                if block in ('<b>', '<B>'):
                    font.set_bold(True)
                elif block in ('</b>', '</B>'):
                    font.set_bold(False)
                elif block in ('<i>', '<I>'):
                    font.set_italic(True)
                elif block in ('</i>', '</I>'):
                    font.set_italic(False)
                elif block in ('<u>', '<U>'):
                    font.set_underline(True)
                elif block in ('</u>', '</U>'):
                    font.set_underline(False)
                else:
                    size = font.size(block)
                    # surf,size tuple
                    # print "'" + block + "'"
                    surf_line.append((font.render(block, 1, color), size))
            surfs.append(surf_line)
        
        fio.close()
        
        # compose surfs into a complete image
        # First: find out the target image size
        x = 0
        y = 0
        for surf_line in surfs:
            x_inner = 0
            for (surf, size) in surf_line:
                x_inner += size[0]
            y += font.get_linesize()
            x = max(x_inner, x)
        
        final_surf = pygame.surface.Surface((x, y), flags=pygame.SRCALPHA)
        final_surf.fill((255,255,255,0))
        
        # Do a bunch of blitting
        x = 0
        y = 0
        for surf_line in surfs:
            for (surf, size) in surf_line:
                final_surf.blit(surf, (x, y))
                x += size[0]
            y += font.get_linesize()
            x = 0
        
        # Convert the final_surf to an opengl texture
        data = pygame.image.tostring(final_surf, "RGBA", False)
        #for c in data:
        #    print ord(c)
        
        # print len(data)
        # print final_surf.get_size()
        
        self.dataTexture(data, final_surf.get_size(), alpha=True)
        del final_surf
        del surfs
    
    # set opengl texture to that of an image from a fileref
    def imageTexture(self, fileref, alpha=False, repeat=None):
        pyimage = pygame.image.load(fileref, 'namehint.jpg')
        self.size = pyimage.get_size()
        
        if alpha:
            data = pygame.image.tostring(pyimage, "RGBA", False)
        else:
            data = pygame.image.tostring(pyimage, "RGB", False)
        
        self.tex_id, self.uv_size = GLTexture._newTexture(data, self.size, alpha=alpha, repeat=repeat)
        del pyimage
        del data

    # Create a texture from data
    def dataTexture(self, data, (w, h), alpha=False, repeat=None):
        self.size = (w,h)
        self.tex_id, self.uv_size = GLTexture._newTexture(data, self.size, alpha=alpha, repeat=repeat)
    
    # Set opengl texture to a blank texture of the given size
    def emptyTexture(self, (w,h), alpha=False, repeat=None):
        self.size = (w,h)
        if alpha:
            dsize = 4*w*h
        else:
            dsize = 3*w*h
        
        # Create data representing many zeros
        data = chr(0) * dsize
        self.tex_id, self.uv_size = GLTexture._newTexture(data, self.size, alpha=alpha, repeat=repeat)
        del data
    
    def updateTexture(self, (x, y), (w,h), data, alpha=False):
        GLTexture._updateTexture(self.tex_id, (x,y), (w,h), data, alpha=alpha)
        
    # Create a new opengl texture from data, size, and properties
    @classmethod
    def _newTexture(self, data, (w,h), alpha=False, repeat=None):
        """
        Returns: tex, size, uv
        -tex is the opengl texture
        -size is the original image size (for aspect)
        -uv is the (0,0)-(u,v) image loc in texture (0.0 to 1.0)
        """
        # Get the smallest power-of-two larger than w, h
        (p2w,p2h) = (1,1)
        while p2w < w:
            p2w = p2w << 1
        while p2h < h:
            p2h = p2h << 1
        
        # Set the uv info, indicating what part of the texture holds the actual image.
        uv = (float(w)/p2w, float(h)/p2h)

        glGetError() # Clear error flag
        tex = glGenTextures(1)
        checkGLError("glGenTextures")
        glBindTexture(GL_TEXTURE_2D, tex)
        checkGLError("glBindTexture")
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        if repeat == "both" or repeat == "x":
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        else:
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        if repeat == "both" or repeat == "y":
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        else:
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        checkGLError("glTexParameter")
        
        # Generate the actual texture
        # print p2w, p2h
        if alpha:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, p2w, p2h, 0, GL_RGBA,
                GL_UNSIGNED_BYTE, "0"*4*p2w*p2h)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)
        else:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, p2w, p2h, 0, GL_RGB,
                GL_UNSIGNED_BYTE, "0"*3*p2w*p2h)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, data)

        checkGLError("glTexImage2D")
        # print tex, uv
        return tex, uv

    @classmethod
    def _updateTexture(self, tex, (x, y), (w,h), data, alpha=False):
        if alpha:
            format = GL_RGBA
        else:
            format = GL_RGB
        glBindTexture(GL_TEXTURE_2D, tex)
        #print w*h*3
        #print len(data)
        #print ord(data[-1])
        
        glTexSubImage2D(GL_TEXTURE_2D, 0, x, y, w, h, format, GL_UNSIGNED_BYTE, data)

    def __del__(self):
        glDeleteTextures([self.tex_id])
