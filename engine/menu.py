from slide import slide
from text import text
from AoIimage import AoIimage

import pygame

import music
import os

from time import localtime, strftime
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
import parameters
import globals
from engine.Save import save
from FilePath import FilePath
from SlideManager import SlideManager
from engine.filemanager import filemanager

#Function to toggle zip mode on or off from the menu
def togglezip():
    parameters.setzipstate(not parameters.getzipstate())
    if parameters.getzipstate():
        check.update(visible = 1)
    else:
        check.update(visible = 0)
    
#Called when the "quit" option is clicked on menumain. Builds the quit menu UI on the screen
def quitmenumainenter():
    #menumain.gethotspots()
    nbHotspots=menumain.gethotspotsize()
    for j in range((nbHotspots-1),-1,-1):
        menumain.detachhotspot(j)
    quitmenumain.update(visible = 1)
    menumain.attachhotspot((235, 282, 55, 30), 'grab', {'action' : 'quitgame','zip':0})
    menumain.attachhotspot((325, 282, 55, 30), 'grab', {'action' : 'quitmenuexit','zip':0})
    
#Called when the quit menu is exited. Restores the default menu to it's original state
def quitmenuexit():
    nbHotspots=menumain.gethotspotsize()
    for j in range((nbHotspots-1),-1,-1):
        menumain.detachhotspot(j)
    menumain.attachhotspot((500, 300, 200, 40), 'grab', {'dest' :'return_root','zip':0}) #append a hotspot to this slide
    menumain.attachhotspot((500, 340, 200, 40), 'grab', {'dest' :'return','zip':0}) #append a hotspot to this slide
    menumain.attachhotspot((500, 380, 200, 40), 'grab', {'dest' : 'loadmenu','zip':0, 'push':1})
    menumain.attachhotspot((500, 420, 200, 40), 'grab', {'action' : 'optionmenuenter','zip':0, 'push':1})
    if (SlideManager.getCurrentSlide().getrealname()=="intro"):
        # The save menu should not be reachable when no age has been played
        menumain.detachhotspotById('save')
    else:
        menumain.attachhotspot((500, 460, 200, 40), 'grab', {'dest' : 'savemenu','zip':0, 'push':1},'save')
    menumain.attachhotspot((500, 500, 200, 40), 'grab', {'action' : 'quitmenumainenter','zip':0})
    quitmenumain.update(visible = 0)

#Quits the game
def quitgame():
    globals.quit = 1

#Called when the "options" option is clicked. Builds the options menu UI on the screen
def optionmenuenter():

    menumain.updatestate('mousepos', (0,0))
    
    nbHotspots=menumain.gethotspotsize()
    for j in range((nbHotspots-1),-1,-1):
        menumain.detachhotspot(j)
    
    optionmenubk.update(visible = 1)
    menumain.attachhotspot((461, 422, 55, 30), 'grab', {'action' : optionmenuexit,'zip':0})
    menumain.attachhotspot((252, 425, 20, 20), 'grab', {'action' : togglezip,'zip':0})
    if parameters.getzipstate():
        check.update(visible = 1)
    if parameters.gettransquality() == 'None':
        transopt.update(rect = (252,245), visible = 1)
        menumain.attachhotspot((252, 245, 20, 20), 'grab', {'drag' : transdrag,'zip':0})
    if parameters.gettransquality() == 'Fastest':
        transopt.update(rect = (252,285), visible = 1)
        menumain.attachhotspot((252, 285, 20, 20), 'grab', {'drag' : transdrag,'zip':0})
    if parameters.gettransquality() == 'Normal':
        transopt.update(rect = (252,323), visible = 1)
        menumain.attachhotspot((252, 323, 20, 20), 'grab', {'drag' : transdrag,'zip':0})
    if parameters.gettransquality() == 'Best':
        transopt.update(rect = (252,364), visible = 1)
        menumain.attachhotspot((252, 364, 20, 20), 'grab', {'drag' : transdrag,'zip':0})

