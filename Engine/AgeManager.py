from Age import Age
from Archive import Archive
from Parameters import Parameters

"""
This class handles some minimal logic for age loading, and the concept of
putting ages in memory for quick access.

setAge    - sets (loads) the current age, by age name.
bufferAge - loads and age into memory and keeps it there, for fast access.
"""

class AgeManager:
    currentAge = None
    
    unbufferedAge = None
    bufferedAges = {}
    
    def __init__(self, engine):
        self.engine = engine
    
    def loadAge(self, ageName):
        # Use parameters
        params = {"type":Parameters.age_type, "file_loc":Parameters.age_folder}
        arch = Archive(ageName, params)
        
        # the .py files need to be somewhere on the path, all together
        exec """from $AGE.$AGE import $AGE
age = $AGE(ageName, arch, params, self.engine)""".replace("$AGE", ageName)
        age.init()
        return age
    
    def bufferAge(self, ageName):
        # loads the age in the background (on the buffer).
        # Makes the age available on short notice. IE the menu should be buffered,
        # since it can come up at any time, and must come up quickly. (No time to parse xml)
        age = self.loadAge(ageName)
        
        self.bufferedAges[ageName] = age
        return age
    
    def setAge(self, ageName):
        if ageName in self.bufferedAges.keys():
            # Bring up the pre-buffered age, leaving the current age in memory
            # eg reference to unbufferedAge is kept
            self.currentAge = self.bufferedAges[ageName]
        elif self.unbufferedAge is not None and self.unbufferedAge.getName() == ageName:
            # go back to a non-prebuffered age which is still in memory.
            self.currentAge = self.unbufferedAge
        else:
            # Load the age, scrap the current age
            age = self.loadAge(ageName)
            
            self.unbufferedAge = age
            # Clean the buffers of the current age
            if self.currentAge is not None:
                self.currentAge.clearBuffers()
            self.currentAge = self.unbufferedAge
        return self.currentAge
    
    def getAge(self):
        return self.currentAge
