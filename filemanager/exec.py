
import bpy
import os
from pathlib import Path

project_folder = Path("F:\\Universidad\\Robomap\\Desarrollo\\blender-editor\\")
filename = project_folder / Path(".\\filemanager\\__init__.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
