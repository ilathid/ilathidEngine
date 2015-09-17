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

#User defined object Class
import pygame
import globals
from pygame.locals import *
from FilePath import FilePath

class userobject:
    # ID counter for saving
    _curid = 0

    # fileref : an instance of FilePath
    # layer   : items with a bigger layer ID will appear on top of items with a lower layer ID
    def __init__(self, fileref = None, rect = None, visible = 1, slide = None, layer = 1):
        #File info
        self._file = fileref
        #Rect
        if rect != None:
            if len(rect) == 4:
                self._rect = pygame.Rect(rect)
            else:
                self._rect = pygame.Rect(rect,(0,0))
        else:
            self._rect = None
        #Layer
        self.layer = layer
        #Visiblity
        self._visible = visible
        #Buffer for what is "behind" object
        self._bgsurface = None
        #Buffer to hold current object 
        self._objectsurface = None
        #Slide object is attached to
        # FIXME: this code is weird. Clarify if '_slide' is a string or a slide object.
        # atm looks like it can be both
        self._slide = None
        if slide != None:
            if globals.menuslides.has_key(slide):
                globals.menuslides[slide].attachobject(self)
            else:
                slide.attachobject(self)
            
        #Defaults
        self._defaults = None
        #object ID
        self._id = "object" + str(userobject._curid)
        userobject._curid += 1
        
        #Add ID to global object list (used for saving and loading)
        globals.objects[self._id] = self

    #Object file
    def getfile(self):
        return self._file
    
    #Object Rect
    def getrect(self):
        #Must return a COPY of the rect, or the user can change it using this pointer
        return pygame.Rect(self._rect)
    
    #Checks visibility
    def isvisible(self):
        return self._visible

    #Draws object to screen buffer.
    def _draw(self):
        pass

    #Changes any of objects's attributes and draws objedct to screen buffer.
    def update(self, fileref = None, rect = None, visible = None):
        pass

    #Internal function used for redrawing screen
    def _redraw(self, state):
        pass
    
    #Clears buffers for memory management
    def _clearbuffers(self):
        self._bgsurface  = None
        self._objectsurface = None

    #Returns the object name (used for saving and loading)
    def getname(self):
        return self._id

    #Save the current state of the object
    def _save(self):
        #Create an empty dictionary to hold state
        saveval = {}
        #Add items to the dictionary
        saveval['file'] = self._file.getFileName()
        saveval['datfile'] = self._file.getArchivename()
        saveval['encryption'] = self._file.getEncryption()
        saveval['rect'] = self._rect
        saveval['visible'] = self._visible      

        #Save name of attached slide
        if self._slide != None:
            saveval['slide'] = self._slide.getname()
        else:
            saveval['slide'] = None

        #Return the saved state        
        return saveval

    #Load the object with the passed state.
    def _load(self, saveinfo):
        #Get my state from the list of states
        mysaveinfo = saveinfo[self._id]
        #Set my properties to match the save state
        self._file = FilePath(mysaveinfo['file'], mysaveinfo['datfile'], mysaveinfo['encryption'])
        self._rect = mysaveinfo['rect']
        self._visible = mysaveinfo['visible']        

        #set slide to instance of named slide
        if mysaveinfo['slide'] != None:
            self._slide = globals.currentage.getslide(mysaveinfo['slide'])
        else:
            self._slide = None

    #Set the defaults for the object to return to when a "New Game" is requested
    def setdefault(self):
        self._defaults = self._save()
        
    #load the defaults for the object for a "New Game"
    def loaddefaults(self):
        self._load({self._id : self._defaults})
    
    #Set the slide object is attached to
    def _setslide(self, slide):
        if self._slide != None:
            #If currently attached to a slide, detach object from that slide
            tmpslide = self._slide
            self._slide = None
            tmpslide.detachobject(self)
        #Set new slide object is attached to
        self._slide = slide

    #Gets the slide the object is attached to
    def getslide(self):
        return self._slide
