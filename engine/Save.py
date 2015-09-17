

class save:
    def __init__(self,name = None, age = None, image = None, date= None):
        
        if image is not None and len(image) != 3:
            raise Exception("Parameter must be a triplet (file, archive, encryption)")
        
        self._name  = name
        self._age   = age
        self._image = image
        self._date  = date
    
    def getname(self):
        return self._name
    
    def setname(self,name):
        self._name=name
    
    def getage(self):
        return self._age
    
    def setage(self,age):
        self._age=age
    
    def getimage(self):
        return self._image
    
    def setimage(self,image):
        if len(image) != 3:
            raise Exception("Parameter must be a triplet (file, archive, encryption)")

        self._image=image
    
    def getdate(self):
        return self._date
    
    def setdate(self,date):
        self._date=date
