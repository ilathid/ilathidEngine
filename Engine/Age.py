import xml.dom.minidom
from Slide import Slide, Slide2d
from Slide3d import Slide3d
from Image import Image
#from music import Music
#from movie import movie
from Archive import FilePath
from Geometry import geomFromSide, img2scr, Geometry3d, Geometry2d
from Archive import Archive
from Parameters import Parameters
from Logger import Logger

import threading

def unpackInts(node):
    if node is not None and len(node) > 0:
        _str = getText(node[0].childNodes)
        if _str is not None and len(_str) > 0:
            return map(lambda x: int(x), _str.split(","))
    return []
    
def unpackGeom3d(node):
    # Just a guess...
    sides = "NESW"
    
    """ Returns a list of geoms, in case the rects span more than one face. """
    geoms = []
    rect_list = unpackInts(node)
    hx = rect_list[0]
    hy = rect_list[1]
    hw = rect_list[2]
    hh = rect_list[3]

    side_start = int(hx/1024)
    side_end = int((hx+hw)/1024)
    
    if side_start == side_end:
        x1 = (hx % 1024) / 1024.0
        x2 = ((hx+hw) % 1024) / 1024.0
        y1 = 1.0 - hy / 1024.0
        y2 = 1.0 - (hy+hh) / 1024.0
        
        geoms.append(geomFromSide(sides[side_start], (x1, y1), (x2, y2)))
    else:
        x1 = (hx % 1024) / 1024.0
        x2 = 1
        y1 = hy / 1024.0
        y2 = (hy+hh) / 1024.0
        geoms.append(geomFromSide(sides[side_start], (x1, y1), (x2, y2)))
        
        side_start = side_start + 1
        while side_start < side_end:
            x1 = 0
            x2 = 1
            y1 = hy / 1024.0
            y2 = (hy+hh) / 1024.0
            geoms.append(geomFromSide(sides[side_start], (x1, y1), (x2, y2)))
            side_start = (side_start + 1) % 4
            # TODO does side_start need % here?
        
        # in case of wrapping
        side_start = side_start % 4
        x1 = 0
        x2 = ((hx+hw) % 1024) / 1024.0
        y1 = hy / 1024.0
        y2 = (hy+hh) / 1024.0
        
        print "side start: %d" % (side_start)
        geoms.append(geomFromSide(sides[side_start], (x1, y1), (x2, y2)))
    return geoms    

def unpackGeom2d(node):
    """ Returns a list of geoms (only ever has one element) """
    geoms = []
    rect_list = unpackInts(node)
    hx = rect_list[0]
    hy = rect_list[1]
    hw = rect_list[2]
    hh = rect_list[3]

    geoms.append(Geometry2d(img2scr([(hx,hy), (hx,hy+hh), (hx+hw,hy+hh), (hx+hw,hy)])))
    return geoms

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

