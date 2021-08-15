
import bpy
import os
from pathlib import Path

project_folder = Path("D:\\alberto\\Universidad\\Robomap\\Fuente\\")
filename = project_folder / Path(".\\blender-editor-plan_editor\\filemanager\\__init__.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
