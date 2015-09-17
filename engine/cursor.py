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

#Cursor Class

import os, pygame
import globals
import parameters
from pygame.locals import *
from FilePath import FilePath

class cursor:
    #Last cursor position
    _pos = (0,0)
    #Background
    _bgsurface = None
    #Enabled
    _enabled = 1
    
    def __init__(self, name, file = None, datfile = None, encrypted = 0, alpha = (0,0), hotspot = (0,0), trans = 'none'):
        #File info
        self._file = file
        self._datfile = datfile
        self._encrypted = encrypted
        #Alpha pos
        self._alpha = alpha
        #Hotspot pos
        self._hotspot = hotspot
        #Default Transition
        self._transition = trans
        #Cursor name
        self._name = name
        #Cursor Surface
        self._cursorsurface = None
        #Visible state
        self._visible = 0
        
        self._cursorsurface = globals.loadimage( FilePath(os.path.join(parameters.getcursorpath(), self._file),
                                                          None, self._encrypted, isAbsolute=True) )
         
        #Add cursor to the dictionary of cursors for later lookup
        globals.cursors[name] = self

    #Cursor file info
    def getfile(self):
        return (self._file, self._datfile, self._encrypted)

    #Visible?
    def isvisible(self):
        return self._visible
    
    #Cursor Alpha position
    def getalphapos(self):
        return self._alpha

    #Cursor hotspot position
    def gethotspotpos(self):
        return self._hotspot

    #Cursor transition style
    def gettransition(self):
        return self._transition

    def render(self):
        if cursor._enabled and self._visible:
            self._cursorsurface.draw(cursor._pos[0], cursor._pos[1])
    
    def renderAt(self, x, y):
        if cursor._enabled and self._visible:
            self._cursorsurface.draw(x, y)
            
    #Updates any of the cursors properties and updates the screen if needed
    def update(self, file = None, datfile = None, encryption = None, alpha = None, hotspot = None, trans = None):

        #Update settings
        if file != None:
            self._file = file
        if datfile != None:
            self._datfile = datfile
        if encryption != None:
            self._encryption = encryption
        if alpha != None:
            self._alpha = alpha
        if hotspot != None:
            self._hotspot = hotspot
        if trans != None:
            self._trans = trans
        #If any of these changed, we need to reload the file
        if file != None or datfile != None or encryption != None or alpha != None:
            self._cursorsurface = globals.loadfile(parameters.getcursorpath(), self._file, self._datfile, self._encrypted)
            self._cursorsurface.set_colorkey(self._cursorsurface.get_at(self._alpha))

    #Enables the cursor, and shows it on the screen
    def enable(self):        
        cursor._enabled = 1
        globals.curcursor._show()

    #Disables the cursor and hides it
    def disable(self):
        globals.curcursor._hide()
        cursor._enabled = 0

    #Gets the enabled state
    def isenabled(self):
        return cursor._enabled      

    #Hides the cursor
    def _hide(self):
        if globals.curcursor == self and cursor._enabled:
            self._visible = 0

    #Shows the cursor
    def _show(self):        
        if globals.curcursor == self and cursor._enabled:
            self._visible = 1
            #Check if we need to load the file
            if self._cursorsurface == None:
                self._cursorsurface = globals.loadimage( FilePath(os.path.join(parameters.getcursorpath(), self._file),
                                                                  None, self._encrypted, isAbsolute=True) )
                # FIXME; transparency with OpenGL
                #self._cursorsurface.set_colorkey(self._cursorsurface.get_at(self._alpha))           

    def _handlemousemove(self, event):
        #Update position based on a pygame event
        cursor._pos = event.pos

def initcursors():
    #Builds default cursors
    fwdcursor = cursor('forward',parameters.fwdcursor_file, parameters.fwdcursor_datfile, parameters.fwdcursor_encrypted,
                       parameters.fwdcursor_alpha, parameters.fwdcursor_hotspot, 'fade')
    fistcursor = cursor('action', parameters.fistcursor_file, parameters.fistcursor_datfile, parameters.fistcursor_encrypted,
                        parameters.fistcursor_alpha, parameters.fistcursor_hotspot)
    grabcursor = cursor('grab', parameters.grabcursor_file, parameters.grabcursor_datfile, parameters.grabcursor_encrypted,
                        parameters.grabcursor_alpha, parameters.grabcursor_hotspot)
    leftcursor = cursor('left', parameters.leftcursor_file, parameters.leftcursor_datfile, parameters.leftcursor_encrypted,
                        parameters.leftcursor_alpha, parameters.leftcursor_hotspot, 'left')
    rightcursor = cursor('right', parameters.rightcursor_file, parameters.rightcursor_datfile,parameters.rightcursor_encrypted,
                         parameters.rightcursor_alpha, parameters.rightcursor_hotspot, 'right')
    right180cursor = cursor('right180', parameters.right180cursor_file, parameters.right180cursor_datfile,parameters.right180cursor_encrypted,
                            parameters.right180cursor_alpha, parameters.right180cursor_hotspot, 'right')
    left180cursor = cursor('left180', parameters.left180cursor_file, parameters.left180cursor_datfile, parameters.left180cursor_encrypted,
                           parameters.left180cursor_alpha, parameters.left180cursor_hotspot, 'left')
    upcursor = cursor('up', parameters.upcursor_file, parameters.upcursor_datfile,parameters.upcursor_encrypted,
                      parameters.upcursor_alpha, parameters.upcursor_hotspot, 'up')
    downcursor = cursor('down', parameters.downcursor_file, parameters.downcursor_datfile, parameters.downcursor_encrypted,
                        parameters.downcursor_alpha, parameters.downcursor_hotspot, 'down')
    zipcursor = cursor('zip', parameters.zipcursor_file, parameters.zipcursor_datfile, parameters.zipcursor_encrypted,
                       parameters.zipcursor_alpha, parameters.zipcursor_hotspot, 'fade')
    arrowcursor = cursor('arrow', parameters.arrowcursor_file, parameters.arrowcursor_datfile, parameters.arrowcursor_encrypted,
                         parameters.arrowcursor_alpha, parameters.arrowcursor_hotspot,)
    magnifyPcursor = cursor('magnifyP', parameters.magnifyPcursor_file, parameters.magnifyPcursor_datfile, parameters.magnifyPcursor_encrypted,
                         parameters.magnifyPcursor_alpha, parameters.magnifyPcursor_hotspot,)
    magnifyMcursor = cursor('magnifyM', parameters.magnifyMcursor_file, parameters.magnifyMcursor_datfile, parameters.magnifyMcursor_encrypted,
                         parameters.magnifyMcursor_alpha, parameters.magnifyMcursor_hotspot,)
