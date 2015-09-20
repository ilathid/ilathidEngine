from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
            Extension("Media",
                 ["Media.pyx", "MediaPlayer.c", "timehelper.c", "alibrary.c", "packetbuffer.c"],
                 language='c',
                 include_dirs=[r'.', '/usr/local/include'],
                 library_dirs=[r'.', '/usr/local/lib'],
                 extra_compile_args=['-g2'],
                 libraries=['avformat', 'avutil', 'rt', 'avcodec', 'swscale', 'ao', 'pthread']
                 )]

setup(
    name = 'Media',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
