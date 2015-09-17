from Logger import Logger
import threading
from Media import Media
from GLTexture import GLTexture
from SlideObject import SlideObject

"""
- when a video finishes, on next event call a callback.
  - callback
  - get last texture from video file, and trash it
  - clear texture (set to off)

- on render
  - if texture is on, draw
  - get last texture from video file, and store it if it exists

Movie can be given a playback condition. (seperate from normal condition state)
- if the playback condition is satisfied, the movie is both LOADED and PLAYED. If not, the movie is neither loaded nor played.

""" 

class Movie(SlideObject):
    _end_callback = None
    def __init__(self, geom, filepath):
        self.geom = geom
        self.isLoaded = False
        # init movie here
        self.filepath = filepath
        self.end_movie_event = False
        # print "uv",self.tex.getUV()
        # prep for playback thread here
        self.vfr = None
        self.tex_empty = True
        # payback includes self.tex.updateTexture(data)
    
    def setAutoPlayback(self, scond = "", fcond = None, looping=False):
        self._auto_looping = looping
        if fcond is None:
            self._auto_cond_string = scond
        else:
            self._auto_cond_func = fcond
    
    def makeBuffers(self):
        if self.isLoaded: return
        print "Make Movie " + self.filepath.getFilePath()
        self.movie = Media(self.filepath.getFilePath())
        self.movie.init()
        
        self.tex = GLTexture()
        # print "size",self.movie.size
        self.tex.emptyTexture(self.movie.getFrameSize())
        self.isLoaded = True
        
    def clearBuffers(self):
        if not self.isLoaded: return
        print "Clean Movie"
        self.movie.stop()
        self.movie.close()
        del self.movie
        del self.tex
        self.isLoaded = False
    
    def getDuration(self):
        if not self.isLoaded: return
        return self.movie.getDuration()
    
    def play(self, loop=True, starttime=-1):
        # clear the texture
        self.tex_empty = True
        Logger.log("Playing: <b>"+self.filepath.getFileName()+"</b>")
        if not self.isLoaded:
            raise Exception("Movie isn't loaded")
        if not self.movie.isPlaying():
            if starttime != -1:
                self.movie.seek(starttime)
            if loop:
                self.movie.loop()
            else:
                self.movie.play()
            self.end_movie_event = True
    
    def setEndCallback(self, callback):
        self._end_callback = callback
    
    def doEvents(self, events, dt):
        if not self.checkCondition() or not self.isLoaded:
            self.end_movie_event = False
            return
        if self._end_callback is not None and self.end_movie_event and not self.movie.isPlaying():
            # end of movie event
            self._end_callback()
        return events
    
    def stop(self):
        if not self.isLoaded: return
        self.movie.stop()
        self.end_movie_event = False
    
    def pause(self):
        if not self.isLoaded: return
        self.movie.pause()
    
    def __del__(self):
        self.movie.stop()
        self.movie.close()
        del self.movie
        del self.tex

    def render(self):
        # print "Checking Movie Condition"
        if not self.checkCondition(): return
        if not self.isLoaded:
            #print "Not Loaded"
            return
        if not self.movie.isPlaying():
            #print "Not Playing"
            if self.tex_empty:
                return
            self.tex_empty = True
            
        # Try updating texture if needed
        new_vfr = self.movie.getFrame()
        if new_vfr[1] > 0 and new_vfr[2] > 0:
            if self.vfr != None:
                del self.vfr
            self.vfr = new_vfr
            self.tex.updateTexture((0,0), (self.vfr[1], self.vfr[2]), self.vfr[0])
            if self.tex_empty:
                #print "First Frame"
                pass
            self.tex_empty = False
        else:
            #print "Old Frame"
            pass

        # Based on geom, simply render to screen using self.tex
        if not self.tex_empty:
            self.geom.renderTexture(self.tex)
