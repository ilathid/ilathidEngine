from distutils.core import setup, Extension

module1 = Extension('colorspace',
                    # include_dirs = ['/usr/local/include'],
                    # library_dirs = ['/usr/local/lib'],
                    sources = ['engine/extensions/colorspace.c'])

setup (name = 'PackageName',
       version = '1.0',
       description = 'This is an exceedingly simple extension to speed up a bif for loop',
       ext_modules = [module1])
