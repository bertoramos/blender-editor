
bl_info = {
    "name": "File Manager",
    "author": "Alberto Ramos Sanchez",
    "version": (1, 4, 2),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar Panel > Options Panel",
    "description": "File manager: export/import scenarios",
    "category": "Import-Export",
    "wiki_url": "https://github.com/bertoramos/blender-editor"
}

import bpy

# begin remove
import os
import sys
from pathlib import Path

project_folder = Path("C:\\Users\\alber\\Desktop\\IPS_BLENDER\\Robomap_Blender\\robomap_repo\\blender-editor\\")
dir = project_folder / Path(".\\filemanager\\")
if not dir in sys.path:
    sys.path.append(str(dir))
# end remove

# begin local import: Change to from . import MODULE
import scene_export
# end local import: Change to from . import MODULE

# begin remove
import importlib
# importlib.reload(module)
importlib.reload(scene_export)
# end remove

operadores = [scene_export]
paneles = []

def register():
    for op in operadores:
        op.autoregister()
    for p in paneles:
        p.autoregister()

def unregister():
    for op in operadores:
        op.autounregister()
    for p in paneles:
        p.autounregister()

if __name__=='__main__':
    register()
