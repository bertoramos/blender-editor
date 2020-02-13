
bl_info = {
    "name": "Utilities",
    "author": "Alberto Ramos Sanchez",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "",
    "description": "General Utilities",
    "category": "System",
}

import os
import sys
import bpy

# For testing
dir = "D:\\PE\\Desarrollo\\utilities\\"
if not dir in sys.path:
    sys.path.append(dir)

# TODO: Change to from . import MODULE
import delete_override
import object_properties
import opengl_activate

# Remove
import importlib
importlib.reload(delete_override)
importlib.reload(object_properties)
importlib.reload(opengl_activate)

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
