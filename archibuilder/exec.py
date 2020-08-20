
import bpy
import os
from pathlib import Path

project_folder = Path("D:\\blender_editor\\")
filename = project_folder / Path(".\\blender-editor\\archibuilder\\__init__.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
