
import bpy
from mathutils import Vector
from bpy.types import Operator
from math import pi

from bpy_extras.object_utils import AddObjectHelper, object_data_add
import bmesh

import pose
import pathContainer as pc
import addGeomCursor as agc
import pathDrawer as pd

import pathCreatorPanel as pcp

def autoregister():
    bpy.utils.register_class(StartPosesListener)
    bpy.utils.register_class(StopPosesListener)
    bpy.utils.register_class(SavePose)
    bpy.utils.register_class(UndoPose)
    bpy.utils.register_class(RemoveLastSavedPose)

def autounregister():
    bpy.utils.unregister_class(StartPosesListener)
    bpy.utils.register_class(StopPosesListener)
    bpy.utils.unregister_class(SavePose)
    bpy.utils.unregister_class(UndoPose)
    bpy.utils.unregister_class(RemoveLastSavedPose)

_TOL = 0.001

def equals(v1: Vector, v2: Vector, TOL):
    return abs(v1.x - v2.x) <= TOL and abs(v1.y - v2.y) <= TOL and abs(v1.z - v2.z) <= TOL


class CursorListener:

    listener = None

    @staticmethod
    def save_new_location():
        if CursorListener.listener is None:
            return False
        # Guardar posicion actual del cursor geométrico en lista
        pd.create_arrow(CursorListener.listener.current_pose)
        pc.TempPathContainer().appendPose(CursorListener.listener.current_pose, pd.line_mesh_name, pd.arrow_mesh_name)
        # Guardar posicion actual como posicion fija
        CursorListener.listener.fixed_pose = CursorListener.listener.current_pose
        # Crear una nueva linea que empiece en la posición actual del cursor geometrico
        # y desplazamos levemente uno de los puntos de la línea para no crear un punto, sino una recta
        pd.draw_line(CursorListener.listener.fixed_pose.loc, CursorListener.listener.fixed_pose.loc + Vector((_TOL, 0, 0)))

        return True

    @staticmethod
    def remove_last_location():
        if CursorListener.listener is None:
            return False
        tmp = pc.TempPathContainer()
        if len(tmp) > 0:

            last_pose, mesh_line_name, mesh_arrow_name = tmp.removeLast()

            location = bpy.data.objects[mesh_line_name].data.vertices[0].co
            a = bpy.data.objects[mesh_line_name].rotation_euler.x
            b = bpy.data.objects[mesh_line_name].rotation_euler.y
            g = bpy.data.objects[mesh_line_name].rotation_euler.z
            CursorListener.listener.fixed_pose = pose.Pose.fromVector(location, Vector((a, b, g)))

            location = bpy.data.objects[mesh_line_name].data.vertices[1].co
            a = bpy.data.objects[mesh_arrow_name].rotation_euler.x
            b = bpy.data.objects[mesh_arrow_name].rotation_euler.y
            g = bpy.data.objects[mesh_arrow_name].rotation_euler.z
            CursorListener.listener.current_pose = pose.Pose.fromVector(location + Vector((_TOL, 0, 0)), Vector((a, b, g)))

            pd.remove_line()
            pd.draw_line(CursorListener.listener.fixed_pose.loc, CursorListener.listener.current_pose.loc + Vector((_TOL, 0, 0)))
            bpy.data.objects[CursorListener.listener._cursor_name].location.xyz = CursorListener.listener.current_pose.loc + Vector((_TOL, 0, 0))
            bpy.data.objects[CursorListener.listener._cursor_name].rotation_euler = CursorListener.listener.current_pose.rotation

            line = bpy.data.objects[mesh_line_name]
            bpy.data.objects.remove(line, do_unlink=True)

            arrow = bpy.data.objects[mesh_arrow_name]
            bpy.data.objects.remove(arrow, do_unlink=True)
        else:
            CursorListener.listener.current_pose = CursorListener.listener.init_pose
            CursorListener.listener.fixed_pose = CursorListener.listener.init_pose

            pd.remove_line()
            pd.draw_line(CursorListener.listener.fixed_pose.loc, CursorListener.listener.current_pose.loc + Vector((_TOL, 0, 0)))
            bpy.data.objects[CursorListener.listener._cursor_name].location.xyz = CursorListener.listener.current_pose.loc + Vector((_TOL, 0, 0))
            bpy.data.objects[CursorListener.listener._cursor_name].rotation_euler = CursorListener.listener.current_pose.rotation

        return True

    @staticmethod
    def is_cursor_in_initial_loc():
        return bpy.data.objects[CursorListener.listener._cursor_name].location == CursorListener.init_pose.loc

    @staticmethod
    def addListener(listener):
        CursorListener.listener = listener

    @staticmethod
    def delListener():
        del CursorListener.listener
        CursorListener.listener = None

    def __init__(self):
        initial_loc = Vector((0, 0, 0))
        initial_angle = Vector((0, pi/2, 0))
        self.init_pose = pose.Pose.fromVector(initial_loc, initial_angle)
        pd.draw_line(initial_loc, initial_loc + Vector((_TOL, 0, 0)))
        self._cursor_name = agc.addGeomCursor(self.init_pose)
        self._current_pose = self.init_pose
        self._fixed_pose = self.init_pose

    def get_current_pose(self):
        return self._current_pose

    def get_fixed_pose(self):
        return self._fixed_pose

    def set_current_pose(self, pose):
        self._current_pose = pose

    def set_fixed_pose(self, pose):
        self._fixed_pose = pose

    current_pose = property(get_current_pose, set_current_pose)
    fixed_pose = property(get_fixed_pose, set_fixed_pose)

    def __del__(self):
        geomCursorObj = bpy.data.objects[self._cursor_name]
        bpy.data.objects.remove(geomCursorObj, do_unlink=True)
        pd.delete_last_line()

    def _get_pose(self):
        loc = bpy.data.objects[self._cursor_name].location.xyz
        angle = Vector((bpy.data.objects[self._cursor_name].rotation_euler.x, bpy.data.objects[self._cursor_name].rotation_euler.y, bpy.data.objects[self._cursor_name].rotation_euler.z))
        return pose.Pose.fromVector(loc, angle)

    def fire(self):
        new_pose = self._get_pose()
        if new_pose != self._current_pose:
            self._current_pose = new_pose
            pd.update_line(self._fixed_pose.loc, self._current_pose.loc)
            print("New pose ", new_pose)
        else:
            print("No changes")

