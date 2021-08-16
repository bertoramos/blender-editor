
import bpy
from bpy_extras.io_utils import ExportHelper

from pathlib import Path
import os

import json

# begin local import: Change to from . import MODULE
import pathContainer as pc
import path
# end local import: Change to from . import MODULE

def autoregister():
    global classes
    classes = [ExportPosesOperator, LoadPosesOperator]

    for c in classes:
        bpy.utils.register_class(c)

def autounregister():
    global classes

    for c in classes:
        bpy.utils.unregister_class(c)

def parse_data(json_poses):
    try:
        poses = []
        for p in json_poses['poses']:
            poses.append(path.Pose(p['x'], p['y'], p['z'], p['rx'], p['ry'], p['rz']))
    except Exception:
        return False
    return poses

def read_poses(path, name):
    if not (path / name).is_file():
        return None

    with open(path / name, 'r') as outfile:
        data = json.load(outfile)
        return data
    return None

def export_poses(path, name, data_poses):
    if not os.access(path, os.W_OK):
        return False

    with open(path / name, 'w') as outfile:
        json.dump(data_poses, outfile)
        return True
    return False

class LoadPosesOperator(bpy.types.Operator, ExportHelper):
    bl_idname = "export.load_poses_operator"
    bl_label = "Load poses from file"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    def execute(self, context):
        # filepath
        filepath_str = self.filepath
        filepath = Path(filepath_str)
        path = filepath.parent
        name = Path(filepath.name)

        if ( json_poses := read_poses(path, name) ) is None:
            self.report({'ERROR'}, f"Cannot read {str(path / name)}")
        else:
            self.report({'INFO'}, f"Path loaded from {str(path / name)}")

        if not (poses := parse_data(json_poses) ):
            self.report({'ERROR'}, "Error while parsing poses. Check file content.")
        else:
            pc.PathContainer().loadPoses(poses)

        return {'FINISHED'}


class ExportPosesOperator(bpy.types.Operator, ExportHelper):
    bl_idname = "export.export_poses_operator"
    bl_label = "Export poses to file"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    def execute(self, context):
        # poses
        poses = pc.PathContainer().poses
        json_poses = {'num_poses': len(poses),
                      'poses': []}
        for p in poses:
            json_poses['poses'].append({
                'x': p.x,
                'y': p.y,
                'z': p.z,
                'rx': p.alpha,
                'ry': p.beta,
                'rz': p.gamma,
            })

        # filepath
        filepath_str = self.filepath
        filepath = Path(filepath_str)
        path = filepath.parent
        name = Path(filepath.name)

        if not export_poses(path, name, json_poses):
            self.report({'ERROR'}, f"Cannot write in {str(path / name)}")
        else:
            self.report({'INFO'}, f"Exported path in {str(path / name)}")
        return {'FINISHED'}
