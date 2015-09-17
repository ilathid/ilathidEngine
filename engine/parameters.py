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

#Engine parameters

import os

testCustomAge = None
visualizeHotspots = False

#Screen Settings
screensize = (800,600)
colordepth = 24
fullscreen = 0
backgroundcolor = (0, 0, 0)
backgroundfile = None
backgrounddatfile = None
backgroundalpha = None

#Slide settings
slidesize = (512,384)
slidepos = None

#Encryption settings
encryption_key = 'ilathid'
encryption_rounds = 2

#Zip mode settings
#Set to 1 to completely disable zipmode
zipmodedisabled = 0
#Current zip state
zipstate = 0

#Game settings
firstslide = None
firstuislide = None

#Menu settings
menu_rect = None

#Save settings
previewsize = (133,100)

#Inventory settings
itemsize = 40
inv_vertical = 0
inv_rect = None
showatstart = 1
show_alpha = 255
hide_alpha = 50
scroll_file = 'scroll.bmp'
scroll_datfile = None
scroll_alpha = (0,0)

#Movie settings
movieinterval = 34

def getmovieinterval():
    return movieinterval

def setmovieinterval(interval):
    global movieinterval
    movieinterval = interval

#Transition Settings
transquality = 'Best'
scroll_best = 30
scroll_normal = 40
scroll_fastest = 50

# By how much to increment transparency every frame (over 255)
# We're using OpenGL and any reasonably modern GPU, even those of phones,
# can handle the best settings.
fade_best = 7
fade_normal = 7
fade_fastest = 7

delay_best = 25 # approx 40 FPS
delay_normal = 25
delay_fastest = 25

#Paths
item_path = os.path.join('enginedata')
cursor_path = os.path.join('engine','enginedata','cursors')
save_path = os.path.join('data','save')
data_path = ('data')

#Cursor parameters
#File
fwdcursor_file = 'fwd.png'
fistcursor_file = 'fist.png'
grabcursor_file = 'grab.png'
leftcursor_file = 'left.png'
rightcursor_file = 'right.png'
right180cursor_file = 'right180.png'
left180cursor_file = 'left180.png'
upcursor_file = 'up.png'
downcursor_file = 'down.png'
zipcursor_file = 'zip.png'
arrowcursor_file = 'arrow.png'
magnifyPcursor_file = 'plus.png'
magnifyMcursor_file = 'minus.png'
#Encryption
fwdcursor_encrypted = 0
fistcursor_encrypted = 0
grabcursor_encrypted = 0
leftcursor_encrypted = 0
rightcursor_encrypted = 0
right180cursor_encrypted = 0
left180cursor_encrypted = 0
upcursor_encrypted = 0
downcursor_encrypted = 0
zipcursor_encrypted = 0
arrowcursor_encrypted = 0
magnifyPcursor_encrypted = 0
magnifyMcursor_encrypted = 0
#Datfile
fwdcursor_datfile = None
fistcursor_datfile = None
grabcursor_datfile = None
leftcursor_datfile = None
rightcursor_datfile = None
right180cursor_datfile = None
left180cursor_datfile = None
upcursor_datfile = None
downcursor_datfile = None
zipcursor_datfile = None
arrowcursor_datfile = None
magnifyPcursor_datfile = None
magnifyMcursor_datfile = None
#Alpha position
fwdcursor_alpha = (1,1)
fistcursor_alpha = (1,1)
grabcursor_alpha = (1,1)
leftcursor_alpha = (1,1)
rightcursor_alpha = (1,1)
right180cursor_alpha = (1,1)
left180cursor_alpha = (1,1)
upcursor_alpha = (1,1)
downcursor_alpha = (1,1)
zipcursor_alpha = (3,1)
arrowcursor_alpha = (1,1)
magnifyPcursor_alpha = (1,1)
magnifyMcursor_alpha = (1,1)
#Hotspot position
fwdcursor_hotspot = (7,2)
fistcursor_hotspot = (7,7)
grabcursor_hotspot = (7,7)
leftcursor_hotspot = (1,5)
rightcursor_hotspot = (15,5)
right180cursor_hotspot = (15,5)
left180cursor_hotspot = (1,5)
upcursor_hotspot = (10,1)
downcursor_hotspot = (5,15)
zipcursor_hotspot = (7,7)
arrowcursor_hotspot = (3,2)
magnifyPcursor_hotspot = (7,7)
magnifyMcursor_hotspot = (7,7)