class Age(object):
    isLoaded = False    
    
    def __init__(self, ageName, arch, params, engine):
        self.ageName = ageName
        self.arch = arch
        self.params = params
        self.engine = engine
        self._slides = {}
        # self._movies = {}
        # self._images = {}
        # self._musics = {}
        
        # TODO: Age Slide Memory Management Thread
        #self.t = threading.Thread(None, target=self._t_buffer)
        self._blk  = threading.Semaphore(1)     
    
    # Crate an age from a XML file
    # filename : XML file describing the age
    def loadXML(self):
        """ Initializes the age data using an age.xml file in the root of the archive """
        # Get the xml file from the archive
        fpxml = FilePath("age.xml", self.arch)
        
        self._slides = {}
        # self._movies = {}
        # self._images = {}
        # self._musics = {}
        
        # Threading for background memory management.
        # TODO: Think and organize
        #self.t = threading.Thread(None, target=self._t_buffer)
        #self._blk  = threading.Semaphore(1)
        
        # Parse xml file
        fpfile = fpxml.open()
        xmlfile = xml.dom.minidom.parse(fpfile)
        fpfile.close()
        
        if len(xmlfile.childNodes) != 1 or xmlfile.childNodes[0].localName != 'age':
            raise Exception("Age XML files must contain a single root element called 'age'")
        
        rootnode = xmlfile.childNodes[0]
        
        if not rootnode.hasAttribute("name"):
            raise Exception("Age root node needs a 'name' attribute")
        self._name = rootnode.getAttribute("name")
        if not rootnode.hasAttribute("start"):
            raise Exception("Age root node needs a 'start' attribute")
        
        # TODO: When a player asks to go to an age, and doesn't specify a slide, 
        # maybe this can be used.
        # Right now linking to ages requires age.slide, so that the target slide is
        # always specified.
        self._firstSlide = rootnode.getAttribute("start")
        
        for node in rootnode.childNodes:
            if node.localName == "slide":
                self._readslide(node)
            # elif node.localName == "music":
            #     self._readmusic(node)
            # elif node.localName == "movie":
            #     self._readmovie(node)
            elif node.localName is not None:
                print "WARNING, Unknown XML node <%s> in age file" % node.localName
        
        #self._slides[first_slide].display()
        self.loaded()
    
    def loaded(self):
        pass
    
    # # Get the name of the slide where the player should start in this age
    # def getStartLocation(self):
    #     return self._firstSlide
    
    # read a <slide> tag from the XML file and build a 'slide' object from it
    def _readslide(self, node):
        slideid = node.getAttribute("id")
        is3D = (node.getAttribute("is3D") == "true")
        
        if is3D:
            filenodes = [subnode for subnode in node.childNodes if subnode.localName == "file"]
            
            filepaths = []
            for filenode in filenodes:
                filename = "slides/" + getText(filenode.childNodes)
                
                if filenode.hasAttribute('archive'):
                    archive = Archive(filenode.getAttribute('archive'), self.params.file_loc)
                else:
                    archive = self.arch
                filepaths.append(FilePath(filename, archive))
            
            s = Slide3d(slideid, '3d', filepaths)
        else:
            filenode = node.getElementsByTagName("file")[0]
            filename = "slides/" + getText(filenode.childNodes)
            
            if filenode.hasAttribute('archive'):
                archive = Archive(filenode.getAttribute('archive'), self.params.file_loc)
            else:
                archive = self.arch
            
            s = Slide(slideid, "2d", FilePath(filename, archive))
        
        for subnode in node.childNodes:
            
            if subnode.localName == "file":
                # already handled above
                continue
            
            # Hotspot
            elif subnode.localName == "hotspot":
                hotspot = self._readhotspot(subnode, s)
                    
            # On entrance
            elif subnode.localName == "onentry":
                # print "XML: Found onentry function " + str(getText(subnode.childNodes)) + ", will add to " + str(s)
                onentrance_str = getText(subnode.childNodes)
                # onentrance_fn = lambda: getattr(self, onentrance_str)(self)
                onentrance_fn = getattr(self, onentrance_str)
                s.callbacks['entry'] = onentrance_fn
                
            # On exit
            elif subnode.localName == "onexit":
                onexit_str = getText(subnode.childNodes)
                onexit_fn = getattr(self, onexit_str)
                s.callbacks['exit'] = onexit_fn
            
            # Slide 'image' (sprite)
            elif subnode.localName == "image":
                self._readimage(subnode, s)
               
            elif subnode.localName == "minimapCoords":
                # This tag is used by the age editor, tolerate it
                pass
            
            elif subnode.localName is not None:
                raise Exception("Unknown XML element <%s> found under <slide>" % subnode.localName)
                # print "Unknown XML element <%s> found under <slide>" % subnode.localName
                
        self._slides[slideid] = s
        
    def _readhotspot(self, node, s):
        cursortype = node.getAttribute('cursor')
        print "Read Hotspot for slide " + s.name
        destOrientation = 0
        if node.hasAttribute('destOrientation'):
            destOrientation = node.getAttribute('destOrientation')
            
        cond_string = None
        cond_tags = node.getElementsByTagName('cond')
        if len(cond_tags) == 1:
            cond_string = getText(cond_tags[0].childNodes)
        
        rect_node = node.getElementsByTagName('rect')
        if s.getType() == "3d":
            geoms = unpackGeom3d(rect_node)
        if s.getType() == "2d":
            geoms = unpackGeom2d(rect_node)
        
        #polygon_list = []
        #polygon_node = node.getElementsByTagName('polygon')
        #polygon_list = unpackInts(polygon_node)
                
        destination_tags = node.getElementsByTagName('dest')
        action_tags = node.getElementsByTagName('action')
        if len(destination_tags) == 1:
            dest_slide = getText(destination_tags[0].childNodes)
            for geom in geoms:
                h = self.engine.Hotspot(geom, dest=dest_slide, cursor=cursortype, dest_dir=(0, int(destOrientation)))
                if cond_string is not None:
                    h.setCondString(cond_string)
                s.attachObject(h)
        if len(action_tags) == 1:
            action_str = getText(action_tags[0].childNodes)
            action = lambda: getattr(self, action_str)()
            for geom in geoms:
                h = self.engine.Hotspot(geom, callback=action, cursor=cursortype)
                if cond_string is not None:
                    h.setCondString(cond_string)
                s.attachObject(h)
    
    # read an <image> tag from XML
    # node : the XML node to read from
    # s : the slide this <image> appears under
    def _readimage(self, node, s):
        img_id = node.getAttribute('id')
        filenode = node.getElementsByTagName("file")[0]
        filename = "images/" + getText(filenode.childNodes)
        
        if filenode.hasAttribute('archive'):
            archive = Archive(filenode.getAttribute('archive'), self.params.file_loc)
        else:
            archive = self.arch

        cond_string = None
        cond_tags = node.getElementsByTagName('cond')
        if len(cond_tags) == 1:
            cond_string = getText(cond_tags[0].childNodes)
        
        # rects need to be converted to an x/y/z coordinate based on:
        # - the texture size (rects are in texture coordinates)
        rect_node = node.getElementsByTagName('rect')
        if s.getType() == "3d":
            geoms = unpackGeom3d(rect_node)
        if s.getType() == "2d":
            geoms = unpackGeom2d(rect_node)
        
        if len(geoms) > 1:
            raise Exception("Image must not span cube sides")            
                
        i = Image(geoms[0], FilePath(filename, archive))
        if cond_string is not None:
            i.setCondString(cond_string)
        s.attachObject(i)
    
    # read a <music> tag from the XML file and build a 'Music' object from it
    def _readmusic(self, node):
        pass
