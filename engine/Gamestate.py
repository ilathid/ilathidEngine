# Gamestate

# Gamestate Condition Tree
# This is used to store gamestate logic, to spare on trivial callback functions
# lightImage.setCondition(GSAnd(GSOr("SomeArea.door1_locked", "SomeArea.door1_broken"), GSNot("PowerAge.PowerArea.isPoweredDown")))
class GSCondNode:
    nodes = []
    def __init__(self, *nodes):
        self.nodes = []
        for node in nodes:
            if isinstance(node, str):
                self.nodes.append(GSCondLeaf(node))
            else:
                self.nodes.append(node)

class GSNand(GSCondNode):   
    def evaluate(self, gamestate):
        for node in self.nodes:
            if node.evaluate(gamestate): return False
        return True

class GSNot(GSNand):
    pass

class GSAnd(GSCondNode):
    def evaluate(self, gamestate):
        for node in self.nodes:
            if not node.evaluate(gamestate): return False
        return True
        
class GSOr(GSCondNode):
    def evaluate(self, gamestate):
        for node in self.nodes:
            if node.evaluate(gamestate): return True
        return False



class GSCond:
    node = ""
    def __init__(self, node):
        self.node = node

class GSCondEquals(GSCond):
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        
    def evaluate(self, gamestate):
        val1 = gamestate.getState(self.node1)
        return val1 == self.node2
        
class GSCondEqualsNode(GSCond):
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        
    def evaluate(self, gamestate):
        val1 = gamestate.getState(self.node1)
        val2 = gamestate.getState(self.node2)
        return val1 == val2

class GSCondLeaf(GSCond):
    def evaluate(self, gamestate):
        return gamestate.getState(self.node) # Just a true/false get

# Idea:
# 1. Gamestate variables are:
#    T/F
#    Numeric
#    String
# 2. Unset variables are None
# 3. Whoever USES a gamestate variable must also know its default value, e.g. the default exists only for that context and is set in that context.


# e.g.
#
# year = spaceAge.getState("computer_state.year")
# if year == None: year = 1985
# draw to screen: image of 1985

# Also:
# spaceAge = gamestate.getState("SpaceAge")
# gamestate.getState("SpaceAge.var1")
# is equal to
# spaceAge.getState("var1")

# This way an age need not know anything about another age.

class Gamestate:
    name = ""
    elements = {} # Other Gamestate elements, or key:values
    ticket = 0    # To check if anything has modified this gamestate
    
    def __init__(self, name):
        self.name = name
    
    def getState(self, expression):
        return self.getList(expression.split("."))
    
    def getList(self, parts):        
        # First find if this gamestate name is in the parts
        while self.name in parts:
            parts.pop(0)
        
        if len(parts) == 0:
            return None
        
        p1 = parts.pop(0)
        if p1 in self.elements:
            it = self.elements[p1]
            if isinstance(it, Gamestate): # this is becoming a habit...
                return it.getList(parts)
            else:
                return it
        return None
        
    def setState(self, parts, value):
        self.setList(parts.split("."), value)
        
    def setList(self, parts, value):
        # First find if this gamestate name is in the parts
        while self.name in parts:
            parts.pop(0)
        
        p1 = parts.pop(0)
        if len(parts) > 0:
            if not p1 in self.elements or not isinstance(self.elements[p1], Gamestate):
                self.elements[p1] = Gamestate(p1)
            self.elements[p1].setList(parts, value)
        else:
            self.elements[p1] = value
        
        # Update the ticket number
        self.ticket = (self.ticket + 1) % (1 << 16)
    
    def getTicket(self):
        return self.ticket
    
    def hasChanged(self, ticket):
        return ticket != self.ticket
            
gs = Gamestate("game")
gs.setState("light_on", True)
gs.setState("light_num", 5)
gs.setState("Area1.foggy", True)
# print gs
# print gs.elements
c1 = GSAnd("light_on", GSNot("Area1.sunny"))
print c1.evaluate(gs)
c2 = GSAnd("light_on", GSCondEquals("light_num", 4))
print c2.evaluate(gs)
c2 = GSAnd("light_on", GSCondEquals("light_num", 5))
print c2.evaluate(gs)
c2 = GSAnd("distant_age.light_on", GSCondEquals("light_num", 5))
print c2.evaluate(gs)
gs.setState("distant_age.light_on", True)
print c2.evaluate(gs)
