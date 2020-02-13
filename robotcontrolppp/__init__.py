
bl_info = {
    "name": "Robotcontrol",
    "author": "Alberto Ramos Sanchez",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar Panel > Archibuilder Panel",
    "description": "Robot communication module",
    "category": "Development",
}

import os
import sys
import bpy

# For testing
dir = "D:\\Ingenieria Informática\\#4.19.20\\Semestre1\\PE\\Desarrollo\\robotcontrolppp\\"
if not dir in sys.path:
    sys.path.append(dir)

# TODO: Change to from . import MODULE
import addGeomCursor
import pathCreationEditor
import pose
import pathContainer
import pathDrawer
import pathCreatorPanel

# Remove
import importlib
importlib.reload(addGeomCursor)
importlib.reload(pathCreationEditor)
importlib.reload(pose)
importlib.reload(pathContainer)
importlib.reload(pathDrawer)
importlib.reload(pathCreatorPanel)

operadores = [pathCreationEditor]
paneles = [pathCreatorPanel]

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