#        musicid = node.getAttribute("id")
#        musictype = node.getAttribute("type")
#        
#        filenode = node.getElementsByTagName("file")[0]
#        filename = getText(filenode.childNodes)
#        
#        volnode = node.getElementsByTagName("volume")[0]
#        vol = float(getText(volnode.childNodes))
#        
#        m = Music(name=musicid, filename=filename, musictype=musictype, vol=vol)
#        self._musics[musicid] = m
#        
    # read a <movie> tag from the XML file and build a 'movie' object from it
    def _readmovie(self, node):
        pass
#        movieid = node.getAttribute("id")
#        filenode = node.getElementsByTagName("file")[0]
#        filename = getText(filenode.childNodes)
#        
#        rect_str = getText(node.getElementsByTagName('rect')[0].childNodes)
#        rect_list = map(lambda x: int(x), rect_str.split(","))
#        
#        endfuncElems = node.getElementsByTagName("endfunc")
#        if len(endfuncElems) > 0:
#            endfunc_str = getText(endfuncElems[0].childNodes)
#            endfunc = lambda: getattr(self.ageName, endfunc_str)(self)
#        else:
#            endfunc = None
#            
#        m = movie(filename, (rect_list[0], rect_list[1], rect_list[2], rect_list[3]), endfunc=endfunc)
#        self._movies[movieid] = m

    # The name of this age
    def getName(self):
        return self.ageName

    def getFirstSlide(self):
        return self._slides[self._firstSlide]

    def getSlide(self, name):
        if not name in self._slides:
            raise Exception("No such slide: %s in age %s" % (name, self._name))
        return self._slides[name]
    
    def getAllSlides(self):
        return self._slides
    
#    def getMusic(self, musicid):
#        return self._musics[musicid]
    
    # Buffer Thread
    def _t_start(self):
        #if self.t.is_alive():
        #    self.t.join()
        #self.t.start()
        pass
    
    def _t_buffer(self):
        self._blk.acquire()
        for slide in self._slides.values():
            if slide.getName() in self.slds:
                slide.makeBuffers()
                Logger.log("Age: Loaded " + slide.getName())
            else:
                slide.clearBuffers()
        self._blk.release()

    # Given a set of slides the age should have preloaded, either load or unload slides as needed, using threading.        
    def manageBuffers(self, slide_name):
        if self.isLoaded: return
        links = self.getSlide(slide_name).getLinks()
        self._blk.acquire()
        self.slds = []
        for link in links:
            parts = link.split(".")
            if len(parts) == 1 and parts[0] in self._slides:
                self.slds.append(parts[0])
            if len(parts) == 2 and parts[0] == self.ageName and parts[1] in self._slides:
                self.slds.append(parts[1])
        self._blk.release()
        self._t_start()
        self.isLoaded = True
        
    def clearBuffers(self):
        for slide in self._slides.values():
            slide.clearBuffers()
        self.isLoaded = False
