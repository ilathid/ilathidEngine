import xml.dom.minidom
from slide import slide
from AoIimage import AoIimage
from music import Music
from movie import movie
from FilePath import FilePath
from Slide3D import Slide3D
import globals

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

class age(object):
    
    # Crate an age from a XML file
    # filename : XML file describing the age
    def __init__(self, filename, supertype):
        self._filename = filename
        self._slides = {}
        self._movies = {}
        self._images = {}
        self._musics = {}
        
        xmlfile = xml.dom.minidom.parse(filename)
        
        if len(xmlfile.childNodes) != 1 or xmlfile.childNodes[0].localName != 'age':
            raise Exception("Age XML files must contain a single root element called 'age'")
        
        rootnode = xmlfile.childNodes[0]
        
        self._name = rootnode.getAttribute("name")
        self._firstSlide = rootnode.getAttribute("start")
        #first_slide = rootnode.getAttribute("start")
        
        for node in rootnode.childNodes:
            if node.localName == "slide":
                self._readslide(node, supertype)
            elif node.localName == "music":
                self._readmusic(node)
            elif node.localName == "movie":
                self._readmovie(node, supertype)
            elif node.localName is not None:
                print "WARNING, Unknown XML node <%s> in age file" % node.localName
                
        #self._slides[first_slide].display()
    
    # Get the name of the slide where the player should start in this age
    def getStartLocation(self):
        return self._firstSlide
    
    # read a <slide> tag from the XML file and build a 'slide' object from it
    def _readslide(self, node, supertype):
        slideid = node.getAttribute("id")
        is3D = (node.getAttribute("is3D") == "true")
        
        if is3D:
            filenodes = [subnode for subnode in node.childNodes if subnode.localName == "file"]
            
            filenames = []
            archives = []
            for filenode in filenodes:
                filename = getText(filenode.childNodes)
                filenames.append(filename)
                
                if filenode.hasAttribute('archive'):
                    archive = filenode.getAttribute('archive')
                else:
                    archive = None
                archives.append(archive)
            
            s = Slide3D(realname=slideid, filename=filenames, datfile=archives, encrypted=["0","0","0","0","0","0"])
        else:
            filenode = node.getElementsByTagName("file")[0]
            filename = getText(filenode.childNodes)
            
            if filenode.hasAttribute('archive'):
                archive = filenode.getAttribute('archive')
            else:
                archive = None
            
            s = slide(realname=slideid, filename=filename, datfile=archive)
        
        for subnode in node.childNodes:
            
            if subnode.localName == "file":
                # already handled above
                continue
            
            # Hotspot
            elif subnode.localName == "hotspot":
                cursortype = subnode.getAttribute('cursor')
                
                destOrientation = 0
                if subnode.hasAttribute('destOrientation'):
                    destOrientation = subnode.getAttribute('destOrientation')
                
                rect_list = []
                rect_node = subnode.getElementsByTagName('rect')
                if rect_node is not None and len(rect_node) > 0:
                    rect_str = getText(rect_node[0].childNodes)
                    if rect_str is not None and len(rect_str) > 0:
                        rect_list = map(lambda x: int(x), rect_str.split(","))
                
                polygon_list = []
                polygon_node = subnode.getElementsByTagName('polygon')
                if polygon_node is not None and len(polygon_node) > 0:
                    polygon_str = getText(polygon_node[0].childNodes)
                    if polygon_str is not None and len(polygon_str) > 0:
                        polygon_list = map(lambda x: int(x), polygon_str.split(","))
                        
                destination_tags = subnode.getElementsByTagName('dest')
                if len(destination_tags) == 1:
                    dest_slide = getText(destination_tags[0].childNodes)
                else:
                    dest_slide = None
                
                action_tags = subnode.getElementsByTagName('action')
                if len(action_tags) == 1:
                    action_str = getText(action_tags[0].childNodes)
                    action = lambda: getattr(supertype, action_str)(self)
                else:
                    action = None

                if len(rect_list) == 4:
                    hx = rect_list[0]
                    hy = rect_list[1]
                    hw = rect_list[2]
                    hh = rect_list[3]
                    
                    # Check if the hotspot spans on more than one cube face. If so then split it to simplify
                    # the math later
                    img_start = int(hx/1024)
                    img_end = int((hx + hw)/1024)
    
                    if img_start != img_end:
                        s.attachhotspot((hx, hy, (img_start+1)*1024 - hx ,hh),
                                        cursortype, keywords={'dest':dest_slide, 'action':action, 'destOrientation': int(destOrientation)})
                        s.attachhotspot(((img_start+1)*1024, hy, hx + hw - (img_start+1)*1024, hh),
                                        cursortype, keywords={'dest':dest_slide, 'action':action, 'destOrientation': int(destOrientation)})
                    else:
                        s.attachhotspot((hx, hy, hw, hh), cursortype,
                                        keywords={'dest':dest_slide, 'action':action, 'destOrientation': int(destOrientation)})
                else:
                    # TODO: check if polygon spans more than 1 face
                    s.attachhotspot(polygon_list, cursortype, mapType='polygon',
                                    keywords={'dest':dest_slide, 'action':action, 'destOrientation': int(destOrientation)})
                    
            # On entrance
            elif subnode.localName == "onentrance":
                onentrance_str = getText(subnode.childNodes)
                onentrance_fn = lambda: getattr(supertype, onentrance_str)(self)
                s.onentrance(onentrance_fn)
                
            # On exit
            elif subnode.localName == "onexit":
                onexit_str = getText(subnode.childNodes)
                onexit_fn = lambda: getattr(supertype, onexit_str)(self)
                s.onexit(onexit_fn)
            
            # Slide 'image' (sprite)
            elif subnode.localName == "image":
                self._readimage(subnode, s)
               
            elif subnode.localName == "minimapCoords":
                # This tag is used by the age editor, tolerate it
                pass
            
            elif subnode.localName is not None:
                raise Exception("Unknown XML element <%s> found under <slide>" % subnode.localName)
                
        self._slides[slideid] = s
        
    # read an <image> tag from XML
    # node : the XML node to read from
    # s : the slide this <image> appears under
    def _readimage(self, node, s):
        img_id = node.getAttribute('id')
        filenode = node.getElementsByTagName("file")[0]
        filename = getText(filenode.childNodes)
        
        if filenode.hasAttribute('archive'):
            archive = filenode.getAttribute('archive')
        else:
            archive = None
        
        rect_str = getText(node.getElementsByTagName('rect')[0].childNodes)
        rect_list = map(lambda x: int(x), rect_str.split(","))
        
        alpha_str = getText(node.getElementsByTagName('alpharef')[0].childNodes)
        alpha_list = map(lambda x: int(x), alpha_str.split(","))
        
        # TODO: add encryption support
        i = AoIimage(FilePath(filename, archive, 0), rect=(rect_list[0], rect_list[1]), slide=s,
                     alpha=(alpha_list[0], alpha_list[1]))
        
        self._images[img_id] = i
    
    # read a <music> tag from the XML file and build a 'Music' object from it
    def _readmusic(self, node):
        musicid = node.getAttribute("id")
        musictype = node.getAttribute("type")
        
        filenode = node.getElementsByTagName("file")[0]
        filename = getText(filenode.childNodes)
        
        volnode = node.getElementsByTagName("volume")[0]
        vol = float(getText(volnode.childNodes))
        
        m = Music(name=musicid, filename=filename, musictype=musictype, vol=vol)
        self._musics[musicid] = m
        
    # read a <movie> tag from the XML file and build a 'movie' object from it
    def _readmovie(self, node, supertype):
        movieid = node.getAttribute("id")
        filenode = node.getElementsByTagName("file")[0]
        filename = getText(filenode.childNodes)
        
        rect_str = getText(node.getElementsByTagName('rect')[0].childNodes)
        rect_list = map(lambda x: int(x), rect_str.split(","))
        
        endfuncElems = node.getElementsByTagName("endfunc")
        if len(endfuncElems) > 0:
            endfunc_str = getText(endfuncElems[0].childNodes)
            endfunc = lambda: getattr(supertype, endfunc_str)(self)
        else:
            endfunc = None
            
        m = movie(filename, (rect_list[0], rect_list[1], rect_list[2], rect_list[3]), endfunc=endfunc)
        self._movies[movieid] = m

    # The name of this age
    def getname(self):
        return self._name

    def getFileName(self):
        return self._filename

    def getslide(self, name):
        if name in self._slides:
            return self._slides[name]
        else:
            return globals.menuslides[name]
    
    def getAllSlides(self):
        return self._slides
    
    def getMusic(self, musicid):
        return self._musics[musicid]
