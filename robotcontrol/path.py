
import bpy
from mathutils import Vector, Euler
from bpy_extras.object_utils import object_data_add
import bmesh

import utils

from math import degrees, pi

import time


def draw_line(p1, p2):
    verts = [p1, p2]
    edges = [(verts.index(p1), verts.index(p2))]

    faces = []

    mesh = bpy.data.meshes.new(name="Line")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(bpy.context, mesh, operator=None)

    line_mesh_name = mesh.name
    line_obj = bpy.data.objects[line_mesh_name]

    line_obj.lock_location[0:3] = (True, True, True)
    line_obj.lock_rotation[0:3] = (True, True, True)
    line_obj.lock_scale[0:3] = (True, True, True)
    line_obj.hide_select = True
    line_obj.protected = True

    return line_mesh_name

def update_line(line_mesh_name, p1, p2):
    line_mesh = bpy.data.objects[line_mesh_name].data

    bm = bmesh.new()
    bm.from_mesh(line_mesh)

    for i, v in enumerate(bm.verts):
        if i == 1:
            v.co = p2

    bm.to_mesh(line_mesh)
    bm.free()
    line_mesh.update()

def create_arrow(pose):
    #bpy.ops.object.empty_add(type='SINGLE_ARROW')
    bpy.ops.object.armature_add()
    arrow = bpy.context.selected_objects[0]

    arrow.rotation_euler = Vector((0, pi/2, 0))
    arrow.scale /= 2

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    arrow_mesh_name = arrow.name
    arrow.location = pose.loc
    arrow.rotation_euler = Vector((pose.rotation.x, pose.rotation.y, pose.rotation.z))

    arrow.lock_location[0:3] = (True, True, True)
    arrow.lock_rotation[0:3] = (True, True, True)
    arrow.lock_scale[0:3] = (True, True, True)
    arrow.protected = True
    arrow.hide_select = True

    return arrow_mesh_name

def update_arrow(arrow_name, pose):
    bpy.data.objects[arrow_name].location = pose.loc
    bpy.data.objects[arrow_name].rotation_euler = pose.rotation

def draw_pose_note(context, name, pose, color, font, font_align):
    # Draw notes
    num_dec = len(str(( bpy.context.scene.TOL - int(bpy.context.scene.TOL) )))-2
    loc = pose.loc
    rot = pose.rotation

    txt = '(x={:0.4f}, y={:0.4f}, z={:0.4f}) [meters]'.format(loc.x, loc.y, loc.z)

    hint_space = 10
    rotation = 0
    loc_note_name = utils.draw_text(context, name, txt, loc, color, hint_space, font, font_align, rotation)

    bpy.data.objects[loc_note_name].lock_location[0:3] = (True, True, True)
    bpy.data.objects[loc_note_name].lock_rotation[0:3] = (True, True, True)
    bpy.data.objects[loc_note_name].lock_scale[0:3] = (True, True, True)
    bpy.data.objects[loc_note_name].protected = True

    txt = '(x={:0.4f}, y={:0.4f}, z={:0.4f}) degrees'.format(degrees(rot.x), degrees(rot.y), degrees(rot.z))

    rot_note_name = utils.draw_text(context, name, txt, loc, color, hint_space, font, font_align, rotation)

    bpy.data.objects[rot_note_name].location += rot.to_matrix().col[2]

    bpy.data.objects[rot_note_name].lock_location[0:3] = (True, True, True)
    bpy.data.objects[rot_note_name].lock_rotation[0:3] = (True, True, True)
    bpy.data.objects[rot_note_name].lock_scale[0:3] = (True, True, True)
    bpy.data.objects[rot_note_name].protected = True

    return loc_note_name, rot_note_name

class Line:

    def __init__(self, fixed_loc, current_loc):
        self._fixed_loc = fixed_loc
        self._current_loc = current_loc
        self._line_name = draw_line(self._fixed_loc, self._current_loc + Vector((bpy.context.scene.TOL, 0, 0)))

    def move(self, loc):
        self._current_loc = loc

    def _get_fixed_loc(self):
        return self._fixed_loc

    def _get_current_loc(self):
        return self._current_loc

    def _set_fixed_loc(self, loc):
        self._fixed_loc = loc

    def _set_current_loc(self, loc):
        self._current_loc = loc

    fixed_loc = property(_get_fixed_loc, _set_fixed_loc)
    current_loc = property(_get_current_loc, _set_current_loc)

    def redraw(self):
        update_line(self._line_name, self.fixed_loc, self.current_loc)

    def __del__(self):
        bpy.data.objects.remove(bpy.data.objects[self._line_name], do_unlink=True)
        bpy.data.meshes.remove(bpy.data.meshes[self._line_name], do_unlink=True)

class Arrow:

    def __init__(self, init_pose):
        self._current_pose = init_pose
        self._arrow_name = create_arrow(self._current_pose)

    def move(self, current_pose):
        self._current_pose = current_pose

    def redraw(self):
        update_arrow(self._arrow_name, self._current_pose)

    def _get_pose(self):
        return self._current_pose

    current_pose = property(_get_pose)

    def __del__(self):
        arrow = bpy.data.objects[self._arrow_name]
        bpy.data.objects.remove(bpy.data.objects[self._arrow_name], do_unlink=True)

