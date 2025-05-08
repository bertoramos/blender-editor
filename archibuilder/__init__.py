
bl_info = {
    "name": "Archibuilder",
    "author": "Alberto Ramos Sanchez",
    "version": (1, 6, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar Panel > Archibuilder Panel",
    "description": "Scene editor",
    "category": "Scene",
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
dir = project_folder / Path(".\\archibuilder\\")
if not dir in sys.path:
    sys.path.append(str(dir))
# end remove

# begin local import: Change to from . import MODULE
import wallOperator
import obstacleOperator
import envBuilderPanel
import decoratePanel
import geom_math
import ceilOperator
import hideAreaOperator
import beaconOperator
import beaconPanel
import hideScenarioOperator
import selectScenarioOperator
import selectedObjInfoPanel
# end local import: Change to from . import MODULE

# begin remove
import importlib
importlib.reload(wallOperator)
importlib.reload(envBuilderPanel)
importlib.reload(decoratePanel)
importlib.reload(obstacleOperator)
importlib.reload(geom_math)
importlib.reload(ceilOperator)
importlib.reload(hideAreaOperator)
importlib.reload(beaconOperator)
importlib.reload(beaconPanel)
importlib.reload(hideScenarioOperator)
importlib.reload(selectScenarioOperator)
importlib.reload(selectedObjInfoPanel)
# end remove

operadores = [wallOperator, obstacleOperator, ceilOperator, hideAreaOperator, beaconOperator, hideScenarioOperator, selectScenarioOperator]

paneles = [envBuilderPanel, decoratePanel, beaconPanel, selectedObjInfoPanel]

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
