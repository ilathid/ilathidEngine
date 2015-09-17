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

#Slide Class

import pygame
import globals
import parameters
from filemanager import filemanager
from FilePath import FilePath
from SlideManager import SlideManager

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *

class slide:
    
    #Current Hotspot
    _currenthotspot = None
    #Current Transition
    _currenttrans = 'none'
    
    #Slide ID counter for saving
    _curid = 0

    def __init__(self, realname = None, filename = None, datfile = None, encrypted = 0, type = 'std'):
        #File info
        self._realname = realname
        self._file = [filename]
        self._datfile = [datfile]
        self._encrypted = [encrypted]
        
        self._is3D = False
        
        #Buffer to hold slide BMP
        self._slide_texture = [None]
        self._setInitialValues()
        
    def _setInitialValues(self):
        #Hotspot list
        self._hotspots = []
        #Attached objects
        self._attachedobjects = []
        #Attached exit functions
        self._ontransfns = {}
        #Slide data
        self._state = {}
        #Slide delay
        self._delay = 0
        #Function to run on entrance
        self._onenterfn = None
        #Function to run on exit
        self._onexitfn = None
        #Slide Type
        self._type = type
        if type == 'menu' or type == 'ui':
            self._delay = 0
        #Is slide visible
        self._visible = 0
        #Timers paused by this slide
        self._pausedtimers = []
        
        
        #Slide ID
        self._slideid = 'slide' + str(slide._curid)
        slide._curid += 1

        #Defaults
        self._defaults = None

    def is3D(self):
        return self._is3D

    #File and datfile
    # texid : in case the slide has more than 1 texture
    def setfile(self, texid, filename, datfile = None, encrypted = 0):
        self._file[texid] = filename
        self._datfile[texid] = datfile
        self._encrypted[texid] = encrypted
        self._slide_texture[texid] = None

    # texid : in case the slide has more than 1 image
    def getfile(self, texid=0):
        return (self._file[texid], self._datfile[texid], self._encrypted[texid])
    
    # Get the resolved slide image file path
    # texid: in case the slide has multiple images
    def getFullFilePath(self, texid=0):
        if self._datfile is None:
            return (filemanager.find_slide(self._file[texid]), None, self._encrypted[texid])
        else:
            return (self._file[texid], filemanager.find_slide(self._datfile[texid]), self._encrypted[texid])
    
    def getrealname(self):
        return self._realname

    #Set state variables
    # state: a dictionary of variables
    def setstate(self, state):
        self._state = state

    def getstatevariables(self):
        #Must return a copy or the user can change list through this pointer
        return self._state.copy()

    def getstate(self, variable):
        try:
            return self._state[variable]
        except:
            return None

    def getAllStateVariables(self):
        return self._state

    def updatestate(self, variable, value):
        self._state[variable] = value

    #Slide delay
    def setdelay(self, delay):
        self._delay = delay

    def getdelay(self):
        return self._delay

    #Slide visibility
    def isvisible(self):
        return self._visible

    #Attached objects
    def hasobject(self, obj):
        if obj in self._attachedobjects:
            return 1
        else:
            return 0    
    
    def attachobject(self, obj):
        #If not already attached
        if obj not in self._attachedobjects:
            #Attach it
            self._attachedobjects.append(obj)
            
            # sort objects depending on their 'layer' property, because on some slides
            # there may be some objects that need to appear on top of others
            self._attachedobjects.sort(key=lambda o: o.layer)
            
            #Set it's slide
            obj._setslide(self)

    def detachobject(self, obj):
        #If object is attached
        if obj in self._attachedobjects:
            #Clear the objects buffers and slides
            obj._clearbuffers()
            obj._setslide(None)
            #Remove object from list of attached objects
            self._attachedobjects.remove(obj)

    #Attached per slide exit functions
    def hastransfn(self, slide):
        return self._ontransfns.has_key(slide)

    def attachtransfn(self, slide, func):
        self._ontransfns[slide] = func

    def detachtransfn(self, slide):
        if self._ontransfns.has_key(slide):
            del self._ontransfns[slide]

    #Function to run when exiting slide
    def onexit(self, func):
        self._onexitfn = func

    #Function to run when entering slide
    def onentrance(self, func):
        self._onenterfn = func

    #Slide Type
    def gettype(self):
        return self._type

    #Attached hotspots
    # mapType  : 'rect' or 'polygon'
    # shape    : the rectangle where this hotspot is located (a tuple of format [x, y, width, height])
    # cursor   : cursor type to show when mouse is over this hotspot
    # dest     : identifier of the slide to go to on click
    # keywords : a map of settings. Contains dest, transover, action, drag, zip, push
    #                push means that the menu will be added to the slide stack instead of replacing the topmost menu
    def attachhotspot(self, shape, cursor, keywords, mapType='rect', id=None):
      
        #Built struct with required items
        tmphotspot = {'mapType': mapType, 'map': shape, 'cursor': cursor}
        
        if 'destOrientation' in keywords:
            tmphotspot['destOrientation'] = keywords['destOrientation']
        
        #Add other items for this hotspot
        keys = keywords.keys()
        if id != None:
            tmphotspot['id']=id
        for kw in keys:
            if kw == 'dest' and keywords[kw]!= None and keywords[kw]!= '':
                
                # I know usually you don't do type checks in python, but when refactoring, after you changed the
                # type of the variable, it's VERY painful to get incorrect types from old code lingering all over.
                # So check it explicitely as a precondition.
                if keywords[kw] is not None and not (isinstance(keywords[kw], str) or isinstance(keywords[kw], unicode)):
                    raise Exception("the destination must be a string now., not %s" % type(keywords[kw]))
                
                tmphotspot['dest'] = keywords[kw]
            if kw == 'transover' and keywords[kw]!= None and keywords[kw]!= '': tmphotspot['transover'] = keywords[kw]
            elif kw == 'action' and keywords[kw]!= None and keywords[kw]!= '': tmphotspot['action'] = keywords[kw]
            elif kw == 'drag' and keywords[kw]!= None and keywords[kw]!= '': tmphotspot['drag'] = keywords[kw]
            elif kw == 'push' and keywords[kw]!= None and keywords[kw]!= '': tmphotspot['push'] = keywords[kw]

            #If zip, prepend hotspot, else append it.
            if kw == 'zip' and keywords[kw]!= None and keywords[kw]!= '':
                #If zip, prepend hotspot, else append it.
                self._hotspots[0:0] = [tmphotspot]
            else:
                self._hotspots.append(tmphotspot)

    # delete a hotspot previously attached with 'attachhotspot'
    def detachhotspot(self, pos):
        if len(self._hotspots) >= pos:
            del self._hotspots[pos]
    
    def detachhotspotById(self, hotspotid):
        for i in range (len(self._hotspots)):
            if (self._hotspots[i].has_key('id') and self._hotspots[i]['id']==hotspotid):
                del self._hotspots[i]
                #We find it,we exit
                break
    
    def getId(self):
        return self._slideid
    
    def gethotspotsize(self):
        return len(self._hotspots)

    def updatehotspot(self, pos, rect, cursor, dest = None, transover = None, action = None, drag = None):
        
        # I know usually you don't do type checks in python, but when refactoring, after you changed the
        # type of the variable, it's VERY painful to get incorrect types from old code lingering all over.
        # So check it explicitely as a precondition.
        if dest is not None and not (isinstance(dest, str) or isinstance(dest, unicode)):
            raise Exception("the destination must be a string now., not %s" % type(dest))
            
        if len(self._hotspots) >= pos:
            #Built struct with required items
            tmphotspot = {'map': rect, 'cursor': cursor}
            #Add other items for this hotspot
            if dest != None: tmphotspot['dest'] = dest
            if transover != None: tmphotspot['transover'] = transover
            if action != None: tmphotspot['action'] = action
            if drag != None: tmphotspot['drag'] = drag
            #Update hotspot
            self._hotspots[pos] = tmphotspot

    # Draws slide to screen buffer
    def render(self, x=0, y=0):
        # Render
        self._getTexture(0).draw(x, y)
        
        # Draw each visible attached object
        glEnable(GL_BLEND)
        for obj in self._attachedobjects:
            if obj.isvisible():
                obj.render()
            
    
    # Enter slide and run entrance function.
    # DO NOT CALL THIS FUNCTION EXTERNALLY, TO SHOW A SLIDE USE THE SLIDE MANAGER
    def enter(self, oldslide, enter = 1):
        print "slide.py Enter BEGIN :",self._realname, self._type
        
        
        #Display the proper way for the new slide
        if self._type == 'menu':
            #Set transition type to fade
            slide._currenttrans = 'fade'
            if enter:
                #Stop timers
                for timer in [timer for timer in globals.timers.values() if timer.isrunning()]:
                    timer.pause()
                    self._pausedtimers.append(timer)
        elif self._type == 'ui':
            slide._currenttrans = 'fade'
        elif self._type == 'object':
            #Set transition type to fade
            slide._currenttrans = 'fade'
            #Append the last slide to the list of slides that can be "return"ed to
            if enter:
                #Stop timers
                for timer in [timer for timer in globals.timers.values() if timer.isrunning()]:
                    timer.pause()
                    self._pausedtimers.append(timer)
        else:
            #Std slide
            print "slide.py :display STD SlideManager.getCurrentSlide() =", SlideManager.getCurrentSlide().getrealname()
            
            #If this is the first Std slide displayed, no transition (UI will do it for us)
            if len(SlideManager._slide_stack) == 0:
                slide._currenttrans = 'none'
            else:
                #Otherwise Get the current hotspots transition or 'fade' if there is none
                if slide._currenthotspot != None:
                    if slide._currenthotspot.has_key('transover'):
                        #Hotspot is overriding the default transition
                        slide._currenttrans = slide._currenthotspot['transover']
                    else:
                        #Use the default transition
                        slide._currenttrans = globals.cursors[slide._currenthotspot['cursor']].gettransition()
                else:
                    slide._currenttrans = 'fade'
                    
            print "slide.py :display STD NOW after change _currentslide name=", self._realname
            
        
        #Perform the transition between the last slide and this one
        globals.dotrans(self, oldslide)
        
        
        #For all slide types:
        #Clear the current hotspot
        slide._currenthotspot = None
        #Set this slide to be visible
        self._visible = 1
        #If entering this slide run it's entrance functions
        if enter:
            if self._onenterfn:
                if globals.functions.has_key(self._onenterfn):
                    globals.functions[self._onenterfn]()
                else:
                    #print "slide.py :onenterfct",self._onenterfn
                    self._onenterfn()
        
        pos = pygame.mouse.get_pos()
        pygame.mouse.set_pos((pos[0] + 1, pos[1]))
        #If this is a delay slide, count down the delay and display the dest of the first hotspot
        if self._delay > 0:
            pygame.time.delay(self._delay * 1000)
            nextslide = self._state[0]
            nextslide.enter(oldslide, self)
            
        print "slide.py : END of slide.display"

    #Run exit functions
    def _exit(self, newslide):
        #Clear the buffers of this slide and all attached items
        self._clearbuffers()
        #Run exit function
        if self._onexitfn:
            #print "slide.py :exitFct=",self._onexitfn
            if globals.functions.has_key(self._onexitfn):
                globals.functions[self._onexitfn]()
            else:
                self._onexitfn()
        #Run per slide exit function
        if self._ontransfns.has_key(newslide):
            self._ontransfns.get(newslide)()
        #Set self to hidden
        self._visible = 0
        #Unpause all timers that were paused by entering this slide
        for timer in self._pausedtimers:
            timer.pause()
        #Clear the list of paused timers
        self._pausedtimers = []
        
    #Sets cursor for current hotspot
    def _mousemove(self, pos):
        if self._type == 'std' or self._type == 'object':
            #If a Std or Object slide, adjust the event position for the slide's offset on the screen
            pos = (pos[0] - globals.screenrect.left, pos[1] - globals.screenrect.top)
        #If the mouse is already over a hotspot, set the cursor to be the one for that hotspot
        if not self.is3D() and slide._currenthotspot != None:
            if slide._currenthotspot['map'].collidepoint(pos):
                globals.curcursor = globals.cursors.get(slide._currenthotspot.get('cursor'))
                if globals.curcursor is None:
                    raise Exception("Cannot find cursor '" + slide._currenthotspot.get('cursor') + "'")
                return

        #If the mouse is not already over a hotspot, find the hotspot it's now over
        if self.is3D():
            # 3D slides use another hotspot routine   
            return
        else:
            for hotspot in self._hotspots:
                if (hotspot.get('zip',0) and parameters.zipstate) or not hotspot.has_key('zip'):
                    if (hotspot.get('mapType') == 'rect'):
                        tmprect = pygame.Rect(hotspot.get('map'))
                        if tmprect:
                            if tmprect.collidepoint(pos):
                                slide._currenthotspot = dict(hotspot)
                                slide._currenthotspot['map'] = tmprect
                                globals.curcursor = globals.cursors.get(hotspot.get('cursor'))
                                return
                    elif (hotspot.get('mapType') == 'polygon'):
                        pass # TODO: implement polygon hotspots
        
        #If we didn't find a hotspot:
        #Set the current hotspot to None
        slide._currenthotspot = None
        #Return the default hotspot for the slide type
        if self._type == 'ui':
            globals.curcursor = globals.cursors.get('arrow')
        else:
            globals.curcursor = globals.cursors.get('forward')
        return

    #Responds to a mouse click
    # @return (dragFunction, transitionOccurred)
    def processClick(self):
        #If there is a current hotspot
        if slide._currenthotspot:
            #If action, run it.
            if slide._currenthotspot.has_key('action'):
                if globals.functions.has_key(slide._currenthotspot.get('action')):
                    globals.functions[slide._currenthotspot.get('action')]()
                else:
                    slide._currenthotspot.get('action')()
                return (None, False)
            
            #If draggable hotspot, return the drag function (What's that??)
            if slide._currenthotspot.has_key('drag'):
                return (slide._currenthotspot.get('drag'), False)
            
            #If destination is a slide
            if slide._currenthotspot.has_key('dest'):
                nextslide = slide._currenthotspot.get('dest')
                #If this is a menu or object "return"
                if nextslide == 'return':
                    SlideManager.popSlide()
                    return (None, True)
                else:                    
                    #Destination is a normal slide
                    #Display the new slide, do run entrance functions
                    if globals.currentage is not None:
                        s = globals.currentage.getslide(nextslide)
                    else:
                        s = globals.menuslides[nextslide]
                    
                    if s.is3D():
                        s.yaw_angle = slide._currenthotspot['destOrientation']
                        s.pitch_angle = 0.0
                    
                    if slide._currenthotspot is not None and slide._currenthotspot.has_key('push') and slide._currenthotspot['push']:
                        SlideManager.pushSlide(s)
                    else:
                        SlideManager.replaceTopSlide(s)
                    return (None, True)

        return (None, False)

    #Returns the engine assigned slide name, used for saving/loading
    def getname(self):
        return self._slideid

    #Set the defaults for the slide to return to when a "New Game" is requested
    def setdefaults(self):
        self._defaults = self._save()

    #load the defaults for the slide for a "New Game"
    def loaddefaults(self):
        self._load({self._slideid : self._defaults})        

    #Save all info about slides state
    def _save(self):
        #Create an empty dictionary to hold state
        saveval = {}
        #Add items to the dictionary
        saveval['file'] = ";".join(self._file)
        saveval['datfile'] = ";".join(self._datfile)
        saveval['encrypted'] = ";".join(self._encrypted)
        saveval['state'] = self._state
        saveval['delay'] = self._delay
        saveval['enterfn'] = self._onenterfn
        saveval['exitfn'] = self._onexitfn
        saveval['type'] = self._type
        saveval['visible'] = self._visible

        #Replace the list of attached objects with object names
        tmplist = []
        for object in self._attachedobjects:
            tmplist.append(object.getname())

        saveval['objects'] = tmplist

        #Replace the slides in the list of exit functions with slide names
        tmpdict = {}
        for exitfn in self._ontransfns:
            tmpdict[exitfn.getname()] = self._ontransfns[exitfn]

        saveval['transfns'] = tmpdict

        #Replace the slides in the list of hotspots with slide names
        #tmplist = []
        #for hotspot in self._hotspots:
        #    tmpdict = dict(hotspot)
        #    if tmpdict.has_key('dest'):
        #        if tmpdict['dest'] != 'return' and tmpdict['dest'] != 'return_root':
        #            tmpdict['dest'] = tmpdict['dest'].getname()
        #    tmplist.append(tmpdict)

        saveval['hotspots'] = self._hotspots

        #Replace the timers in the list of paused timers with timer names
        tmplist = []
        for timer in self._pausedtimers:
            tmplist.append(timer.getname())

        saveval['pausedtimers'] = tmplist

        #Return the saved state        
        return saveval

    #Load a saved state and set the slide to it
    def _load(self, saveinfo):
        #Get my state from the list of states
        saveinfo = saveinfo[self._slideid]
        #Set my properties to match the save state
        self._file = saveinfo['file'].split(";")
        self._datfile = saveinfo['datfile'].split(";")
        self._encrypted = saveinfo['encrypted'].split(";")
        self._state = saveinfo['state']
        self._delay = saveinfo['delay']
        self._onenterfn = saveinfo['enterfn']
        self._onexitfn = saveinfo['exitfn']
        self._type = saveinfo['type']
        self._visible = saveinfo['visible']

        #Replace the list of object names with actual objects 
        tmplist = saveinfo['objects']
        self._attachedobjects = []
        for object in tmplist:
            self._attachedobjects.append(globals.objects[object])
        self._attachedobjects.sort(key=lambda o: o.layer)
        
        #Replace the list of slide names with actual slides 
        tmpdict = saveinfo['transfns']
        self._ontransfns = {}
        for exitfn in tmpdict.items():
            self._ontransfns[globals.currentage.getslide(exitfn[0])] = exitfn[1]

        self._hotspots = saveinfo['hotspots']

        #Replace the list of timer names with actual timers 
        tmplist = saveinfo['pausedtimers']
        self._pausedtimers = []
        for timer in tmplist:
            self._pausedtimers.append(globals.timers[timer])        

    #Clear all buffers for memory management
    def _clearbuffers(self):
        for object in self._attachedobjects:
            object._clearbuffers()
            
        # set all members to None
        self._slide_texture = map(lambda x:None, self._slide_texture)

    # texid: in case the slide has multiuple textures.
    def _getTexture(self, texid):
        
        if self._slide_texture[texid] == None:
            self._slide_texture[texid] = globals.loadimage(FilePath(self._file[texid],
                                                                    self._datfile[texid],
                                                                    self._encrypted[texid]))
            
        return self._slide_texture[texid]
