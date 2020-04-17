
import bpy
from mathutils import Vector, Euler
import bmesh

import utils
import overlap_check

def create_point(loc):
    bpy.ops.object.empty_add(location=loc)
    return bpy.context.active_object

def create_bmesh(obj):
    tmp = obj.copy()
    tmp.data = obj.data.copy()
    bpy.context.scene.collection.objects.link(tmp)

    [o.select_set(False) for o in bpy.data.objects]
    tmp.select_set(True)
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
    tmp.select_set(False)

    bm = bmesh.new()
    bm.from_mesh(tmp.data)
    bm.transform(tmp.matrix_world)

    bpy.data.objects.remove(tmp, do_unlink=True)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    return bm

def create_edge_pairs(bm, loc, pos):
    verts = [(v.co.xyz - loc) for v in bm.verts] # Normalized vertex to center
    edges = [(e.verts[0].co.xyz - loc, e.verts[1].co.xyz - loc) for e in bm.edges]
    edges_pairs = []
    for e in edges:
        pair = verts.index(e[0]), verts.index(e[1])
        edges_pairs.append(pair)
    verts = [v + pos for v in verts] # Translate to pos
    return verts, edges_pairs

def generate_area(robot_obj, pos0, pos1):
    """
    Input:
        - robot_obj : object that represents robot
        - loc0 (Vector) : start location of path to check
        - loc1 (Vector) : end location of path to check
    returns:
        - name of mesh created
    """
    offset = (pos1.loc - pos0.loc)

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = robot_obj
    robot_obj.select_set(True)

    bpy.ops.object.duplicate()

    copy_obj = bpy.context.active_object
    copy_obj.location = pos0.loc

    bpy.ops.object.editmode_toggle()

    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False},
                                     TRANSFORM_OT_translate={"value":offset[:],
                                                             "orient_type":'NORMAL',
                                                             "orient_matrix":((1, 0, 0),
                                                                              (0, 1, 0),
                                                                              (0, 0, 1)),
                                                             "orient_matrix_type":'NORMAL',
                                                             "constraint_axis":(False, False, True),
                                                             "mirror":False, "use_proportional_edit":False,
                                                             "proportional_edit_falloff":'SMOOTH',
                                                             "proportional_size":1,
                                                             "use_proportional_connected":False,
                                                             "use_proportional_projected":False,
                                                             "snap":False,
                                                             "snap_target":'CLOSEST',
                                                             "snap_point":(0, 0, 0),
                                                             "snap_align":False,
                                                             "snap_normal":(0, 0, 0),
                                                             "gpencil_strokes":False,
                                                             "cursor_transform":False,
                                                             "texture_space":False,
                                                             "remove_on_cancel":False,
                                                             "release_confirm":False,
                                                             "use_accurate":False})


    bpy.ops.mesh.extrude_edges_move(MESH_OT_extrude_edges_indiv={"use_normal_flip":False, "mirror":False},
                                    TRANSFORM_OT_translate={"value":(-offset)[:],
                                                            "orient_type":'GLOBAL',
                                                            "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                                            "orient_matrix_type":'GLOBAL',
                                                            "constraint_axis":(False, False, False),
                                                            "mirror":False,
                                                            "use_proportional_edit":False,
                                                            "proportional_edit_falloff":'SMOOTH',
                                                            "proportional_size":1,
                                                            "use_proportional_connected":False,
                                                            "use_proportional_projected":False,
                                                            "snap":False,
                                                            "snap_target":'CLOSEST',
                                                            "snap_point":(0, 0, 0),
                                                            "snap_align":False,
                                                            "snap_normal":(0, 0, 0),
                                                            "gpencil_strokes":False,
                                                            "cursor_transform":False,
                                                            "texture_space":False,
                                                            "remove_on_cancel":False,
                                                            "release_confirm":False,
                                                            "use_accurate":False})

    bpy.ops.object.editmode_toggle()

    return copy_obj

def check_collision(robot_obj, pos0, pos1, objects):
    """
    robot_obj : object that represents robot
    loc0 : start location
    loc1 : end location
    objects : object to check collition
    """
    area = generate_area(robot_obj, pos0, pos1)
    bmarea = create_bmesh(area)
    overlap = False
    for obj, (f1, f2, f3) in objects:
        bmobj = create_bmesh(obj)
        if overlap_check.check_overlap(bmobj, bmarea, f1,f2,f3):
            print(obj.name)
            overlap = True
        bmobj.free()
        if overlap:
            break
    bmarea.free()
    bpy.data.objects.remove(area, do_unlink=True)
    return overlap
