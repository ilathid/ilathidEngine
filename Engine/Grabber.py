# TODO: Remove this class. It is a bad idea. Grabbing should be handled on a case-by-case basis.
# If anything, there should only be a helper class for grabbing&dragging operations.

# Grabbing and Dragging is a generic action, and should be planned as such.
# When the player clicks, something needs to remember where in case a drag event is detected.
# Also, which draggable item is in question needs to be remembered. It is acceptable to only consider one possability. If this item is no longer draggable when the mouse begins to move, no items are dragged.
# Draggability is in the item's own checking function.
# Easiest: The dragger is in the slide. When any slide item is clicked on, the slide decides what (if anything) is being dragged. This may be the slide itself, if it is 3d and draggable view is enabled.
# When the mouse moves more than the threshold ammount after the click, the dragging is registered with the selected item. Only one item may be dragged at a time. That item recieves 'callbacks' for motions (as it is dragged around) and for release.

import pygame.locals
from Parameters import Parameters
from CursorManager import CursorManager

class Grabber:
    grab_pos = None
    grabbing = False
    
    item = None
    
    def attatch(self, item, pos):
        if item.isGrabbable():
            self.item = item
            self.grab_pos = pos
    
    def doEvents(self, events):
        release = False
        for event in events:
            if self.item is not None and self.item.isGrabbable() and not self.grabbing and event.type == pygame.locals.MOUSEMOTION:
                if abs(event.pos[0] - self.grab_pos[0]) + abs(event.pos[1] - self.grab_pos[1]) > Parameters.drag_threshold:
                    self.grabbing = True
                    print "Grab at " + str(self.grab_pos)
                    # CursorManager.setCursor("grab")
            if self.grabbing and event.type == pygame.locals.MOUSEMOTION:
                release = self.item.drag(event.pos, grab_pos=self.grab_pos)
            if release or (self.item is not None and event.type == pygame.locals.MOUSEBUTTONUP):
                # CursorManager.setCursor("fwd")
                if self.grabbing:
                    self.item.release(event.pos)
                    events.remove(event)
                self.grabbing = False
                self.item = None
        return events

class Grabbable:
    """ A Grabbable is an object that can be manipulated by dragging."""
    # When a grabble item is clicked on and dragged, it needs to be added to the grabber object. When the object is dragged around with the mouse, its drag function will be called, allowing custom actions to be done. When the object is released, the release function is called.
    
    def isGrabbable(self):
        return True
    
    def drag(self, pos, grab_pos=None):
        pass
        
    def release(self, pos, grab_pos=None):
        pass
