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

import os, pygame, re
import globals
from parameters import *
from userobject import userobject
from pygame.locals import *
from GLTexture import GLTexture

#Markup tag classes
class _markup:
    def __init__(self, val):
        self.val = val

class _markup_bold(_markup):
    def __repr__(self): return ['</B>','<B>'][self.val]

class _markup_italic(_markup):
    def __repr__(self): return ['</I>','<I>'][self.val]

class _markup_underline(_markup):
    def __repr__(self): return ['</U>','<U>'][self.val]

#Parses string and replaces <xx> tags with class instances
def _markup_split(text):
    import re
    blocks = re.split('(</?[biuBIU]>)', text)
    blocks = [ s for s in blocks if s != '' ]
    for i in range(len(blocks)):
        if blocks[i] in ('<b>', '<B>'):
            blocks[i] = _markup_bold(1)
        elif blocks[i] in ('</b>', '</B>'):
            blocks[i] = _markup_bold(0)
        elif blocks[i] in ('<i>', '<I>'):
            blocks[i] = _markup_italic(1)
        elif blocks[i] in ('</i>', '</I>'):
            blocks[i] = _markup_italic(0)
        elif blocks[i] in ('<u>', '<U>'):
            blocks[i] = _markup_underline(1)
        elif blocks[i] in ('</u>', '</U>'):
            blocks[i] = _markup_underline(0)
    return blocks

