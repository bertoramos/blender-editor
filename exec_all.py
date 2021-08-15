
import os
from pathlib import Path

project_folder = Path("D:\\alberto\\Universidad\\Robomap\\Fuente\\")

filename = project_folder / Path(".\\blender-editor-plan_editor\\utilities\\exec.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))

filename = project_folder / Path(".\\blender-editor-plan_editor\\archibuilder\\exec.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))

filename = project_folder / Path(".\\blender-editor-plan_editor\\robotcontrol\\exec.py")
exec(compile(open(filename).read(), str(filename), 'exec'))

filename = project_folder / Path(".\\blender-editor-plan_editor\\filemanager\\exec.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
