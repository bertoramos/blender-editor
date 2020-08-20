
import os
from pathlib import Path

project_folder = Path("D:\\blender_editor\\")

filename = project_folder / Path(".\\blender-editor\\utilities\\exec.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))

filename = project_folder / Path(".\\blender-editor\\archibuilder\\exec.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))

filename = project_folder / Path(".\\blender-editor\\robotcontrol\\exec.py")
exec(compile(open(filename).read(), str(filename), 'exec'))

filename = project_folder / Path(".\\blender-editor\\filemanager\\exec.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
