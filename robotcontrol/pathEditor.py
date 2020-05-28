
import bpy
from mathutils import Vector, Euler
from math import pi

import cursorListener as cl
import path
import pathContainer as pc
import pathEditorPanel as pep
import robot as robot_tools
import collision_detection
import utils


keymaps = []

def autoregister():
    global classes
    classes = [SavePoseOperator, UndoPoseOperator, RemoveLastSavedPoseOperator, PathEditorLog, MoveCursorToLastPoseOperator, SelectCursorOperator, ClearPathOperator]
    for cls in classes:
        bpy.utils.register_class(cls)


    global pd
    pd = PathDrawer()
    cl.CursorListener.add_observer(pd)

    # keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new(SavePoseOperator.bl_idname, type='A', value='PRESS', ctrl=True, shift=True)
        keymaps.append((km, kmi))

        kmi = km.keymap_items.new(UndoPoseOperator.bl_idname, type='U', value='PRESS', ctrl=True, shift=True)
        keymaps.append((km, kmi))

        kmi = km.keymap_items.new(MoveCursorToLastPoseOperator.bl_idname, type='M', value='PRESS', ctrl=True, shift=True)
        keymaps.append((km, kmi))

def autounregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)


    global pd
    cl.CursorListener.rm_observer(pd)

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()


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

    def notifyStop(self, operator):
        pathContainer = pc.PathContainer()
        temp = pc.TempPathContainer()

        temp.pushActions()

        del self.current_action
        self.current_action = None
        showCeil()

    def notifyStart(self, operator):
        if len(robot_tools.RobotSet()) <= 0:
            operator.report({'ERROR'}, 'No robot available : add a robot to create a path')
            bpy.ops.scene.stop_cursor_listener('INVOKE_DEFAULT')
            return

        idx = bpy.context.scene.selected_robot_props.prop_robot_id
        assert idx >= 0 and idx in robot_tools.RobotSet(), "Error : no robot selected or not in list"

        robot = robot_tools.RobotSet().getRobot(idx)

        last_action = pc.PathContainer().getLastAction()

        if len(pc.PathContainer()) > 0 and last_action is not None:
            # Obtenemos ultima pose como inicio para crear nuevas poses
            loc = last_action.p1.loc
            angle = last_action.p1.rotation
        else:
            loc = robot.loc + Vector((bpy.context.scene.TOL, bpy.context.scene.TOL, bpy.context.scene.TOL))
            angle = robot.rotation
            #angle.y = pi/2.0

        # Movemos el cursor a la posicion de comienzo
        new_pose = path.Pose.fromVector(loc, angle)
        cl.CursorListener.set_pose(new_pose)

        self.current_action = path.Action(new_pose, new_pose)

        cl.CursorListener.select_cursor()
        hideCeil()



    def notifyChange(self, current_pose):
        if self.current_action is not None:
            self.current_action.move(current_pose)

