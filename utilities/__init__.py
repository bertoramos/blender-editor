
bl_info = {
    "name": "Utilities",
    "author": "Alberto Ramos Sanchez",
    "version": (1, 6, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "General Utilities",
    "category": "System",
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
dir = project_folder / Path(".\\utilities\\")
if not dir in sys.path:
    sys.path.append(str(dir))
# end remove

# begin local import: Change to from . import MODULE
import delete_override
import object_properties
import opengl_activate
# end local import: Change to from . import MODULE

# begin remove
import importlib
importlib.reload(delete_override)
importlib.reload(object_properties)
importlib.reload(opengl_activate)
# end remove

operadores = [delete_override, opengl_activate]

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
