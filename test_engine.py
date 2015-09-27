#!/usr/bin/env python
# import Engine

import sys
sys.path += ['.']

from Engine.Engine import Engine
from Engine.Parameters import Parameters
from Engine.Lib.IlathidInterface import IlathidInterface
from Engine.Gamestate import Gamestate
from DniDefaults import defaults

# Set a bunch of parameters
Parameters.grab_view = True
Parameters.lock_view = False
Parameters.fullscreen = True
Parameters.cursor_scale = 1
Parameters.draw_hotspots = False
Parameters.slide_size_2d = (800,600)
#Parameters.slide_2d_padding = (10,10,10,10)

# Parameters.vfov = 30.0 # 53 deg horizontal fov
Parameters.vfov = 53.0 # 53 deg vertical fov = 94.3 horizontal
# Parameters.vfov = 175.0

#Parameters.max_fps = 45
Parameters.II_bar_color = (.6,.55,.65, .9)

# Load Gamestate Defaults
Gamestate.loadDefaults(defaults)

# The game engine
E = Engine()

# Make and attatch the interface layer extension
II = IlathidInterface(E)
E.attatchLayer(II)

# E.gotoSlide("TestAge.testSlide")
# E.gotoSlide("ZenGarden.ZenGarden1")
E.gotoAge("ZenGarden")
# E.gotoSlide("KopakanAge.KopakanAge1")
# E.gotoSlide("ShellAge.Center of Bridge")
# E.gotoSlide("Dni.dni1")
# E.gotoSlide("Dni.dni1")

E.run()
