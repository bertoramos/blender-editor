
bl_info = {
    "name": "Robotcontrol",
    "author": "Alberto Ramos Sanchez",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar Panel > Archibuilder Panel",
    "description": "Robot communication module",
    "category": "Animation",
    "wiki_url": "https://github.com/bertoramos/blender-editor"
}


import bpy

# begin remove
import os
import sys
from pathlib import Path

project_folder = Path("F:\\Universidad\\Robomap\\Desarrollo\\blender-editor\\")

dir = project_folder / Path(".\\robotcontrol\\")
if not dir in sys.path:
    sys.path.append(str(dir))
# end remove

# begin local import: Change to from . import MODULE
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
import connectionHandler
import robotCommunicationOperator
import communicationPanel
import simulationOperator
import calibrationOperator
import data_export
import manualControlOperator
import hudWriter
# end local import: Change to from . import MODULE

# begin remove
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
importlib.reload(simulationOperator)
importlib.reload(calibrationOperator)
importlib.reload(data_export)
importlib.reload(manualControlOperator)
importlib.reload(hudWriter)
# end remove

operadores = [cursorListener, pathEditor, robot, robot_props, robotCommunicationOperator, simulationOperator, calibrationOperator, data_export, manualControlOperator, hudWriter]
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
