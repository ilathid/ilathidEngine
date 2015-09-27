from distutils.core import setup
import py2exe
import os

origIsSystemDLL = py2exe.build_exe.isSystemDLL # save the orginal before we edit it
def isSystemDLL(pathname):
    # checks if the freetype and ogg dll files are being included
    if os.path.basename(pathname).lower() in ("libfreetype-6.dll", "libogg-0.dll", "sdl_ttf.dll"):
            return 0
    return origIsSystemDLL(pathname) # return the orginal function
py2exe.build_exe.isSystemDLL = isSystemDLL # override the default function with this one

# equivalent command line with options is:
# python setup.py py2exe --compressed --bundle-files=2 --dist-dir="my/dist/dir" --dll-excludes="w9xpopen.exe"
options = {'py2exe': {
           'compressed':1,  
           'bundle_files': 2, 
           'excludes': ["OpenGL", "test_engine"],
           'dist_dir': "exebuild",
           "includes": ["ctypes", "logging"],
           'dll_excludes': ['w9xpopen.exe']
           }}
setup(
  windows=[
    {
      "script": 'runner.py',
      "icon_resources": [(1, "mandil.ico")]
    }
  ],
  options=options
)