
import bpy
import cursorListener as cl

from mathutils import Vector
from math import pi
import path
import pathContainer as pc
import pathEditorPanel as pep
import collapse_check

def autoregister():
    global pd
    pd = PathDrawer()
    cl.CursorListener.add_observer(pd)

    bpy.utils.register_class(PoseProps)
    bpy.types.Scene.pose_props = bpy.props.PointerProperty(type=PoseProps)

    bpy.utils.register_class(SavePoseOperator)
    bpy.utils.register_class(UndoPoseOperator)
    bpy.utils.register_class(RemoveLastSavedPoseOperator)
    bpy.utils.register_class(ShortcutPathEditor)

    bpy.utils.register_class(PathEditorLog)
    bpy.utils.register_class(MoveCursorToLastPoseOperator)

    bpy.ops.scene.shortcut_path_editor('INVOKE_DEFAULT')

def autounregister():
    global pd
    cl.CursorListener.rm_observer(pd)

    bpy.utils.unregister_class(PoseProps)
    del bpy.types.Scene.pose_props

    bpy.utils.unregister_class(SavePoseOperator)
    bpy.utils.unregister_class(UndoPoseOperator)
    bpy.utils.unregister_class(RemoveLastSavedPoseOperator)
    bpy.utils.unregister_class(ShortcutPathEditor)

    bpy.utils.unregister_class(PathEditorLog)
    bpy.utils.unregister_class(MoveCursorToLastPoseOperator)


def hideCeil():
    for obj in bpy.data.objects:
        if obj.object_type == 'CEIL':
            obj.hide_set(True)

def showCeil():
    for obj in bpy.data.objects:
        if obj.object_type == 'CEIL':
            obj.hide_set(False)

class PathDrawer(cl.Observer):

    def __init__(self):
        self.current_pose = None
        self.current_action = None

    def notifyStop(self):
        pathContainer = pc.PathContainer()
        temp = pc.TempPathContainer()
        temp.pushActions()
        del self.current_action
        self.current_action = None
        bpy.ops.scene.shortcut_path_editor('INVOKE_DEFAULT')
        showCeil()

    def notifyStart(self):
        if len(pc.PathContainer()) > 0:
            # Obtenemos ultima pose como inicio para crear nuevas poses
            last_action = pc.PathContainer().getLast()
            loc = last_action.p1.loc
            angle = last_action.p1.rotation
            vel = last_action.speed
        else:
            # O si no se han creado, la posicion donde está el robot
            # TODO: Obtener posicion de robot
            # TODO: Operador para crear el robot y que el usuario lo situe
            loc = Vector((0, 0, 0))
            angle = Vector((0, pi/2, 0))
            vel = bpy.context.scene.pose_props.prop_speed
        # Movemos el cursor a la posicion de comienzo
        new_pose = path.Pose.fromVector(loc, angle)
        cl.CursorListener.set_pose(new_pose)

        self.current_action = path.Action(new_pose, new_pose, vel)
        cl.CursorListener.select_cursor()
        hideCeil();

    def notifyChange(self, current_pose):
        if self.current_action is not None:
            self.current_action.move(current_pose)


class PoseProps(bpy.types.PropertyGroup):
    prop_speed: bpy.props.FloatProperty(min=0.0, max=100.0, default=5.0)

class SavePoseOperator(bpy.types.Operator):
    bl_idname = "scene.save_pose"
    bl_label = "Save Pose"
    bl_description = "Save pose"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global pd
        # w = bpy.context.scene.robot_props.prop_width + bpy.context.scene.robot_props.prop_margin_width
        # h = bpy.context.scene.robot_props.prop_height + bpy.context.scene.robot_props.prop_margin_height

        # Guardamos nueva action y dibujamos la informacion para la action previa
        pd.current_action.draw_annotation(context)
        pc.TempPathContainer().appendAction(pd.current_action)

        # Siguiente action
        p0 = pd.current_action.p1
        p1 = pd.current_action.p1
        vel = bpy.context.scene.pose_props.prop_speed
        pd.current_action = path.Action(p0, p1, vel)

        cl.CursorListener.select_cursor()
        return {'FINISHED'}

class UndoPoseOperator(bpy.types.Operator):
    bl_idname = "scene.undo_pose"
    bl_label = "Undo Pose"
    bl_description = "Undo pose"

    @classmethod
    def poll(cls, context):
        return len(pc.TempPathContainer()) > 0

    def execute(self, context):
        last_action = pc.TempPathContainer().removeLast()
        # Eliminamos flecha y linea que representa la ultima accion guardada
        del pd.current_action
        pd.current_action = last_action
        pd.current_action.del_annotation()
        return {'FINISHED'}

class RemoveLastSavedPoseOperator(bpy.types.Operator):
    bl_idname = "scene.remove_last_saved_pose"
    bl_label = "Remove Last Saved Pose"
    bl_description = "Remove last saved pose"

    @classmethod
    def poll(cls, context):
        return len(pc.PathContainer()) > 0

    def execute(self, context):
        action = pc.PathContainer().removeLast()
        del action
        return {'FINISHED'}

class MoveCursorToLastPoseOperator(bpy.types.Operator):
    bl_idname = "scene.move_to_last_pose"
    bl_label = "Move cursor to last pose"
    bl_description = "Move cursor to last pose"

    @classmethod
    def poll(cls, context):
        return pd.current_action is not None

    def execute(self, context):
        pose0 = pd.current_action.p0
        pd.current_action.move(pose0)
        cl.CursorListener.set_pose(pose0)
        return {'FINISHED'}

class ShortcutPathEditor(bpy.types.Operator):
    bl_idname = "scene.shortcut_path_editor"
    bl_label = "Shortcut Path Editor"
    bl_description = "Shortcut"

    def __init__(self):
        pass

    def __del__(self):
        pass

    def execute(self, context):
        return {'FINISHED'}

    def modal(self, context, event):
        if event.ctrl and event.type == 'U':
            self.report({'INFO'}, "Undo save")
            if len(pc.TempPathContainer()) > 0:
                pc.bpy.ops.scene.undo_pose()
        elif event.ctrl and event.type == 'R':
            self.report({'INFO'}, "Remove path")
            bpy.ops.scene.remove_last_saved_pose()
        elif event.ctrl and event.type == 'D':
            self.report({'INFO'}, "Save pose")
            bpy.ops.scene.save_pose()
        elif event.type == 'ESC':
            return {'FINISHED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class PathEditorLog(bpy.types.Operator):
    bl_idname = "screen.patheditor_log"
    bl_label = "PathEditor Log"
    bl_description = "Logger"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        import datetime as dt
        date = str(dt.datetime.now())
        log = "PathEditor | " + date + "\n"
        log += "\tPathContainer : " + str(len(pc.PathContainer())) + "\n"
        log += "\tTempPathContainer : " + str(len(pc.TempPathContainer())) + "\n"
        self.report({'INFO'}, log)
        return {'FINISHED'}