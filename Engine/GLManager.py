from Parameters import Parameters
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
from ctypes import util
try:
    from OpenGL.platform import win32
except AttributeError:
    pass

# This is a 'static class'. I have no idea if this is good programming practice. Might as well find out.
class GLManager():
    # Stores state of opengl device
    
    MODE2D = 0
    MODE3D = 1
    mode = None

    screensize = None
    
    rotx = 0
    roty = 0

    picking = False

    @classmethod
    def init(self, screen_size):
        """ Initialize the GLManager module, which defaults to 3d view."""
        if screen_size is None:
            raise Exception("GLManager: Need Screen Size")
        if self.screensize is not None:
            raise Exception("GLManager: init can't be called twice")
            
        self.screensize = screen_size
        
        bg = Parameters.backgroundcolor
        
        glEnable(GL_TEXTURE_2D) # can be disabled for drawing without texture
        glClearColor(bg[0], bg[1], bg[2], 0.0)
        glDisable (GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        
        (width, height) = self.screensize

        # Prepare Viewport
        glViewport(0, 0, width, height)
        
        # Prep for 3d
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(Parameters.vfov, float(width)/float(height), 0.1, 500.0)
        # 53 by 88: 4.5 views around
        # 32 by 53: 7 views around
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotated(-GLManager.rotx, 1, 0, 0)
        glRotated(GLManager.roty, .01, 1, 0 )
        
        GLManager.mode = GLManager.MODE3D
        #GLManager.model_mat = glGetDoublev(GL_MODELVIEW_MATRIX)
        #GLManager.proj_mat  = glGetDoublev(GL_PROJECTION_MATRIX)
        #GLManager.view_mat  = glGetIntegerv(GL_VIEWPORT)


    @classmethod
    def setMode3d(self):
        """ Switch to 3d mode, for following with opengl calls which draw in 3d """
        if GLManager.mode == GLManager.MODE3D:
            return
        if GLManager.picking:
            raise Exception("GLManager: Can't change modes while picking")
            
        glDisable (GL_BLEND);

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotated(-GLManager.rotx, 1, 0, 0)
        glRotated(GLManager.roty, .01, 1, 0 )
        
        GLManager.mode = GLManager.MODE3D

    @classmethod
    def setMode2d(self):
        """ Switch to 2d mode, for following with opengl calls which draw in 2d """
        if GLManager.mode == GLManager.MODE2D:
            return
        if GLManager.picking:
            raise Exception("GLManager: Can't change modes while picking")

        (width, height) = self.screensize

        glEnable (GL_BLEND);

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, width, height, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        GLManager.mode = GLManager.MODE2D

        
    @classmethod
    def viewRotate(self, x, y):
        """ Rotate the 3d perspective by x and y """
        GLManager.viewRotation(GLManager.rotx + x, GLManager.roty + y)
    
    @classmethod
    def viewRotation(self, x, y):
        """ Set the 3d perspective rotation to x and y """
        x = max(min(x, 90), -90)
        y = (y + 180) % 360 - 180
        GLManager.rotx = x
        GLManager.roty = y
        
        if GLManager.mode == GLManager.MODE3D and not GLManager.picking:
            glLoadIdentity()
            
            glRotated(-x, 1, 0, 0)
            glRotated(y, .01, 1, 0 )

    @classmethod
    def init_pick(self, pos):
        """
Initialize picking

What this does is set up a 5x5 test area at position pos on the screen. Then objects
are 'drawn', and finally end_pick indicates which objects showed up in the test area.
This is used for mouse position testing over 3d polygons.

You must be in the desired drawing mode (2d or 3d) /before/ calling this method.
        """
        glSelectBuffer(512)
        vm = glGetIntegerv(GL_VIEWPORT)
        (width, height) = self.screensize
        
        glRenderMode(GL_SELECT)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPickMatrix(pos[0],vm[3]-pos[1],5,5,vm)
        
        if GLManager.mode == GLManager.MODE3D:
            gluPerspective(50.0, float(width)/float(height), 0.1, 500.0)
        else:
            gluOrtho2D(0, width, height, 0)            
            
        GLManager.picking = True

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        if GLManager.mode == GLManager.MODE3D:
            glRotated(-GLManager.rotx, 1, 0, 0)
            glRotated(GLManager.roty, .01, 1, 0 )
    
    @classmethod
    def end_pick(self):
        """
        leaves picking mode, and returns a hit list of items which were picked.
        
        Basically, if return value len is > 0, then the screen position intersects the polygon that was drawn.
        """
        hits = glRenderMode(GL_RENDER)
        GLManager.picking = False
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
                
        return hits
            
    @classmethod
    def project3d(self, (x,y,z)):
        """ Another method for testing polygons. Returns the screen coordinates of an xyz coordinate """
        mm = glGetDoublev(GL_MODELVIEW_MATRIX)
        pm  = glGetDoublev(GL_PROJECTION_MATRIX)
        vm  = glGetIntegerv(GL_VIEWPORT)
        return gluProject(x, y, z, mm, pm, vm)
    
    @classmethod
    def getMode(self):
        """ 2d or 3d """
        return GLManager.mode
        
    @classmethod
    def drawPolygon3d(self, points, rgb=(1,1,1), width=1, filled=False):
        """
        Draws a 3d polygon
        rgb can have 3 or 4 elements. If it has 4, the last is a transparency value.
        """
        GLManager._drawPolygon(points, "3d", rgb=rgb, width=width, filled=filled)

    @classmethod
    def _drawPolygon(self, points, mode, rgb=(1,1,1), width=1, filled=False):
        if mode == "2d":
            GLManager.setMode2d()
            vFunc = glVertex2fv
        elif mode == "3d":
            GLManager.setMode3d()
            vFunc = glVertex3fv
        glDisable(GL_TEXTURE_2D)        
        if len(rgb) == 3:
            glColor4d( rgb[0], rgb[1], rgb[2], 1)
        elif len(rgb) == 4:
            glColor4d( rgb[0], rgb[1], rgb[2], rgb[3])
        else:
            raise Exception("GLManager: rgb needs 3 or 4 colors")

        if not filled:
            glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )

        # How does opengl know which visible area of the polygon to fill?

        glLineWidth(width)
        glBegin(GL_POLYGON) 
        #print "points:"
        for point in points:
            vFunc( point )
            #print point
        vFunc( points[0])
        glEnd()

        if not filled:
            glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

        glColor4d(1,1,1, 1)
        # glDisable(GL_BLEND); 
        glEnable(GL_TEXTURE_2D)

    @classmethod
    def drawPolygon2d(self, points, rgb=(1,1,1), width=1, filled=False):
        """
        Draws a 2d polygon
        rgb can have 3 or 4 elements. If it has 4, the last is a transparency value.
        """
        GLManager._drawPolygon(points, "2d", rgb=rgb, width=width, filled=filled)
            
    @classmethod
    def clear(self):
        """
        Clears the OpenGL display buffer
        """
        glClear(GL_COLOR_BUFFER_BIT)

def checkGLError(commandname):
    errorcode = glGetError()
    if errorcode != GL_NO_ERROR:
        raise Exception("OpenGL error " + errorcode + " in " + commandname)
