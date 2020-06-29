
import bpy
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper
from math import pi

import path

def addGeomCursor(initial_pose):
    bpy.ops.mesh.primitive_cone_add()
    geomCursor = bpy.context.selected_objects[0]
    geomCursor.name = 'geom_cursor'
    geomCursor.location = Vector((initial_pose.x, initial_pose.y, initial_pose.z))
    geomCursor.rotation_euler = Vector((initial_pose.alpha, initial_pose.beta + pi/2, initial_pose.gamma))
    geomCursor.dimensions.xyz = Vector((0.5, 1.0, 1.0))

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    if geomCursor.active_material is None:
        mat = bpy.data.materials.new("Material_cursor")
        geomCursor.active_material = mat
    mat.diffuse_color = Vector((0.0, 1.0, 1.0, 1.0))

    geomCursor.lock_location[0:3] = (False, False, True)
    geomCursor.lock_rotation[0:3] = (True, True, False)
    geomCursor.lock_scale[0:3] = (True, True, True)
    geomCursor.protected = True

    geomCursor.object_type = "GEOMETRIC_CURSOR"

    return geomCursor.name


class GeometricCursor:

    def __init__(self, init_pose):
        self._init_pose = init_pose
        self._current_pose = init_pose
        self._cursor_name = addGeomCursor(self._init_pose)

    def _get_pose(self):
        loc = bpy.data.objects[self._cursor_name].location.xyz
        angle = Vector((bpy.data.objects[self._cursor_name].rotation_euler.x, bpy.data.objects[self._cursor_name].rotation_euler.y, bpy.data.objects[self._cursor_name].rotation_euler.z))
        self._current_pose = path.Pose.fromVector(loc, angle)
        return self._current_pose

    current_pose = property(_get_pose)

    def move_to_origin(self):
        """
        Mueve el cursor a la posicion inicial
        """
        self._current_pose = self._init_pose

    def move(self, new_pose):
        """
        Mueve cursor a una nueva pose
        """
        self._current_pose = new_pose

    def select(self):
        # Seleccionamos solamente el cursor
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[self._cursor_name]
        bpy.data.objects[self._cursor_name].select_set(True)

    def redraw(self):
        bpy.data.objects[self._cursor_name].location = self._current_pose.loc
        bpy.data.objects[self._cursor_name].rotation_euler = Vector((self._current_pose.rotation.x , self._current_pose.rotation.y, self._current_pose.rotation.z))

    def __del__(self):
        cursor = bpy.data.objects[self._cursor_name]
        mesh = cursor.data
        material = cursor.active_material
        bpy.data.objects.remove(cursor, do_unlink=True)
        bpy.data.meshes.remove(mesh, do_unlink=True)
        bpy.data.materials.remove(material, do_unlink=True)
