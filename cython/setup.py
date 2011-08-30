from distutils.core import setup, Extension

ext_module = Extension('ext',
                   sources = ['ext.c'])

setup(name = 'Ext',
      version = '0.1',
      description = 'This is a extension demo',
      ext_modules = [ext_module])

