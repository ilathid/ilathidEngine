    # Note: I consider the following a unwise function to ever need to use
    # def detachobject(self, obj):
            
    # Note: Replace back to object-layers if needed
    def layerAbove(self, obj1, obj2):
        self.slide_objects.remove(obj1)
        i = self.slide_objects.index(obj2)
        self.slide_objects.insert(i+1, obj1)
        
    def layerTop(self, obj):
        self.slide_objects.remove(obj)
        self.slide_objects.append(obj)
    
    def layerBottom(self, obj):
        self.slide_objects.remove(obj)
        self.slide_objects.insert(0, obj)
