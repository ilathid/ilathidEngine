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

#User handled screen area Class and support functions
import pygame
import globals
from pygame.locals import *

class userarea:
    # ID counter for saving
    _curid = 0

    def __init__(self, rect = None, enabled = 0, visible = 0):
        #Rect
        if rect != None:
            self._rect = pygame.Rect(rect)
        else:
            self._rect = None
        #Visiblity and Enabled
        if rect != None:
            self._visible = visible
            self._enabled = enabled
        else:
            self._visible = 0
            self._enabled = 0
        #Buffer for what is "behind" object
        self._bgsurface = None
        #Buffer to hold current object 
        self._areasurface = None
        #Init state
        self._initialized = 0
            
        #Defaults
        self._defaults = None
        #object ID
        self._id = "uha" + str(userarea._curid)
        userarea._curid += 1
        
        #Add ID to global object list (used for saving and loading)
        globals.userareas[self._id] = self
        globals.userareasordered.append(self)

    #Object Rect
    def getrect(self):
        #Must return a COPY of the rect, or the user can change it using this pointer
        return pygame.Rect(self._rect)
    
    #Checks visibility
    def isvisible(self):
        return self._visible

    #Checks if enabled
    def isenabled(self):
        return self._enabled

    #Draws area to screen buffer.
    def _draw(self):
        pass

    #Changes any of objects's attributes and draws area to screen buffer.
    def update(self, rect = None, visible = None, enabled = None):
        pass

    #Internal function used for redrawing screen
    def _redraw(self, state):
        pass
    
    #Returns the object name (used for saving and loading)
    def getname(self):
        return self._id

    #Save the current state of the object
    def _save(self):
        saveval = {}
        saveval['rect'] = self._rect
        saveval['visible'] = self._visible
        saveval['enabled'] = self._enabled
        return saveval

    #Load the object with the passed state.
    def _load(self, saveinfo):
        mysaveinfo = saveinfo[self._id]
        self._rect = mysaveinfo['rect']
        self._visible = mysaveinfo['visible']
        self._enabled = mysaveinfo['enabled']

    #Object Defaults
    def setdefault(self):
        self._defaults = self._save()

    def loaddefaults(self):
        self._load({self._id : self._defaults})

    #Event handler, gets engine events if enabled
    def _handleevent(self, event):
        pass

    #Redraw all items from an area up
    def _redrawfrom(self, restore = 0, rect = None):
        if rect == None:
            #If rect is not passed, rect is the rect of the area to be redrawn
            dirtyrect = self._rect
        else:
            #Otherwise expand rect to include the area to be redrawn
            dirtyrect = rect.union(self._rect)
        #Skip this whole thing if it is the highest area
        if globals.userareasordered[-1] != self:
            #Make a list of areas above this one that are visible
            arealist = list([curarea for curarea in globals.userareasordered[globals.userareasordered.index(self) + 1:] if curarea.isvisible()])
            #Temp list of areas that need to be redrawn
            tmpupdatelist = []
            #Loop until no overlapping objects are found
            changed = 1
            while changed:
                changed = 0
                #Temp list to loop through (don't want to change the list while looping)
                tmparealist = list(arealist)
                for curarea in tmparealist:
                    #Compare each area with the area to be updated
                    #If it is in this area add it to the list of areas to be updated
                    if curarea.getrect().colliderect(dirtyrect):
                        dirtyrect = curarea.getrect().union(dirtyrect)
                        tmpupdatelist.append(curarea)
                        arealist.remove(curarea)
                        changed = 1
            #Create list that is in the same order as the original
            updatelist = list([curarea for curarea in globals.userareasordered if curarea in tmpupdatelist])
            if restore == 0:
                #Clear areas
                updatelist.reverse()
                for curarea in updatelist:
                    curarea._redraw(0)
            else:
                #Restore the areas
                for curarea in updatelist:
                    curarea._redraw(1)
        return dirtyrect
                    