#Screen Settings
def setscreensize(size):
    global screensize
    screensize = size

def getscreensize():
    global screensize
    return screensize

def setcolordepth(size):
    global screensize
    screensize = size

def getcolordepth():
    global screensize
    return screensize

def setfullscreen(screen = 1):
    global fullscreen
    fullscreen = screen

def isfullscreen():
    global fullscreen
    return fullscreen

def setbackgroundcolor(color):
    global backgroundcolor
    backgroundcolor = color

def getbackgroundcolor():
    global backgroundcolor
    return backgroundcolor

def setbackgroundfile(filename, datfile = None, alpha = None):
    global backgroundfile, backgrounddatfile, backgroundalpha
    backgroundfile = filename
    backgrounddatfile = datfile
    backgroundalpha = alpha

def getbackgroundfile():
    global backgroundfile
    return backgroundfile

def getbackgrounddatfile():
    global backgrounddatfile
    return backgrounddatfile

def getbackgroundalpha():
    global backgroundalpha
    return backgroundalpha

#Slide settings
def setslidesize(size):
    global slidesize
    slidesize = size

def getslidesize():
    global slidesize
    return slidesize

#Encryption settings
def setencryptionkey(key):
    global encryption_key
    encryption_key = key

def getencryptionkey():
    global encryption_key
    return encryption_key

def setencryptionrounds(rounds):
    global encryption_rounds
    encryption_rounds = rounds

def getencryptionrounds():
    global encryption_rounds
    return encryption_rounds

#Zip mode settings
def setzipmodedisabled(zip_newval):
    global zipmodedisabled, zipstate
    zipmodedisabled = zip_newval
    if zip_newval: zipstate = 0

def getzipmodedisabled():
    global zipmodedisabled
    return zipmodedisabled

def setzipstate(zip_newval):
    global zipstate, zipmodedisabled
    if not zipmodedisabled: zipstate = zip_newval

def getzipstate():
    global zipstate
    return zipstate

#Game settings
def setfirstslides(slide1, slide2 = None):
    global firstslide, firstuislide
    firstslide = slide1
    firstuislide = slide2

def getfirstslides():
    global firstslide, firstuislide
    return [firstslide, firstuislide]

#Menubar Settings
def setmenurect(rect):
    global menu_rect
    menu_rect = rect

def getmenurect():
    global menu_rect
    return menu_rect

#Save settings
def setpreviewsize(size):
    global previewsize
    previewsize = size

def getpreviewsize():
    global previewsize
    return previewsize

#Inventory settings
def setinventoryheight(size):
    global itemsize
    itemsize = size

def getinventoryheight():
    global itemsize
    return itemsize

def setinventoryshowatstart(hide):
    global showatstart
    showatstart = hide

def getinventoryshowatstart():
    global showatstart
    return showatstart

def setinventoryshow(alpha):
    global show_alpha
    show_alpha = alpha

def getinventoryshow():
    global show_alpha
    return show_alpha

def setinventoryhide(alpha):
    global hide_alpha
    hide_alpha = alpha

def getinventoryhide():
    global hide_alpha
    return hide_alpha

def setscroll(filename, datfile = None, alpha = None):
    global scroll_file, scroll_datfile, scroll_alpha
    scroll_file = filename
    scroll_datfile = datfile
    scroll_alpha = alpha

def getscrollfile():
    global scroll_file
    return scroll_file

def getscrolldatfile():
    global scroll_datfile
    return scroll_datfile

def getscrollalpha():
    global scroll_alpha
    return scroll_alpha

#Transition Settings
def settransquality(quality):
    global transquality
    transquality = quality

def gettransquality():
    global transquality
    return transquality

def setfadevelocity(quality, velocity):
    global fade_best, fade_normal, fade_fastest
    if quality == 'Best':
        fade_best = velocity
    elif quality == 'Normal':
        fade_normal = velocity
    elif quality == 'Fastest':
        fade_fastest= velocity

def getfadevelocity():
    global fade_best, fade_normal, fade_fastest
    if transquality == 'Best':
        return fade_best
    elif transquality == 'Normal':
        return fade_normal
    elif transquality == 'Fastest':
        return fade_fastest

def setscrollvelocity(quality, velocity):
    global scroll_best, scroll_best, scroll_fastest
    if quality == 'Best':
        scroll_best = velocity
    elif quality == 'Normal':
        scroll_best = velocity
    elif quality == 'Fastest':
        scroll_fastest= velocity
    
