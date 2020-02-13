
bl_info = {
    "name": "Archibuilder",
    "author": "Alberto Ramos Sanchez",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar Panel > Archibuilder Panel",
    "description": "Scene editor",
    "category": "Scene",
}

import os
import sys
import bpy

# For testing
dir = "D:\\PE\\Desarrollo\\archibuilder\\"
if not dir in sys.path:
    sys.path.append(dir)

# TODO: Change to from . import MODULE
import wallOperator
import obstacleOperator
import envBuilderPanel
import decoratePanel
import geom_math
import ceilOperator
import hideAreaOperator
import beaconOperator

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

operadores = [wallOperator, obstacleOperator, ceilOperator, hideAreaOperator, beaconOperator]

paneles = [envBuilderPanel, decoratePanel]

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
