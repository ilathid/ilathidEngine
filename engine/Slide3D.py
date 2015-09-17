"""
                   .7a000BBBWBBBBB0B8Z;.                    
               :XZ80000Z7;,.   .:rXZ8B08827                 
             S0ZZ02r                  :ra0Z88X              
           aZa82;                         7aZZZS            
         SZaZ7                              .SZZZr          
       iZ2aS                 i                 SZa2:        
      2aa2.                 ,W                  ra2ar       
     a2aX                   S8:                   2SaS      
    ZS7.                    2X2                    i7SS     
   aXSXZS0WWWWWWB088BWWWW0aaXrX8aBWWWW088BWWWWWWW0S2SS27    
  ;SS2 X.         7        Xr;;X       i           7 ZXZ    
 .ZXS   Z7       XZZ      87rrrSX     7ZZ.       ;2   aXZ   
 ;SSr    ar     ra;S2     ar;;r7a    :2rXZ      :2    aXa,  
 arZ      Zr   72rrrS2   ZX;;rrrXS  :Z7rrX2    .0     i272  
 ar8       0, 8Ba222280 ,B2222222B rBa22228W: .Z       a7Z  
,SrZ        Zr:::::::,. ; ,,,:::. ;.,,::::,;i 0        S7a, 
,XXX         8         XX         a,         W         7X2: 
,X7X          W,     XZX2Z      ,aSSZ.     .Z          7X2i 
,S7Z           Zi  :2S7;rSS     Z7rrXar    Z           SXa. 
 2rZ            2 Sa7r;;;rSX  :a7r;;;7Sa  a            aXa  
 2Xa            :2X7;;rr7XSBX,WZX7;r;rrX2a            rSS7  
 i2X7          ZaX7SSZ88ZSi  7 .Xa88Z2X7rS2           a7Z.  
  8X2        0MBZar2        7a,       ;ZZ8B@2        :2X2   
  ,aS8      ;       Z      X2Xa7      7     7Z       aXZ    
   72SX              0    2S7r72r    a,             2Sai    
    222S              8  aZSXXX28X  2:             2Sa;     
     2a22             .Z;XXXX777X2 Si            ,aSZ7      
      Xa2ar             S         2,            2aaZ,       
        aaaZ.            B       a.           iaaZS         
         i8aZ2:           0     Si          rZaZa,          
           r8ZZZS         .Z   Xi        :2ZZZZi            
             ;aZZ8Za;       ; i,      7a8ZZZS,              
                iS0B0000Zar:SSX:7a8B00000X:                 
                    :XZ880B00Z80B08Za7.
"""

#Slide Class

import parameters
from engine import globals
from slide import slide

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *

