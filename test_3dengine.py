#!/usr/bin/env python
# import Engine
from Engine.Engine import Engine
from Engine.Parameters import Parameters
from Lib.IlathidInterface import IlathidInterface
from Engine.Gamestate import Gamestate

# Set a bunch of parameters
Parameters.grab_view = True
Parameters.lock_view = False
Parameters.fullscreen = True
Parameters.cursor_scale = 1
Parameters.draw_hotspots = False
Parameters.slide_size_2d = (800,600)
#Parameters.slide_2d_padding = (10,10,10,10)

#Parameters.max_fps = 45
Parameters.II_bar_color = (.6,.55,.65, .9)

# Load Gamestate Defaults
#from DniDefaults import defaults
#Gamestate.loadDefaults(defaults)

# The game engine
E = Engine()

# Make and attatch the interface layer extension
II = IlathidInterface()
E.attatchLayer(II)

E.gotoSlide("TestAge.testSlide")
#E.gotoSlide("ZenGarden.ZenGarden1")
#E.gotoSlide("Dni.dni1")
#E.gotoSlide("Dni.dni37")

E.run()
