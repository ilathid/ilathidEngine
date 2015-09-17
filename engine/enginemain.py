import pygame, pygame.constants
from pygame.locals import *
import globals, parameters, music
from slide import slide
from AoIimage import AoIimage
from text import text
from gametimer import timer
from menubar import menubararea
from inventoryfloat import inventory
from item import item
from cursor import *
from menu import *
from AoIMovie import movie
from music import Music
from sound import *
from SlideManager import SlideManager

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

#Handles the movie's event from the engine
def moviehandler(event):
    #Skip if there are no movies playing
    if (globals.playing != []):
        #Build a list of all unpaused, visible, playing movies
        tmpmovielist = [ curmovie for curmovie in globals.playing if (curmovie.isvisible() and (not curmovie.ispaused())) ]
        #If there are any:
        if (tmpmovielist != []):
            if globals.curcursor.isenabled():
                tmpmovierects = []
                for curmovie in tmpmovielist:
                    clipped = curmovie._rect.clip(globals.curcursor.getrect())
                    if (clipped.size != (0,0,)):
                        tmpmovierects.append(clipped)

                if (tmpmovierects != []):
                    globals.curcursor._hide(tmpmovierects)
                    globals.curcursor._show()
        #Stop any finished movies
        for curmovie in tmpmovielist:
        #If the movie is not busy, it's done playing
            if (not curmovie._movie.get_busy()):
                #Stop it and allow the exit function to be called
                curmovie.stop(0)


#Add the event handler to the engine
globals.eventhandlers[globals.MOVIEEVENT] = moviehandler

class fakeevent:
    def __init__(self, evttype):
        self.type = evttype

MOVE_MARGIN = 100

# Movement mode for 3D slides
CENTER_MOUSE = 1
FREE_MOUSE = 2
mode = CENTER_MOUSE

is_in_3d_slide = False

