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

#Transition effects
import pygame
import globals, parameters
from slide import slide
from pygame.locals import *
from SlideManager import SlideManager

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *

#Fades old image to new image (Std and Object only)
def fade(newslide, oldslide):
    
    #print "== fade =="
    #print "From ",  "None" if oldslide is None else oldslide.getrealname()
    #print "To ", newslide.getrealname()
    #import traceback
    #traceback.print_stack()
    
    # Don't fade to yourself
    if oldslide is not None and oldslide.getname() == newslide.getname():
        return
    
    # FIXME: what use is this for??
    #If this is a UI slide, call the special trans for UI
    #if newslide._type == 'ui' and len(SlideManager._slide_stack) >= 2 and SlideManager._slide_stack[-2].gettype() == 'menu':
    #    menufadeout(newslide)
    #    return
    #If this is a menu slide, call the special trans for menu
    #elif oldslide is None or newslide._type == 'menu':
    #    menufadein(newslide)
    #    return
    
    if oldslide is None:
        menufadein(newslide)
        return
    
    #Object and Std slides need to be slide size and slide area only
    
    bothSimilar = (oldslide.is3D() == newslide.is3D())
    
    # Prepare OpenGL
    if bothSimilar:
        if oldslide.is3D():
            globals.prepare3DViewport()
        else:
            globals.prepare2DViewport()
    
    previous_time = pygame.time.get_ticks()
    
    #Fade new image into old image, from alpha = 1 to alpha = 255 with a configured step 
    for i in range(1, 255, parameters.getfadevelocity()):
        #Pause configurable delay
        if i > 1:
            new_time = pygame.time.get_ticks() 
            already_elapsed_time = new_time - previous_time
            time_to_wait = parameters.getdelay() - already_elapsed_time
            if time_to_wait > 0:
                pygame.time.delay(time_to_wait)
            previous_time = new_time
        
        if not bothSimilar:
            if oldslide.is3D():
                globals.prepare3DViewport()
            else:
                globals.prepare2DViewport()
            
        if oldslide.is3D():
            glPushMatrix()
            glRotatef(oldslide.pitch_angle, 1, 0, 0)
            glRotatef(oldslide.yaw_angle, 0, 1, 0)
            
        oldslide.render()
        
        if oldslide.is3D():
            glPopMatrix()
        
        glColor4f(1.0, 1.0, 1.0, i/255.0)
        
        if not bothSimilar:
            if newslide.is3D():
                globals.prepare3DViewport()
            else:
                globals.prepare2DViewport()
        
        if newslide.is3D():
            glPushMatrix()
            glRotatef(newslide.pitch_angle, 1, 0, 0)
            glRotatef(newslide.yaw_angle, 0, 1, 0)
        
        newslide.render()
        
        if newslide.is3D():
            glPopMatrix()
            
        glColor4f(1.0, 1.0, 1.0, 1.0)
        
        pygame.display.flip()

    #Show the cursor
    globals.curcursor._show()

#menu fade in
def menufadein(newslide):
    
    #print "== menufadein =="
    #print "TO ", newslide.getrealname()
    
    # Prepare OpenGL
    globals.prepare2DViewport()
    #glEnable(GL_BLEND)
    glEnable(GL_COLOR_MATERIAL)
    #glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    
    previous_time = pygame.time.get_ticks()
    
    #Fade new image into old image, from alpha = 1 to alpha = 255 with a configured step 
    for i in range(1, 255, parameters.getfadevelocity()):
        #Pause configurable delay
        if i > 1:
            new_time = pygame.time.get_ticks() 
            already_elapsed_time = new_time - previous_time
            time_to_wait = parameters.getdelay() - already_elapsed_time
            if time_to_wait > 0:
                pygame.time.delay(time_to_wait)
            previous_time = new_time
        
        pygame.event.get()
        
        glClear(GL_COLOR_BUFFER_BIT)
        
        glColor4f(i/255.0, i/255.0, i/255.0, 1.0)
        newslide.render()
        
        pygame.display.flip()

    glColor4f(1.0, 1.0, 1.0, 1.0)
    #glDisable(GL_BLEND)

    #Show the cursor
    globals.curcursor._show()

#menu fade out
def menufadeout(newslide):
    
    #print "== menufadeout =="
    #print "FROM ", newslide.getrealname()
    
    # Prepare OpenGL
    globals.prepare2DViewport()
    glEnable(GL_COLOR_MATERIAL)
    #glEnable(GL_BLEND)
    #glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    
    #Fade new image into old image, from alpha = 1 to alpha = 255 with a configured step 
    for i in range(1, 255, parameters.getfadevelocity()):
        #Pause configurable delay
        pygame.time.delay(parameters.getdelay())
                
        glClear(GL_COLOR_BUFFER_BIT)
        
        glColor4f((255 - i)/255.0, (255 - i)/255.0, (255 - i)/255.0, 1.0)
        newslide.render()
        
        pygame.display.flip()

    glColor4f(1.0, 1.0, 1.0, 1.0)
    #glDisable(GL_BLEND)

    #Show the cursor
    globals.curcursor._show()

