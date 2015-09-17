#!/usr/bin/env python
import time
import pygame

from OpenGL.GL import *
from OpenGL.GLU import *

from Engine.Slide import Slide3d
from Engine.FilePath import FilePath
from Engine.Movie import Movie
from Engine.Image import Image
from Engine.GLTexture import GLTexture
from Engine.GLManager import GLManager
from Engine.Geometry import Geometry3d
#from Archive import Archive_file
from Engine.Archive import Archive

from pygame.locals import *

(width,height) = (800,600)
pygame.init()
#screen = pygame.display.set_mode((width,height), HWSURFACE|OPENGL|FULLSCREEN|DOUBLEBUF) # 
screen = pygame.display.set_mode((width,height), HWSURFACE|OPENGL|DOUBLEBUF) # 

GLManager.init((width,height))
GLManager.setMode3d()

# Create the archive object - name, location
# arch = Archive_file("test_slide_files", "")
arch = Archive("TestAge", {"type":"file", "file_loc":"Data"})
#NESWTB
slide = Slide3d("testslide", "3d", [FilePath("testSlide/ZenGarden10_n.jpg", arch),
    FilePath("testSlide/ZenGarden10_e.jpg", arch),
    FilePath("testSlide/ZenGarden10_s.jpg", arch),
    FilePath("testSlide/ZenGarden10_w.jpg", arch),
    FilePath("testSlide/ZenGarden10_t.jpg", arch),
    FilePath("testSlide/ZenGarden10_b.jpg", arch)])

fp = FilePath("sample.mpg", arch)
mo = Movie(Geometry3d((1,1,2),(.5,1,2),(.5,-.5,2),(1,-.5,2)), fp)
slide.attachObject(mo)

fp = FilePath("testSlide/ZenGarden10_e.jpg", arch)
print dir(Image)
im = Image(Geometry3d((-1,.25,2),(-.5,.25,2),(-.5,-.5,2),(-1,-.5,2)), fp)
slide.attachObject(im)

slide.makeBuffers()

def run():
    rotation = -90
    dr = .1
    mo.play()
    while True:
        for event in pygame.event.get():
            # print event
            if event.type == QUIT:
                mo.stop()
                return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                mo.stop()
                return
            if event.type == KEYDOWN and event.key == K_SPACE:
                mo.play()
                dr = 0
            if event.type == KEYDOWN and event.key == K_p:
                mo.pause()
                dr = .1
        # glMatrixMode(GL_PROJECTION)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotated(0, 1, 0, 0)
        glRotated(rotation, .01, 1, 0 )
        rotation = rotation - dr*3

        glClear(GL_COLOR_BUFFER_BIT)
        
        # Render
        try:
            slide.render()
        except:
            pass
        
        pygame.display.flip()
        
run()
