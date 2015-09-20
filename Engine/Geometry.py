from GLManager import GLManager
from Parameters import Parameters
import OpenGL.GL as GL
import OpenGL.GLU as GLU        

"""
Design decision: 
In Parametes:
    slide_size_3d    = (1024,1024)
    slide_size_2d    = (800,600)
    slide_2d_padding = (0,0,0,0) # top, bottom, left, right

are used to map slide image coordinates ('rects' from the age editor) to 2d and 3d geoms. This means the engine expects all slide textures to be of the specified dimensions. There were several reasons for this decision:

- it seems desirable that the age-editor and age .py files work in image-coordinates if they want to, as this is the most natural to game designers.
- it was hard to come up with a good design in which geoms store the shape information in image-coordinate form. This is because, in order to convert an image-coord to a screen coordinate, any object had to know something about the size of the slide image which was used to generate the slide texture, and the area on the screen where the slide was being rendered. This would have required some kind of heirarchical render mechanism, I think, as the information is far removed:
slide->texture->image coords
slide->decides area where slide is rendered on screen
slide->slide_object->geom->renders a texture, using above info from the slide.

The new design means that all coordinate conversion happens when the age is loaded. It wasn't desirable to read all 2d slide images to determine their size, so a standard size is used.
"""

def img2scr(points):
    """ Takes a position in 2d-slide image coordinates and makes a screen point via parameters """ 
    (sx,sy) = Parameters.slide_size_2d
    (pt,pb,pl,pr) = Parameters.slide_2d_padding
    (ww,hw) = Parameters.windowsize
    
    # True height/width of window area
    w = ww - pl - pr
    h = hw - pt - pb
    
    # Keep aspect, center window
    if h > w * float(sy)/sx:
        # decrease height of render area, keeping aspect
        new_h = w * float(sy)/sx
        pt += (h-new_h)/2
        h = new_h
    else:
        # decrease width of render area, keeping aspect
        new_w = h*float(sx)/sy
        pl += (w-new_w)/2
        w = new_w
        
    output = []
    for (x,y) in points:
        output.append((pl + x*w/sx, pt + y*h/sy))
    # print output
    return output

def geomFromSide(side, p1=(0,0), p2=(1,1)):
    """ Builds a rectangular geom on the face of a 10x10x10 cube """
    # If polygons are desireable, and if polygons are on the face of a cube, then
    #       we should really want this to be a bit more generic
    (x1,y1) = p1
    (x2,y2) = p2
    x1 = -10 + 20*x1
    x2 = -10 + 20*x2
    y1 = -10 + 20*y1
    y2 = -10 + 20*y2
    
    if side == "N":
        p1 = (x1,y2,-10) # up left
        p2 = (x1,y1,-10) # down left
        p3 = (x2,y1,-10) # down right
        p4 = (x2,y2,-10) # up right
    if side == "E":
        p1 = (10,y2,x1)
        p2 = (10,y1,x1)
        p3 = (10,y1,x2)
        p4 = (10,y2,x2)
    if side == "S":
        p1 = (-x1,y2,10)
        p2 = (-x1,y1,10)
        p3 = (-x2,y1,10)
        p4 = (-x2,y2,10)
    if side == "W":
        p1 = (-10,y2,-x1)
        p2 = (-10,y1,-x1)
        p3 = (-10,y1,-x2)
        p4 = (-10,y2,-x2)
    if side == "T":
        p1 = (x1,10,-y1) # bottom left
        p2 = (x1,10,-y2) # top left
        p3 = (x2,10,-y2) # top right
        p4 = (x2,10,-y1) # bottom right
    if side == "B":
        p1 = (-x2,-10,-y2) # top right
        p2 = (-x2,-10,-y1) # bottom right
        p3 = (-x1,-10,-y1) # bottom left
        p4 = (-x1,-10,-y2) # top left
    return Geometry3d([p1,p2,p3,p4])

class Geometry:
    _points = []
    type = "UNSPECIFIED"
    pos = (0,0)
    
    def __init__(self, points, pos=(0,0)):

        #Can use an average position. (Is this useless?)
        if pos is None:
            pavg_x = 0.0
            pavg_y = 0.0
            for (x,y) in points:
                pavg_x += x
                pavg_y += y
            pavg_x = float(pavg_x)/len(points)
            pavg_y = float(pavg_y)/len(points)
            
            points2 = []
            for (x,y) in points:
                points2.append((x-pavg_x, y-pavg_y))
            
            self.pos = (pavg_x,pavg_y)
            self._points = points2
        else:
            self.pos = pos
            self._points = list(points)
    
    def getPoints(self):
        points = []
        
        # Offset by self.pos
        if len(self.pos) == 2:
            (x0,y0) = self.pos
            for (x,y) in self._points:
                points.append((x0+x,y0+y))
        elif len(self.pos) == 3:
            (x0,y0,z0) = self.pos
            for (x,y,z) in self._points:
                points.append((x0+x,y0+y,z0+z))
        return points
    
    def setPosition(self,pos):
        self.pos = pos
    
    def setSize(self,size):
        self.pos = pos
    
    def getType(self):
        return self.type
    
    def renderPolygon(self, rgb=(1,1,1), width=1, filled=False):
        """ render geom as a polygon, with rgb or rgba"""
        points = self.getPoints()
        if self.type == "2d":
            GLManager._drawPolygon(points, "2d", rgb=rgb, width=width, filled=filled)
        if self.type == "3d":
            GLManager._drawPolygon(points, "3d", rgb=rgb, width=width, filled=filled)

    def renderTexture(self, texture):
        """ Render this geom with a texture """
        points = self.getPoints()
        if len(points) != 4:
            raise Exception("Geoms must have 4 points to render a texture")
            
        if self.type == "2d":
            vFunc = GL.glVertex2fv
            GLManager.setMode2d()
        if self.type == "3d":
            vFunc = GL.glVertex3fv
            GLManager.setMode3d()
        
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture.tex_id)
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0, 0)
        vFunc( points[0] )
        GL.glTexCoord2f(0,texture.uv_size[1])
        vFunc( points[1] )
        GL.glTexCoord2f(texture.uv_size[0], texture.uv_size[1])
        vFunc( points[2] )
        GL.glTexCoord2f(texture.uv_size[0],0)
        vFunc( points[3] )
        GL.glEnd()

class Geometry2d(Geometry):
    type = "2d"
    
class Geometry3d(Geometry):
    type = "3d"
    
    def __init__(self, points, pos=(0,0,0)):
        if pos is None:
            pavg_x = 0.0
            pavg_y = 0.0
            pavg_z = 0.0
            for (x,y,z) in points:
                pavg_x += x
                pavg_y += y
                pavg_z += z
            pavg_x = pavg_x/len(points)
            pavg_y = pavg_y/len(points)
            pavg_z = pavg_z/len(points)
            
            points2 = []
            for (x,y,z) in points:
                points2.append((x-pavg_x, y-pavg_y, z-pavg_z))
            
            self.pos = (pavg_x,pavg_y,pavg_z)
            self._points = points2
        else:
            self.pos = pos
            self._points = list(points)
