
import bpy
from mathutils import Vector, Euler
import robot_props
import cursorListener as cl

from math import radians, pi
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

    def getRobotByName(self, name):
        for robot in RobotSet.__instance.__set:
            if robot.name == name:
                return robot

    def deleteRobot(self, idn):
        for robot in RobotSet.__instance.__set:
            if robot.idn == idn:
                RobotSet.__instance.__set.remove(robot)
                robot_obj = bpy.data.objects[robot.name]
                for obj in bpy.data.objects[robot.name].children:
                    drop(obj)
                drop(robot_obj)
                break

    def __contains__(self, idn):
        for robot in RobotSet.__instance.__set:
            if robot.idn == idn:
                return True
        return False

    def clear(self):
        RobotSet.__instance.__set = set()

    def __iter__(self):
        return iter(RobotSet.__instance.__set)

    def __len__(self):
        return len(RobotSet.__instance.__set)

class Robot:

    def __init__(self, idn, name, area_name, robot_type, ip, port):
        """
        Parameters:
            - id (int) : robot id
            - name (str) : robot name
            - area_name (str) : area name (bounding box)
            - type (tuple) : robot type. A tuple in robot_types
        """
        assert type(idn) == int, "Error: expected int, get " + str(idn)
        self.__idn = idn
        self.__name = str(name)
        self.__area_name = str(area_name)
        self.__ip = ip
        self.__port = port

        assert robot_type in robot_props.robot_types, "Error: robot_types does not contain " + str(type)
        self.__robot_type = robot_type

    def __get_idn(self):
        return self.__idn

    def __get_name(self):
        return self.__name

    def __get_area_name(self):
        return self.__area_name

    def __get_loc(self):
        return bpy.data.objects[self.__name].location.xyz

    def __set_loc(self, loc):
        assert type(loc) == Vector, "Error: expected Vector location"
        bpy.data.objects[self.__name].location.xyz = loc

    def __get_rotation(self):
        return bpy.data.objects[self.__name].rotation_euler

    def __set_rotation(self, rotation):
        assert type(rotation) == Euler, "Error: expected Euler, get " + str(rotation)
        bpy.data.objects[self.__name].rotation_euler = rotation

    def __get_robot_type(self):
        return self.__robot_type

    def __get_ip(self):
        return self.__ip

    def __get_port(self):
        return self.__port

    def __hash__(self):
        return self.__idn

    def __eq__(self, other):
        return self.__idn == other.idn

    idn = property(__get_idn)
    name = property(__get_name)
    area_name = property(__get_area_name)
    loc = property(__get_loc, __set_loc)
    rotation = property(__get_rotation, __set_rotation)
    robot_type = property(__get_robot_type)
    ip = property(__get_ip)
    port = property(__get_port)


