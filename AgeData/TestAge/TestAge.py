from Engine.Age import Age
from Engine.Slide3d import Slide3d
from Engine.Archive import FilePath
from Engine.Geometry import Geometry3d
from Engine.Movie import Movie

import threading

class TestAge(Age):

    def init(self):
        self._slides = {}
        
        slide = Slide3d("testSlide", "3d", [FilePath("testSlide/ZenGarden10_n.jpg", self.arch),
            FilePath("testSlide/ZenGarden10_e.jpg", self.arch),
            FilePath("testSlide/ZenGarden10_s.jpg", self.arch),
            FilePath("testSlide/ZenGarden10_w.jpg", self.arch),
            FilePath("testSlide/ZenGarden10_t.jpg", self.arch),
            FilePath("testSlide/ZenGarden10_b.jpg", self.arch)])
        

        fp2 = FilePath("sample.mpg", self.arch)
        geom = Geometry3d([(-1,1,-4.5),(-1,-2,-4.5),(2,-2,-4.5),(2,1,-4.5)])
        self.mov = Movie(geom, fp2)
        slide.attachObject(self.mov)

        geom = Geometry3d([(-1,1,-4.5),(2,1,-4.5),(2,-2,-4.5),(-1,-2,-4.5)])
        hp = self.engine.Hotspot(geom, callback=self.play_mov, cursor='grab')
        slide.attachObject(hp)
        
        self.mov_playing = True
        
        self._slides['testSlide'] = slide
        slide.callbacks['entry'] = self.on_entry1
        
    
    def on_entry1(self, slide):
        self.mov.makeBuffers()
        self.mov.play(loop=True)
    
    def play_mov(self):
        if not self.mov_playing:
            self.mov.play(loop=True)
            self.mov_playing = True
        else:
            self.mov.stop()
            self.mov_playing = False
