from Gamestate import Gamestate

class SlideObject:
    debug = False
    
    # Conditions and Gamestate
    _cond_string = None
    _cond_callback = None
    old_cond = None
    ticket = -1
    
    callbacks = {}
    
    def setCondString(self, string):
        self._cond_string = string
    
    def setCondCallback(self, callback):
        self._cond_callback = callback
    
    def checkCondition(self):
        if self.ticket == Gamestate.ticket:
            return self.old_cond
        ret = True
        if self._cond_callback is not None:
            #print "func cond"
            ret = self._cond_callback()
        elif self._cond_string is not None:
            #print "String cond"
            ret = Gamestate.evaluate(self._cond_string)
        #print "Condition: " + str(ret)
        self.old_cond = ret
        self.ticket = Gamestate.ticket
        return ret
    
    # Events
    # called when the player enters a slide containing this object
    # Only called if the object cond is satisfied.
    def _slide_entry(self):
        pass
    def _slide_exit(self):
        pass
    
    
    def __init__(self):
        pass
    
    def setDebug(self, debug):
        self.debug = debug
        
    def makeBuffers(self):
        pass
        
    def clearBuffers(self):
        pass
    
    def __del__(self):
        pass

    def doEvents(self, events, dt):
        return events

    def render(self, geom=None):
        pass
