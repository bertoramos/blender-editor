
bl_info = {
    "name": "Archibuilder",
    "author": "Alberto Ramos Sanchez",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar Panel > Archibuilder Panel",
    "description": "Scene editor",
    "category": "Scene",
    "wiki_url": "https://github.com/bertoramos/blender-editor"
}

import os
import sys
import bpy
from pathlib import Path

# For testing
project_folder = Path("D:\\blender_editor\\")
dir = project_folder / Path(".\\blender-editor\\archibuilder\\")
if not dir in sys.path:
    sys.path.append(str(dir))

# TODO: Change to from . import MODULE
import annotation_update
import wallOperator
import obstacleOperator
import envBuilderPanel
import decoratePanel
import geom_math
import ceilOperator
import hideAreaOperator
import beaconOperator
import beaconPanel

# Remove
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
importlib.reload(annotation_update)

operadores = [wallOperator, obstacleOperator, ceilOperator, hideAreaOperator, beaconOperator, annotation_update]

paneles = [envBuilderPanel, decoratePanel, beaconPanel]

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