def mainloop():
    pygame.init()
    globals.init()
    pygame.mouse.set_visible(0)
    parameters.setcursorpath(os.path.join('engine', 'enginedata', 'cursors'))
    parameters.settextpath(os.path.join('engine', 'enginedata', 'text'))
    initcursors()
    globals.curcursor = globals.cursors['forward']

    filemanager.push_dir(os.path.join('data', 'menu'))

    for curitem in globals.userareasordered:
        curitem._handleevent(fakeevent('init'))
        if curitem.isvisible():
            curitem._draw()
            
    menubar = menubararea((0, 0, parameters.getscreensize()[0], 40),
                          (0, 0, parameters.getscreensize()[0], 5), menumain, 1)
    
    defaultui = None
    startslides = parameters.getfirstslides()
    
    if not startslides[1]:
        print "==> Slide 1 is nul!! Will use bg.bmp"
        defaultui = slide('bg.bmp', type = 'ui')
        defaultui._bmpbuffer = pygame.Surface(globals.screenrect.size)
        defaultui._bmpbuffer.fill(parameters.getbackgroundcolor())
        startslides[1] = defaultui
        startslides[0]=defaultui
    
    # for the start, init the state manager manually... (FIXME)
    SlideManager._slide_stack.append(startslides[0])
    startslides[0].enter(None)
    
    globals.quit = 0
    drag = None
    
    # The area the cursor is currently in
    uha = None
    
    lastpos = (0,0)
    
    defaultui = None
    startslides = parameters.getfirstslides()
    if not startslides[1]:
        defaultui = slide('background','bg.bmp', type = 'ui')
        defaultui._bmpbuffer = pygame.Surface(globals.screenrect.size)
        defaultui._bmpbuffer.fill(parameters.getbackgroundcolor())
        uislide = defaultui
        startslides[1] = uislide
    
    #globals.transoverride = 'initfade'

    WIDTH = parameters.getscreensize()[0]
    HEIGHT = parameters.getscreensize()[1]
    
    previous_time = pygame.time.get_ticks()
    
    while not globals.quit:        
        new_time = pygame.time.get_ticks() 
        dt = new_time - previous_time
        
        # 16 milliseconds is roughly 60 FPS. Cap after that.
        if dt < 16:
            pygame.time.wait(16 - dt)
            new_time = pygame.time.get_ticks() 
            dt = new_time - previous_time
            
        previous_time = new_time
        
        for event in pygame.event.get():
            if globals.eventhandlers.has_key(event.type):
                globals.eventhandlers[event.type](event)
            elif event.type == pygame.USEREVENT:
                #print "event.type==USEREVENT"
                globals.timers[event.timerid].trigger()
            elif event.type == pygame.MOUSEMOTION and globals.curcursor.isenabled():
                if event.pos != lastpos:
                    lastpos = event.pos
                    #print event.pos
                    if uha != None:
                        if not uha.getrect().collidepoint(event.pos):
                            tmpevent = fakeevent('mouseexit')
                            uha._handleevent(tmpevent)
                            uha = None
                    #Route mouse event to proper object
                    if drag != None:
                        update = drag(event)
                        if update:
                            globals.curcursor._hide()
                            #Update mouse cursor with new location
                            globals.curcursor._handlemousemove(event)
                            globals.curcursor._show()
                    else:
                        #Mouse movement
                        #Hide mouse cursor
                        globals.curcursor._hide()
                        #Update mouse cursor with new location
                        globals.curcursor._handlemousemove(event)
                        uhatrapped = 0
                        for area in [item for item in globals.userareasordered if item.isenabled()]:
                            if area.getrect().collidepoint(event.pos):
                                if uha != None:
                                    if area != uha:
                                        tmpevent = fakeevent('mouseexit')
                                        uha._handleevent(tmpevent)
                                        uha = area
                                        tmpevent = fakeevent('mouseenter')
                                        uha._handleevent(tmpevent)
                                else:
                                    uha = area
                                    tmpevent = fakeevent('mouseenter')
                                    uha._handleevent(tmpevent)
                                uhatrapped = uha._handleevent(event)
                                break
                        if not uhatrapped:
                            current_slide = SlideManager.getCurrentSlide()
                            if current_slide.gettype() == 'menu':
                                if globals.screenrect.collidepoint(event.pos):
                                    if current_slide.isvisible():
                                        #print "MOUSE MOVE1 slide._currentuislide.name ",slide._currentuislide._realname
                                        current_slide._mousemove(event.pos)
                            else:
                                if globals.screenrect.collidepoint(event.pos):
                                    #print "if globals"
                                    if current_slide.isvisible():
                                        #print "if slide._currenslide"
                                        current_slide._mousemove(event.pos)
                        globals.curcursor._show()
            elif event.type == pygame.MOUSEBUTTONDOWN and globals.curcursor.isenabled():
                drag = None
                uhatrapped = 0
                for area in [item for item in globals.userareasordered if item.isenabled()]:
                    if area.getrect().collidepoint(event.pos):
                        uhatrapped = area._handleevent(event)
                        break
                if not uhatrapped:
                    current_slide = SlideManager.getCurrentSlide()
                    if current_slide.gettype() == 'menu':
                        if globals.screenrect.collidepoint(event.pos):
                            if current_slide.isvisible():
                                (drag, transitionOccurred) = current_slide.processClick()
                    else:
                        if globals.screenrect.collidepoint(event.pos):
                            if current_slide.isvisible():
                                (drag, transitionOccurred) = current_slide.processClick()
                    if drag:
                        update = drag(event)
                        if update:
                            globals.curcursor._hide()
                            #Update mouse cursor with new location
                            globals.curcursor._handlemousemove(event)
                            globals.curcursor._show()
                    # Ignore mouse movement that may have occurred during the transition
                    if transitionOccurred:
                        if mode == CENTER_MOUSE:
                            pygame.mouse.set_pos([WIDTH/2, HEIGHT/2])
            elif event.type == pygame.MOUSEBUTTONUP and globals.curcursor.isenabled():
                #print "event.type == pygame.MOUSEBUTTONUP and globals.curcursor.isenabled()"
                if drag != None:
                    drag(event)
                    drag = None
                uhatrapped = 0
                for area in [item for item in globals.userareasordered if item.isenabled()]:
                    if area.getrect().collidepoint(event.pos):
                        uhatrapped = area._handleevent(event)
                        break
            elif event.type == pygame.KEYDOWN:
                uhatrapped = 0
                for area in [item for item in globals.userareasordered if item.isenabled()]:
                    uhatrapped = area._handleevent(event)
                    if uhatrapped:
                        break
                if not uhatrapped:
                    if event.key == pygame.K_q:
                        globals.quit = 1
                if event.key == pygame.K_ESCAPE:
                    globals.stopallsound()
                    music.stopmusic()
                    
                    current_slide = SlideManager.getCurrentSlide()
                    if current_slide.gettype() == 'menu':
                        SlideManager.popSlide()
                    else:
                        SlideManager.pushSlide(menumain)
            elif event.type == pygame.QUIT:
                globals.quit = 1
               
        # == Rendering
        s =  SlideManager.getCurrentSlide()
        if s.is3D():
            globals.prepare3DViewport()
            
            (mx, my) = pygame.mouse.get_pos()
            
            if mode == CENTER_MOUSE:
                dx = mx - WIDTH/2
                dy = my - HEIGHT/2
                pygame.mouse.set_pos([WIDTH/2, HEIGHT/2])
                
                if is_in_3d_slide: # avoid jump when entering slide by calculating delta the 2nd time only
                    s.yaw_angle += dt*0.006 * dx
                    if s.yaw_angle < 0: s.yaw_angle += 360
                    elif s.yaw_angle > 360: s.yaw_angle -= 360
                    
                    s.pitch_angle += dt*0.006 * dy
                    if s.pitch_angle < -60:s. pitch_angle = -60
                    elif s.pitch_angle > 60: s.pitch_angle = 60
            else:
                if my < MOVE_MARGIN:
                    s.pitch_angle -= dt*0.1 * float(MOVE_MARGIN - my)/float(MOVE_MARGIN)
                    if s.pitch_angle < -60: s.pitch_angle = -60
                elif my > HEIGHT - MOVE_MARGIN:
                    s.pitch_angle += dt*0.1 * (1.0 - float(HEIGHT - my)/float(MOVE_MARGIN))
                    if s.pitch_angle > 60: s.pitch_angle = 60
                    
                if mx < MOVE_MARGIN:
                    s.yaw_angle -= dt*0.1 * float(MOVE_MARGIN - mx)/float(MOVE_MARGIN)
                    if s.yaw_angle < 0: s.yaw_angle += 360
                elif mx > WIDTH - MOVE_MARGIN:
                    s.yaw_angle += dt*0.1 * (1.0 - float(WIDTH - mx)/float(MOVE_MARGIN))
                    if s.yaw_angle > 359: s.yaw_angle -= 360
            
            # rotate camera
            glRotatef(s.pitch_angle, 1, 0, 0)
            glRotatef(s.yaw_angle, 0, 1, 0)
            
            is_in_3d_slide = True
        else:
            is_in_3d_slide = False
            globals.prepare2DViewport()
        
        # No need for transparency to render slides (don't move this class into Slide.render because
        # transitions still need it enabled)
        glDisable(GL_BLEND)
        
        if s.is3D():
            s.render()
        else:
            s.render()
        
        if s.is3D():
            s.pickHotSpot(mx, my)
            
            # back to 2D for the rest
            globals.prepare2DViewport()
        
        if globals.curcursor is not None:
            glEnable(GL_BLEND)
            
            if s.is3D() and mode == CENTER_MOUSE:
                globals.curcursor.renderAt(WIDTH/2, HEIGHT/2)
            else:  
                globals.curcursor.render()
        
        pygame.display.flip()
         
    for curtimer in globals.timers.values():
        curtimer.stop()
    #sys.exit()
