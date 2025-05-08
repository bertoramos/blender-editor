
import bpy
import os
from pathlib import Path
# Get the real path of the current script
def get_script_folder():
    # Check if the script is being run from a Blender Text Editor or external file
    if bpy.context.space_data.type == 'TEXT_EDITOR':
        script_path = bpy.context.space_data.text.filepath
        if script_path:
            return Path(os.path.realpath(script_path)).parent
        else:
            return None
    else:
        return None

project_folder = Path(get_script_folder())
filename = project_folder / Path(".\\filemanager\\__init__.py")
exec(compile(open(str(filename)).read(), str(filename), 'exec'))
