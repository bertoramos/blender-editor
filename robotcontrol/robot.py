
import bpy
from mathutils import Vector
import robot_props

from math import radians
import utils

def autoregister():
    RobotSet()
    bpy.utils.register_class(RobotItem)
    bpy.types.Scene.robot_collection = bpy.props.CollectionProperty(type=RobotItem)

    bpy.utils.register_class(AddRobotOperator)
    bpy.utils.register_class(DeleteRobotOperator)

def autounregister():
    RobotSet().clear()
    bpy.utils.unregister_class(RobotItem)
    del bpy.types.Scene.robot_collection

    bpy.utils.unregister_class(AddRobotOperator)
    bpy.utils.unregister_class(DeleteRobotOperator)

def drop(obj):
    obj_name = obj.name
    mesh = obj.data
    material = obj.active_material

    # Eliminamos objeto
    if obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)

    # Eliminamos el mesh que lo forma
    if mesh is not None:
        mesh_name = mesh.name
        if mesh_name in bpy.data.meshes:
            bpy.data.meshes.remove(bpy.data.meshes[mesh_name], do_unlink=True)
        if mesh_name in bpy.data.lights:
            bpy.data.lights.remove(bpy.data.lights[mesh_name], do_unlink=True)

    # Eliminamos su material
    if material is not None:
        material_name = material.name
        if material_name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[material_name], do_unlink=True)
    # bpy.ops.select_all
    bpy.ops.object.select_all(action='DESELECT')

def draw_robot_note(context, loc, text, color, font, font_align):
    # Draw notes
    name = "Robot_note"
    hint_space = 10
    rotation = 0
    robot_note = utils.draw_text(context, name, text, loc, color, hint_space, font, font_align, rotation)

    bpy.data.objects[robot_note].lock_location[0:3] = (True, True, True)
    bpy.data.objects[robot_note].lock_rotation[0:3] = (True, True, True)
    bpy.data.objects[robot_note].lock_scale[0:3] = (True, True, True)
    bpy.data.objects[robot_note].protected = True

    return robot_note

class RobotSet:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__set = set()
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def addRobot(self, robot):
        assert isinstance(robot, Robot), "Error: expected robot, get " + str(type(robot))
        RobotSet.__instance.__set.add(robot)

    def getRobot(self, idn):
        for robot in RobotSet.__instance.__set:
            if robot.idn == idn:
                return robot

    def deleteRobot(self, idn):
        for robot in RobotSet.__instance.__set:
            if robot.idn == idn:
                RobotSet.__instance.__set.remove(robot)
                drop(bpy.data.objects[robot.name])
                drop(bpy.data.objects[robot.note_name])
                break

    def clear(self):
        RobotSet.__instance.__set = set()

    def __iter__(self):
        return iter(RobotSet.__instance.__set)

    def __len__(self):
        return len(RobotSet.__instance.__set)

class Robot:

    def __init__(self, idn, name, note_name, loc, robot_type):
        """
        Parameters:
            - id (int) : robot id
            - name (str) : robot name
            - note_name (str) : note name
            - loc (mathutils.Vector) : location in world
            - type (tuple) : robot type. A tuple in robot_types
        """
        assert type(idn) == int, "Error: expected int, get " + str(idn)
        self.__idn = idn
        self.__name = str(name)
        self.__note_name = str(note_name)

        assert type(loc) == Vector, "Error: expected Vector location"
        self.__loc = loc

        assert robot_type in robot_props.robot_types, "Error: robot_types does not contain " + str(type)
        self.__robot_type = robot_type

    def __get_idn(self):
        return self.__idn

    def __get_name(self):
        return self.__name

    def __get_note_name(self):
        return self.__note_name

    def __get_loc(self):
        return self.__loc

    def __set_loc(self, loc):
        assert type(loc) == Vector, "Error: expected Vector location"
        self.__loc = loc

    def __get_robot_type(self):
        return self.__robot_type

    def __hash__(self):
        return self.__idn

    def __eq__(self, other):
        return self.__idn == other.idn

    idn = property(__get_idn)
    name = property(__get_name)
    note_name = property(__get_note_name)
    loc = property(__get_loc, __set_loc)
    robot_type = property(__get_robot_type)


