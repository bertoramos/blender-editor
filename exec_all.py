
import os
from pathlib import Path

project_folder = Path("D:\\Universidad\\MUSIANI\\Robomap\\Fuente\\blender_editor_modificable_plan_editor\\")

filename = project_folder / Path(".\\utilities\\exec.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))

print(project_folder)
filename = project_folder / Path(".\\archibuilder\\exec.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
print(project_folder)

filename = project_folder / Path(".\\robotcontrol\\exec.py")
exec(compile(open(filename).read(), str(filename), 'exec'))

filename = project_folder / Path(".\\filemanager\\exec.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
