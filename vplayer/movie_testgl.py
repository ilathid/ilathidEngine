import sys
sys.path.append( "../" )
from engine import MoviePlayer
from engine import colorspace as cs

import time
import threading

import pygame

from OpenGL.GL import *
from OpenGL.GLU import *

from pygame.locals import *

class VCallback:
    overlay = None
    bufdata = None
    bufused = True
    vfr = None
    vfrused = True
    tex = None
    
    VTHREAD = False
    
    def __init__(self, fn):
    
        self._blk  = threading.Semaphore(1)
    
        f = open(fn, 'rb')
        data = f.read()
        f.close()
		
        print "data",len(data)
        
        self.movie = MoviePlayer.MoviePreloaded(data)
        self.movie.setCallback(self)
    
        self.size = self.movie.getSize()
        print "SIZE",self.size
        #(width,height) = (1280,1024)
        (width,height) = (800,600)
        pygame.init()
        screen = pygame.display.set_mode((width,height), HWSURFACE|DOUBLEBUF|OPENGL|FULLSCREEN)
    
    
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, float(width)/height, .1, 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
        # glEnable(GL_DEPTH_TEST)
        
        # glShadeModel(GL_FLAT)
        glClearColor(1.0, 1.0, 1.0, 0.0)
        # glColor(1.0, 1.0, 0.0, 0.0)

        self.tex = None
        
    
    def run(self):
        t1 = time.time()
        # tl = t1
        rotation = 0.0
        location = 0.0
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        while True:
            for event in pygame.event.get():
                # print event
                if event.type == QUIT:
                    self.movie.stop()
                    return
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.movie.stop()
                    return
                if event.type == KEYDOWN and event.key == K_p:
                    self.movie.pause()
                if event.type == KEYDOWN and event.key == K_5:
                    self.movie.seek(5.0)
                if event.type == KEYDOWN and event.key == K_SPACE:
                    self.movie.play()
                if event.type == KEYDOWN and event.key == K_l:
                    # self.movie.play({'loop':True, 'loopstart':1.0, 'loopend':5.0)
                    self.movie.play({'loop':True, 'loopstart':1.8, 'loopseek':True,'loopend':3.5})
                if event.type == KEYDOWN and event.key == K_s:
                    self.movie.stop()
            # print "events",time.time() - tl
            # tl = time.time()
            # Do Stuff
            time_passed = time.time() - t1
            if time_passed < 1.0/20:
                time.sleep(1.0/20 - time_passed)
            time_passed = time.time() - t1
            print "fr",1.0/time_passed
            t1 = time.time()
            # print "Framerate",1/time_passed
            
            # print rotation
            rotation = rotation + time_passed*15
            location = location - time_passed*20
            if location < -450.2:
                location = 0
            # glMatrixMode(GL_PROJECTION)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glRotated(180, 0, 1, 0)
            glRotated(rotation, 0, 0, 1 )
            glTranslated(0,0,location)

            # glBindTexture(GL_TEXTURE_2D, self.tex)
            if not self.VTHREAD:
                self._blk.acquire()
                vfrused = self.vfrused
                if not vfrused:
                    vfr = self.vfr
                    self.vfrused = True
                self._blk.release()
                if not vfrused and vfr != None:
                    self.convert(vfr)
                    
            self._blk.acquire()
            bufused = self.bufused
            if not bufused:
                bufdata = self.bufdata
                (szx,szy) = self.tex_size
                self.bufused = True
            self._blk.release()
            if not bufused and bufdata != None and time_passed < 1.0/10:
                try:
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                    glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
                    glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )

                    if self.tex == None:
                        szx_p2 = 1
                        while szx_p2 < szx:
                            szx_p2 = szx_p2 << 1
                        szy_p2 = 1
                        while szy_p2 < szy:
                            szy_p2 = szy_p2 << 1
                        
                        self.x2 = float(self.x1)/szx_p2
                        self.y2 = float(self.y1)/szy_p2
                        
                        print "p2",szx_p2,szy_p2
                        data = 'a' * (szx_p2*szy_p2*3)
                        self.tex = glGenTextures(1)
                        glBindTexture(GL_TEXTURE_2D, self.tex)
                        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, szx_p2, szy_p2, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
                        # generate initial texture
                        del data
                    tl = time.time()
                    glBindTexture(GL_TEXTURE_2D, self.tex)
                    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, szx, szy, GL_RGB, GL_UNSIGNED_BYTE, bufdata)
                    print "tc",time.time()-tl
                except:
                    print "Failed to update tex"
                del bufdata

            # print "tg",time.time() - tl            
            
            glClear(GL_COLOR_BUFFER_BIT)
            # print "opengl_clear",time.time() - tl
            # tl = time.time()
            glEnable(GL_TEXTURE_2D)
                        
            glBegin(GL_QUADS)
            
            # glTexCoord2f(0.0, 0.0)
            # glVertex3f(-2.0, -1.0, 0.0)
            # glTexCoord2f(0.0, 1.0)
            # glVertex3f(-2.0, 1.0, 0.0)
            # glTexCoord2f(1.0, 1.0)
            # glVertex3f(0.0, 1.0, 0.0)
            # glTexCoord2f(1.0, 0.0)
            # glVertex3f(0.0, -1.0, 0.0)
            
            glTexCoord2f(0.0, 0.0)
            glVertex3f(self.x1/2, self.y1/2, 500.0)
            glTexCoord2f(0.0, self.y2)
            glVertex3f(self.x1/2, -self.y1/2, 500.0)
            glTexCoord2f(self.x2, self.y2)
            glVertex3f(-self.x1/2, -self.y1/2, 500.0)
            glTexCoord2f(self.x2, 0.0)
            glVertex3f(-self.x1/2, self.y1/2, 500.0)
            
            glEnd()
            glDisable(GL_TEXTURE_2D)
            # print "draw",time.time() - tl
            # tl = time.time()
            pygame.display.flip()
            # print "flip",time.time() - tl
            tl = time.time()
            # print time_passed
            # time.sleep(0.05)
            
    def onVideoReady( self, vfr ):
        # tl = time.time()
        # print "sz",self.bufdata.size
        if not self.VTHREAD:
            self._blk.acquire()
            self.vfr = vfr
            if self.vfrused == False:
                print "<MISSED>"
            self.vfrused = False
            self._blk.release()
        else:
            self.convert(vfr)

        
    def convert(self, vfr):
        (x1,y1) = vfr.size
        if len(vfr.data[0]) != x1*y1:
            szx1 = len(vfr.data[0])/y1
            szy1 = y1
        else:
            szx1 = x1
            szy1 = y1
        try:
            tl = time.time()
            data = cs.yv2rgb(vfr.data[0], vfr.data[1], vfr.data[2], szx1, szy1)
            print "tl",time.time() - tl
            # if not self.bufused:
            #     print "<MISSED>"
            # else:
            #     print "<CONVERTED>"
            self._blk.acquire()
            self.bufdata = data
            self.tex_size = (szx1, szy1)
            (self.x1,self.y1) = (x1,y1)
            if self.bufused == False:
                print "<MISSED>"
            self.bufused = False
            self._blk.release()
        except Exception as e:
            print "<FAIL CONVERSION>"
            print e
        del vfr
        
        # print "tc",time.time()-tl

#vc = VCallback('test_clip.mpg')
#vc = VCallback('results2.mpg')
#vc = VCallback('hale_bopp_2.mpg')
#vc = VCallback('grb_1.mpg')
#vc = VCallback('centaur_2.mpg')
#vc = VCallback('test.mpg')
vc = VCallback('sample.mpg')
#vc = VCallback('365rev.mpg')
vc.run()