#Intro fade
def initfade(newslide):
    # FIXME: not ported to OpenGL, but what does this do?
    #Create a temp surface and blit the Ui, Std or Object slide, and uhasurface to it (the new image) 
    tempsurface = pygame.Surface(globals.screenrect.size)
    tempsurface.blit(newslide._getbuffersurface(), (0,0))
    tempsurface.blit(globals.slidesurface, globals.screenrect)
    tempsurface.blit(globals.uhabuffer, (0,0))
    #Set surface to be transparent
    tempsurface.set_alpha(0)

    #Copy over the buffered items
    globals.uhasurface.blit(globals.uhabuffer, (0,0))
    globals.screenbuffer.blit(newslide._getbuffersurface(), (0,0))

    #Fade into first scene, from alpha = 1 to alpha = 255 with a configured step 
    for i in range(1,255,parameters.getfadevelocity()):
        #Pause configurable delay
        pygame.time.delay(parameters.getdelay())
        #Update the surface with new alpha value
        tempsurface.set_alpha(i)
        #Hide cursor
        globals.curcursor._hide()
        #Blit updated image to screen
        globals.screensurface.blit(tempsurface, (0,0))
        #If there are any mouse movements pending
        if pygame.event.peek(pygame.MOUSEMOTION):
            #Update cursor with the last one, and remove all of them from the queue
            globals.curcursor._handlemousemove(pygame.event.get(pygame.MOUSEMOTION)[-1])
        #Show the cursor
        globals.curcursor._show()
        #Update the screen
        pygame.display.update()

    #Set alpha to 255 (opaque)    
    tempsurface.set_alpha(255)
    #Hide cursor and add it to the list of updated areas
    globals.curcursor._hide()
    #Blit updated image to screen
    globals.screensurface.blit(tempsurface, (0,0))
    #If there are any mouse movements pending
    if pygame.event.peek(pygame.MOUSEMOTION):
        #Update cursor with the last one, and remove all of them from the queue
        globals.curcursor._handlemousemove(pygame.event.get(pygame.MOUSEMOTION)[-1])
    #Show the cursor
    globals.curcursor._show()
    #Update the screen
    pygame.display.update()


#Slide images to the right
def leftscroll(newslide, oldslide):
    # Prepare OpenGL
    globals.prepare2DViewport()
    
    previous_time = pygame.time.get_ticks()
    
    #Fade new image into old image, from alpha = 1 to alpha = 255 with a configured step 
    for i in range(1, 255, parameters.getfadevelocity()):
        #Pause configurable delay
        if i > 1:
            new_time = pygame.time.get_ticks() 
            already_elapsed_time = new_time - previous_time
            time_to_wait = parameters.getdelay() - already_elapsed_time
            if time_to_wait > 0:
                pygame.time.delay(time_to_wait)
            previous_time = new_time
        
        oldslide.render((i/255.0)*parameters.getscreensize()[0], 0)
        newslide.render((i/255.0)*parameters.getscreensize()[0] - parameters.getscreensize()[0], 0)
        
        pygame.display.flip()


#Slide image to left
def rightscroll(newslide, oldslide):
    # Prepare OpenGL
    globals.prepare2DViewport()
    
    previous_time = pygame.time.get_ticks()
    
    #Fade new image into old image, from alpha = 1 to alpha = 255 with a configured step 
    for i in range(1, 255, parameters.getfadevelocity()):
        #Pause configurable delay
        if i > 1:
            new_time = pygame.time.get_ticks() 
            already_elapsed_time = new_time - previous_time
            time_to_wait = parameters.getdelay() - already_elapsed_time
            if time_to_wait > 0:
                pygame.time.delay(time_to_wait)
            previous_time = new_time
        
        oldslide.render(-(i/255.0)*parameters.getscreensize()[0], 0)
        newslide.render(-(i/255.0)*parameters.getscreensize()[0] + parameters.getscreensize()[0], 0)
        
        pygame.display.flip()

    
