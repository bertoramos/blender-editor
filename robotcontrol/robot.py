
import bpy
from mathutils import Vector
import robot_props

from math import radians

def autoregister():
    RobotSet()
    bpy.utils.register_class(AddRobotOperator)

def autounregister():
    RobotSet().clear()
    bpy.utils.unregister_class(AddRobotOperator)

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
                break

    def clear(self):
        RobotSet.__instance.__set = set()

    def __iter__(self):
        return iter(RobotSet.__instance.__set)

    def __len__(self):
        return len(RobotSet.__instance.__set)

class Robot:

    def __init__(self, idn, name, loc, robot_type):
        """
        Parameters:
            - id (int) : robot id
            - name (str) : robot name
            - loc (mathutils.Vector) : location in world
            - type (tuple) : robot type. A tuple in robot_types
        """
        assert type(idn) == int, "Error: expected int, get " + str(idn)
        self.__idn = idn
        self.__name = str(name)

        assert type(loc) == Vector, "Error: expected Vector location"
        self.__loc = loc

        assert robot_type in robot_props.robot_types, "Error: robot_types does not contain " + str(type)
        self.__robot_type = robot_type

    def __get_idn(self):
        return self.__idn

    def __get_name(self):
        return self.__name

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
    loc = property(__get_loc, __set_loc)
    robot_type = property(__get_robot_type)


def draw_myrobot(name, loc, robot_type, rot, dim, margin):
    bpy.ops.mesh.primitive_cube_add(location=(loc.x, loc.y, loc.z))
    myrobot = bpy.context.active_object
    myrobot.dimensions.xyz = dim.xyz
    myrobot.rotation_euler.z = radians(rot)

    myrobot.protected = True

# TODO: list robots and select to delete

class MyRobot(Robot):

    def __init__(self, idn, name, loc, robot_type, rotation, dim, margin):
        """
        Parameters:
            - idn (int) : robot id
            - name (str) : robot name
            - loc (mathutils.Vector) : location in world
            - type (tuple) : robot type. A tuple in robot_types
            - rotation (float) : rotation angle
            - dim (Vector) : dimension in x, y, z axis
            - margin (Vector) : margin percentage in x, y, z axis
        """
        super().__init__(idn, name, loc, robot_type)
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

        if robot_type == 'MYROBOT':
            rot = scene.myrobot_props.prop_myrobot_rotation
            dim = scene.myrobot_props.prop_myrobot_dim
            margin = scene.myrobot_props.prop_myrobot_margin

            robot = MyRobot(idn, name, loc, robot_type_tuple, rot, dim, margin)
            RobotSet().addRobot(robot)
            draw_myrobot(name, loc, robot_type, rot, dim, margin)

        return {'FINISHED'}
