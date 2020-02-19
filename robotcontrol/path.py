
import bpy
from mathutils import Vector, Euler

from bpy_extras.object_utils import object_data_add
import bmesh

import utils

from math import degrees, pi

_TOL = 0.001

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
    bpy.ops.object.empty_add(type='SINGLE_ARROW')
    arrow = bpy.context.selected_objects[0]
    arrow_mesh_name = arrow.name
    arrow.location = pose.loc
    arrow.rotation_euler = Vector((pose.rotation.x, pose.rotation.y + pi/2, pose.rotation.z))

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
    num_dec = len(str(( _TOL - int(_TOL) )))-2
    loc = pose.loc
    rot = pose.rotation

    txt = '({:0.4f}, {:0.4f}, {:0.4f})'.format(loc.x, loc.y, loc.z)

    hint_space = 10
    rotation = 0
    loc_note_name = utils.draw_text(context, name, txt, loc, color, hint_space, font, font_align, rotation)

    bpy.data.objects[loc_note_name].lock_location[0:3] = (True, True, True)
    bpy.data.objects[loc_note_name].lock_rotation[0:3] = (True, True, True)
    bpy.data.objects[loc_note_name].lock_scale[0:3] = (True, True, True)
    bpy.data.objects[loc_note_name].protected = True

    txt = '({:0.4f}, {:0.4f}, {:0.4f})'.format(degrees(rot.x), degrees(rot.y), degrees(rot.z))

    rot_note_name = utils.draw_text(context, name, txt, loc, color, hint_space, font, font_align, rotation)

    euler_rot = Euler(rot)

    bpy.data.objects[rot_note_name].location += euler_rot.to_matrix().col[2]

    bpy.data.objects[rot_note_name].lock_location[0:3] = (True, True, True)
    bpy.data.objects[rot_note_name].lock_rotation[0:3] = (True, True, True)
    bpy.data.objects[rot_note_name].lock_scale[0:3] = (True, True, True)
    bpy.data.objects[rot_note_name].protected = True

    return loc_note_name, rot_note_name

def draw_speed_note(context, name, action, color, font, font_align):
    # Draw notes
    num_dec = len(str(( _TOL - int(_TOL) )))-2

    p0 = action.p0
    p1 = action.p1
    x = (p0.x + p1.x)/2.0
    y = (p0.y + p1.y)/2.0
    z = (p0.z + p1.z)/2.0
    loc = Vector((x, y, z))

    vel = action.speed

    txt = ""
    txt += '{:0.4f}'.format(vel) + ' m/s'

    hint_space = 10
    rotation = 0
    pose_note_name = utils.draw_text(context, name, txt, loc, color, hint_space, font, font_align, rotation)

    bpy.data.objects[pose_note_name].lock_location[0:3] = (True, True, True)
    bpy.data.objects[pose_note_name].lock_rotation[0:3] = (True, True, True)
    bpy.data.objects[pose_note_name].lock_scale[0:3] = (True, True, True)
    bpy.data.objects[pose_note_name].protected = True

    return pose_note_name

class Line:

    def __init__(self, fixed_loc, current_loc):
        self._fixed_loc = fixed_loc
        self._current_loc = current_loc
        self._line_name = draw_line(self._fixed_loc, self._current_loc + Vector((_TOL, 0, 0)))

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
        #bpy.data.meshes.remove(bpy.data.meshes[self._arrow_name], do_unlink=True)

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
        return Vector((self._a, self._b, self._g))

    def __eq__(self, other):
        return abs(self._x - other.x) <= TOL and abs(self._y - other.y) <= TOL and abs(self._z - other.z) <= TOL and \
                abs(self.alpha - other.alpha) <= TOL and abs(self.beta - other.beta) <= TOL and abs(self.gamma - other.gamma) <= TOL and \
                self.speed == other.speed

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

    def __init__(self, p0, p1, speed):
        """
        p0: pose 0
        p1: pose 1
        """
        self._p0 = p0
        self._p1 = p1
        self._speed = speed
        self._line = draw_line(p0.loc, p1.loc + Vector((_TOL, 0, 0)))
        self._arrow = create_arrow(p1)

    def move(self, pose):
        self._p1 = pose
        update_line(self._line, self._p0.loc, self._p1.loc)
        update_arrow(self._arrow, self._p1)

    def draw_annotation(self, context):
        color = Vector((1.0, 1.0, 1.0, 1.0))
        font = 14
        font_align = 'C'
        self._loc_note_name, self._rot_note_name = draw_pose_note(context, "Note_pose", self.p1, color, font, font_align)
        self._speed_note_name = draw_speed_note(context, "Note_speed", self, color, font, font_align)

    def del_annotation(self):
        loc_note = bpy.data.objects[self._loc_note_name]
        rot_note = bpy.data.objects[self._rot_note_name]
        speed_note = bpy.data.objects[self._speed_note_name]
        bpy.data.objects.remove(loc_note, do_unlink=True)
        bpy.data.objects.remove(rot_note, do_unlink=True)
        bpy.data.objects.remove(speed_note, do_unlink=True)

    def get_p0(self):
        return self._p0

    def get_p1(self):
        return self._p1

    def get_speed(self):
        return self._speed

    def __del__(self):
        bpy.data.objects.remove(bpy.data.objects[self._line], do_unlink=True)
        bpy.data.meshes.remove(bpy.data.meshes[self._line], do_unlink=True)

        arrow = bpy.data.objects[self._arrow]
        bpy.data.objects.remove(arrow, do_unlink=True)

        self.del_annotation()

    p0 = property(get_p0)
    p1 = property(get_p1)
    speed = property(get_speed)

class Annotation:

    def __init__(self, context, name, action, color, font, font_align):
        self._pose_note_name = draw_pose_note(context, name + "_pose", action.p1, color, font, font_align)
        self._speed_note_name = draw_speed_note(context, name + "_speed", action, color, font, font_align)

    def __del__(self):
        pose_note = bpy.data.objects[self._pose_note_name]
        speed_note = bpy.data.objects[self._speed_note_name]
        bpy.data.objects.remove(pose_note, do_unlink=True)
        bpy.data.objects.remove(speed_note, do_unlink=True)