#Slide image up
def downscroll(newslide, oldslide):
    #Create a tempsurface twice the height of the slide
    tempsurface = pygame.Surface((globals.screenrect.width, globals.screenrect.height * 2))
    #Blit old image to the top and new image to the bottom
    tempsurface.blit(globals.slidesurface, (0,0))
    tempsurface.blit(newslide._getbuffersurface(), (0,globals.screenrect.height))
    globals.slidesurface.blit(newslide._getbuffersurface(), (0,0))
    #Create a floating frame to specify the location from the tempsurface to copy, currently set on the old surface
    copyrect = pygame.Rect((0,0),globals.screenrect.size)
    
    dirtyrects = []

    #Slide copyrect across the temp surface from start of old image to start of new image
    #with a configurable step
    for i in range(0, globals.screenrect.height + 1, parameters.getscrollvelocity()):
        #Move copyrect down by step
        copyrect.top = i
        #Hide cursor and add it to the list of updated areas
        dirtyrects.append(globals.curcursor._hide())
        #Blit the area under copyrect to from the tempsurface to the screen
        globals.screensurface.blit(tempsurface, globals.screenrect, copyrect)
        globals.screensurface.blit(globals.uhasurface, globals.screenrect, globals.screenrect)
        #If there are any mouse movements pending
        if pygame.event.peek(pygame.MOUSEMOTION):
            #Update cursor with the last one, and remove all of them from the queue
            globals.curcursor._handlemousemove(pygame.event.get(pygame.MOUSEMOTION)[-1])
        #Show the cursor
        dirtyrects.append(globals.curcursor._show())
        #Add the slides area to the list
        dirtyrects.append(globals.screenrect)
        #Update the screen
        pygame.display.update(dirtyrects)
        #Pause configurable delay
        pygame.time.delay(parameters.getdelay())
        #Clear the list of updated screen areas
        dirtyrects = []

    #Move copyrect to start of new image
    copyrect.top = globals.screenrect.height
    #Hide cursor and add it to the list of updated areas
    dirtyrects.append(globals.curcursor._hide())
    #Blit the area under copyrect to from the tempsurface to the screen
    globals.screensurface.blit(tempsurface, globals.screenrect, copyrect)
    globals.screensurface.blit(globals.uhasurface, globals.screenrect, globals.screenrect)
    #If there are any mouse movements pending
    if pygame.event.peek(pygame.MOUSEMOTION):
        #Update cursor with the last one, and remove all of them from the queue
        globals.curcursor._handlemousemove(pygame.event.get(pygame.MOUSEMOTION)[-1])
    #Show the cursor
    dirtyrects.append(globals.curcursor._show())
    #Add the slides area to the list
    dirtyrects.append(globals.screenrect)
    #Update the screen
    pygame.display.update(dirtyrects)

#Slide image down
def upscroll(newslide, oldslide):
    #Create a tempsurface twice the height of the slide
    tempsurface = pygame.Surface((globals.screenrect.width, globals.screenrect.height * 2))
    #Blit new image to the top and old image to the bottom
    tempsurface.blit(newslide._getbuffersurface(), (0,0))
    tempsurface.blit(globals.slidesurface, (0,globals.screenrect.height))
    globals.slidesurface.blit(newslide._getbuffersurface(), (0,0))
    #Create a floating frame to specify the location from the tempsurface to copy, currently set on the old surface
    copyrect = pygame.Rect((0,globals.screenrect.height),globals.screenrect.size)
    
    dirtyrects = []

    #Slide copyrect across the temp surface from start of old image to start of new image
    #with a configurable step
    for i in range(0, globals.screenrect.height + 1, parameters.getscrollvelocity()):
        #Move copyrect down by step
        copyrect.top = globals.screenrect.height - i
        #Hide cursor and add it to the list of updated areas
        dirtyrects.append(globals.curcursor._hide())
        #Blit the area under copyrect to from the tempsurface to the screen
        globals.screensurface.blit(tempsurface, globals.screenrect, copyrect)
        globals.screensurface.blit(globals.uhasurface, globals.screenrect, globals.screenrect)
        #If there are any mouse movements pending
        if pygame.event.peek(pygame.MOUSEMOTION):
            #Update cursor with the last one, and remove all of them from the queue
            globals.curcursor._handlemousemove(pygame.event.get(pygame.MOUSEMOTION)[-1])
        #Show the cursor
        dirtyrects.append(globals.curcursor._show())
        #Add the slides area to the list
        dirtyrects.append(globals.screenrect)
        #Update the screen
        pygame.display.update(dirtyrects)
        #Pause configurable delay
        pygame.time.delay(parameters.getdelay())
        #Clear the list of updated screen areas
        dirtyrects = []
        
    #Move copyrect to start of new image
    copyrect.top = 0
    #Hide cursor and add it to the list of updated areas
    dirtyrects.append(globals.curcursor._hide())
    #Blit the area under copyrect to from the tempsurface to the screen
    globals.screensurface.blit(tempsurface, globals.screenrect, copyrect)
    globals.screensurface.blit(globals.uhasurface, globals.screenrect, globals.screenrect)
    #If there are any mouse movements pending
    if pygame.event.peek(pygame.MOUSEMOTION):
        #Update cursor with the last one, and remove all of them from the queue
        globals.curcursor._handlemousemove(pygame.event.get(pygame.MOUSEMOTION)[-1])
    #Show the cursor
    dirtyrects.append(globals.curcursor._show())
    #Add the slides area to the list
    dirtyrects.append(globals.screenrect)
    #Update the screen
    pygame.display.update(dirtyrects)