def draw_myrobot(context, name, loc, robot_type, rot, dim, margin):
    bpy.ops.mesh.primitive_cube_add(location=(loc.x, loc.y, loc.z + dim.z/2.0))
    myrobot = bpy.context.active_object
    myrobot.dimensions.xyz = dim.xyz
    myrobot.rotation_euler.z = radians(rot)
    myrobot.name = name

    myrobot.protected = True

    note_name = draw_robot_note(context, Vector((0,0,0)), "Datos de mi robot", Vector((255,255,255,255)), 14, "C")

    bpy.data.objects[note_name].parent = myrobot

    return myrobot.name, note_name

class MyRobot(Robot):

    def __init__(self, idn, name, note_name, loc, robot_type, rotation, dim, margin):
        """
        Parameters:
            - idn (int) : robot id
            - name (str) : robot name
            - note_name (str) : note name
            - loc (mathutils.Vector) : location in world
            - type (tuple) : robot type. A tuple in robot_types
            - rotation (float) : rotation angle
            - dim (Vector) : dimension in x, y, z axis
            - margin (Vector) : margin percentage in x, y, z axis
        """
        super().__init__(idn, name, note_name, loc, robot_type)
        self.__rotation = rotation
        self.__dim = dim
        self.__margin = margin

    def __get_rotation(self):
        return self.__rotation

    def __set_rotation(self, rotation):
        assert type(rotation) == Vector, "Error: expected Vector, get " + str(rotation)
        self.__rotation = rotation

    def __get_dim(self):
        return self.__dim

    def __get_margin(self):
        return self.__margin

    rotation = property(__get_rotation, __set_rotation)
    dim = property(__get_dim)
    margin = property(__get_margin)



"""
Operadores
"""

class RobotItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Unknown")
    idn: bpy.props.IntProperty(name="Id", default=22)
    selected: bpy.props.BoolProperty(name="Delete")

class AddRobotOperator(bpy.types.Operator):
    bl_idname = "scene.add_robot"
    bl_label = "Add Robot"
    bl_description = "Add Robot"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene

        idn = len(RobotSet())

        name = scene.robot_props.prop_robot_name
        loc = scene.robot_props.prop_robot_loc
        robot_type = scene.robot_props.prop_robot_type

        robot_type_tuple = ()
        for ENUM, enum, empty, num in robot_props.robot_types:
            if robot_type == ENUM:
                robot_type_tuple = (ENUM, enum, empty, num)

        robot = None
        if robot_type == 'MYROBOT':
            rot = scene.myrobot_props.prop_myrobot_rotation
            dim = scene.myrobot_props.prop_myrobot_dim
            margin = scene.myrobot_props.prop_myrobot_margin

            complete_name, note_name = draw_myrobot(context, name, loc, robot_type, rot, dim, margin)
            robot = MyRobot(idn, complete_name, note_name, loc, robot_type_tuple, rot, dim, margin)
            RobotSet().addRobot(robot)

        if robot is not None:
            # Añadir item en lista de robots
            scene = context.scene
            myitem = scene.robot_collection.add()
            myitem.name = robot.name
            myitem.idn = robot.idn

        return {'FINISHED'}

class DeleteRobotOperator(bpy.types.Operator):
    bl_idname = "scene.delete_robot"
    bl_label = "Delete robot"
    bl_description = "Delete Robot"

    @classmethod
    def poll(cls, context):
        return len(RobotSet()) > 0

    def execute(self, context):
        scene = context.scene
        for item in scene.robot_collection:
            if item.selected:
                idn = item.idn
                RobotSet().deleteRobot(idn)
                idx = scene.robot_collection.find(item.name)
                scene.robot_collection.remove(idx)
        return {'FINISHED'}
