
import bpy
from mathutils import Vector, Euler
from math import pi

# begin local import: Change to from . import MODULE
import cursorListener as cl
import path
import pathContainer as pc
import pathEditorPanel as pep
import robot as robot_tools
import collision_detection
import utils
# end local import: Change to from . import MODULE

keymaps = []

def autoregister():
    global classes
    classes = [SavePoseOperator,
               UndoPoseOperator,
               PathEditorLog,
               MoveCursorToLastPoseOperator,
               SelectCursorOperator,
               ClearPathOperator,
               MoveCursorSelectedPoseOperator,
               RemoveSelectedPoseOperator,
               InsertPoseBeforeSelectedPoseOperator]
    #

    for cls in classes:
        bpy.utils.register_class(cls)


    global pd
    pd = PathDrawer()
    cl.CursorListener.add_observer(pd)

    #global isModifying
    #isModifying = False
    bpy.types.Scene.isModifying = bpy.props.BoolProperty(name='isModifying', default=False)

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
    for c in classes:
        bpy.utils.unregister_class(c)


    global pd
    cl.CursorListener.rm_observer(pd)

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()

    del bpy.types.Scene.isModifying


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
        self.current_action = None
        self.next_action = None

    def notifyStop(self, operator):
        pathContainer = pc.PathContainer()
        temp = pc.TempPathContainer()

        temp.pushActions()

        del self.current_action
        self.current_action = None
        showCeil()

    def notifyStart(self, operator):
        bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
        bpy.context.scene.cursor.rotation_euler = Euler((0.0, 0.0, 0.0))

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

        # Movemos el cursor a la posicion de comienzo
        new_pose = path.Pose.fromVector(loc, angle)
        cl.CursorListener.set_pose(new_pose)

        self.current_action = path.Action(new_pose, new_pose)

        if len(pc.PathContainer()) == 0:
            self.current_action.set_first_action()

        cl.CursorListener.select_cursor()
        hideCeil()

        pc.TempPathContainer().loadActions()

    def notifyChange(self, current_pose):
        if self.current_action is not None:
            self.current_action.move(current_pose)
            if self.next_action is not None:
                self.next_action.move_fixed(current_pose)


def is_colliding(idx, robot_obj, area_robot_obj, pos0, pos1):
    rs = robot_tools.RobotSet()

    obstacles = []
    obstacles_names = []
    for obj in bpy.data.objects:
        if obj.object_type == "WALL":
            # Create a copy for collision detection
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
            
            # save original name for idetification
            obstacles_names.append(obj.name)
            
            obstacles.append(cube)

            cube.object_type = "TEMPORAL"


        if obj.object_type == "OBSTACLE_MARGIN":
            # Create a copy for collision detection
            o = obj.copy()
            o.parent = None
            o.object_type = "TEMPORAL"

            o.location = obj.parent.location.xyz
            o.dimensions = obj.dimensions.xyz
            o.rotation_euler = obj.parent.rotation_euler

            bpy.context.scene.collection.objects.link(o)
            
            obstacles_names.append(obj.name) # saves original name for identification
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
                        
                        obstacles_names.append(obj.name) # saves original name for identificationssss
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
    res, overlapping_indeces = collision_detection.check_collision(area_robot_obj_tmp, pos0, pos1, obstacles)
    
    # Get obstacle names
    
    obj_colliding_names = [obstacles_names[i] for i in overlapping_indeces if i < len(obstacles_names) and i >= 0 and obstacles_names[i] is not None]
    
    # Remove all objects
    for obj in obstacles:
        if obj.object_type == "TEMPORAL":
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.objects.remove(area_robot_obj_tmp, do_unlink=True)

    return res, obj_colliding_names


def append_pose(self, context):
    global pd
    # validate new action
    pos0 = pd.current_action.p0
    pos1 = pd.current_action.p1

    idx = bpy.context.scene.selected_robot_props.prop_robot_id
    robot = robot_tools.RobotSet().getRobot(idx)
    robot_obj = bpy.data.objects[robot.name]
    area_robot_obj = bpy.data.objects[robot.area_name]

    res, obstacles_names = is_colliding(idx, robot_obj, area_robot_obj, pos0, pos1)

    if res:
        self.report({'ERROR'}, f"Collision detected: Robot will collide if takes this path. Obstacles: {obstacles_names}")
        return {'FINISHED'}
    else:
        self.report({'INFO'}, "Undetected collision")

    # Guardamos nueva action y dibujamos la informacion para la action previa
    pd.current_action.draw_annotation(context)
    pc.TempPathContainer().appendAction(pd.current_action)

    # Siguiente action
    p0 = pd.current_action.p1
    p1 = pd.current_action.p1
    pd.current_action = path.Action(p0, p1)

    cl.CursorListener.select_cursor()

    return {'FINISHED'}