#Called when the options menu is exited. Restores the default menu to it's original state
def optionmenuexit():
    nbHotspots=menumain.gethotspotsize()
    for j in range((nbHotspots-1),-1,-1):
        menumain.detachhotspot(j)
    menumain.attachhotspot((500, 300, 200, 40), 'grab', {'dest' :'return_root','zip':0})
    menumain.attachhotspot((500, 340, 200, 40), 'grab', {'dest' :'return','zip':0})
    menumain.attachhotspot((500, 380, 200, 40), 'grab', {'dest' : 'loadmenu','zip':0, 'push':1})
    menumain.attachhotspot((500, 420, 200, 40), 'grab', {'action' : 'optionmenuenter','zip':0, 'push':1})
    if (SlideManager.getCurrentSlide().getrealname()=="intro"):
        # The save menu should not be reachable when no age has been played
        menumain.detachhotspotById('save')
    else:
        menumain.attachhotspot((500, 460, 200, 40), 'grab', {'dest' : 'savemenu','zip':0, 'push':1},'save')
    menumain.attachhotspot((500, 500, 200, 40), 'grab', {'action' : 'quitmenumainenter','zip':0})
    check.update(visible = 0)
    transopt.update(visible = 0)
    optionmenubk.update(visible = 0)

#Drag function for the transition slider
def transdrag(event):
    if event.type == pygame.MOUSEMOTION:
        if event.pos[0] != menumain.getstate('mousepos')[0]:
            pygame.mouse.set_pos((menumain.getstate('mousepos')[0], event.pos[1]))
            return 0
        elif event.pos[1] - menumain.getstate('mouseposrelative')[1] < 244:
            pygame.mouse.set_pos((event.pos[0], 244 + menumain.getstate('mouseposrelative')[1]))
            return 0
        elif event.pos[1] - menumain.getstate('mouseposrelative')[1] > 364:
            pygame.mouse.set_pos((event.pos[0], 364 + menumain.getstate('mouseposrelative')[1]))
            return 0
        transopt.update(rect = (252,event.pos[1] - menumain.getstate('mouseposrelative')[1]))
        menumain.updatehotspot(2,(252,event.pos[1]  - menumain.getstate('mouseposrelative')[1] ,20,20),'grab', drag = transdrag)
        return 1
    elif event.type == pygame.MOUSEBUTTONDOWN:
        globals.curcursor = globals.cursors.get('action')
        tmppos = transopt.getrect().topleft
        menumain.updatestate('mousepos', event.pos)
        menumain.updatestate('mouseposrelative', (event.pos[0] - tmppos[0], event.pos[1] - tmppos[1]))
    elif event.type == pygame.MOUSEBUTTONUP:
        if transopt.getrect().top < 265:
            transopt.update(rect = (252,245))
            menumain.updatehotspot(2,(252,245, 20, 20), 'grab', drag = transdrag)
            parameters.settransquality('None')
        elif transopt.getrect().top > 264 and transopt.getrect().top < 300:
            transopt.update(rect = (252,285))
            menumain.updatehotspot(2,(252,285, 20, 20), 'grab', drag = transdrag)
            parameters.settransquality('Fastest')
        elif transopt.getrect().top > 299 and transopt.getrect().top < 349:
            transopt.update(rect = (252,323))
            menumain.updatehotspot(2,(252,323, 20, 20), 'grab', drag = transdrag)
            parameters.settransquality('Normal')
        else:
            transopt.update(rect = (252,364))
            menumain.updatehotspot(2,(252,364, 20, 20), 'grab', drag = transdrag)
            parameters.settransquality('Best')
        menumain.updatestate('mousepos', None)
        menumain.updatestate('mouseposrelative', None)
        return 1

