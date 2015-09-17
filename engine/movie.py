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
from filemanager import filemanager
from userarea import *
from pygame.locals import *
import globals

#Handles the movie's event from the engine
def moviehandler(event):
    #Skip if there are no movies playing
    if globals.playing != []:
        #Build a list of all unpaused, visible, playing movies
        tmpmovielist = [curmovie for curmovie in globals.playing if curmovie.isvisible() and not curmovie.ispaused()]
        #If there are any:
        if tmpmovielist != []:
            #Get one of the movies rects
            dirtyrect = tmpmovielist[0].getrect()
            #Make a rect that encompasses all movies rects
            dirtyrect.unionall_ip([item.getrect() for item in tmpmovielist])
            #find the lowest playing movie in the list of user areas
            lowest = len(globals.userareasordered)
            for curmovie in tmpmovielist:
                if globals.userareasordered.index(curmovie) < lowest:
                    lowest = globals.userareasordered.index(curmovie)
            #Hide all objects above the lowest item that are in the rect made earlier
            dirtyrect = userarea._redrawfrom(globals.userareasordered[lowest], 0, dirtyrect)
            #If this movie has an old background saved, draw it to the uhabuffer
            if globals.userareasordered[lowest]._bgsurface != None:
                globals.uhabuffer.fill((0,0,0,0), globals.userareasordered[lowest]._rect)
                globals.uhabuffer.blit(globals.userareasordered[lowest]._bgsurface, globals.userareasordered[lowest]._rect)
            #Redraw the lowest movie
            globals.userareasordered[lowest]._draw()
            #Restore all objects above the lowest movie in the compund rect
            #As a side effect this causes ALL the movies to be redrawn
            dirtyrect = userarea._redrawfrom(globals.userareasordered[lowest], 1, dirtyrect)
            #Update the screen
            globals.updateuhasurface(dirtyrect)
        #Stop any finished movies
        for curmovie in tmpmovielist:
            #If the movie is not busy, it's done playing
            if not curmovie._movie.get_busy():
                #Stop it and allow the exit function to be called
                curmovie.stop(0)

#Add the event handler to the engine
globals.eventhandlers[globals.MOVIEEVENT] = moviehandler

