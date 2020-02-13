
import bpy
from mathutils import Vector

from bpy_extras.object_utils import object_data_add
import bmesh

import pose

line_mesh_name = None
arrow_mesh_name = None

def draw_line(p1, p2):
    verts = [p1, p2]
    edges = [(verts.index(p1), verts.index(p2))]

    faces = []

    mesh = bpy.data.meshes.new(name="Line")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(bpy.context, mesh, operator=None)

    global line_mesh_name
    line_mesh_name = mesh.name
    line_obj = bpy.data.objects[line_mesh_name]

    line_obj.lock_location[0:3] = (True, True, True)
    line_obj.lock_rotation[0:3] = (True, True, True)
    line_obj.lock_scale[0:3] = (True, True, True)
    line_obj.hide_select = True

def remove_line():
    line = bpy.data.objects[line_mesh_name]
    bpy.data.objects.remove(line, do_unlink=True)

def update_line(p1, p2):
    global line_mesh_name
    line_mesh = bpy.data.objects[line_mesh_name].data

    bm = bmesh.new()
    bm.from_mesh(line_mesh)

    for i, v in enumerate(bm.verts):
        if i == 1:
            v.co = p2

    bm.to_mesh(line_mesh)
    bm.free()
    line_mesh.update()

def delete_last_line():
    global line_mesh_name
    line_mesh = bpy.data.objects[line_mesh_name]
    bpy.data.objects.remove(line_mesh, do_unlink=True)

def create_arrow(pose):
    bpy.ops.object.empty_add(type='SINGLE_ARROW')
    arrow = bpy.context.selected_objects[0]
    global arrow_mesh_name
    arrow_mesh_name = arrow.name
    arrow.location = pose.loc
    arrow.rotation_euler = pose.rotation

    arrow.lock_location[0:3] = (True, True, True)
    arrow.lock_rotation[0:3] = (True, True, True)
    arrow.lock_scale[0:3] = (True, True, True)
    arrow.hide_select = True