def getscrollvelocity():
    global scroll_best, scroll_best, scroll_fastest
    if transquality =='Best':
        return scroll_best
    elif transquality == 'Normal':
        return scroll_best
    elif transquality == 'Fastest':
        return scroll_fastest

def setdelay(quality, delay):
    global delay_best, delay_normal, delay_fastest
    if quality == 'Best':
        delay_best = delay
    elif quality == 'Normal':
        delay_normal = delay
    elif quality == 'Fastest':
        delay_fastest= delay

def getdelay():
    global delay_best, delay_normal, delay_fastest
    if transquality == 'Best':
        return delay_best
    elif transquality == 'Normal':
        return delay_normal
    elif transquality == 'Fastest':
        return delay_fastest

#Path settings
def settextpath(path):
    global text_path
    text_path = path

def gettextpath():
    global text_path
    return text_path

def setitempath(path):
    global item_path
    item_path = path

def getitempath():
    global item_path
    return item_path

def setcursorpath(path):
    global cursor_path
    cursor_path = path

def getcursorpath():
    global cursor_path
    return cursor_path

def setsavepath(path):
    global save_path
    save_path = path

def getsavepath():
    global save_path
    return save_path

def setdatapath(path):
    global data_path
    data_path = path

def getdatapath():
    global data_path
    return data_path

#Cursor settings
def setfwdcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: fwdcursor_file = filename
    if datfile != None: fwdcursor_datfile = datfile
    if alpha != None: fwdcursor_alpha = alpha
    if hotspot != None: fwdcursor_hotspot = hotspot

def setfistcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: fistcursor_file = filename
    if datfile != None: fistcursor_datfile = datfile
    if alpha != None: fistcursor_alpha = alpha
    if hotspot != None: fistcursor_hotspot = hotspot

def setgrabcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: grabcursor_file = filename
    if datfile != None: grabcursor_datfile = datfile
    if alpha != None: grabcursor_alpha = alpha
    if hotspot != None: grabcursor_hotspot = hotspot

def setleftcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: leftcursor_file = filename
    if datfile != None: leftcursor_datfile = datfile
    if alpha != None: leftcursor_alpha = alpha
    if hotspot != None: leftcursor_hotspot = hotspot

def setrightcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: rightcursor_file = filename
    if datfile != None: rightcursor_datfile = datfile
    if alpha != None: rightcursor_alpha = alpha
    if hotspot != None: rightcursor_hotspot = hotspot

def setright180cursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: right180cursor_file = filename
    if datfile != None: right180cursor_datfile = datfile
    if alpha != None: right180cursor_alpha = alpha
    if hotspot != None: right180cursor_hotspot = hotspot

def setleft180cursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: left180cursor_file = filename
    if datfile != None: left180cursor_datfile = datfile
    if alpha != None: left180cursor_alpha = alpha
    if hotspot != None: left180cursor_hotspot = hotspot

def setupcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: upcursor_file = filename
    if datfile != None: upcursor_datfile = datfile
    if alpha != None: upcursor_alpha = alpha
    if hotspot != None: upcursor_hotspot = hotspot

def setdowncursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: downcursor_file = filename
    if datfile != None: downcursor_datfile = datfile
    if alpha != None: downcursor_alpha = alpha
    if hotspot != None: downcursor_hotspot = hotspot

def setzipcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: zipcursor_file = filename
    if datfile != None: zipcursor_datfile = datfile
    if alpha != None: zipcursor_alpha = alpha
    if hotspot != None: zipcursor_hotspot = hotspot

def setarrowcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: arrowcursor_file = filename
    if datfile != None: arrowcursor_datfile = datfile
    if alpha != None: arrowcursor_alpha = alpha
    if hotspot != None: arrowcursor_hotspot = hotspot
    
def setmagnifyPcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: magnifyPcursor_file = filename
    if datfile != None: magnifyPcursor_datfile = datfile
    if alpha != None: magnifyPcursor_alpha = alpha
    if hotspot != None: magnifyPcursor_hotspot = hotspot

def setmagnifyMcursor(filename = None, datfile = None, alpha = None, hotspot = None):
    if filename != None: magnifyMcursor_file = filename
    if datfile != None: magnifyMcursor_datfile = datfile
    if alpha != None: magnifyMcursor_alpha = alpha
    if hotspot != None: magnifyMcursor_hotspot = hotspot