def menuenter():
    
    if globals.playerinventory != None:
        globals.playerinventory.update(visible = 0, enabled = 0)
    
    if globals.currentage is None or SlideManager.getBaseSlide().gettype() == 'menu':
        # The save menu should not be reachable when no age has been played
        menumain.detachhotspotById('save')
    else:
        menumain.attachhotspot((500, 460, 200, 40), 'grab', {'dest' : 'savemenu','zip':0, 'push':1},'save')
        
    musicmain.playmusic()

def menuexit():
    if globals.playerinventory != None:
        globals.playerinventory.update(visible = 1, enabled = 1)

def load0():
    load(0)
def load1():
    load(1)
def load2():
    load(2)
def load3():
    load(3)
def load4():
    load(4)
def load5():
    load(5)
def load6():
    load(6)
def load7():
    load(7)
def load8():
    load(8)
def load9():
    load(9)
def load(i):
    print "load game ",i
    (slide, music) = globals.loadGame('save.'+str(i))
    #The parsing of Save file has ended, we can launch the game

    #start music
    if music is not None:
        globals.currentage.getMusic(music).playmusic()
    
    SlideManager.resetStackTo([slide])

def save0():
    menusave(0)
def save1():
    menusave(1)
def save2():
    menusave(2)
def save3():
    menusave(3)
def save4():
    menusave(4)
def save5():
    menusave(5)
def save6():
    menusave(6)
def save7():
    menusave(7)
def save8():
    menusave(8)
def save9():
    menusave(9)

def menusave(i):
    print "save game ",i
    #Open index and search the last
    try:
        tmpfile=open(os.path.join(parameters.getsavepath(), 'index.sav'),'rb')
        data=tmpfile.readlines()
        tmpfile.close()
    except:
        pass
    
    if not os.path.exists(parameters.getsavepath()):
        os.makedirs(parameters.getsavepath())
    
    #Build the save file specific
    name = 'save.'+str(i)
    f = file(os.path.join(parameters.getsavepath(), name),'w')
    #print 'saved slide ',slide._save(slide._currentslide)
    hd = XMLGenerator(f) # handler's creation
    
    hd.startDocument()
    hd.startElement("Save", AttributesImpl({}))
    hd.startElement("age", AttributesImpl({}))
    hd.characters(globals.currentage.getFileName())
    hd.endElement("age")
    hd.startElement("music", AttributesImpl({"name": music.getcurrentStdMusic().getname()}))
    hd.endElement("music")
    hd.startElement("slide", AttributesImpl({}))
    # items in the stack beyond the first item are supposed to be menus, ignore them
    hd.characters(SlideManager.getBaseSlide().getrealname())
    hd.endElement("slide")
    hd.startElement("states", AttributesImpl({}))
    
    import pickle
    import base64
    
    for (k,v) in globals.menuslides.items():
        if (isinstance(v,slide)):
            #We remove the slideload and menu_root
            if (v.getrealname().startswith("slideload")==False and v.getrealname().startswith("menu_root")==False):
                # serialize the state dictionary using Pickle, then encode it in base64 so that it fits well in XML
                state = base64.b64encode(pickle.dumps(v.getAllStateVariables()))
                hd.startElement("state", AttributesImpl({"name": k, "state": state}))
                hd.endElement("state")
    for (k,v) in globals.currentage.getAllSlides().items():
        # serialize the state dictionary using Pickle, then encode it in base64 so that it fits well in XML
        state = base64.b64encode(pickle.dumps(v.getAllStateVariables()))
        hd.startElement("state", AttributesImpl({"name": k, "state": state}))
        hd.endElement("state")
    hd.endElement("states")
    hd.endElement("Save")
    hd.endDocument()
    f.close()
    date = strftime("%a, %d %b %Y %H:%M:%S", localtime())
    currentslideimg = SlideManager.getBaseSlide().getFullFilePath()

    #Build the key of saveIndex
    name = 'save'+str(i)
    #Retrieve the Save object :
    if (globals.saves.has_key(name)):
        mySave=globals.saves[name]
        mySave.setdate(date)
        mySave.setimage(currentslideimg)
        mySave.setage(globals.currentage.getFileName())
    else:
        globals.saves[name] = save(name, globals.currentage.getFileName(), currentslideimg, date)
    globals.saveSaveIndex('saveIndex.xml')
    #We exit the game
    quitgame()

