
import bpy
from mathutils import Vector

from bpy.props import BoolProperty

import geomCursor as gc
import path
import pathContainer as pc
import robot
import utils


def autoregister():
    global classes
    classes = [StartPosesListener, StopPosesListener]
    for cls in classes:
        bpy.utils.register_class(cls)


def autounregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

bpy.types.Scene.is_cursor_active = BoolProperty(name = 'is_cursor_active', default = False)

class CursorListener:

    listener = None
    _observers = []

    @staticmethod
    def addListener(listener):
        CursorListener.listener = listener

    @staticmethod
    def delListener():
        del CursorListener.listener
        CursorListener.listener = None

    def __init__(self):
        initial_loc = Vector((0, 0, 0))
        initial_angle = Vector((0, 0, 0))
        init_pose = path.Pose.fromVector(initial_loc, initial_angle)
        self.current_pose = init_pose
        self._geomCursor = gc.GeometricCursor(init_pose)

    @staticmethod
    def set_pose(new_pose):
        """
        Move cursor to a specific pose
        """
        CursorListener.listener._geomCursor.move(new_pose)
        CursorListener.listener._geomCursor.redraw()

    @staticmethod
    def select_cursor():
        """
        Select geometric cursor asociated to CursorListener.listener
        """
        CursorListener.listener._geomCursor.select()

    @staticmethod
    def add_observer(observer):
        CursorListener._observers.append(observer)

    @staticmethod
    def rm_observer(observer):
        if observer in CursorListener._observers:
            CursorListener._observers.remove(observer)

    def __del__(self):
        del self._geomCursor

    def fire(self):
        """
        Acciones tomadas por el listener al lanzarse
        """
        for o in self._observers:
            o.notifyChange(self._geomCursor.current_pose)

# Method handler
def cursor_update(context):
    """
    Handler que se lanza cada vez que se produce un cambio en el depsgraph
    """
    if CursorListener.listener is not None:
        CursorListener.listener.fire() # Lanzamos listener

def isListenerActive():
    return cursor_update in bpy.app.handlers.depsgraph_update_post

class StopPosesListener(bpy.types.Operator):
    """
    Para el listener y notifica a los observadores
    """
    bl_idname = "scene.stop_cursor_listener"
    bl_label = "Stop editor"
    bl_description = "Stop cursor listener"

    @classmethod
    def poll(cls, context):
        # Esta activo el listener?
        return isListenerActive()

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        # Desactivar listeners
        for scene in bpy.data.scenes:
            scene.is_cursor_active = False
        # Notifica a los observers que se va a parar el listener
        for observer in CursorListener._observers:
            observer.notifyStop(self)

        # Desactivamos listener
        CursorListener.delListener()
        bpy.app.handlers.depsgraph_update_post.remove(cursor_update)

        # Deseleccionamos todo objeto
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}

class StartPosesListener(bpy.types.Operator):
    """
    Activa el listener y notifica a los observadores
    """
    bl_idname = "scene.start_cursor_listener"
    bl_label = "Start editor"
    bl_description = "Start cursor listener"

    @classmethod
    def poll(cls, context):
        # Esta activo el listener?
        import communicationOperator as co
        in_rob_mode = bpy.context.scene.com_props.prop_mode == co.robot_modes_summary.index("ROBOT_MODE")
        return in_rob_mode and len(robot.RobotSet()) > 0 and not isListenerActive() and context.scene.selected_robot_props.prop_robot_id >= 0

    def execute(self, context):
        # Indica que se activó el cursor
        for scene in bpy.data.scenes:
            scene.is_cursor_active = True

        # Activamos listener
        CursorListener.addListener(CursorListener())
        bpy.app.handlers.depsgraph_update_post.append(cursor_update)

        # Informamos a observers que se activó el listener
        for observer in CursorListener._observers:
            observer.notifyStart(self)
        return {'FINISHED'}

class Observer:

    def __init__(self):
        pass

    def notifyStop(self):
        """
        Se notifica al Observer que se paró el listener
        """
        pass

    def notifyStart(self):
        """
        Se notifica al Observer que se arrancó el listener
        """
        pass

    def notifyChange(self, current_pose):
        """
        Se notifica al Observer que se produjo un cambio en el cursor geométrico
        """
        pass
