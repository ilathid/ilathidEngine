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
    def __init__(self, rect = None, bgfile = None, bgdatfile = None, bgencryption = 0, hidealpha = 50, showalpha = 150, mouseoveralpha = 255, visible = 0, enabled = 0):
        #Init base object
        userarea.__init__(self, rect, enabled, visible)
        #File info
        self._bgfile = bgfile
        self._bgdatfile = bgdatfile
        self._bgencryption = bgencryption
        #Alpha settings
        self._hidealpha = hidealpha
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
        #Surface for back scroll arrow
        self._backsurface = None
        #Rect for back scroll arrow
        self._backrect = None
        #Surface for fwd scroll arrow
        self._fwdsurface = None
        #Rect for fwd scroll arrow
        self._fwdrect = None
        #First item in list currently displayed on screen
        self._startitem = None
        #Last item in list displayed on screen (it may be obscured by fwd arrow)
        self._enditem = None
        #Default settings for "New Game"
        self._defaults = None

    #Draws area to screen buffer.
    def _draw(self):
        #Save the area behind this one
        self._bgsurface = pygame.Surface(self._rect.size).convert_alpha()
        self._bgsurface.fill((0,0,0,0))
        self._bgsurface.blit(globals.uhabuffer, (0,0), self._rect)
        #Clear the scroll item rects (they might not be needed)
        self._backrect = None
        self._fwdrect = None
        #Clear the ending item (it will be set by this function)
        self._enditem = None
        #Create the tmp surface to draw to
        self._areasurface = pygame.Surface(self._rect.size).convert_alpha()
        self._areasurface.fill((0,0,0,0))
        #Load the background file if needed, and copy it to the temp surface
        if self._bgfilesurface == None:
            if self._bgfile != None:
                self._bgfilesurface = globals.loadfile(parameters.getitempath(), self._bgfile, self._bgdatfile, self._bgencryption)
                self._areasurface.blit(self._bgfilesurface, (0,0))
        else:
            self._areasurface.blit(self._bgfilesurface, (0,0))
        #If there are any items
        if len(self._itemimages):
            #If this is the first time this was drawn, set the starting item to be the first item in the inventory
            if self._startitem == None:
                self._startitem = 0
            #This will be used to tell when the inventory is full and no more items will fit in the temp surface
            currentpos = 0
            #Get the max position we can draw to, based on the orientation of the rect
            if self._rect.width > self._rect.height:
                limit = self._rect.width
            else:
                limit = self._rect.height
            #If the starting item is not the first, add the back scroll arrow
            if self._startitem > 0:
                #Set the scroll arrows alpha depending on state and mouse position
                if self._state == 1:
                    if self._currentitem == 'back':
                        self._backsurface.set_alpha(self._mouseoveralpha)
                    else:
                        self._backsurface.set_alpha(self._showalpha)
                else:
                    self._backsurface.set_alpha(self._hidealpha)
                #Blit the scroll item to the inventory and get it's rect
                self._backrect = self._areasurface.blit(self._backsurface, (0,0))
                #Add the scroll items size to the current position
                if self._rect.width > self._rect.height:
                    currentpos += self._backrect.width
                else:
                    currentpos += self._backrect.height
            #Loop thorough the items, starting with _startitem and go until there is no more room
            for item in range(self._startitem,len(self._itemimages)):
                #Set the items alpha depending on state and mouse position
                if self._state == 1:
                    if self._currentitem == item:
                        self._itemimages[item][0].set_alpha(self._mouseoveralpha)
                    else:
                        self._itemimages[item][0].set_alpha(self._showalpha)
                else:
                    self._itemimages[item][0].set_alpha(self._hidealpha)
                #Blit the items image to the proper place in the inventory and save its rect
                #then add it's size to the current position
                if self._rect.width > self._rect.height:
                    self._itemimages[item][1] = self._areasurface.blit(self._itemimages[item][0],(currentpos, 0))
                    currentpos += self._itemimages[item][1].width
                else:
                    self._itemimages[item][1] = self._areasurface.blit(self._itemimages[item][0],(0, currentpos))
                    currentpos += self._itemimages[item][1].height
                #If the current position is greater than the limit, we will need to add the fwd scroll item
                if currentpos >= limit:
                    #Set the scroll arrows alpha depending on state and mouse position
                    if self._state == 1:
                        if self._currentitem == 'fwd':
                            self._fwdsurface.set_alpha(self._mouseoveralpha)
                        else:
                            self._fwdsurface.set_alpha(self._showalpha)
                    else:
                        self._fwdsurface.set_alpha(self._hidealpha)
                    #Get the size of the forward scroll arrow
                    self._fwdrect = self._fwdsurface.get_rect()
                    #Blist the scroll arrow to the very end of the inventory and save it's rect (it may overwrite any item already there)
                    if self._rect.width > self._rect.height:
                        self._areasurface.fill((0,0,0,0), (self._rect.width - self._fwdrect.width, 0, self._rect.height, self._fwdrect.width))
                        self._fwdrect = self._areasurface.blit(self._fwdsurface, (self._rect.width - self._fwdrect.width, 0))
                    else:
                        self._areasurface.fill((0,0,0,0), (0, self._rect.height - self._fwdrect.height, self._rect.height, self._fwdrect.width))
                        self._fwdrect = self._areasurface.blit(self._fwdsurface, (0, self._rect.height - self._fwdrect.height))
                    #Save the last item that was drawn, the break out (can't draw any more items)
                    self._enditem = item
                    break
            else:
                #If we were able to draw all the way to the last item, we don't need the fwd scroll arrow
                #So just save the last item drawn
                self._enditem = len(self._itemimages)
        #Blit our temp surface to the UHA buffer
        globals.uhabuffer.blit(self._areasurface, self._rect)
        
    #Changes any of area's attributes.
    def update(self, rect = None, bgfile = None, bgdatfile = None, bgencryption = None, hidealpha = None, showalpha = None, mouseoveralpha = None, visible = None, enabled = None):
        #This will hold the area of the screen effected by this update
        dirtyrect = None
        if self._visible:
            #Hide all areas above this one, and restore the background
            dirtyrect = userarea._redrawfrom(self)
            globals.uhabuffer.fill((0,0,0,0), self._rect)
            globals.uhabuffer.blit(self._bgsurface, self._rect)
        #Update attributes
        if rect != None:
            self._rect = pygame.Rect(rect)
        if bgfile != None:
            self._bgfile = bgfile
        if bgdatfile != None:
            self._bgdatfile = bgdatfile
        if bgencryption != None:
            self._bgencryption = bgencryption
        if hidealpha != None:
            self._hidealpha = hidealpha
        if showalpha != None:
            self._showalpha = showalpha
        if mouseoveralpha != None:
            self._mouseoveralpha = mouseoveralpha
        if visible != None:
            self._visible = visible
        if enabled != None:
            self._enabled = enabled
        #If any of the following changed, reload the background file
        if bgfile != None or bgdatfile != None or bgencryption != None:
            self._bgfilesurface = None
        if self._visible:
            #Hide all areas above this one
            dirtyrect = userarea._redrawfrom(self, 0, dirtyrect)
            #Draw area
            self._draw()
        if dirtyrect != None:
            #Restore all areas above this one (if needed)
            dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
            globals.updateuhasurface(dirtyrect)
                
    #Redraws (or clears) an area. Used internaly by the engine
    def _redraw(self, state):
        if state:
            #Save the background and repaint the area
            #Save the background behind this area
            self._bgsurface = pygame.Surface(self._rect.size).convert_alpha()
            self._bgsurface.fill((0,0,0,0))
            self._bgsurface.blit(globals.uhabuffer, (0,0), self._rect)
            #Redraw area
            globals.uhabuffer.blit(self._areasurface, self._rect)
        else:
            #Restore background and clear background buffer
            if self._bgsurface != None:
                globals.uhabuffer.fill((0,0,0,0), self._rect)
                globals.uhabuffer.blit(self._bgsurface, self._rect)
                self._bgsurface = None

    #Handles event messages from the engine
    def _handleevent(self, event):
        if event.type == 'init':
            #If init, initialize the area
            self._handleinit()
        elif event.type == 'mouseenter':
            #If enter, do entrance function
            self._handleenter()
        elif event.type == 'mouseexit':
            #If exit, do exit function
            self._handleexit()
        elif event.type == pygame.MOUSEMOTION:
            #If mouse has moved, find the currently highlighted item
            self._handlemove(event)
            #Return 1 so this event is not passed to other objects
            return 1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #If a click, show the current item if one is selected (or scroll if needed)
            if self._currentitem != None:
                if self._currentitem != 'back' and self._currentitem != 'fwd':
                    #It's not a scroll arrow, so call it's click function
                    self._itemlist[self._currentitem]._click()
                elif self._currentitem == 'back':
                    #it's the back arrow, so decrement the starting item
                    if self._startitem != 0:
                        self._startitem -= 1
                else:
                    #Its fwd scroll so increment the starting item
                    if self._enditem != len(self._itemimages):
                        self._startitem +=1
                if self._visible:
                    #Hide all areas above this one
                    dirtyrect = userarea._redrawfrom(self)
                    #Restore the background
                    globals.uhabuffer.fill((0,0,0,0), self._rect)
                    globals.uhabuffer.blit(self._bgsurface, self._rect)
                    #Draw the updated inventory
                    self._draw()
                    #Redraw all areas above this one
                    dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
                    #Update the screen
                    globals.updateuhasurface(dirtyrect)
            #Return 1 so this event is not passed to other objects
            return 1

    #Handles initializing the area when the engine starts
    def _handleinit(self):
        #If there are any items in the inventory load them
        if len(self._itemlist):
            for item in self._itemlist:
                self._itemimages.append([item._draw(),None])
        #Load the background file if needed
        if self._bgfile != None:
            self._bgfilesurface = globals.loadfile(parameters.getitempath(), self._bgfile, self._bgdatfile, self._bgencryption)
        #Load the srcoll images
        self._backsurface = globals.loadfile(parameters.getitempath(), 'backscroll.bmp', None, 0)
        self._backsurface.set_colorkey(self._backsurface.get_at((0,0)))
        self._fwdsurface = globals.loadfile(parameters.getitempath(), 'fwdscroll.bmp', None, 0)
        self._fwdsurface.set_colorkey(self._fwdsurface.get_at((0,0)))
        #Set the state of this object to initialized
        self._initialized = 1
        #Make the inventory visible now that it is initialized
        self._visible = 1

    #Handles updating the area when the mouse enters it
    def _handleenter(self):
        #Set the state to "activated"
        self._state = 1
        #If the inventory is visible, and the show and hide alphas are different, we need to redraw the inventory
        if self._visible and (self._hidealpha != self._showalpha):
            #Hide all areas above this one
            dirtyrect = userarea._redrawfrom(self)
            #Restore the background
            globals.uhabuffer.fill((0,0,0,0), self._rect)
            globals.uhabuffer.blit(self._bgsurface, self._rect)
            #Draw the updated inventory
            self._draw()
            #Redraw all areas above this one
            dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
            #Set the cursor to be an arrow
            globals.curcursor = globals.cursors['arrow']
            #Update the screen
            globals.updateuhasurface(dirtyrect)

    def _handleexit(self):
        #Set the state to "deactivated"
        self._state = 0
        #If the inventory is visible and the show and hide alphas are different or there is a highlighted item
        if self._visible and (self._hidealpha != self._showalpha or self._currentitem != None):
            #Hide all areas above this one
            dirtyrect = userarea._redrawfrom(self)
            #Restore the background
            globals.uhabuffer.fill((0,0,0,0), self._rect)
            globals.uhabuffer.blit(self._bgsurface, self._rect)
            #Clear the current item
            self._currentitem = None
            #Draw the updated inventory
            self._draw()
            #Redraw all areas above this one
            dirtyrects = userarea._redrawfrom(self, 1, dirtyrect)
            #Update the screen
            globals.updateuhasurface(dirtyrect)
        #Clear the current item
        self._currentitem = None

    #Handles all mouse movement inside area
    def _handlemove(self, event):
        #Only check movement if visible
        if self._visible:
            #If there are any items in the inventory
            if len(self._itemlist):
                #Adjust the event position to be relative to the topleft of the inventory bar
                pos = (event.pos[0] - self._rect.left, event.pos[1] - self._rect.top)
                #If the back scroll arrow is displayed
                if self._backrect != None:
                    #Check if the mouse is over the back scroll arrow
                    if self._backrect.collidepoint(pos):
                        #If so, set the back scroll arrow to be the highlighted item if it is not already
                        if self._currentitem != 'back':
                            self._currentitem = 'back'
                            #If the item needs to be highlighted
                            if self._mouseoveralpha != self._showalpha:
                                #Hide all areas above this one
                                dirtyrect = userarea._redrawfrom(self)
                                #Restore the background
                                globals.uhabuffer.fill((0,0,0,0), self._rect)
                                globals.uhabuffer.blit(self._bgsurface, self._rect)
                                #Draw the updated inventory
                                self._draw()
                                #Redraw all areas above this one
                                dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
                                #Update the screen
                                globals.updateuhasurface(dirtyrect)
                        #Found the current item, so return
                        return
                #If the forward scroll arrow is displayed
                if self._fwdrect != None:
                    #Check if the mouse is over the forward scroll arrow
                    if self._fwdrect.collidepoint(pos):
                        #If so, set the forward scroll arrow to be the highlighted item if it is not already
                        if self._currentitem != 'fwd':
                            self._currentitem = 'fwd'
                            #If the item needs to be highlighted
                            if self._mouseoveralpha != self._showalpha:
                                #Hide all areas above this one
                                dirtyrect = userarea._redrawfrom(self)
                                #Restore the background
                                globals.uhabuffer.fill((0,0,0,0), self._rect)
                                globals.uhabuffer.blit(self._bgsurface, self._rect)
                                #Draw the updated inventory
                                self._draw()
                                #Redraw all areas above this one
                                dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
                                #Update the screen
                                globals.updateuhasurface(dirtyrect)
                        #Found the current item, so return
                        return
                #If it wasn't the back or fwd arrows, loop through items to find the current one
                for item in range(self._startitem, self._enditem + 1):
                    #This is to prevent an "out of bounds" error caused by the +1 above
                    if item < len(self._itemimages):
                        #Check if the mouse is over this item
                        if self._itemimages[item][1].collidepoint(pos):
                            #If so, set this item to be the highlighted item if it is not already
                            if self._currentitem != item:
                                self._currentitem = item
                                #If the item needs to be highlighted
                                if self._mouseoveralpha != self._showalpha:
                                    #Hide all areas above this one
                                    dirtyrect = userarea._redrawfrom(self)
                                    #Restore the background
                                    globals.uhabuffer.fill((0,0,0,0), self._rect)
                                    globals.uhabuffer.blit(self._bgsurface, self._rect)
                                    #Draw the updated inventory
                                    self._draw()
                                    #Redraw all areas above this one
                                    dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
                                    #Update the screen
                                    globals.updateuhasurface(dirtyrect)
                            #Found the current item, so return
                            return
                #If we got here the mouse is not over any items, so set the current item to None, and redraw the inventory
                self._currentitem = None
                #An item may need to be un-highlighted
                if self._mouseoveralpha != self._showalpha:
                    #Hide all areas above this one
                    dirtyrect = userarea._redrawfrom(self)
                    #Restore the background
                    globals.uhabuffer.fill((0,0,0,0), self._rect)
                    globals.uhabuffer.blit(self._bgsurface, self._rect)
                    #Draw the updated inventory
                    self._draw()
                    #Redraw all areas above this one
                    dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
                    #Update the screen
                    globals.updateuhasurface(dirtyrect)

    #Adds an item to the inventory
    def add(self, item):
        #Only add it if it's not already there
        if item not in self._itemlist:
            #Add it to the inventory
            self._itemlist.append(item)
            #If the inventory bar has been initialized, load the item
            if self._initialized:                
                self._itemimages.append([item._draw(),None])
            #Redraw the inventory if needed
            if self._visible:
                #Hide all areas above this one
                dirtyrect = userarea._redrawfrom(self)
                #Restore the background
                globals.uhabuffer.fill((0,0,0,0), self._rect)
                globals.uhabuffer.blit(self._bgsurface, self._rect)
                #Draw the updated inventory
                self._draw()
                #Redraw all areas above this one
                dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
                #Update the screen
                globals.updateuhasurface(dirtyrect)

    #Remove and item from the inventory
    def remove(self, item):
        #Only remove it if it is in the inventory
        if item in self._itemlist:
            #Delete this items image
            del self._itemimages[self._itemlist.index(item)]
            #Remove the item from the inventory
            self._itemlist.remove(item)
            #Redraw the inventory if needed
            if self._visible:
                #Hide all areas above this one
                dirtyrect = userarea._redrawfrom(self)
                #Restore the background
                globals.uhabuffer.fill((0,0,0,0), self._rect)
                globals.uhabuffer.blit(self._bgsurface, self._rect)
                #Draw the updated inventory
                self._draw()
                #Redraw all areas above this one
                dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
                #Update the screen
                globals.updateuhasurface(dirtyrect)

    #Internal function called by the item when it's properties have changed
    def _itemupdate(self, item):
        #Only update if the item is in the players inventory
        if item in self._itemlist:
            #If initialized, reload the items image
            if self._initialized:                
                self._itemimages[self._itemlist.index(item)] = [item._draw(),None]
            #Redraw the inventory if needed
            if self._visible:
                #Hide all areas above this one
                dirtyrect = userarea._redrawfrom(self)
                #Restore the background
                globals.uhabuffer.fill((0,0,0,0), self._rect)
                globals.uhabuffer.blit(self._bgsurface, self._rect)
                #Draw the updated inventory
                self._draw()
                #Redraw all areas above this one
                dirtyrect = userarea._redrawfrom(self, 1, dirtyrect)
                #Update the screen
                globals.updateuhasurface(dirtyrect)

    #Check if the item is in the inventory
    def hasitem(self, item):
        if item in self._itemlist:
            return 1
        else:
            return 0

    #Save the current state of the area
    def _save(self):
        #Save base object's settings
        saveval = userarea._save(self)
        #Save this areas settings
        saveval['bgfile'] = self._bgfile
        saveval['bgdatfile'] = self._bgdatfile
        saveval['bgencyption'] = self._bgencyption
        saveval['hidealpha'] = self._hidealpha
        saveval['showalpha'] = self._showalpha
        saveval['mouseoveralpha'] = self._mouseoveralpha
        if self._itemlist == []:
            saveval['itemlist'] = []
        else:
            #Replace items with thier names
            tmpitemlist = []
            for curitem in self._itemlist:
                tmpitemlist.append(curitem.getname())
            saveval['itemlist'] = tmpitemlist
        #Return saved state
        return saveval

    #Load the object with the passed state.
    def _load(self, saveinfo):
        #Load base object's settings
        userarea._load(self, saveinfo)
        #Get my save state from the list
        mysaveinfo = saveinfo[self._id]
        #Set my propeties to those in the saved state
        self._bgfile = mysaveinfo['bgfile']
        self._bgdatfile = mysaveinfo['bgdatfile']
        self._bgencyption = mysaveinfo['bgencyption']
        self._hidealpha = mysaveinfo['hidealpha'] 
        self._showalpha = mysaveinfo['showalpha']
        self._mouseoveralpha = mysaveinfo['mouseoveralpha']
        if mysaveinfo['itemlist'] == []:
            self._itemlist = []
        else:
            #Replace item names with thier instances
            self._itemlist = []
            for curitem in mysaveinfo['itemlist']:
                self._itemlist.append(globals.items[curitem])
        