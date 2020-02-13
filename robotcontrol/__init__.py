
bl_info = {
    "name": "Robotcontrol",
    "author": "Alberto Ramos Sanchez",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar Panel > Archibuilder Panel",
    "description": "Robot communication module",
    "category": "Animation",
}

import os
import sys
import bpy

# For testing
dir = "D:\\PE\\Desarrollo\\robotcontrol\\"
if not dir in sys.path:
    sys.path.append(dir)

# TODO: Change to from . import MODULE
import geomCursor
import path
import pathContainer
import cursorListener
import pathEditor
import pathEditorPanel
import collapse_check
import utils

# Remove
import importlib
importlib.reload(geomCursor)
importlib.reload(path)
importlib.reload(pathContainer)
importlib.reload(cursorListener)
importlib.reload(pathEditor)
importlib.reload(pathEditorPanel)
importlib.reload(collapse_check)
importlib.reload(utils)

operadores = [cursorListener, pathEditor]
paneles = [pathEditorPanel]

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
