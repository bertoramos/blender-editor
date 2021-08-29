
import bpy
import os
from pathlib import Path

project_folder = Path("E:\\Robomap\\blender-editor-master\\")
filename = project_folder / Path(".\\filemanager\\__init__.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