#Movie Class
class movie(userarea):
    'class for replaying movies in SMPEG format'
    def __init__(self, filename = None, rect = None, cursor = 0, looping = 0, endfunc = None):
        #Looping movie
        self._looping = looping
        #Looping moves must allow cursor use, and may not have an exit function
        if looping:
            self._cursor = 1
            self._endfunc = None
        else:
            self._cursor = cursor
            self._endfunc = endfunc
        #Paused state of the movie
        self._paused = 0
        #Is the movie currently playing (even if paused)
        self._playing = 0
        #Internal Pygame movie object
        self._movie = None
        #Allow a two element rect to be specified (x,y), or 4 element (x,y,w,h)
        #if a two element is passed in, use (x,y,0,0)
        #Then init the base object
        if rect != None:
            if len(rect) > 2:
                userarea.__init__(self, rect, 0, 0)
            else:
                userarea.__init__(self, (rect,(0,0)), 0, 0)
        else:
            userarea.__init__(self, None, 0, 0)
        #Movie file. Compression and encryption are not supported at this time
        self._file = filename

    #Draws area to screen buffer.
    def _draw(self):
        #Only draw if visible
        if self._visible:
            #Save the area behind the movie
            self._bgsurface = pygame.Surface(self._rect.size).convert_alpha()
            self._bgsurface.fill((0,0,0,0))
            self._bgsurface.blit(globals.uhabuffer, (0,0), self._rect)
            #Draw the current contents of the movie out to the screen
            globals.uhabuffer.blit(self._areasurface, self._rect)

    #Changes any of objects's attributes and draws area to screen buffer.
    def update(self, file = None, rect = None, cursor = None, looping = None, endfunc = None, visible = None):
        #Rect to hold updatd screen area
        dirtyrect = None
        #If playing, changing rect or visibility need to restore the old bg and hide the items above it
        if self._playing:
            #Update the visibility (can only be changed when the movie is playing)
            if visible != None:
                self._visible = visible
        else:
            #These items can only be changed if the movie is not playing
            if file != None:
                self._file = file
            #If changed to a looping movie, set this movie to show the cursor, and clear the end function
            #Otherwise set the cursor and end function to the new values, if any
            if looping != None:
                self._looping = looping
                if looping:
                    self._cursor = 1
                    self._endfunc = None
                else:
                    if cursor != None:
                        self._cursor = cursor
                    if endfunc != None:
                        self._endfunc = endfunc
            else:
                if cursor != None:
                    self._cursor = cursor
                if endfunc != None:
                    self._endfunc = endfunc
        #Rect can be changed no matter what
        if rect != None:
            if len(rect) > 2:
                self._rect = pygame.Rect(rect)
            else:
                self._rect = pygame.Rect(rect,(0,0))
            #If the movie is playing, set the rect size to the movie size
            if self._playing:
                self._rect.size = self._movie.get_size()
        #If movie is visible hide everything above it and redraw it
        if self._visible:
            dirtyrect = userarea._redrawfrom(self, 0, dirtyrect)
            self._draw()
        #If any areas have been hidden by this update, restore all items hidden so far
        #then update the screen
        if dirtyrect != None:
            dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
            globals.updateuhasurface(dirtyrect)
                
    #Internal function used for redrawing screen
    def _redraw(self, state):
        if state:
            #Save area behind move
            self._bgsurface = pygame.Surface(self._rect.size).convert_alpha()
            self._bgsurface.fill((0,0,0,0))
            self._bgsurface.blit(globals.uhabuffer, (0,0), self._rect)
            #Draw movie to the buffer
            globals.uhabuffer.blit(self._areasurface, self._rect)
        else:
            #If there is a stored background, draw it to the buffer and clear the stored background
            if self._bgsurface != None:
                globals.uhabuffer.fill((0,0,0,0), self._rect)
                globals.uhabuffer.blit(self._bgsurface, self._rect)
                self._bgsurface = None

    #Is this a looping movie
    def islooping(self):
        return self._looping

    #Is this movie playing
    def isplaying(self):
        return self._playing

    #Is this movie paused (should always return 0 if not playing)
    def ispaused(self):
        return self._paused

    #Pause the movie, and hide it. Passing 1 to this function leaves the movie on the screen    
    def pause(self, donthide = 0):
        #If the movie is playing
        if self._playing:
            #Pause/unpause the internal movie object
            self._movie.pause()
            if self._paused:
                #If movie was paused and hidden, make it visible
                if not self._visible:
                    self.update(visible = 1)
            else:
                #Otherwise set the visibility of the movie
                self.update(visible = donthide)
            #Toggle the paused flag
            self._paused = not self._paused

    def play(self):
        #Only play if the movie is not already playing
        if not self._playing:
            #Create a movie object
            self._movie = pygame.movie.Movie(filemanager.find_movie(self._file))
            #Read the movies size, and adjust the rect
            self._rect.size = self._movie.get_size()
            #Create the output surface for the movie
            self._areasurface = pygame.Surface(self._rect.size)
            #Set the movie to render to the output surface
            self._movie.set_display(self._areasurface)
            #Make the movie visible
            self._visible = 1
            #Add this movie to the list of playing movies
            globals.playing.append(self)
            #Set the internal "playing" flag
            self._playing = 1
            #Play the movie (loop if requested)
            print 'play movie size',self._movie.get_size()
            print 'play movie length',self._movie.get_length()
            print 'play movie audio',self._movie.has_audio()
            print 'play movie video',self._movie.has_video()
            self._movie.play()
            #If this movie disables the cursor, do so
            if self._cursor == 0:
                globals.curcursor.disable()
            #If this is the only movie, start the engine timer for movies
            if len(globals.playing) == 1:
                pygame.time.set_timer(globals.MOVIEEVENT, parameters.getmovieinterval())

    #Stop the movie if playing and optionally run the end function                
    def stop(self, abort = 1):
        #Do nothing if it's not playing
        if self._playing:
            #Stop the internal object
            self._movie.stop()
            #Hide the movie
            self.update(visible = 0)
            #Remove myself from the list of playing movies
            globals.playing.remove(self)
            #Destroy the internal movie object
            self._movie = None
            #Clear the playing and paused flags
            self._playing = 0
            self._paused = 0
            #If requested, run the end function if there is one
            if self._endfunc != None and not abort:
                self._endfunc()
            #If this was the last movie playing, stop the engine timer (save some cpu time)
            if len(globals.playing) == 0:
                pygame.time.set_timer(globals.MOVIEEVENT, 0)
            #If this movie hid the cursor
            if self._cursor == 0:
                #If the cursor is currently disabled
                if not globals.curcursor.isenabled():
                    #If no other movies are hiding the cursor
                    if not len([item for item in globals.playing if item._cursor == 0]):
                        #Enable the cursor
                        globals.curcursor.enable()
            
    #Save the current state of the object
    def _save(self):
        #Save base object's settings
        saveval = userarea._save(self)
        #Save this areas settings
        saveval['looping'] = self._looping
        saveval['cursor'] = self._cursor
        saveval['endfunc'] = self._endfunc
        saveval['paused'] = self._paused
        saveval['playing'] = self._playing
        saveval['file'] = self._file
        #Return the saved state
        return saveval

    #Load the object with the passed state.
    def _load(self, saveinfo):
        #Load base object's settings
        userarea._load(self, saveinfo)
        #Get my save state from the list
        saveval = saveinfo[self._id]
        #Set my propeties to those in the saved state
        self._looping = saveval['looping'] 
        self._cursor = saveval['cursor'] 
        self._endfunc = saveval['endfunc']
        self._paused = saveval['paused']
        self._playing = saveval['playing']
        self._file = saveval['file']
