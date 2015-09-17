# A setup script showing how to extend py2exe.
#
# In this case, the py2exe command is subclassed to create an installation
# script for InnoSetup, which can be compiled with the InnoSetup compiler
# to a single file windows installer.
#
# By default, the installer will be created as dist\Output\setup.exe.

#@PyDevCodeAnalysisIgnore

from distutils.core import setup
import py2exe
import sys

# Those are NOT system DLLs to be ignore, manually fix py2exe's stupidity
origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
    if os.path.basename(pathname).lower() in ["sdl_ttf.dll", "libogg-0.dll"]:
        return 0
    return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

################################################################
# arguments for the setup() call

Ilathid = dict(
    script = "Ilathid.pyw",
    icon_resources = [(1,"mandil.ico")],
    dest_base = r"prog\Ilathid")
    

engine = dict(
    script = "engine\\enginemain.py",
    dest_base = r"prog\engine")

zipfile = r"lib\shardlib"

# py2exe has a hard time with OpenGL so we exclude it and then bundle it manually
options = {"py2exe": {"compressed": 1,
                      "optimize": 2,
                      "includes": ["ctypes", "logging", "pygame"],
                      "excludes": ["OpenGL"]}}

################################################################
import os,glob

class InnoScript:
    def __init__(self,
                 name,
                 lib_dir,
                 dist_dir,
                 windows_exe_files = [],
                 lib_files = [],
                 version = "1.0"):
        self.lib_dir = lib_dir
        self.dist_dir = dist_dir
        if not self.dist_dir[-1] in "\\/":
            self.dist_dir += "\\"
        self.name = name
        self.version = version
        self.windows_exe_files = [self.chop(p) for p in windows_exe_files]
        self.lib_files = [self.chop(p) for p in lib_files]
        self.data_files=[glob.glob("ilathid_low.gif"),glob.glob("Dni\\images\\*"), glob.glob("Dni\\movies\\*"),
                  glob.glob("Dni\\music\\*"), glob.glob("Dni\\slides\\*"),
                  glob.glob("Dni\\text/*"), glob.glob("engine\\enginedata\\cursors\\*")]
        

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]
    
    def create(self, pathname="dist\\Ilathid.iss"):
        self.pathname = pathname
        ofi = self.file = open(pathname, "w")
        print >> ofi, "; WARNING: This script has been created by py2exe. Changes to this script"
        print >> ofi, "; will be overwritten the next time py2exe is run!"
        print >> ofi, r"[Languages]"
        print >> ofi, r'Name: en; MessagesFile: "compiler:Default.isl"'
        print >> ofi, r'Name: fr; MessagesFile: "compiler:Languages\French.isl"'
        #print >> ofi, r'Name: sp; MessagesFile: "compiler:Languages\SpanishStd-5-5.1.11.isl"'
        print >> ofi, r'Name: ge; MessagesFile: "compiler:Languages\German.isl"'
        #print >> ofi, r'Name: cr; MessagesFile: "compiler:Languages\Croatian-5-5.1.11.isl"'
        print >> ofi, r"[Messages]"
        print >> ofi, r"en.BeveledLabel=English"
        print >> ofi, r"fr.BeveledLabel=French"
        #print >> ofi, r"sp.BeveledLabel=Spanish"
        print >> ofi, r"ge.BeveledLabel=German"
        #print >> ofi, r"cr.BeveledLabel=Croatian"
        print >> ofi, r"[Setup]"
        print >> ofi, r"AppName=%s" % self.name
        print >> ofi, r"AppVerName=%s %s" % (self.name, self.version)
        print >> ofi, r"DefaultDirName={pf}\%s" % self.name
        print >> ofi, r"DefaultGroupName=%s" % self.name
        print >> ofi, r"Compression=lzma/max"
        print >> ofi, r"SolidCompression=yes"
        print >> ofi, r'SetupIconFile="..\Ilathid.ico"'
        print >> ofi

        print >> ofi, r"[Files]"
        print >> ofi, r'Source: "..\engine\enginedata\*"; DestDir: "{app}\prog\engine\enginedata"; Flags: ignoreversion recursesubdirs'
        print >> ofi, r'Source: "..\data\*"; DestDir: "{app}\prog\data"; Flags: ignoreversion recursesubdirs'
        for path in self.windows_exe_files + self.lib_files:
            print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))
        print >> ofi, r'Source: "..\Readme.txt"; DestName: "Readme.txt"; DestDir: "{app}\prog"; Languages: en; Flags: isreadme'
        print >> ofi, r'Source: "..\ReadmeFR.txt"; DestName: "Lisezmoi.txt"; DestDir: "{app}\prog"; Languages: fr; Flags: isreadme'
        print >> ofi, r'Source: "..\ReadmeSP.txt"; DestName: "Leame.txt"; DestDir: "{app}\prog"; Languages: sp; Flags: isreadme'
        print >> ofi, r'Source: "..\ReadmeGE.txt"; DestName: "Liesmich.txt"; DestDir: "{app}\prog"; Languages: ge; Flags: isreadme'
        print >> ofi, r'Source: "..\ReadmeCR.txt"; DestName: "Citanjemene.txt"; DestDir: "{app}\prog"; Languages: cr; Flags: isreadme'
        print >> ofi

        print >> ofi, r"[Icons]"
        for path in self.windows_exe_files:
            print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\%s"; WorkingDir: "{app}\%s"' % (self.name, path,os.path.dirname(path))
        print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"' % self.name

    def compile(self):
        try:
            import ctypes
        except ImportError:
            try:
                import win32api
            except ImportError:
                import os
                os.startfile(self.pathname)
            else:
                print "Ok, using win32api."
                win32api.ShellExecute(0, "compile",
                                                self.pathname,
                                                None,
                                                None,
                                                0)
        else:
            print "Cool, you have ctypes installed."
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                                                      self.pathname,
                                                      None,
                                                      None,
                                                      0)
            if res < 32:
                raise RuntimeError, "ShellExecute failed, error %d" % res


################################################################

from py2exe.build_exe import py2exe
import sys,os
newdirname = os.path.realpath(os.path.dirname(sys.argv[0]))
sys.path.append(os.path.join(newdirname, 'engine'))

class build_installer(py2exe):
    # This class first builds the exe file(s), then creates a Windows installer.
    # You need InnoSetup for it.
    def run(self):
        # First, let py2exe do it's work.
        py2exe.run(self)

        lib_dir = self.lib_dir
        dist_dir = self.dist_dir
        
        
        # create the Installer, using the files py2exe has created.
        script = InnoScript("Ilathid",
                            lib_dir,
                            dist_dir,
                            self.windows_exe_files,
                            self.lib_files)
        print "*** creating the inno setup script***"
        script.create()
        print "*** compiling the inno setup script***"
        script.compile()
        # Note: By default the final setup.exe will be in an Output subdirectory.

################################################################

setup(
    options = options,
    # The lib directory contains everything except the executables and the python dll.
    zipfile = zipfile,
    windows = [Ilathid],
    #console = [engine],
    # use out build_installer class as extended py2exe build command
    cmdclass = {"py2exe": build_installer},
    )