def apply_modification(self, context):
    global pd
    # validate current_action and next_action
    pos0 = pd.current_action.p0
    pos1 = pd.current_action.p1
    pos2 = getattr(pd.next_action, 'p1', None)

    idx = bpy.context.scene.selected_robot_props.prop_robot_id
    robot = robot_tools.RobotSet().getRobot(idx)
    robot_obj = bpy.data.objects[robot.name]
    area_robot_obj = bpy.data.objects[robot.area_name]

    res_first_action, first_obstacles_names = is_colliding(idx, robot_obj, area_robot_obj, pos0, pos1)

    res_second_action, second_obstacles_names = is_colliding(idx, robot_obj, area_robot_obj, pos1, pos2) if pos2 is not None else False

    if res_first_action or res_second_action:
        self.report({'ERROR'}, f"Collision detected: Robot will collide if takes this path. Obstacles: {first_obstacles_names + second_obstacles_names}")
        return {'FINISHED'}
    else:
        self.report({'INFO'}, "Undetected collision")

    # Guardamos nueva action y dibujamos la informacion para la action previa
    pd.current_action.draw_annotation(context)
    #pc.TempPathContainer().appendAction(pd.current_action)

    last_action = pc.TempPathContainer().getLastAction()
    pd.next_action = None

    # Siguiente action
    p1 = last_action.p1
    pd.current_action = path.Action(p1, p1)

    cl.CursorListener.select_cursor()
    context.scene.isModifying = False

    cl.CursorListener.set_pose(p1)

    return {'FINISHED'}

class SavePoseOperator(bpy.types.Operator):
    bl_idname = "scene.save_pose"
    bl_label = "Save pose"
    bl_description = "Save pose"

    @classmethod
    def poll(cls, context):
        return context.scene.is_cursor_active

    def execute(self, context):
        if context.scene.isModifying:
            return apply_modification(self, context)
        else:
            return append_pose(self, context)
        return {'FINISHED'}

class UndoPoseOperator(bpy.types.Operator):
    bl_idname = "scene.undo_pose"
    bl_label = "Undo Pose"
    bl_description = "Undo pose"

    @classmethod
    def poll(cls, context):
        return len(pc.TempPathContainer()) > 0 and not context.scene.isModifying

    def execute(self, context):
        last_action = pc.TempPathContainer().removeLast()
        # Eliminamos flecha y linea que representa la ultima accion guardada
        del pd.current_action
        pd.current_action = last_action
        pd.current_action.del_annotation()
        return {'FINISHED'}

"""
class RemoveLastSavedPoseOperator(bpy.types.Operator):
    bl_idname = "scene.remove_last_saved_pose"
    bl_label = "Remove Last Saved Pose"
    bl_description = "Remove last saved pose"

    @classmethod
    def poll(cls, context):
        global isModifying
        running_plan = context.scene.com_props.prop_running_nav
        paused_plan = context.scene.com_props.prop_paused_nav
        return len(pc.PathContainer()) > 0 and (not running_plan or (running_plan and paused_plan)) and not isModifying

    def execute(self, context):
        action = pc.TempPathContainer().removeLastAction()
        del action
        last_action = pc.TempPathContainer().getLastAction()

        cl.CursorListener.set_pose(last_action.p1)
        pd.current_action = last_action

        return {'FINISHED'}
"""

class ClearPathOperator(bpy.types.Operator):
    bl_idname = "scene.clear_path"
    bl_label = "Clear all path"
    bl_description = "Clear path"

    @classmethod
    def poll(cls, context):
        running_plan = context.scene.com_props.prop_running_nav
        paused_plan = context.scene.com_props.prop_paused_nav
        return len(pc.PathContainer()) > 0 and (not running_plan or (running_plan and paused_plan)) and not context.scene.is_cursor_active

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

class MoveCursorSelectedPoseOperator(bpy.types.Operator):
    bl_idname = "scene.move_cursor_selected_pose"
    bl_label = "Move cursor to selected pose"
    bl_description = "Move cursor to selected pose"

    @classmethod
    def poll(cls, context):
        # Si algun elemento seleccionado es una pose de la ruta activa
        for obj in bpy.context.selected_objects:
            if obj.object_type == "PATH_ELEMENTS_POSE":
                return True
        if context.scene.isModifying:
            return False
        return False

    def execute(self, context):
        global pd

        for obj in context.selected_objects:
            for action_index, action in enumerate(pc.TempPathContainer()):
                if obj.name_full == action._arrow:
                    cl.CursorListener.set_pose(action.p1)
                    pd.current_action = action

                    if len(pc.TempPathContainer()) > action_index + 1:
                        next_action = pc.TempPathContainer()[action_index + 1]
                        pd.next_action = next_action

                    cl.CursorListener.select_cursor()

                    # remove anotation
                    pd.current_action.del_annotation()

                    context.scene.isModifying = True
                    return {'FINISHED'}
        return {'FINISHED'}