def confirmsave0():
    confirmsave(0)
def confirmsave1():
    confirmsave(1)
def confirmsave2():
    confirmsave(2)
def confirmsave3():
    confirmsave(3)
def confirmsave4():
    confirmsave(4)
def confirmsave5():
    confirmsave(5)
def confirmsave6():
    confirmsave(6)
def confirmsave7():
    confirmsave(7)
def confirmsave8():
    confirmsave(8)
def confirmsave9():
    confirmsave(9)
def confirmsave(nb):
    print "confirmsave game ",nb
    for j in range((savemenu.gethotspotsize()-1),-1,-1):
        savemenu.detachhotspot(j)
    savemenubk.update(visible = 1)
    confirmSavetext.update(visible = 1)
    savemenu.attachhotspot((250, 272, 110, 30), 'grab', {'action' : tabSave[nb],'zip':0})
    savemenu.attachhotspot((460, 422, 55, 30), 'grab', {'dest' : 'menumain','zip':0})
  
def confirmover0():
    confirmover(0)
def confirmover1():
    confirmover(1)
def confirmover2():
    confirmover(2)
def confirmover3():
    confirmover(3)
def confirmover4():
    confirmover(4)
def confirmover5():
    confirmover(5)
def confirmover6():
    confirmover(6)
def confirmover7():
    confirmover(7)
def confirmover8():
    confirmover(8)
def confirmover9():
    confirmover(9)
def confirmover(nb):
    print "confirmover game ",nb
    for j in range((savemenu.gethotspotsize()-1),-1,-1):
        savemenu.detachhotspot(j)
    savemenubk.update(visible = 1)
    confirmOverWtext.update(visible = 1)
    savemenu.attachhotspot((250, 272, 110, 30), 'grab', {'action' : tabSave[nb],'zip':0})
    savemenu.attachhotspot((460, 422, 55, 30), 'grab', {'dest' : 'menumain','zip':0})

globals.functions['quitgame']=quitgame
globals.functions['quitmenuexit']=quitmenuexit
globals.functions['quitmenumainenter']=quitmenumainenter
globals.functions['optionmenuenter']=optionmenuenter


#Slides for the load, they must be "UI" type to display the next slide properly (see enginemain on mouseevent management)
slideload0 = slide('slideload0','pres.jpg', type = 'ui')
slideload0.onentrance(load0)
globals.menuslides['slideload0']=slideload0
slideload1 = slide('slideload1','pres.jpg', type = 'ui')
slideload1.onentrance(load1)
globals.menuslides['slideload1']=slideload1
slideload2 = slide('slideload2','pres.jpg', type = 'ui')
slideload2.onentrance(load2)
globals.menuslides['slideload2']=slideload2
slideload3 = slide('slideload3','pres.jpg', type = 'ui')
slideload3.onentrance(load3)
globals.menuslides['slideload3']=slideload3
slideload4 = slide('slideload4','pres.jpg', type = 'ui')
slideload4.onentrance(load4)
globals.menuslides['slideload4']=slideload4
slideload5 = slide('slideload5','pres.jpg', type = 'ui')
slideload5.onentrance(load5)
globals.menuslides['slideload5']=slideload5
slideload6 = slide('slideload6','pres.jpg', type = 'ui')
slideload6.onentrance(load6)
globals.menuslides['slideload6']=slideload6
slideload7 = slide('slideload7','pres.jpg', type = 'ui')
slideload7.onentrance(load7)
globals.menuslides['slideload7']=slideload7
slideload8 = slide('slideload8','pres.jpg', type = 'ui')
slideload8.onentrance(load8)
globals.menuslides['slideload8']=slideload8
slideload9 = slide('slideload9','pres.jpg', type = 'ui')
slideload9.onentrance(load9)
globals.menuslides['slideload9']=slideload9