# Method handler
def cursor_update(context):
    CursorListener.listener.fire()

class StopPosesListener(bpy.types.Operator):
    bl_idname = "scene.stop_poses_listener"
    bl_label = "Save path / Stop"

    @classmethod
    def poll(cls, context):
        return cursor_update in bpy.app.handlers.depsgraph_update_post

    def execute(self, context):
        pathContainter = pc.PathContainer()
        temp = pc.TempPathContainer()
        temp.pushPoses()

        CursorListener.delListener()
        bpy.app.handlers.depsgraph_update_post.remove(cursor_update)
        bpy.utils.unregister_class(pcp.ToolsPanel)
        return {'FINISHED'}

class StartPosesListener(bpy.types.Operator):
    bl_idname = "scene.start_poses_listener"
    bl_label = "Start create path"

    @classmethod
    def poll(cls, context):
        return cursor_update not in bpy.app.handlers.depsgraph_update_post

    def execute(self, context):
        CursorListener.addListener(CursorListener())
        bpy.app.handlers.depsgraph_update_post.append(cursor_update)
        bpy.utils.register_class(pcp.ToolsPanel)
        return {'FINISHED'}

class SavePose(bpy.types.Operator):
    bl_idname = "scene.save_pose"
    bl_label = "Save Pose"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        resCode =  CursorListener.save_new_location()
        if not resCode:
            self.report({'ERROR'}, "Can't add pose to list. Check you started to create a new plan")
        else:
            self.report({'INFO'}, "Pose was save")
        return {'FINISHED'}

class UndoPose(bpy.types.Operator):
    bl_idname = "scene.undo_pose"
    bl_label = "Undo Pose"

    @classmethod
    def poll(cls, context):
        return len(pc.TempPathContainer()) > 0 or CursorListener.is_cursor_in_initial_loc()

    def execute(self, context):
        resCode =  CursorListener.remove_last_location()
        if not resCode:
            self.report({'ERROR'}, "Can't remove pose.")
        return {'FINISHED'}

def remove_last_saved_pose():
    if len(pc.PathContainer()) > 0:
        last_pose, line_name, arrow_name = pc.PathContainer().removeLast()
        line = bpy.data.objects[line_name]
        bpy.data.objects.remove(line, do_unlink=True)
        arrow = bpy.data.objects[arrow_name]
        bpy.data.objects.remove(arrow, do_unlink=True)
    return True

class RemoveLastSavedPose(bpy.types.Operator):
    bl_idname = "scene.remove_last_saved_pose"
    bl_label = "Remove Last Saved Pose"

    @classmethod
    def poll(cls, context):
        return len(pc.PathContainer()) > 0

    def execute(self, context):
        resCode = remove_last_saved_pose()
        if not resCode:
            self.report({'ERROR'}, "Can't remove pose.")
        return {'FINISHED'}
