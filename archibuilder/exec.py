
import bpy
import os
from pathlib import Path

project_folder = Path("D:\\Universidad\\MUSIANI\\Robomap\\Fuente\\blender_editor_modificable_plan_editor\\")
filename = project_folder / Path(".\\archibuilder\\__init__.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
