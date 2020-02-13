
import bpy
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper

def addGeomCursor(initial_pose):
    bpy.ops.mesh.primitive_cone_add()
    geomCursor = bpy.context.selected_objects[0]
    geomCursor.name = 'geom_cursor'
    geomCursor.location = Vector((initial_pose.x, initial_pose.y, initial_pose.z))
    geomCursor.rotation_euler = Vector((initial_pose.alpha, initial_pose.beta, initial_pose.gamma))

    geomCursor.dimensions.xyz = Vector((0.5, 1.0, 1.0))
    if geomCursor.active_material is None:
        mat = bpy.data.materials.new("Material_cursor")
        geomCursor.active_material = mat
    mat.diffuse_color = Vector((0.0, 1.0, 1.0, 1.0))

    return geomCursor.name