class Pose:

    def __init__(self, x, y, z, alpha, beta, gamma):
        self._x = x
        self._y = y
        self._z = z
        self._a = alpha
        self._b = beta
        self._g = gamma

    @classmethod
    def fromVector(cls, loc, angle):
        return cls(loc.x, loc.y, loc.z, angle.x, angle.y, angle.z)

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_z(self):
        return self._z

    def get_a(self):
        return self._a

    def get_b(self):
        return self._b

    def get_g(self):
        return self._g

    def get_loc(self):
        return Vector((self.x, self.y, self.z))

    def get_rotation(self):
        return Euler((self._a, self._b, self._g))

    def __eq__(self, other):
        return abs(self._x - other.x) <= bpy.context.scene.TOL and abs(self._y - other.y) <= bpy.context.scene.TOL and abs(self._z - other.z) <= bpy.context.scene.TOL and \
                abs(self.alpha - other.alpha) <= bpy.context.scene.TOL and abs(self.beta - other.beta) <= bpy.context.scene.TOL and abs(self.gamma - other.gamma) <= bpy.context.scene.TOL

    def __str__(self):
        return "Location(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ") " + \
            "Angle(" + str(self.alpha) + ", " + str(self.beta) + ", " + str(self.gamma) + ") "

    x = property(get_x)
    y = property(get_y)
    z = property(get_z)
    alpha = property(get_a)
    beta = property(get_b)
    gamma = property(get_g)
    loc = property(get_loc)
    rotation = property(get_rotation)

class Action:

    def __init__(self, p0, p1):
        """
        p0: pose 0
        p1: pose 1
        """
        self._p0 = p0
        self._p1 = p1
        self._line = draw_line(p0.loc, p1.loc + Vector((bpy.context.scene.TOL, 0, 0)))
        self._arrow = create_arrow(p1)
        self._timestamp = int(time.time())

        bpy.data.objects[self._line].object_type = "PATH_ELEMENTS"
        bpy.data.objects[self._arrow].object_type = "PATH_ELEMENTS"

        self._first_action = False

        self._loc_note_name = ""
        self._rot_note_name = ""
        self._pre_loc_note_name = ""
        self._pre_rot_note_name = ""

    def set_first_action(self):
        self._first_action = True
        self._pre_arrow = create_arrow(self._p0)

        bpy.data.objects[self._pre_arrow].object_type = "PATH_ELEMENTS"

    def move(self, pose):
        self._p1 = pose
        update_line(self._line, self._p0.loc, self._p1.loc)
        update_arrow(self._arrow, self._p1)

    def draw_annotation(self, context):
        color = Vector((1.0, 1.0, 1.0, 1.0))
        font = 14
        font_align = 'C'
        self._loc_note_name, self._rot_note_name = draw_pose_note(context, "Note_pose", self.p1, color, font, font_align)

        bpy.data.objects[self._loc_note_name].object_type = "PATH_ELEMENTS"
        bpy.data.objects[self._rot_note_name].object_type = "PATH_ELEMENTS"

        if self._first_action:
            self._pre_loc_note_name, self._pre_rot_note_name = draw_pose_note(context, "Pre_note_pose", self.p0, color, font, font_align)

            bpy.data.objects[self._pre_loc_note_name].object_type = "PATH_ELEMENTS"
            bpy.data.objects[self._pre_rot_note_name].object_type = "PATH_ELEMENTS"

    def del_annotation(self):

        if self._loc_note_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[self._loc_note_name], do_unlink=True)
        if self._rot_note_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[self._rot_note_name], do_unlink=True)

        if self._first_action and self._pre_loc_note_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[self._pre_loc_note_name], do_unlink=True)
        if self._first_action and self._pre_rot_note_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[self._pre_rot_note_name], do_unlink=True)


    def get_p0(self):
        return self._p0

    def get_p1(self):
        return self._p1

    def _get_timestamp(self):
        return self._timestamp

    def __del__(self):
        if self._line in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[self._line], do_unlink=True)
        if self._line in bpy.data.meshes:
            bpy.data.meshes.remove(bpy.data.meshes[self._line], do_unlink=True)

        if self._arrow in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[self._arrow], do_unlink=True)
        if self._first_action and self._pre_arrow in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[self._pre_arrow], do_unlink=True)

        self.del_annotation()

    def __str__(self):
        return str(self.p0) + "--" + str(self.p1)

    p0 = property(get_p0)
    p1 = property(get_p1)
    timestamp = property(_get_timestamp)

class Annotation:

    def __init__(self, context, name, action, color, font, font_align):
        self._pose_note_name = draw_pose_note(context, name + "_pose", action.p1, color, font, font_align)

    def __del__(self):
        pose_note = bpy.data.objects[self._pose_note_name]
        bpy.data.objects.remove(pose_note, do_unlink=True)
