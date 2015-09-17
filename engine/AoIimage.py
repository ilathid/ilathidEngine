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

#Image Class
import pygame
from parameters import *
from pygame.locals import *
from userobject import userobject
import globals
from FilePath import FilePath

class AoIimage(userobject):

    # fileref : an instance of class FilePath
    # layer   : items with a bigger layer ID will appear on top of items with a lower layer ID
    def __init__(self, fileref = None, rect = None, visible = 1, angle = 0,
                 alpha = None, slide = None, ratio = None, layer = 1):
        
        # I know usually in Python you don't verify types but this will help detect problems during the current refactor.
        if not isinstance(fileref, FilePath):
            raise Exception("fileref must be a FilePath object")
    
        #Angle
        self._angle = angle
        #Alpha pixel
        self._alpha = alpha
        # The image
        self._texture = None
        #ratio if the image must fit to a special Rect
        self._ratio=ratio
        
        #Init BaseClass
        userobject.__init__(self, fileref, rect, visible, slide, layer=layer)
        
        #It shouldn't be visible if the required properties are none
        if self._file == None or self._rect == None:
            self._visible = 0

    #Image Angle
    def getangle(self):
        return self._angle
    
    #Alpha settings
    def isalpha(self):
        if self._alpha != None:
            return 1
        else:
            return 0

    def getalpha(self):
        return self._alpha
    
    def isratio(self):
        if self._ratio != None:
            return 1
        else:
            return 0

    def getratio(self):
        return self._ratio

    def isvisible(self):
        return self._visible

    #Changes any of Image's attributes and updates the screen buffer.
    def update(self, fileref = None, rect = None, visible = None, alpha = None, angle = None, ratio = None):
        dirtyrect = None
        
        # I know usually in Python you don't verify types but this will help detect problems during the current refactor.
        if fileref is not None and not isinstance(fileref, FilePath):
            raise Exception("fileref must be a FilePath object")
  
        #Update attributes
        if fileref != None:
            self._file = fileref
        if rect != None:
            if len(rect) == 4:
                self._rect = pygame.Rect(rect)
            else:
                self._rect = pygame.Rect(rect,(0,0))
        if visible != None:
            self._visible = visible
        if alpha != None:
            self._alpha = alpha
        if angle != None:
            self._angle = angle
        if ratio != None:
            self._ratio = ratio
        
        if self._file == None or self._rect == None:
            self._visible = 0
        #If Updated image is visible, clear everything above it's new area and redraw
        if globals.isslidevisible(self._slide):
            if self._visible:
                #load with new options if needed
                if fileref:
                    self._texture = globals.loadimage(self._file, isSlide = False)
                    self._rect.size = [self._objectsurface.getWidth(), self._objectsurface.getHeight()]
                return
            else:
                #Image is not visible, so clear it's buffers to save mem
                self._clearbuffers()
        else:
            #Image is not visible, so clear it's buffers to save mem
            self._clearbuffers()
                
    #Draws Image to screen buffer.
    def render(self):
        if globals.isslidevisible(self._slide):
            #Load image if needed
            if self._objectsurface == None:
                self._objectsurface = globals.loadimage(self._file, isSlide = False)
            #Build destination rect
            self._rect.size = [self._objectsurface.getWidth(), self._objectsurface.getHeight()]
                       
            #If alpha, set color key
            # TODO: OpenGL vs alpha
            #if self._alpha != None:
            #    self._objectsurface.set_colorkey(self._objectsurface.get_at(self._alpha))

            if self._visible:
                #Draw image
                if self._ratio != None:
                    self._objectsurface.scaleDraw(self._rect.left, self._rect.top,self._ratio[0],self._ratio[1])
                else:
                    self._objectsurface.draw(self._rect.left, self._rect.top)
                return self._rect
            
    #Clears objects buffers to save mem.
    def _clearbuffers(self):
        #Clear the base objects buffers
        userobject._clearbuffers(self)