class Slide3D(slide):

    # filename:  a list of 6 items [North, East, South, West, Top, Bottom]
    # datfile:   a list of 6 items [North, East, South, West, Top, Bottom]
    # encrypted: a list of 6 items [North, East, South, West, Top, Bottom]
    def __init__(self, filename, datfile, encrypted, type = 'std', realname = None,):
        
        if len(filename) != 6:
            raise Exception("A 3D slide must be built from 6 images, but received filenames " + str(filename))
        if len(datfile) != 6:
            raise Exception("A 3D slide must be built from 6 images, but received archive list " + str(datfile))
        if len(encrypted) != 6:
            raise Exception("A 3D slide must be built from 6 images")
        
        # Camera angle, for 3D slides
        self.yaw_angle = 0.0
        self.pitch_angle = 0.0
    
        #File info
        self._realname = realname
        self._file = filename
        self._datfile = datfile
        self._encrypted = encrypted
        
        #Buffer to hold slide BMPs
        self._slide_texture = [None, None, None, None, None, None]
        self._setInitialValues()
        
        self._is3D = True


    # Given the current yaw angle, return the min and max hotspot X that are on the screen
    def getHotspotMinMaxX(self, yaw_angle):
        # Calculations here are all approximate but good enough
        min_x = (yaw_angle + 13)/360.0 * 1024*4
        max_x = min_x + 1024
        
        min_x += 50
        max_x -= 350
        
        if min_x > 1024*4:
            min_x -= 1024*4
            max_x -= 1024*4
        
        return (min_x, max_x)

    # Clip a hotspot to the parts of it that are on-screen
    # @param x hotspot X coordinate
    # @param w hotpot width
    # @param min_x Minimum X currently visible
    # @param max_x Maximum X currently visible
    # @return The trimmed hotspot (x, w), where 'w' will be zero if the hotspot is not visible at all
    def restrainHotspotTo(self, x, w, min_x, max_x):
        
        if x < 1024 and max_x > 4096:
            min_x -= 4096
            max_x -= 4096
    
        x2 = x + w
        
        # Reject hotspots that are totally off-screen
        if x + w < min_x:
            return (0, 0)
        elif x > max_x:
            return (0, 0)
        
        # Trim hotspots to the visible part of them
        if x < min_x:
            x = min_x
            w = abs(x2 - x) # re-adjust width
        if x + w > max_x:
            w = max_x - x

        
        return (x, w)
                
    # Draws slide to screen buffer
    def render(self):
        
        glDisable(GL_DEPTH_TEST) # No Z buffer
        
        # Front (overflow from the usual size 10 to 12 to avoid "cracks" on the edges of the cube)
        self._getTexture(0).bind()
        glBegin(GL_QUADS)
        glTexCoord2f(-0.1, -0.1)
        glVertex3fv( (-12, 12,  -10) )
        glTexCoord2f(1.1, -0.1)
        glVertex3fv( (12,  12,  -10) )
        glTexCoord2f(1.1, 1.1)
        glVertex3fv( (12,  -12, -10) )
        glTexCoord2f(-0.1, 1.1)
        glVertex3fv( (-12, -12, -10) )
        glEnd()
        
        # Back (overflow from the usual size 10 to 12 to avoid "cracks" on the edges of the cube)
        self._getTexture(2).bind()
        glBegin(GL_QUADS)
        glTexCoord2f(1.1, -0.1)
        glVertex3fv( (-12, 12,  10) )
        glTexCoord2f(-0.1, -0.1)
        glVertex3fv( (12,  12,  10) )
        glTexCoord2f(-0.1, 1.1)
        glVertex3fv( (12,  -12, 10) )
        glTexCoord2f(1.1, 1.1)
        glVertex3fv( (-12, -12, 10) )
        glEnd()
        
        # Left
        self._getTexture(3).bind()
        glBegin(GL_QUADS)
        glTexCoord2f(1, 0)
        glVertex3fv( (-10, 10,  -10) )
        glTexCoord2f(0, 0)
        glVertex3fv( (-10, 10,  10) )
        glTexCoord2f(0, 1)
        glVertex3fv( (-10, -10, 10) )
        glTexCoord2f(1, 1)
        glVertex3fv( (-10, -10, -10) )
        glEnd()
        
        # Right
        self._getTexture(1).bind()
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3fv( (10, 10,  -10) )
        glTexCoord2f(1, 0)
        glVertex3fv( (10, 10,  10) )
        glTexCoord2f(1, 1)
        glVertex3fv( (10, -10, 10) )
        glTexCoord2f(0, 1)
        glVertex3fv( (10, -10, -10) )
        glEnd()
        
        # Top
        self._getTexture(4).bind()
        glBegin(GL_QUADS)
        glTexCoord2f(1, 0)
        glVertex3fv( (10, 10.0, 10) )
        glTexCoord2f(0, 0)
        glVertex3fv( (-10,  10.0, 10) )
        glTexCoord2f(0, 1)
        glVertex3fv( (-10,  10.0, -10) )
        glTexCoord2f(1, 1)
        glVertex3fv( (10, 10.0, -10) )
        glEnd()
        
        # Bottom
        self._getTexture(5).bind()
        glBegin(GL_QUADS)
        glTexCoord2f(1, 0)
        glVertex3fv( (10, -10.0, -10) )
        glTexCoord2f(0, 0)
        glVertex3fv( (-10,  -10.0, -10) )
        glTexCoord2f(0, 1)
        glVertex3fv( (-10,  -10.0, 10) )
        glTexCoord2f(1, 1)
        glVertex3fv( (10, -10.0, 10) )
        glEnd()
        
        # Draw each visible attached object
        # TODO: adapt object rendering code for 3D
        glEnable(GL_BLEND)
        for obj in self._attachedobjects:
            if obj.isvisible():
                obj.render()
    
        # ==== Hotspot debug ====
        if parameters.visualizeHotspots:
            (min_x, max_x) = self.getHotspotMinMaxX(self.yaw_angle)
            #print min_x, max_x
            
            for curr in self._hotspots:
                if curr['mapType'] == 'polygon':
                    coords = curr['map']
                    i = 0
                    glColor3f(1.0, 0.0, 0.0)
                    glLineWidth(3)
                    glBegin(GL_LINE_STRIP)
                    while i < len(coords) - 2:
                        x = coords[i]
                        y = coords[i + 1]
                        
                        # Convert to OpenGL coords (we use a cube of size 20)
                        # The X coordinate indicates on which face of the cube a hotspot is
                        # The front face has X coordinates 0 to 1023, the right face has 1024 to 2047, etc...
                        x = (x % 1024) / 1024.0 * 20.0 - 10.0
                        y = (1.0 - y / 1024.0) * 20.0 - 10.0
                        if coords[i] < 1024:
                            # front
                            glVertex3fv( (x, y, -10) )
                        elif coords[i] < 1024*2:
                            # right
                            glVertex3fv( (10, y, x) )
                        elif coords[i] < 1024*3:
                            # back
                            glVertex3fv( (-x, y, 10) )
                        elif coords[i] < 1024*4:
                            # left
                            glVertex3fv( (-10, y, -x) )
                        i += 2
                    glEnd()
                    continue
                    
                rect = list(curr['map']) # format (x, y, w, h)
                x = rect[0]
                y = rect[1]
                w = rect[2]
                h = rect[3]
            
                (x, w) = self.restrainHotspotTo(x, w, min_x, max_x)
                if (w == 0): continue
                    
                # Convert to OpenGL coords (we use a cube of size 20)
                # The X coordinate indicates on which face of the cube a hotspot is
                # The front face has X coordinates 0 to 1023, the right face has 1024 to 2047, etc...
                x = (x % 1024) / 1024.0 * 20.0 - 10.0
                y = (1.0 - y / 1024.0) * 20.0 - 10.0
                w = w / 1024.0 * 20.0
                h = h / 1024.0 * 20.0
    
                glColor3f(1.0, 0.0, 0.0)
                glLineWidth(3)
                if rect[0] < 1024:
                    # front
                    glBegin(GL_LINE_STRIP)
                    glVertex3fv( (x,     y,     -10) )
                    glVertex3fv( (x + w, y,     -10) )
                    glVertex3fv( (x + w, y - h, -10) )
                    glVertex3fv( (x,     y - h, -10) )
                    glVertex3fv( (x,     y,     -10) )
                    glEnd()
                elif rect[0] < 1024*2:
                    # right
                    glBegin(GL_LINE_STRIP)
                    glVertex3fv( (10, y    , x) )
                    glVertex3fv( (10, y    , x + w) )
                    glVertex3fv( (10, y - h, x + w) )
                    glVertex3fv( (10, y - h, x) )
                    glVertex3fv( (10, y    , x) )
                    glEnd()
                elif rect[0] < 1024*3:
                    # back
                    glBegin(GL_LINE_STRIP)
                    glVertex3fv( (-x,     y,     10) )
                    glVertex3fv( (-x - w, y,     10) )
                    glVertex3fv( (-x - w, y - h, 10) )
                    glVertex3fv( (-x,     y - h, 10) )
                    glVertex3fv( (-x,     y,     10) )
                    glEnd()
                elif rect[0] < 1024*4:
                    # left
                    glBegin(GL_LINE_STRIP)
                    glVertex3fv( (-10, y    , -x) )
                    glVertex3fv( (-10, y    , -x - w) )
                    glVertex3fv( (-10, y - h, -x - w) )
                    glVertex3fv( (-10, y - h, -x) )
                    glVertex3fv( (-10, y    , -x) )
                    glEnd()
            glColor3f(1.0, 1.0, 1.0)
    
    p_matrix = None
    
    def pickHotSpot_getMatrices(self):
        width = parameters.getscreensize()[0]
        height = parameters.getscreensize()[1]
        
        modelviewMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        
        if Slide3D.p_matrix is None:
            Slide3D.p_matrix = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = [0, 0, width, height]
        return (modelviewMatrix, Slide3D.p_matrix, viewport)
        
    def sameSign(self, a, b):
        if a < 0 and b < 0:
            return True
        if a > 0 and b > 0:
            return True
        return False
    
    def pointInTriangle(self, p1, p2, p3, p):
        a = (p1[0] - p[0])*(p2[1] - p[1]) - (p2[0] - p[0])*(p1[1] - p[1])
        b = (p2[0] - p[0])*(p3[1] - p[1]) - (p3[0] - p[0])*(p2[1] - p[1])
        if not self.sameSign(a, b):
            return False
        c = (p3[0] - p[0])*(p1[1] - p[1]) - (p1[0] - p[0])*(p3[1] - p[1])
        return self.sameSign(b, c)
    
    # Find which hotspot is under the cursor if any
    # mx : mouse x
    # my : mouse y
    def pickHotSpot(self, mx, my):
        # check hotspots by using simple OpenGL picking.
        
        #width = parameters.getscreensize()[0]
        height = parameters.getscreensize()[1]
        #modelviewMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        #projectionMatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        #viewport = [0, 0, width, height]
        
        (modelviewMatrix, projectionMatrix, viewport) = self.pickHotSpot_getMatrices() 
        mouse_p = (mx, height - my)
        
        (min_x, max_x) = self.getHotspotMinMaxX(self.yaw_angle)
        
        hotspotFound = False
        for curr in self._hotspots:
            
            if curr['mapType'] == 'polygon':
                continue # TODO: implement polygon hotspots
            
            rect = list(curr['map']) # format (x, y, w, h)
            
            x = rect[0]
            y = rect[1]
            w = rect[2]
            h = rect[3]
            
            (x, w) = self.restrainHotspotTo(x, w, min_x, max_x)
            if (w == 0): continue
            
            # Convert to OpenGL coords (we use a cube of size 20)
            # The X coordinate indicates on which face of the cube a hotspot is
            # The front face has X coordinates 0 to 1023, the right face has 1024 to 2047, etc...
            x = (x % 1024) / 1024.0 * 20.0 - 10.0
            y = (1.0 - y / 1024.0) * 20.0 - 10.0
            w = w / 1024.0 * 20.0
            h = h / 1024.0 * 20.0
            
            if rect[0] < 1024:
                # North
                
                # Project the coords in 2D screen space
                p1 = gluProject(x,     y,     -10, modelviewMatrix, projectionMatrix, viewport)
                p2 = gluProject(x + w, y,     -10, modelviewMatrix, projectionMatrix, viewport)
                p3 = gluProject(x + w, y - h, -10, modelviewMatrix, projectionMatrix, viewport)
                p4 = gluProject(x,     y - h, -10, modelviewMatrix, projectionMatrix, viewport)
            elif rect[0] < 1024*2:
                # East
                
                # Project the coords in 2D screen space
                p1 = gluProject(10, y,     x,     modelviewMatrix, projectionMatrix, viewport)
                p2 = gluProject(10, y,     x + w, modelviewMatrix, projectionMatrix, viewport)
                p3 = gluProject(10, y - h, x + w, modelviewMatrix, projectionMatrix, viewport)
                p4 = gluProject(10, y - h, x,     modelviewMatrix, projectionMatrix, viewport)
            elif rect[0] < 1024*3:
                # South
                
                # Project the coords in 2D screen space
                p1 = gluProject(-x,     y,     10, modelviewMatrix, projectionMatrix, viewport)
                p2 = gluProject(-x - w, y,     10, modelviewMatrix, projectionMatrix, viewport)
                p3 = gluProject(-x - w, y - h, 10, modelviewMatrix, projectionMatrix, viewport)
                p4 = gluProject(-x,     y - h, 10, modelviewMatrix, projectionMatrix, viewport)
            elif rect[0] < 1024*4:
                # West
                
                # Project the coords in 2D screen space
                p1 = gluProject(-10, y,     -x,     modelviewMatrix, projectionMatrix, viewport)
                p2 = gluProject(-10, y,     -x - w, modelviewMatrix, projectionMatrix, viewport)
                p3 = gluProject(-10, y - h, -x - w, modelviewMatrix, projectionMatrix, viewport)
                p4 = gluProject(-10, y - h, -x,     modelviewMatrix, projectionMatrix, viewport)
            else:
                raise Exception("Hotspot coords too large")
            
            #x1_at_my = x4 + (x1 - x4)*(my - y1)/(y4 - y1)
            #x2_at_my = x3 + (x2 - x3)*(my - y2)/(y3 - y2)
            #mouse_inside = (mx >= min(x1_at_my, x2_at_my) and mx <= max(x1_at_my, x2_at_my))
            
            mouse_inside = self.pointInTriangle(p1, p2, p3, mouse_p) or self.pointInTriangle(p1, p3, p4, mouse_p)
            
            if mouse_inside:
                slide._currenthotspot = curr
                globals.curcursor = globals.cursors.get(curr.get('cursor'))
                if globals.curcursor is None:
                    raise Exception("Cannot find cursor '" + curr.get('cursor') + "'")
                hotspotFound = True
                break
            
        if not hotspotFound:
            # no hotspot under the mouse
            #Set the current hotspot to None
            slide._currenthotspot = None
            #Return the default hotspot for the slide type
            if self._type == 'ui':
                globals.curcursor = globals.cursors.get('arrow')
            else:
                globals.curcursor = globals.cursors.get('forward')
        
        
        
