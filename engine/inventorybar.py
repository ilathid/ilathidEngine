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

#Inventory Class
import pygame
import globals, parameters
from userarea import userarea
from pygame.locals import *

class inventory(userarea):
    def __init__(self, rect = None, minrect = None, bgfile = None, bgdatfile = None, bgencryption = 0, showalpha = 150, mouseoveralpha = 255, visible = 0, enabled = 0):
        #Init base object
        userarea.__init__(self, rect, enabled, visible)
        #Small rect for when mouse is not over area
        if minrect != None:
            self._minrect = pygame.Rect(minrect)
        else:
            self._minrect = None
        #Current rect of area
        self._currentrect = self._minrect
        #File info
        self._bgfile = bgfile
        self._bgdatfile = bgdatfile
        self._bgencryption = bgencryption
        #Alpha settings
        self._showalpha = showalpha
        self._mouseoveralpha = mouseoveralpha
        #List of objects in inventory
        self._itemlist = []
        #List of images for objects in inventory
        self._itemimages = []
        #Currently highlighted item:
        self._currentitem = None
        #Background surface
        self._bgfilesurface = None
        #Current alpha state
        self._state = 0
        #Surface for left scroll arrow
        self._leftsurface = None
        #Rect for left scroll arrow
        self._leftrect = None
        #Surface for right scroll arrow
        self._rightsurface = None
        #Rect for right scroll arrow
        self._rightrect = None
        #First item in list currently displayed on screen
        self._firstitem = None
        #Last item in list displayed on screen (it may be obscured by right arrow)
        self._enditem = None
        #Default settings for "New Game"
        self._defaults = None
        
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

    #Draws area to screen buffer.
    def _draw(self):
        self._bgsurface = pygame.Surface(self._currentrect.size).convert_alpha()
        self._bgsurface.fill((0,0,0,0))
        self._bgsurface.blit(globals.uhabuffer, (0,0), self._currentrect)
        self._leftrect = None
        self._rightrect = None
        self._enditem = None
        self._areasurface = pygame.Surface(self._currentrect.size).convert_alpha()
        self._areasurface.fill((0,0,0,0))
        if self._bgfilesurface == None:
            if self._bgfile != None:
                self._bgfilesurface = globals.loadfile(parameters.getitempath(), self._bgfile, self._bgdatfile, self._bgencryption)
                self._areasurface.blit(self._bgfilesurface, (0,0))
        else:
            self._areasurface.blit(self._bgfilesurface, (0,0))
        if len(self._itemimages):
            if self._startitem == None:
                self._startitem = 0
            currentpos = 0
            if self._currentrect.width > self._currentrect.height:
                limit = self._currentrect.width
            else:
                limit = self._currentrect.height
            if self._startitem > 0:
                if self._currentitem == 'left':
                    self._leftsurface.set_alpha(self._mouseoveralpha)
                else:
                    self._leftsurface.set_alpha(self._showalpha)
                self._leftrect = self._areasurface.blit(self._leftsurface, (0,0))
                if self._currentrect.width > self._currentrect.height:
                    currentpos += self._leftrect.width
                else:
                    currentpos += self._leftrect.height
            for item in range(self._startitem,len(self._itemimages)):
                if self._currentitem == item:
                    self._itemimages[item][0].set_alpha(self._mouseoveralpha)
                else:
                    self._itemimages[item][0].set_alpha(self._showalpha)
                if self._currentrect.width > self._currentrect.height:
                    self._itemimages[item][1] = self._areasurface.blit(self._itemimages[item][0],(currentpos, 0))
                    currentpos += self._itemimages[item][1].width
                else:
                    self._itemimages[item][1] = self._areasurface.blit(self._itemimages[item][0],(0, currentpos))
                    currentpos += self._itemimages[item][1].height
                if currentpos >= limit:
                    if self._currentitem == 'right':
                        self._rightsurface.set_alpha(self._mouseoveralpha)
                    else:
                        self._rightsurface.set_alpha(self._showalpha)
                    self._rightrect = self._rightsurface.get_rect()
                    if self._currentrect.width > self._currentrect.height:
                        self._areasurface.fill((0,0,0,0), (self._currentrect.width - self._rightrect.width, 0, self._currentrect.height, self._rightrect.width))
                        self._rightrect = self._areasurface.blit(self._rightsurface, (self._currentrect.width - self._rightrect.width, 0))
                    else:
                        self._areasurface.fill((0,0,0,0), (0, self._currentrect.height - self._rightrect.height, self._currentrect.height, self._rightrect.width,))
                        self._rightrect = self._areasurface.blit(self._rightsurface, (0, self._currentrect.height - self._rightrect.height))
                    self._enditem = item
                    break
            else:
                self._enditem = len(self._itemimages)
        globals.uhabuffer.blit(self._areasurface, self._currentrect)
        
    #Changes any of area's attributes.
    def update(self, rect = None, minrect = None, bgfile = None, bgdatfile = None, bgencryption = None, showalpha = None, mouseoveralpha = None, visible = None, enabled = None):
        if self._visible:
            # TODO: OpenGL
            globals.uhabuffer.fill((0,0,0,0), self._currentrect)
            globals.uhabuffer.blit(self._bgsurface, self._currentrect)
        #Update attributes
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
        if bgfile != None:
            self._bgfile = bgfile
        if bgdatfile != None:
            self._bgdatfile = bgdatfile
        if bgencryption != None:
            self._bgencryption = bgencryption
        if showalpha != None:
            self._showalpha = showalpha
        if mouseoveralpha != None:
            self._mouseoveralpha = mouseoveralpha
        if visible != None:
            self._visible = visible
        if enabled != None:
            self._enabled = enabled
        #If any of the following changed, reload the file
        if bgfile != None or bgdatfile != None or bgencryption != None:
            self._bgfilesurface = None
        if self._visible:
            #Draw area
            self._draw()
            return
                
    #Redraws (or clears) an area. Used internaly by the engine
    def _redraw(self, state):
        if state:
            #Save the background and repaint the area
            #Save area behind area
            self._bgsurface = pygame.Surface(self._currentrect.size).convert_alpha()
            self._bgsurface.fill((0,0,0,0))
            self._bgsurface.blit(globals.uhabuffer, (0,0), self._currentrect)
            #Redraw area
            globals.uhabuffer.blit(self._areasurface, self._currentrect)
        else:
            #Restore background and clear background buffer
            if self._bgsurface != None:
                globals.uhabuffer.fill((0,0,0,0), self._currentrect)
                globals.uhabuffer.blit(self._bgsurface, self._currentrect)
                self._bgsurface = None

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
            self._menuslide = globals.currentage.getslide(mysaveinfo['menuslide'])

    #Handles event messages from the engine
    def _handleevent(self, event):
        if event.type == 'init':
            #If init, initialize the area
            print 'init'
            self._handleinit()
        elif event.type == 'mouseenter':
            #If enter, do entrance function
            print 'enter'
            self._handleenter()
        elif event.type == 'mouseexit':
            #If exit, do exit function
            print 'exit'
            self._handleexit()
        elif event.type == pygame.MOUSEMOTION:
            self._handlemove(event)
            return 1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #If a click, show the current item
            if self._currentitem != None:
                if self._currentitem != 'left' and self._currentitem != 'right':
                    self._itemlist[self._currentitem]._click()
                elif self._currentitem == 'left':
                    if self._startitem != 0:
                        self._startitem -= 1
                else:
                    if self._enditem != len(self._itemimages):
                        self._startitem +=1
                if self._visible:
                    # TODO: OpenGL
                    globals.uhabuffer.fill((0,0,0,0), self._currentrect)
                    globals.uhabuffer.blit(self._bgsurface, self._currentrect)
                    self._draw()
                    return 1
                
        return 0

    #Handles initializing the area when the engine starts
    def _handleinit(self):
        self._itemimages = []
        if len(self._itemlist):
            for item in self._itemlist:
                self._itemimages.append([item._draw(),None])
        self._startitem = None
        self._enditem = None
        self._currentitem = None
        if self._bgfile != None:
            self._bgfilesurface = globals.loadfile(parameters.getitempath(), self._bgfile, self._bgdatfile, self._bgencryption)
        self._leftsurface = globals.loadfile(parameters.getitempath(), 'left.png', None, 0)
        self._rightsurface = globals.loadfile(parameters.getitempath(), 'right.png', None, 0)
        self._initialized = 1

    #Handles updating the area when the mouse enters it
    def _handleenter(self):
        self._state = 1
        self._currentitem = None
        self._visible = 1
        self._currentrect = self._rect

    def _handleexit(self):        
        self._state = 0
        if self._visible:
            dirtyrect = None
            globals.uhabuffer.fill((0,0,0,0), self._currentrect)
            globals.uhabuffer.blit(self._bgsurface, self._currentrect)
            self._currentitem = None
            self._currentrect = self._minrect
            self._visible = 0
        self._currentitem = None

    def _handlemove(self, event):
        if len(self._itemlist):
            pos = (event.pos[0] - self._currentrect.left, event.pos[1] - self._currentrect.top)
            if self._leftrect != None:
                if self._leftrect.collidepoint(pos):
                    if self._currentitem != 'left':
                        self._currentitem = 'left'
                        if self._mouseoveralpha != self._showalpha:
                            # TODO: OpenGL
                            globals.uhabuffer.fill((0,0,0,0), self._currentrect)
                            globals.uhabuffer.blit(self._bgsurface, self._currentrect)
                    return
            if self._rightrect != None:
                if self._rightrect.collidepoint(pos):
                    if self._currentitem != 'right':
                        self._currentitem = 'right'
                        if self._mouseoveralpha != self._showalpha:
                            # TODO: OpenGL
                            globals.uhabuffer.fill((0,0,0,0), self._currentrect)
                            globals.uhabuffer.blit(self._bgsurface, self._currentrect)
                            self._draw()
                    return
            for item in range(self._startitem, self._enditem + 1):
                if item < len(self._itemimages):
                    if self._itemimages[item][1].collidepoint(pos):
                        if self._currentitem != item:
                            self._currentitem = item
                            if self._mouseoveralpha != self._showalpha:
                                # TODO: OpenGL
                                globals.uhabuffer.fill((0,0,0,0), self._currentrect)
                                globals.uhabuffer.blit(self._bgsurface, self._currentrect)
                                self._draw()
                        return
            self._currentitem = None
            if self._mouseoveralpha != self._showalpha:
                # TODO: OpenGL
                globals.uhabuffer.fill((0,0,0,0), self._currentrect)
                globals.uhabuffer.blit(self._bgsurface, self._currentrect)
                self._draw()

    def add(self, item):
        if item not in self._itemlist:
            self._itemlist.append(item)
            if self._initialized:                
                self._itemimages.append([item._draw(),None])

    def remove(self, item):
        if item in self._itemlist:
            del self._itemimages[self._itemlist.index(item)]
            self._itemlist.remove(item)

    def itemupdate(self, item):
        if item in self._itemlist:
            if self._initialized:                
                self._itemimages[self._itemlist.index(item)] = [item._draw(),None]

    def hasitem(self, item):
        if item in self._itemlist:
            return 1
        else:
            return 0