#Slide for "New game" return_root, also on type =UI because it is a transition slide
def newgameenter():
    # FIXME: at this time there is no code to clean up paths added by 'push_age'
    
    if parameters.testCustomAge is not None:
        exec """from $AGE import $AGE
filemanager.push_age('$AGE')
globals.currentage = $AGE()""".replace("$AGE", parameters.testCustomAge)
    else:
        from DniChamberAge import DniAge
        filemanager.push_age('Dni')
        globals.currentage = DniAge()
    
    #from FooAge import FooAge
    #filemanager.push_age('FooAge')
    #globals.currentage = FooAge()
    
    SlideManager.resetStackTo([globals.currentage.getslide(globals.currentage.getStartLocation())])
    return None

def savemenuenter():
    if (savemenubk.isvisible):
        confirmOverWtext.update(visible=0)
        confirmSavetext.update(visible=0)
        savemenubk.update(visible=0)
        #we remove the current hotspot on savemenu
        for j in range((savemenu.gethotspotsize()-1),-1,-1):
            savemenu.detachhotspot(j)
    #We must construct again the attachhotspot
    i=0
    j=0
    nbfilesave=0
    for (k,v) in globals.saves.items():
        if i < 5:
            savemenu.attachhotspot((100,75+j, 100 , 75), 'grab', {'action' : tabConfirmOverW[i],'zip':0})
        else:
            if i == 5:
                j=0
            savemenu.attachhotspot((425,75+j, 100 , 75), 'grab', {'action' : tabConfirmOverW[i],'zip':0})
        i=i+1
        nbfilesave=nbfilesave+1
        j=j+100
    #We put for all other possible save the same number=nbfilesave to have always a good order in the save files
    for a in range(i,10):
        if a < 5:
            savemenu.attachhotspot((100,75+j, 100 , 75), 'grab', {'action' : tabConfirmSave[nbfilesave],'zip':0})
        else:
            if a == 5:
                j=0
            savemenu.attachhotspot((425,75+j, 100 , 75), 'grab', {'action' : tabConfirmSave[nbfilesave],'zip':0})
        j=j+100
        
#Create slides and objects that are part of the menu system
musicmain=music.Music('menu','MenuTheme.mp3','menu',1)
menumain = slide('menumain','menumain.jpg', type = 'menu')
menumain.onentrance(menuenter)
menumain.onexit(menuexit)
menumain.attachhotspot((500, 300, 200, 40), 'grab', {'dest' : 'return_root','zip':0})
menumain.attachhotspot((500, 340, 200, 40), 'grab', {'dest' : 'return','zip':0})
menumain.attachhotspot((500, 380, 200, 40), 'grab', {'dest' : 'loadmenu','zip':0, 'push':1})
menumain.attachhotspot((500, 420, 200, 40), 'grab', {'action' : 'optionmenuenter','zip':0, 'push':1})
menumain.attachhotspot((500, 460, 200, 40), 'grab', {'dest' : 'savemenu','zip':0, 'push':1},'save')
menumain.attachhotspot((500, 500, 200, 40), 'grab', {'action' : 'quitmenumainenter','zip':0})
loadmenu = slide('loadmenu','menumain.jpg', type = 'menu')
loadmenu.attachhotspot((77, 35, 30, 25), 'forward', {'dest' : 'return','zip':0})
savemenu = slide('savemenu','menumain.jpg', type = 'menu')
savemenu.onentrance(savemenuenter)
savemenu.attachhotspot((77, 35, 30, 25), 'forward', {'dest' : 'return','zip':0})
newgame = slide('return_root','pres.jpg', type = 'ui')
newgame.onentrance(newgameenter)
globals.menuslides['menumain']=menumain
globals.menuslides['loadmenu']=loadmenu
globals.menuslides['savemenu']=savemenu
globals.menuslides['return_root']=newgame

parameters.setfirstslides(menumain, menumain)

