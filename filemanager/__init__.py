
bl_info = {
    "name": "File Manager",
    "author": "Alberto Ramos Sanchez",
    "version": (1, 6, 0),
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
# Get the real path of the current script
def get_script_folder():
    # Check if the script is being run from a Blender Text Editor or external file
    if bpy.context.space_data.type == 'TEXT_EDITOR':
        script_path = bpy.context.space_data.text.filepath
        if script_path:
            return Path(os.path.realpath(script_path)).parent
        else:
            return None
    else:
        return None

project_folder = Path(get_script_folder())
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
