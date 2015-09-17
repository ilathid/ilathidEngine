from GLTexture import GLTexture
from SlideObject import SlideObject

class Image(SlideObject):
    def __init__(self, geom, filepath):
        # self.geom = geom
        self.geom = geom
        self.filepath = filepath
        self.isLoaded = False
    
    def makeBuffers(self):
        if self.isLoaded: return
        fio = self.filepath.getFile()
        self.tex = GLTexture()
        self.tex.imageTexture(fio, alpha=True) # Passing a file-like object        
        fio.close()
        self.isLoaded = True
        
    def clearBuffers(self):
        del self.tex
        self.isLoaded = False
    
    def __del__(self):
        if self.isLoaded:
            del self.tex

    def render(self):
        if not self.checkCondition(): return
        if not self.isLoaded:
            raise Exception("Image (" + self.name + ") is not in memory!")
        # Based on geom, simply render to screen using self.tex
        self.geom.renderTexture(self.tex)