bench = AoIimage(FilePath('bench.jpg', None, 0), rect = (430,65), slide = menumain)
optionmenubk = AoIimage(FilePath('optionsmenu.jpg', None, 0), rect = (175,122), visible = 0, slide = menumain, layer=2)
quitmenumain = AoIimage(FilePath('quitmenu.jpg', None, 0), rect = (175,122), visible = 0, slide = menumain, layer=2)
transopt = AoIimage(FilePath('radiobutton.bmp', None, 0), rect = (252,245), visible = 0, alpha = (0,0), slide = menumain, layer=3)
check = AoIimage(FilePath('radiobutton.bmp', None, 0), rect = (252,425), visible = 0, alpha = (0,0), slide = menumain, layer=3)
quitmenusave = AoIimage(FilePath('savemenu.jpg', None, 0), rect = (175,122), visible = 0, slide = savemenu, layer=2)

toptext = text(FilePath('AC.TTF', None, 0), (100, 35, 400, 100), 'The Ages of Ilathid', (0,0,0), 1, 0, 26, None, menumain)
urutext = text(FilePath('Ilathidhi01.ttf', None, 0), (100, 135, 400, 100), 'URU live is not dead', (0,0,0), 1, 0, 14, None, menumain)
newtext = text(FilePath('AC.TTF', None, 0), (500, 300, 200, 40), 'New Game', (0,0,0), 1, 0, 35, None, menumain)
restext = text(FilePath('AC.TTF', None, 0), (500, 340, 200, 40), 'Resume Game', (0,0,0), 1, 0, 35, None, menumain)
loadtext = text(FilePath('AC.TTF', None, 0), (500, 380, 200, 40), 'Load Game', (0,0,0), 1, 0, 35, None, menumain)
optext = text(FilePath('AC.TTF', None, 0), (500, 420, 200, 40), 'Options', (0,0,0), 1, 0, 35, None, menumain)
savetext = text(FilePath('AC.TTF', None, 0), (500, 460, 200, 40), 'Save Game', (0,0,0), 1, 0, 35, None, menumain)
quittext = text(FilePath('AC.TTF', None, 0), (500, 500, 200, 40), 'Quit Game', (0,0,0), 1, 0, 35, None, menumain)
loadtitle = text(FilePath('AC.TTF', None, 0), (200, 35, 250, 50), 'Load', (0,0,0), 1, 0, 35, None, loadmenu)
savetitle = text(FilePath('AC.TTF', None, 0), (200, 35, 250, 50), 'Save', (0,0,0), 1, 0, 35, None, savemenu)
backloadtitle = text(FilePath('avgardn.ttf', None, 0), (77, 35, 400, 100), 'Back', (0,0,250), 1, 0, 15, None, loadmenu)
backsavetitle = text(FilePath('avgardn.ttf', None, 0), (77, 35, 400, 100), 'Back', (0,0,250), 1, 0, 15, None, savemenu)

###Build the save and load menu slides
#open the encrypted index file

imgLoad=list()
ageLoad=list()
datLoad=list()
imgSave=list()
ageSave=list()
datSave=list()
imgFond=list()
tabLoad=['slideload0','slideload1','slideload2','slideload3','slideload4','slideload5','slideload6','slideload7','slideload8','slideload9']
tabConfirmSave=[confirmsave0,confirmsave1,confirmsave2,confirmsave3,confirmsave4,confirmsave5,confirmsave6,confirmsave7,confirmsave8,confirmsave9]
tabConfirmOverW=[confirmover0,confirmover1,confirmover2,confirmover3,confirmover4,confirmover5,confirmover6,confirmover7,confirmover8,confirmover9]
tabSave=[save0,save1,save2,save3,save4,save5,save6,save7,save8,save9]

#Load the saveIndex file
globals.loadSaveIndex('saveIndex.xml')
#Loop trough the saves files

