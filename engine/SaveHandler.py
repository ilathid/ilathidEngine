from xml.sax.handler import ContentHandler
import globals
from engine.filemanager import filemanager

class SaveHandler(ContentHandler):
    def __init__(self):
        self.music, self.file, self.slide = None, None, None
        self.buffer = ''
    
    def startElement(self,name,attrs):
        if name == 'music':
            self.music = attrs.get('name')
        if name == 'state':
            self.obj = attrs.get('name')
            self.state = attrs.get('state')
            
            import base64
            import pickle
            
            decoded_state = pickle.loads(base64.b64decode(self.state))
            
            #The load has been done before, we put the state for the different slides
            if self.obj in globals.menuslides:
                globals.menuslides[self.obj].setstate(decoded_state)
            elif self.obj in globals.currentage.getAllSlides():
                globals.currentage.getAllSlides()[self.obj].setstate(decoded_state)
    
    def endElement(self,name):
        #We put the buffer in the object
        if name == 'age':
            self.file=str(self.buffer)
            #We load the age so we can update the state afterwards
            
            # FIXME: find a cleaner way to find which age it is than hardcoding
            if "dni.xml" in self.file:
                from DniChamberAge import DniAge
                filemanager.push_age('Dni')
                globals.currentage = DniAge()
            else:
                raise Exception("Unknown age " + self._file)
        if name == 'slide':
            self.slide=str(self.buffer)
        if name == 'Save':
            #save slide load
            self.slide_obj = globals.currentage.getslide(self.slide)

    def characters(self,chars):
        self.buffer = chars
    
