import re
# TODO:
""" Gamestate changes:
- all gamestate variables must be given a default.
- gamestate is a globally accessable module (classmethods)
- Types of gamestate variables should be T/F, Numeric or String. (for ease of saving)

defaults are set like this, perhaps:
defaults = {}
defaults["space.age2.people"] = 45.6
defaults["space.age2.food"] = True
defaults["game.some_option"] = "option_name"

and then in the game initialization:
from ... import defaults
Gamestate.loadDefaults(defaults)

example of test:
from Engine.Gamestate import Gamestate as G
defaults = {'t1':5,'t2':True,'t3':'string','t4':False}
G.loadDefaults(defaults)
print "t1: " + str(G.getVar('t1'))
print "t3: " + G.getVar('t3')
print "t2 and t4: " + str(G.evaluate('t2 and t4'))
print "t2 or t4: " + str(G.evaluate('t2 or t4'))
"""

class Gamestate:
    pattern = re.compile("(and|or|not)")

    vals = {}
    defaults = {}
    ticket = 0
    
    @classmethod
    def setVar(self, var, value):
        if var in Gamestate.defaults.keys():
            Gamestate.vals[var] = value
        else:
            raise Exception("Must initialize key: " + var)
        Gamestate.ticket += 1
    
    @classmethod
    def getVar(self, var):
        #print "get " + var
        if var in Gamestate.defaults.keys():
            if var in Gamestate.vals.keys():
                return Gamestate.vals[var]
            else:
                return Gamestate.defaults[var]
        else:
            raise Exception("Must initialize key: " + var)

    @classmethod
    def loadDefaults(self, defaults):
        """ defaults: dict of key-value pairs """
        Gamestate.defaults = defaults


    # TODO: We talked about executing the string as python code somehow. For now it is just and, or, not and variable names
    @classmethod
    def evaluate(self, string):
        #print "Eval " + string
        groups = Gamestate.pattern.split(string)
        #print groups
        val = None
        op = None
        for group in groups:
            if group.strip() == "and":
                op = "and"
            elif group.strip() == "or":
                op = "or"
            elif group.strip() == "not":
                op = "not"
            else:
                if op is None:
                    val = group.strip()
                else:
                    if op == "and":
                        val = Gamestate.getVar(val) and Gamestate.getVar(group.strip())
                    if op == "or":
                        val = Gamestate.getVar(val) or Gamestate.getVar(group.strip())
                    if op == "not":
                        val = not Gamestate.getVar(group.strip())
        if val is None:
            val = False
        if op is None:
            val = Gamestate.getVar(val.strip())
        return val
