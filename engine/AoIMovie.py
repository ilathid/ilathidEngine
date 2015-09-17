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

#Movie Class and support functions
import parameters
from userarea import *
from pygame.locals import *
from filemanager import filemanager


#Movie Class
class movie(userarea,):
    __module__ = __name__

    def __init__(self, filename = None, rect = None, cursor = 0, looping = 0, endfunc = None, skippable = 0):
        #Looping movie
        self._looping = looping
        #Looping moves must allow cursor use, and may not have an exit function
        if looping:
            self._cursor = 1
            self._endfunc = None
            self._skippable = 0
        else:
            self._cursor = cursor
            self._endfunc = endfunc
            self._skippable = skippable
        #Paused state of the movie
        self._paused = 0
        #Is the movie currently playing (even if paused)
        self._playing = 0
        #Internal Pygame movie object
        self._movie = None
        #Allow a two element rect to be specified (x,y), or 4 element (x,y,w,h)
        #if a two element is passed in, use (x,y,0,0)
        #Then init the base object
        if (rect != None):
            if (len(rect) > 2):
                userarea.__init__(self, rect, 1, 0)
            else:
                userarea.__init__(self, (rect,(0,0,),), 1, 0)
        else:
            userarea.__init__(self, None, 1, 0)
        #Movie file. Compression and encryption are not supported at this time
        self._file = filename
        
        #Add movie to globals list of movies
        #Put directly in age loader 
        #globals.movies[self._realname] = self

    #Draws area to screen buffer.
    def _draw(self):
        pass

    #Changes any of objects's attributes and draws area to screen buffer.
    def update(self, filename = None, rect = None, cursor = None, looping = None, endfunc = None, visible = None, skippable = None):
        if self._playing:
            if (visible != None):
                self._visible = visible
        else:
            if (filename != None):
                self._file = filename
            if (looping != None):
                self._looping = looping
                if looping:
                    self._cursor = 1
                    self._endfunc = None
                    self._skippable = 0
                else:
                    if (cursor != None):
                        self._cursor = cursor
                    if (endfunc != None):
                        self._endfunc = endfunc
                    if (skippable != None):
                        self._skippable = skippable
            else:
                if (cursor != None):
                    self._cursor = cursor
                if (endfunc != None):
                    self._endfunc = endfunc
                if (skippable != None):
                    self._skippable = skippable
        if (rect != None):
            if (len(rect) > 2):
                self._rect = pygame.Rect(rect)
                if self._playing:
                    self._movie.set_display(globals.screensurface, self._rect)
            else:
                self._rect = pygame.Rect(rect, (0,0,))
                if self._playing:
                    self._rect.size = self._movie.get_size()
                    self._movie.set_display(globals.screensurface, self._rect)



    def islooping(self):
        return self._looping



    def isskippable(self):
        return self._skippable



    def isplaying(self):
        return self._playing



    def ispaused(self):
        return self._paused



    def pause(self, donthide = 0):
        if self._playing:
            self._movie.pause()
            if self._paused:
                if (not self._visible):
                    self.update(visible=1)
            else:
                self.update(visible=donthide)
            self._paused = (not self._paused)



    def play(self):
        #pygame.mixer for music deactivation
        if(pygame.mixer):
            pygame.mixer.quit()
        if (not self._playing):
            self._movie = pygame.movie.Movie(filemanager.find_movie(self._file))
            if (self._rect.size == (0,0,)):
                self._rect.size = self._movie.get_size()
            self._areasurface = pygame.Surface(self._rect.size)
            self._movie.set_display(globals.screensurface, self._rect)
            self._visible = 1
            globals.playing.append(self)
            self._playing = 1
            self._movie.play(self._looping)
            if (self._cursor == 0):
                globals.curcursor.disable()
            if (len(globals.playing) == 1):
                pygame.time.set_timer(globals.MOVIEEVENT, parameters.getmovieinterval())



    def stop(self, abort = 1):
        if self._playing:
            self._movie.stop()
            self.update(visible=0)
            globals.playing.remove(self)
            self._movie = None
            self._playing = 0
            self._paused = 0
            if ((self._endfunc != None) and (not abort)):
                if globals.functions.has_key(self._endfunc):
                    globals.functions[self._endfunc]()
                else:
                    self._endfunc()
            if (len(globals.playing) == 0):
                pygame.time.set_timer(globals.MOVIEEVENT, 0)
            if (self._cursor == 0):
                if (not globals.curcursor.isenabled()):
                    if (not len([ item for item in globals.playing if (item._cursor == 0) ])):
                        globals.curcursor.enable()



    def _save(self):
        saveval = userarea._save(self)
        saveval['looping'] = self._looping
        saveval['skippable'] = self._skippable
        saveval['cursor'] = self._cursor
        saveval['endfunc'] = self._endfunc
        saveval['paused'] = self._paused
        saveval['playing'] = self._playing
        saveval['file'] = self._file
        return saveval



    def _load(self, saveinfo):
        userarea._load(self, saveinfo)
        saveval = saveinfo[self._id]
        self._looping = saveval['looping']
        self._skippable = saveval['skippable']
        self._cursor = saveval['cursor']
        self._endfunc = saveval['endfunc']
        self._paused = saveval['paused']
        self._playing = saveval['playing']
        self._file = saveval['file']



    def _handleevent(self, event):
        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_SPACE):
                if (self._skippable and self._playing):
                    self.stop(0)