i=0
nbfilesave=0
j=0
for (k,v) in globals.saves.items():
    if i < 5:
        print "Image", v.getimage()[0], v.getimage()[1], v.getimage()[2]
        imgLoad.append(AoIimage(FilePath(v.getimage()[0], v.getimage()[1], v.getimage()[2], isAbsolute=True),
                                rect=(100,75+j), visible=1, slide=loadmenu, ratio=(100,75)))
        ageLoad.append(text(FilePath('avgardn.ttf', None, 0), (205, 75+j, 190, 20), v.getage(), (0,0,0), 1, 0, 15, None, loadmenu))
        datLoad.append(text(FilePath('avgardn.ttf', None, 0), (205, 105+j, 190, 20), v.getdate(), (0,0,0), 1, 0, 15, None, loadmenu))
        loadmenu.attachhotspot((100,75+j, 100 , 75), 'grab', {'dest' : tabLoad[i],'zip':0})
        
        imgSave.append(AoIimage(FilePath(v.getimage()[0], v.getimage()[1], v.getimage()[2], isAbsolute=True),
                                rect=(100,75+j), visible=1, slide=savemenu, ratio=(100,75)))
        ageSave.append(text(FilePath('avgardn.ttf', None, 0), (205, 75+j, 190, 20), v.getage(), (0,0,0), 1, 0, 15, None, savemenu))
        datSave.append(text(FilePath('avgardn.ttf', None, 0), (205, 105+j, 190, 20), v.getdate(), (0,0,0), 1, 0, 15, None, savemenu))
    else:
        if i == 5:
            j=0
        imgLoad.append(AoIimage(FilePath(v.getimage()[0], v.getimage()[1], v.getimage()[2], isAbsolute=True),
                                rect=(425,75+j), visible=1, slide=loadmenu, ratio=(100,75)))
        ageLoad.append(FilePath(text('avgardn.ttf', None, 0), (530, 75+j, 190, 20), v.getage(), (0,0,0), 1, 0, 15, None, loadmenu))
        datLoad.append(FilePath(text('avgardn.ttf', None, 0), (530, 105+j, 190, 20), v.getdate(), (0,0,0), 1, 0, 15, None, loadmenu))
        loadmenu.attachhotspot((425,75+j, 100 , 75), 'grab', {'dest' : tabLoad[i],'zip':0})
        
        imgSave.append(AoIimage(FilePath(v.getimage()[0], v.getimage()[1], v.getimage()[2], isAbsolute=True),
                                rect=(425,75+j), visible=1, slide=savemenu, ratio=(100,75)))
        ageSave.append(text('avgardn.ttf', None, 0, (530, 75+j, 190, 20), v.getage(), (0,0,0), 1, 0, 15, None, savemenu))
        datSave.append(text('avgardn.ttf', None, 0, (530, 105+j, 190, 20), v.getdate(), (0,0,0), 1, 0, 15, None, savemenu))
    i=i+1
    nbfilesave=nbfilesave+1
    j=j+100

#We put for all other possible save the same number=nbfilesave to have always a good order in the save files
for a in range(i,10):
    if a < 5:
        imgFond.append(AoIimage(FilePath("fond.png", None, 0), rect=(100,75+j), visible=1, slide=savemenu))
    else:
        if a == 5:
            j  =0
        imgFond.append(AoIimage(FilePath("fond.png", None, 0), rect=(425,75+j), visible=1, slide=savemenu))
    j=j+100

#On savemenu put a confirmation image, must be set after all the other images are put to be displayed correctly
savemenubk = AoIimage(FilePath('savemenu.jpg', None, 0), rect = (175,122), visible = 0, slide = savemenu)
confirmOverWtext = text(FilePath('sextalk.ttf', None, 0), (190, 150, 400, 50), 'Overwrite and quit ?', (0,0,0), 0, 0, 30, None, savemenu)
confirmSavetext = text(FilePath('sextalk.ttf', None, 0), (190, 150, 400, 50), 'Save and quit ?', (0,0,0), 0, 0, 30, None, savemenu)

