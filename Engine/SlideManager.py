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

class SlideManager:
    age_manager = None

    # Slides are added to this stack (especially useful for menus)    
    _slide_stack = []
    current_slide = None
    
    def __init__(self, ageManager):
        self.age_manager = ageManager
        
    def pushSlide(self, slide):
        """ slide is a string """
        # stores age name, slide name
        self._slide_stack.push([self.age_manager.getAge().getName(), self.current_slide])
        self.setSlide(slide)
        
    def popSlide(self):
        if len(self._slide_stack) == 0:
            raise Exception('SlideManager: popped from an empty stack')
            
        # on exit
        oldslide = self.getSlide()
        if oldslide != None:
            oldslide.exit()
            
        [age_name, slide_name] = self._slide_stack.pop()
        age = self.age_manager.setAge(age_name)
        self.current_slide = slide_name

        # Load the slide into memory
        slide = self.age_manager.getAge().getSlide(slide_name)
        slide.makeBuffers()

        # Handle slide change
        # age.manageBuffers(slide_name)

        #Do entry callback
        # print "Entering slide " + str(newSlide)
        newSlide.entry()
        
    def getSlide(self):
        """ return: slide object of the current slide """
        if self.age_manager.getAge() != None:
            return self.age_manager.getAge().getSlide(self.current_slide)
        else:
            return None
        
    def setSlide(self, slide):
        """ slide is a string """
        # on exit
        oldslide = self.getSlide()
        if oldslide != None:
            oldslide.exit()

        if slide is None:
            return

        # dot-parse it
        parts = slide.split(".")
        if len(parts) == 1:
            # Just assume it is in the current age
            newAge = self.age_manager.getAge()
            newSlide = newAge.getSlide(parts[0])
        elif len(parts) == 2:
            newAge = self.age_manager.setAge(parts[0])
            newSlide = newAge.getSlide(parts[1])
        else:
            raise Exception('SlideManager: Must be a 1 or 2 part slide name.')

        # Current slide is stored in an age.slide pair, same as everything on the stack
        self.current_slide = newSlide.getName()
        
        # Load the new slide into memory
        newSlide.makeBuffers()
        
        # Handle slide change
        newAge.manageBuffers(self.current_slide)
        
        #Do entry callback
        # print "Entering slide " + str(newSlide)
        newSlide.entry()
        
        return newSlide
