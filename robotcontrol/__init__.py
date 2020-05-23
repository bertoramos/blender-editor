
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
dir = "D:\\alberto\\TFT\\desarrollo\\blender-editor\\robotcontrol\\"
if not dir in sys.path:
    sys.path.append(dir)

# TODO: Change to from . import MODULE
import geomCursor
import path
import pathContainer
import cursorListener
import pathEditor
import pathEditorPanel
import overlap_check
import collision_detection
import utils
import robot
import robot_props
import robot_panel
#import communicationOperator
#import connection_handler
import connectionHandler
import robotCommunicationOperator
import communicationPanel

# Remove
import importlib
importlib.reload(geomCursor)
importlib.reload(path)
importlib.reload(pathContainer)
importlib.reload(cursorListener)
importlib.reload(pathEditor)
importlib.reload(pathEditorPanel)
importlib.reload(overlap_check)
importlib.reload(collision_detection)
importlib.reload(utils)
importlib.reload(robot)
importlib.reload(robot_props)
importlib.reload(robot_panel)
importlib.reload(robotCommunicationOperator)
importlib.reload(connectionHandler)
importlib.reload(communicationPanel)

operadores = [cursorListener, pathEditor, robot, robot_props, robotCommunicationOperator]
paneles = [robot_panel, pathEditorPanel, communicationPanel]

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
