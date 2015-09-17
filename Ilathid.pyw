import sys

sys.path += ['.']

from engine.enginemain import mainloop
import traceback
from engine import parameters
import os

# ==== Let py2exe know we use these modules
from ctypes import util

try:
    from OpenGL.platform import win32
except AttributeError:
    pass

sys.path.insert(0, os.path.join('engine', 'enginedata', 'userobjects'))
parameters.setitempath(os.path.join('engine', 'enginedata', 'items'))
parameters.setscreensize((800, 600))
parameters.setslidesize((800, 600))
parameters.slidepos = (0, 0)
parameters.setmovieinterval(15)
parameters.setfullscreen()


from optparse import OptionParser
parser = OptionParser()
parser.add_option("-a", "--age", dest="agename",
                  help="Load another age than default", metavar="FILE")
parser.add_option("-v", "--viewhotspots", dest="viewHotspots",
                  help="Whether to make hotspots visible for debug purposes (true or false)", metavar="HOTSPOTS")
(options, args) = parser.parse_args()

if options.agename is not None:
    parameters.testCustomAge = options.agename

if options.viewHotspots is not None:
    parameters.visualizeHotspots = (options.viewHotspots=="true")
    if parameters.visualizeHotspots:
        print "== Visualising hotspots enabled! =="
    
try:
    mainloop()
except Exception, e:
    sys.stderr.write("!! Uncaught Exception : " + str(e))
    traceback.print_exc(file=sys.stderr)

print "returned from main loop"