def draw_myrobot(context, name, loc, robot_type, rot, dim, margin, ip, port):

    # Cuerpo
    bpy.ops.mesh.primitive_cube_add(location=(loc.x, loc.y, dim.z/2.0))
    myrobot = bpy.context.active_object
    myrobot.dimensions.xyz = dim.xyz
    myrobot.rotation_euler.z = radians(rot)
    myrobot.name = name

    myrobot.lock_location[0:3] = (False, False, True)
    myrobot.lock_rotation[0:3] = (False, False, False)
    myrobot.lock_scale[0:3] = (True, True, True)
    myrobot.protected = True

    # margen
    bpy.ops.mesh.primitive_cube_add(location=myrobot.location.xyz[:])
    myarea = bpy.context.active_object
    myarea.dimensions.xyz = Vector((dim.x + 2*dim.x*(margin.x/100.0), dim.y + 2*dim.y*(margin.y/100.0), dim.z + 2*dim.z*(margin.z/100.0)))
    myarea.rotation_euler.z = radians(rot)

    myarea.lock_location[0:3] = (True, True, True)
    myarea.lock_rotation[0:3] = (True, True, True)
    myarea.lock_scale[0:3] = (True, True, True)
    myarea.protected = True

    if myarea.active_material is None:
        mat = bpy.data.materials.new("Material_robot_margin" + name)
        myarea.active_material = mat
    mat.diffuse_color = Vector((1, 1, 1, 0.2))

    # icosphere
    minx = min(dim.x, dim.y)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=minx/(2*1.5), location=(loc.x, loc.y, dim.z))
    myico = bpy.context.active_object

    if myico.active_material is None:
        mat = bpy.data.materials.new("Material_robot_icosphere" + name)
        myico.active_material = mat
    mat.diffuse_color = Vector((0, 0, 1, 0.2))

    # Notas
    note_name = draw_robot_note(context, Vector((0,0,0)), str(ip) + ":" + str(port), Vector((255,255,255,255)), 14, "C")


    # Hierarchy area+robot
    myarea.select_set(True)
    myrobot.select_set(True)
    bpy.context.view_layer.objects.active = myrobot
    bpy.ops.object.parent_set()
    myarea.select_set(False)
    myrobot.select_set(False)

    # Set origin
    myrobot.select_set(True)
    save_cursor_loc = bpy.context.scene.cursor.location.xyz
    bpy.context.scene.cursor.location.xyz = Vector((loc.x, loc.y, 0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.scene.cursor.location = save_cursor_loc

    # Hierarchy icosphere + robot
    myico.select_set(True)
    myrobot.select_set(True)
    bpy.context.view_layer.objects.active = myrobot
    bpy.ops.object.parent_set()
    myico.select_set(False)
    myrobot.select_set(False)

    myico.hide_select = True
    #myrobot.hide_select = False
    myarea.hide_select = True
    bpy.data.objects[note_name].parent = myrobot

    myrobot.object_type = "ROBOT"

    return myrobot.name, myarea.name

class MyRobot(Robot):

    def __init__(self, idn, name, note_name, robot_type, dim, margin, ip, port):
        """
        Parameters:
            - idn (int) : robot id
            - name (str) : robot name
            - note_name (str) : note name
            - type (tuple) : robot type. A tuple in robot_types
            - dim (Vector) : dimension in x, y, z axis
            - margin (Vector) : margin percentage in x, y, z axis
        """
        super().__init__(idn, name, note_name, robot_type, ip, port)
        self.__dim = dim
        self.__margin = margin

    def __get_dim(self):
        return self.__dim

    def __get_margin(self):
        return self.__margin

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
        loc = scene.robot_props.prop_robot_loc.xyz
        robot_type = scene.robot_props.prop_robot_type
        ip = scene.robot_props.prop_ip
        port = scene.robot_props.prop_port

        robot_type_tuple = ()
        for ENUM, enum, empty, num in robot_props.robot_types:
            if robot_type == ENUM:
                robot_type_tuple = (ENUM, enum, empty, num)

        robot = None
        if robot_type == 'ROBOMAP':
            rot = scene.myrobot_props.prop_myrobot_rotation
            dim = scene.myrobot_props.prop_myrobot_dim.xyz
            margin = scene.myrobot_props.prop_myrobot_margin.xyz
            rotation = Euler((0, pi/2, radians(rot)))
            loc.z = 0
            complete_name, area_name = draw_myrobot(context, name, loc, robot_type, rot, dim, margin, ip, port)

            robot = MyRobot(idn, complete_name, area_name, robot_type_tuple, dim, margin, ip, port)
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
        return len(RobotSet()) > 0 and not cl.isListenerActive()

    def execute(self, context):
        scene = context.scene
        for item in scene.robot_collection:
            if item.selected:
                idn = item.idn
                RobotSet().deleteRobot(idn)
                idx = scene.robot_collection.find(item.name)
                scene.robot_collection.remove(idx)
                if bpy.context.scene.selected_robot_props.prop_robot_id == idn:
                    bpy.context.scene.selected_robot_props.prop_robot_id = -1
        return {'FINISHED'}