#Text class
class text(userobject):
    
    # fileref : an instance of class FilePath
    def __init__(self, fileref = None, rect = None, string = None, color = (0,0,0), visible = 1,
                 just = 0, size = 0, userlineheight = None, slide = None):
        #Font
        self._font = None
        #String
        self._string = string
        #Color
        self._color = color
        #Justification
        self._just = just
        #Font size
        self._size = size
        #User specified line spacing (some fonts just don't space well on their own)
        self._userlineheight = userlineheight
        #Font specified line spacing
        self._lineheight = None
        #Character spacing table (holds the relative spacing for character pairs)   
        self._chartable = None
        # The rendered text
        self._texture = None
        
        #Init Base Class
        userobject.__init__(self, fileref, rect, visible, slide)
        #Not visible if required attributes are not set
        if self._file == None or self._rect == None or self._string == None:
            self._visible = 0
        else:
            self._visible = visible
        

    def render(self):
        
        if self._texture is None:
            self.prepareTexture()
        
        if self._texture is not None:
            self._texture.draw(self._rect.left, self._rect.top)

    #Text color
    def getcolor(self):
        return self._color

    #Text to be displayed
    def getstring(self):
        return self._string

    #Line height
    def getlineheight(self):
        return self._lineheight    

    #Justification
    def getjust(self):
        return self._just

    #Size
    def getsize(self):
        return self._size

    #Clears buffers to save mem
    def _clearbuffers(self):
        userobject._clearbuffers(self)
        self._font = None
        self._lineheight = None
        self._chartable = None

    #Renders text to the screen
    def _rendertext(self):
        #If the chartable has not yet been built, do so
        if self._chartable == None:
            self._chartable = {}
            for i in range(128):
                c1 = chr(i)
                s1 = self._font.size(c1)[0]
                for j in range(128):
                    c2 = chr(j)
                    s2 = self._font.size(c2)[0]
                    s = c1+c2
                    self._chartable[s] = self._font.size(s)[0] - s1 - s2

        #Split the text at newlines, into a list of lines
        lines = self._string.splitlines();
        #Create a list to hold the output image info
        images = []
        #Set starting offset in the rect
        left = 0
        top = 0 - self._lineheight
        #Keep track of the widest line
        maxwidth = 0

    
        for line in lines:
            #Increment height to a new line 
            top += self._lineheight
            #Check if the last line is longer than all the others
            if left > maxwidth:
                maxwidth = left
            #Go back to the left edge of the rect
            left = 0
            #Clear the copy of the last character of the last line
            lastchar = None
            #Split the line at the markup locations 
            for block in _markup_split(line):
                # handle markup
                if isinstance(block, _markup):
                    if isinstance(block, _markup_bold):
                        self._font.set_bold(block.val)
                    elif isinstance(block, _markup_italic):
                        self._font.set_italic(block.val)
                    elif isinstance(block, _markup_underline):
                        self._font.set_underline(block.val)
                else:
                    #This is not a markup so
                    #Adjust spacing for the combo of the [lastchar,firstchar] combo
                    if lastchar is not None and len(block):
                        left += self._chartable[lastchar + block[0]]
                    #Prevent any further spacing adjustment on this pass
                    softspace = None
                    # try to draw the line
                    if 0 < self._rect.width <= left + self._font.size(block)[0]:
                        # break it up if it's too big
                        for word in block.split():
                            #Render the word
                            surf = self._font.render(word, 1, self._color)
                            #Get its width
                            wordwidth = surf.get_size()[0]
                            #Apply spacing adjustments
                            if softspace is not None:
                                softspace += self._chartable[ ' '+word[0] ]
                                left += softspace + self._font.size(' ')[0]
                            #If this word needs to be wrapped, increment the height to put it on the next line
                            if self._rect.width <= left + wordwidth:
                                top += self._lineheight
                                left = 0
                            #Append the image, it's position, and the tet to the image list
                            images.append((left, top, surf,word))
                            #Add the width to the current width
                            left += wordwidth
                            #Set up spacing adjustment for the next word
                            softspace = self._chartable[ word[-1]+' ' ]
                    elif len(block):
                        #Render the block
                        surf = self._font.render(block, 1, self._color)
                        #Get its width
                        blockwidth = surf.get_size()[0]
                        #Append the image, it's position, and the test to the image list
                        images.append((left, top, surf, block))
                        #Add the width to the current width
                        left += blockwidth
                        #Save the last char of the block for the next blocks spacing adjustment
                        lastchar = block[-1]

        #If there is only one image, return it
        if len(images) == 1:
            self._objectsurface = images[0][2]

        #Set up the rendering limits (height is padded a little bit so as not to cut off decending letters like g)
        useheight = top+self._lineheight + images[-1][2].get_size()[1]
        usewidth = maxwidth
        usewidth = self._rect.width
        useheight = self._rect.height

        #Create final surface to render blocks to, convert_alpha() and fill make it transparent
        final_render = pygame.surface.Surface((usewidth, useheight)).convert_alpha()
        final_render.fill((0,0,0,0))
        
        if self._just == 0:
            #Left justified
            for x,y,i,t in images:
                # uncomment the following to get red boxes around the pieces
                #w,h = i.get_size()
                #surf = pygame.surface.Surface((w,h)).convert_alpha()
                #surf.fill((255,0,0))
                #surf.fill((0,0,0,0), (1,1,w-2,h-2))
                #final_render.blit(surf, (x,y))
                #Blit image to stored position
                final_render.blit(i, (x,y))
        elif self._just == 1 or self._just == 2:
            #Centered or Right justified
            #Check each line to see if any images are on it
            for linenum in range(self._rect.height):
                lineimages = [img for img in images if img[1] == linenum]
                itemimages = []
                #If this line has images
                if lineimages != []:
                    #Get the total width of all the items on this line
                    linewidth = 0
                    for line in lineimages:
                        linewidth += line[2].get_width()
                    #Create a surface to blit the whole line to
                    linesurface = pygame.Surface((linewidth, lineimages[0][2].get_height())).convert_alpha()
                    linesurface.fill((0,0,0,0))
                    #Blit each image to the temp surface
                    for x,y,i,t in lineimages:
                        linesurface.blit(i, (x,0))
                    #Blit the temp surface to the final surface with the proper justification
                    if self._just == 1:
                        final_render.blit(linesurface, ((self._rect.width - linesurface.get_width()) /2, linenum))
                    elif self._just == 2:
                        final_render.blit(linesurface, ((self._rect.width - linesurface.get_width()), linenum))

        return final_render

    #Changes any of Text's attributes and updates the screen buffer.
    def update(self, fileref = None, rect = None, visible = None, string = None, color = None, just = None, size = None, userlineheight = None):
        dirtyrect = None
        
        # Invalidate render
        self._texture = None
        
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
        if string  != None:
            self._string = string
        if color != None:
            self._color = color
        if just != None:
            self._just = just
        if size != None:
            self._size = size
        if userlineheight != None:
            self._userlineheight = userlineheight
        if self._file == None or self._rect == None:
            self._visible = 0
        #If the object is visible, redraw it
        if globals.isslidevisible(self._slide):
            if self._visible:
                #If any of these changed we need to reload the font
                if fileref or size:
                    self._font = globals.loadfont(self._file, self._size, self._datfile, self._encryption)
                    #If default line spacing is not overridden, get the default
                    if self._userlineheight != None:
                        self._lineheight = self._userlineheight
                    else:
                        self._lineheight = self._font.get_linesize()
                    #Clear the character table
                    self._chartable = None
                    #Clear the objects surface
                    self._objectsurface = None
                #If any of these changed we need to rerender the text, so clear the objects surface
                if string or rect or just or userlineheight or color:
                    self._objectsurface = None
                return
            else:
                #Image is not visible, so clear the buffers to save memory
                self._clearbuffers()
        else:
            #Image is not visible, so clear the buffers to save memory
            self._clearbuffers()

    #Draws Text to screen buffer.
    def prepareTexture(self):
        #Load the font if needed 
        if self._font == None:
            self._font = globals.loadfont(self._file, self._size)
            #If default line spacing is not overridden, get the default
            if self._userlineheight != None:
                self._lineheight = self._userlineheight
            else:
                self._lineheight = self._font.get_linesize()

        #newsurface = pygame.Surface((512, 512), pygame.SRCALPHA)
        #newsurface.fill(pygame.Color(0, 0, 0, 0)) # fill with transparency

        newsurface = self._rendertext()
        
        self._texture = GLTexture(newsurface, None, False, False)
        
    