def is_colliding(idx, robot_obj, area_robot_obj, pos0, pos1):
    rs = robot_tools.RobotSet()

    obstacles = []
    for obj in bpy.data.objects:
        if obj.object_type == "WALL":
            bpy.ops.mesh.primitive_cube_add()
            cube = bpy.context.active_object

            cube.dimensions = obj.dimensions.xyz
            cube.location = obj.dimensions.xyz/2.0

            save_cursor_loc = bpy.context.scene.cursor.location.xyz
            bpy.context.scene.cursor.location = Vector((0,0,0))
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.context.scene.cursor.location = save_cursor_loc

            cube.location = obj.location.xyz
            cube.rotation_euler.z = obj.rotation_euler.z

            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

            bpy.context.scene.collection.objects.link(cube)

            obstacles.append(cube)

            cube.object_type = "TEMPORAL"


        if obj.object_type == "OBSTACLE_MARGIN":
            o = obj.copy()
            o.parent = None
            o.object_type = "TEMPORAL"

            o.location = obj.parent.location.xyz
            o.dimensions = obj.dimensions.xyz
            o.rotation_euler = obj.parent.rotation_euler

            bpy.context.scene.collection.objects.link(o)
            obstacles.append(o)

        if obj.object_type == "ROBOT": # Search other robots
            for c in obj.children:
                if c.object_type == "ROBOT_MARGIN": # Get robot margin
                    robot = rs.getRobotByName(obj.name_full)
                    if robot.idn != idx:
                        margin = c
                        o = margin.copy()
                        o.parent = None
                        o.object_type = "TEMPORAL"

                        o.location = margin.parent.location.xyz
                        o.dimensions = margin.dimensions.xyz
                        o.rotation_euler = margin.parent.rotation_euler

                        bpy.context.scene.collection.objects.link(o)
                        obstacles.append(o)

    # Copy robot
    bpy.ops.mesh.primitive_cube_add()
    area_robot_obj_tmp = bpy.context.active_object
    area_robot_obj_tmp.dimensions = Vector((area_robot_obj.dimensions.x, area_robot_obj.dimensions.y, area_robot_obj.dimensions.z))
    area_robot_obj_tmp.location = Vector((robot.loc.x, robot.loc.y, (area_robot_obj.dimensions.z/2.0)))
    area_robot_obj_tmp.rotation_euler.z = pos0.rotation.z

    bpy.ops.object.select_all(action='DESELECT')
    area_robot_obj_tmp.select_set(True)
    save_cursor_loc = bpy.context.scene.cursor.location.xyz
    bpy.context.scene.cursor.location = Vector((robot.loc.x, robot.loc.y, 0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.scene.cursor.location = save_cursor_loc

    # Check
    res = collision_detection.check_collision(area_robot_obj_tmp, pos0, pos1, obstacles)

    # Remove all objects
    for obj in obstacles:
        if obj.object_type == "TEMPORAL":
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.objects.remove(area_robot_obj_tmp, do_unlink=True)

    return res

class SavePoseOperator(bpy.types.Operator):
    bl_idname = "scene.save_pose"
    bl_label = "Append Pose"
    bl_description = "Save pose"

    @classmethod
    def poll(cls, context):
        return context.scene.is_cursor_active

    def execute(self, context):
        global pd
        # validate new action
        pos0 = pd.current_action.p0
        pos1 = pd.current_action.p1
        loc0 = pd.current_action.p0.loc
        loc1 = pd.current_action.p1.loc

        idx = bpy.context.scene.selected_robot_props.prop_robot_id
        robot = robot_tools.RobotSet().getRobot(idx)
        robot_obj = bpy.data.objects[robot.name]
        area_robot_obj = bpy.data.objects[robot.area_name]

        res = is_colliding(idx, robot_obj, area_robot_obj, pos0, pos1)

        self.report({'INFO'}, "Collision : " + str(res))
        if res:
            self.report({'ERROR'}, "Robot will collide if takes this path")
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "Collision : " + str(res))


        # Guardamos nueva action y dibujamos la informacion para la action previa
        pd.current_action.draw_annotation(context)
        pc.TempPathContainer().appendAction(pd.current_action)

        # Siguiente action
        p0 = pd.current_action.p1
        p1 = pd.current_action.p1
        pd.current_action = path.Action(p0, p1)

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
        action = pc.PathContainer().removeLastAction()
        del action
        return {'FINISHED'}

class ClearPathOperator(bpy.types.Operator):
    bl_idname = "scene.clear_path"
    bl_label = "Clear all path"
    bl_description = "Clear path"

    @classmethod
    def poll(cls, context):
        return len(pc.PathContainer()) > 0

    def execute(self, context):
        pc.PathContainer().clear()
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

class SelectCursorOperator(bpy.types.Operator):
    bl_idname = "scene.select_geomcursor"
    bl_label = "Select geometric cursor"
    bl_description = "Select geometric cursor"

    @classmethod
    def poll(cls, context):
        return context.scene.is_cursor_active

    def execute(self, context):
        cl.CursorListener.select_cursor()
        return {'FINISHED'}


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
        for p in pc.PathContainer().poses:
            log += "\t\t" + str(p) + "\n"
        log += "\tTempPathContainer : " + str(len(pc.TempPathContainer())) + "\n"
        self.report({'INFO'}, log)
        return {'FINISHED'}
