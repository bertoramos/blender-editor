
bl_info = {
    "name": "File Manager",
    "author": "Alberto Ramos Sanchez",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar Panel > Options Panel",
    "description": "File manager: export/import scenarios",
    "category": "Import-Export",
    "wiki_url": "https://github.com/bertoramos/blender-editor"
}

import os
import sys
import bpy
from pathlib import Path

# For testing
project_folder = Path("D:\\blender_editor\\")
dir = project_folder / Path(".\\blender-editor\\filemanager\\")
if not dir in sys.path:
    sys.path.append(str(dir))

# TODO: Change to from . import MODULE
# import module
import scene_export

# Remove
import importlib
# importlib.reload(module)
importlib.reload(scene_export)

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
