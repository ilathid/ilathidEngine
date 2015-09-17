from xml.sax.handler import ContentHandler
import globals
from Save import save

class SaveIndexHandler(ContentHandler):
    def __init__(self):
        self.name, self.image, self.date, self.age = None, None, None, None
        self.obj=None
        self.buffer = ''
    
    def startElement(self,name,attrs):
        if name == 'save':
            self.age = attrs.get('age')
            self.image = (attrs.get('image'), attrs.get('image_archive'), attrs.get('image_encryption'))
            self.date = attrs.get('date')
    
    def endElement(self,name):
        #We put the buffer in the object
        if name == 'save':
            self.name=str(self.buffer)
            #We got all things we need, we can create the save objects
            self.obj = save(self.name,self.age,self.image,self.date)
            globals.saves[self.name]=self.obj
    
    def characters(self,chars):
        self.buffer = chars
    
