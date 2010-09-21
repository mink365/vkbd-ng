#!/usr/bin/env python
# ez_setup part(automatic download of setuptools)
from ez_setup import use_setuptools
use_setuptools('0.6c6')
# import setuptools modules
from setuptools import setup
from distutils.command.install import install as _install
from setuptools.command.egg_info import egg_info as _egg_info
# import other modules
import os
import sys
import shutil

### CHECK IF EDJE_CC IS PRESENT IN PATH
edjecc = 0
for check in os.getenv('PATH').split(':'):
   if os.path.isfile(os.path.join(check, 'edje_cc')):
      edjecc = 1

if edjecc != 1:
   print "edje_cc was not found in your PATH. Exitting."
   sys.exit(1)

### CUSTOM CLASSES FOR SETUPTOOLS TO GET RID OF EGG-INFO
class install(_install):
    sub_commands = [('install_lib',     lambda self:False),
                    ('install_headers', lambda self:False),
                    ('install_scripts', lambda self:True),
                    ('install_data',    lambda self:True),
                    ('install_egg_info', lambda self:False)
                   ]

class egg_info(_egg_info):
    def run(self):
        print "Not creating egg_info."

### FUNCTIONS TO RUN BEFORE SETUPTOOLS PART
## Cleanup the tree
def clean():
   # set permissions
   def setperms(fileto, valueof):
      if os.path.isfile(fileto):
         os.chmod(fileto, valueof)

   # remove file
   def removefile(rmfile):
      if os.path.isfile(rmfile):
         os.remove(rmfile)

   # set the permissions
   setperms("data/applications/vkbd-ng.desktop", 0644)
   setperms("data/pixmaps/vkbd.png", 0644)
   setperms("data/pixmaps/vkbd_svg.svg", 0644)

   # remove the edje file
   removefile("data/themes/vkbd.edj")
   
## Build a new edje file
def build():
   # make new edj file
   os.system("edje_cc -v -id data/themes -fd data/themes/images data/themes/vkbd.edc -o data/themes/vkbd.edj")
   os.chmod("data/themes/vkbd.edj", 0644)

### RUN THOSE FUNCTIONS
if sys.argv[1] == "build":
   clean()
   build()
elif sys.argv[1] == "clean":
   clean()

### SETUPTOOLS PART
setup(name = 'Vkbd-ng',
      version = '0.2.0',
      author = 'Mink365',
      author_email = 'mink365@gmail.com',
      description = 'Virtual keyboard based on EFL.Based on vkbd and Keys',
      keywords = 'virtkey keyboard efl enlightenment ecore edje python',
      scripts = ["bin/vkbd-ng"],
      cmdclass = {"install" : install,
                  "egg_info" : egg_info},
      setup_requires = ["python_evas>=0.2.1", "python_ecore>=0.2.1", "python_edje>=0.2.1", "virtkey>=0.01"],
      install_requires = ["python_evas>=0.2.1", "python_ecore>=0.2.1", "python_edje>=0.2.1", "virtkey>=0.01"],
      data_files = [('share/vkbd-ng', ["vkbd/vkbd", "vkbd/cand_panel.py", "vkbd/keyboard.py", "vkbd/toggle_obj.py"]), 
                    ('share/vkbd-ng/themes', ["data/themes/vkbd.edj"]),
                    ('/usr/lib/ibus/', ["vkbd/backend/ibus/ibus-ui-vkbd"]),
                    ('share/pixmaps', ["data/pixmaps/vkbd.png", "data/pixmaps/vkbd_svg.svg"]), 
                    ('share/applications', ["data/applications/vkbd-ng.desktop"]),]
      )
