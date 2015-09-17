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

#Menubar Class
import pygame
import globals
from slide import slide
from userarea import userarea
from pygame.locals import *
from SlideManager import SlideManager

class menubararea(userarea):
    
    def __init__(self, rect = None, minrect = None, menuslide = None, enabled = 0):
        #Small rect for when mouse is not over area
        if minrect != None:
            self._minrect = pygame.Rect(minrect)
        else:
            self._minrect = None
        #Current rect of area
        self._currentrect = self._minrect
        #Menu slide
        self._menuslide = menuslide
        #Init base object
        userarea.__init__(self, rect, enabled, 0)

    #Rect (overridden so that current rect is returned)
    def getrect(self):
        #Must return a COPY of the rect, or the user can change it using this pointer
        return pygame.Rect(self._currentrect)        

    #Minimum Rect
    def getminrect(self):
        #Must return a COPY of the rect, or the user can change it using this pointer
        return pygame.Rect(self._minrect)

    #MaxRect
    def getmaxrect(self):
        #Must return a COPY of the rect, or the user can change it using this pointer
        return pygame.Rect(self._rect)      

    #Changes any of area's attributes.
    def update(self, rect = None, minrect = None, enabled = None):
        #If rect updated
        if rect != None:
            #If currentrect is max rect
            if self._currentrect == self._rect:
                #Set currentrect to new rect
                self._currentrect = pygame.Rect(rect)
            #Set rect to new rect
            self._rect = pygame.Rect(rect)
        #If minrect updated
        if minrect != None:
            #If currentrect is min rect
            if self._currentrect == self._minrect:
                #Set currentrect to new minrect
                self._currentrect = pygame.Rect(minrect)
                #Set minect to new minrect
            self._minrectrect = pygame.Rect(rect)
        #If enabled updated
        if enabled != None:
            #Update enabled status
            self._enabled = enabled
    
    #Returns the area name (used for saving and loading)
    def getname(self):
        return self._id

    #Save the current state of the area
    def _save(self):
        #Save base object's settings
        saveval = userarea._save(self)
        #Save this areas settings
        saveval['minrect'] = self._minrect
        if self._menuslide == None:
            saveval['menuslide'] = None
        else:
            #Replace menuslide with it's name
            saveval['menuslide'] = self._menuslide.getname()
        #Return saved state
        return saveval

    #Load the object with the passed state.
    def _load(self, saveinfo):
        #Load base object's settings
        userarea._load(self, saveinfo)
        #Get my save state from the list
        mysaveinfo = saveinfo[self._id]
        #Set my propeties to those in the saved state
        self._minrect = mysaveinfo['minrect']
        if mysaveinfo['menuslide'] == None:
            self._menuslide = None
        else:
            #Replace menuslide's name with it's instance
            self._menuslide = globals.currentage.getSlide(mysaveinfo['menuslide'])

    #Handles event messages from the engine
    def _handleevent(self, event):
        if event.type == 'mouseenter':
            #If enter, update rect to full size
            self._currentrect = self._rect
        elif event.type == 'mouseexit':
            #If exit, update rect to small size
            self._currentrect = self._minrect
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #If click display menu
            #If menu is already displayed, do nothing
            if SlideManager.getCurrentSlide().gettype() != 'menu':
                #If any non looping movies playing do nothing
                if not len([item for item in globals.playing if not item.islooping()]):
                    SlideManager.pushMenu(self._menuslide)
            
                
        