class RemoveSelectedPoseOperator(bpy.types.Operator):
    bl_idname = "scene.remove_selected_pose"
    bl_label = "Remove selected pose"
    bl_description = "Remove selected pose"

    @classmethod
    def poll(cls, context):
        # Si algun elemento seleccionado es una pose de la ruta activa
        for obj in bpy.context.selected_objects:
            if obj.object_type == "PATH_ELEMENTS_POSE":
                return True
        if context.scene.isModifying:
            return False
        return False

    def execute(self, context):
        global pd

        for obj in context.selected_objects:
            for action_index, action in enumerate(pc.TempPathContainer()):
                if obj.name_full == action._arrow:

                    next_action_index = -1
                    if len(pc.TempPathContainer()) > action_index + 1:
                        next_action_index = action_index + 1

                    # Comprobar colision
                    pos0 = action.p0
                    pos1 = pd.current_action.p1 if next_action_index < 0 else pc.TempPathContainer()[next_action_index].p1

                    idx = bpy.context.scene.selected_robot_props.prop_robot_id
                    robot = robot_tools.RobotSet().getRobot(idx)
                    robot_obj = bpy.data.objects[robot.name]
                    area_robot_obj = bpy.data.objects[robot.area_name]

                    res, obstacles_names = is_colliding(idx, robot_obj, area_robot_obj, pos0, pos1)

                    if res:
                        self.report({'ERROR'}, f"Collision detected: Resulting path after deleting this point is not valid. Obstacles: {obstacles_names}")
                        return {'FINISHED'}
                    else:
                        self.report({'INFO'}, "Undetected collision")



                    p0 = action.p0
                    if next_action_index < 0:
                        # mover punto fijo del current_action a action.p1
                        pd.current_action.move_fixed(p0)
                    else:
                        # mover punto fijo del next_action a action.p1
                        pc.TempPathContainer()[next_action_index].move_fixed(p0)
                    action.del_annotation()
                    pc.TempPathContainer().remove(action_index)

                    return {'FINISHED'}
        return {'FINISHED'}


class InsertPoseBeforeSelectedPoseOperator(bpy.types.Operator):
    bl_idname = "scene.insert_pose_before_selected_pose"
    bl_label = "Insert before selected pose"
    bl_description = "Insert before selected pose"

    @classmethod
    def poll(cls, context):
        # Si algun elemento seleccionado es una pose de la ruta activa
        for obj in bpy.context.selected_objects:
            if obj.object_type == "PATH_ELEMENTS_POSE":
                return True
        if context.scene.isModifying:
            return False
        return False

    def execute(self, context):
        global pd

        for obj in context.selected_objects:
            for action_index, action in enumerate(pc.TempPathContainer()):
                if obj.name_full == action._arrow:
                    # Inserta una nueva action en medio de la pose seleccionada y la anterior
                    p0 = action.p0
                    p1 = action.p1
                    xm, ym = (p1.x + p0.x)/2. , (p1.y + p0.y)/2.
                    med_pose = path.Pose(xm, ym, p0.z, p0.alpha, p0.beta, p0.gamma)

                    # Crea un nuevo action desde la pose añadida hasta la pose seleccionada
                    next_action = path.Action(med_pose, p1)
                    next_action.draw_annotation(context)

                    # Se traslada la action seleccionada al punto intermedio
                    # La pose de este action será el nuevo punto intermedio
                    action.move(med_pose)
                    action.del_annotation()

                    pc.TempPathContainer().insert(action_index + 1, next_action)

                    # Cambia pathdrawer
                    pd.current_action = action
                    pd.next_action = next_action

                    cl.CursorListener.set_pose(action.p1)
                    cl.CursorListener.select_cursor()
                    context.scene.isModifying = True

                    return {'FINISHED'}
        return {'FINISHED'}


################################################################################


update_time = -1

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

        global update_time
        update = update_time < pc.PathContainer().getLastUpdate()
        update_time = pc.PathContainer().getLastUpdate()

        log = "PathEditor | " + date + " | update = " + str(update) + " : " + str(update_time) + "\n"
        log += "\tPathContainer : " + str(len(pc.PathContainer())) + "\n"
        for p in pc.PathContainer().poses:
            log += "\t\t" + str(p) + "\n"
        log += "\tTempPathContainer : " + str(len(pc.TempPathContainer())) + "\n"
        self.report({'INFO'}, log)
        return {'FINISHED'}
