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

#Item Class
import globals, parameters
from pygame.locals import *
from SlideManager import SlideManager

class item:
    #Counter to generate a name for this item
    _curid = 0

    def __init__(self, filename = None, datfile = None, encryption = 0, slide = None , alpha = None, addtoinv = 0):
        #File info
        self._file = filename
        self._datfile = datfile
        self._encryption = encryption
        #Slide to show when selected
        self._slide = slide
        #Alpha position
        self._alpha = alpha
        #If requested add it to the inventory
        if addtoinv:
            globals.playerinventory.add(self)

        #Surface to hold items icon
        self._itemsurface = None
        #Defaults for "New game"
        self._defaults = None

        #Generate a name
        self._id = 'item' + str(item._curid)
        item._curid += 1

        #Add ID to global object list (used for saving and loading)
        globals.items[self._id] = self        

    #Updates any of the items attributes and notifies the inventory
    def update(self, filename = None, datfile = None, encryption = None, slide = None , alpha = None):
        #Update attributes
        if filename != None:
            self._file = filename
        if datfile != None:
            self._datfile = datfile
        if encryption != None:
            self._encryption = encryption
        if slide != None:
            self._slide = slide
        if alpha != None:
            self._alpha = alpha
        if filename or datfile or encryption or alpha:
            self._itemsurface = None
        #Notify the inventory of the change
        globals.playerinventory._itemupdate(self)

    #Creates/updates the items "icon" surface if needed and returns that surface.
    def _draw(self):
        #Load image if needed
        if self._itemsurface == None:
            self._itemsurface = globals.loadfile(parameters.getitempath(), self._file, self._datfile, self._encryption)
            #Set alpha if needed
            if self._alpha != None:
                self._itemsurface.set_colorkey(self._itemsurface.get_at(self._alpha))
        return self._itemsurface

    #Processes click events
    def _click(self):
        #Display the items slide
        SlideManager.pushSlide(self._slide)

    #Saves the items properties
    def _save(self):
        saveval = {}
        saveval['file'] = self._file
        saveval['datfile'] = self._datfile
        saveval['encryption'] = self._encryption
        saveval['alpha'] = self._alpha

        #Save name of attached slide
        if self._slide != None:
            saveval['slide'] = self._slide.getname()
        else:
            saveval['slide'] = None      
           
        return saveval

    #Loads an items properties from a saved state
    def _load(self, saveinfo):
        mysaveinfo = saveinfo[self._id]
        self._file = mysaveinfo['file']
        self._datfile = mysaveinfo['datfile']
        self._encryption = mysaveinfo['encryption']
        self._alpha = mysaveinfo['alpha']

        #set slide to instance of named slide
        if mysaveinfo['slide'] != None:
            self._slide = globals.currentage.getSlide(mysaveinfo['slide'])
        else:
            self._slide = None        

    #Set the defaults for the item to return to when a "New Game" is requested
    def setdefault(self):
        self._defaults = self._save()
        
    #load the defaults for the item for a "New Game"
    def loaddefaults(self):
        self._load({self._id : self._defaults})