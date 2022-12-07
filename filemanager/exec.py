
import bpy
import os
from pathlib import Path

project_folder = Path("C:\\Users\\alber\\Desktop\\IPS_BLENDER\\Robomap_Blender\\robomap_repo\\blender-editor\\")
filename = project_folder / Path(".\\filemanager\\__init__.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
