
import bpy
import os
from pathlib import Path

project_folder = Path("D:\\blender_editor\\")
filename = project_folder / Path(".\\blender-editor\\filemanager\\__init__.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
