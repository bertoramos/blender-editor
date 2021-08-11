
import bpy
from mathutils import Vector, Euler
from math import radians, pi

# begin local import: Change to from . import MODULE
import robot_props
import utils
import path
# end local import: Change to from . import MODULE

keymaps = []

def autoregister():
    global classes
    classes = [RobotItemForSelect, RobotItemForDelete, AddRobotOperator, DeleteRobotOperator, SelectRobotProps, SelectRobotOperator]
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.select_robot_collection = bpy.props.CollectionProperty(type=RobotItemForSelect)
    bpy.types.Scene.delete_robot_collection = bpy.props.CollectionProperty(type=RobotItemForDelete)
    bpy.types.Scene.selected_robot_props = bpy.props.PointerProperty(type=SelectRobotProps)

    RobotSet()

    # keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new(SelectRobotOperator.bl_idname, type='S', value='PRESS', ctrl=True, alt=True)
        keymaps.append((km, kmi))


def autounregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.select_robot_collection
    del bpy.types.Scene.delete_robot_collection
    del bpy.types.Scene.selected_robot_props

    RobotSet().clear()

    # keymap
    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()

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

    bpy.data.objects[robot_note].object_type = "ROBOT_NOTE"

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

    def lock(self):
        pass

    def unlock(self):
        pass

    def activeCamera(self):
        pass

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
        return Euler(bpy.data.objects[self.__name].rotation_euler[0:3])

    def __set_rotation(self, rotation):
        assert type(rotation) == Euler, "Error: expected Euler, get " + str(rotation)
        bpy.data.objects[self.__name].rotation_euler = rotation

    def __get_robot_type(self):
        return self.__robot_type

    def __get_ip(self):
        return self.__ip

    def __get_port(self):
        return self.__port

    def __get_pose(self):
        return path.Pose.fromVector(self.loc, self.rotation)

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
    pose = property(__get_pose)


def draw_myrobot(context, name, loc, robot_type, rot, dim, margin, ip, port):

    # Cuerpo
    bpy.ops.mesh.primitive_cube_add(location=(loc.x, loc.y, dim.z/2.0))
    myrobot = bpy.context.active_object
    myrobot.dimensions.xyz = dim.xyz
    myrobot.rotation_euler.z = radians(rot)
    myrobot.name = name

    myrobot.lock_location[0:3] = (False, False, True)
    myrobot.lock_rotation[0:3] = (True, True, False)
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

    myarea.object_type = "ROBOT_MARGIN"

    # icosphere
    minx = min(dim.x, dim.y)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=minx/(2*1.5), location=(loc.x, loc.y, dim.z))
    myico = bpy.context.active_object

    myico.object_type = "ROBOT"

    if myico.active_material is None:
        mat = bpy.data.materials.new("Material_robot_icosphere" + name)
        myico.active_material = mat
    mat.diffuse_color = Vector((0, 0, 1, 0.2))

    # Notas
    note_name = draw_robot_note(context, Vector((0,0,0)), myrobot.name + " | " + str(ip) + ":" + str(port), Vector((255,255,255,255)), 14, "C")
    bpy.data.objects[note_name].object_type = "ROBOT_NOTE"


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

    bpy.ops.object.camera_add(location=(loc.x, loc.y, dim.z + 0.1), rotation=(-pi/2, pi, pi/2 + myrobot.rotation_euler.z))
    camera = bpy.context.active_object
    camera.scale = Vector((0.25, 0.25, 0.25))
    camera.object_type = "ROBOT_CAMERA"

    camera.select_set(True)
    myrobot.select_set(True)
    bpy.context.view_layer.objects.active = myrobot
    bpy.ops.object.parent_set()
    camera.select_set(False)
    myrobot.select_set(False)

    camera.hide_select = True
    camera.name = myrobot.name_full + "_camera"

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

    def lock(self):
        myrobot = bpy.data.objects[super().name]
        myrobot.lock_location[0:3] = (True, True, True)
        myrobot.lock_rotation[0:3] = (True, True, True)
        myrobot.lock_scale[0:3] = (True, True, True)

        camera = bpy.data.objects[super().name + "_camera"]
        bpy.context.scene.camera = camera

    def unlock(self):
        myrobot = bpy.data.objects[super().name]
        myrobot.lock_location[0:3] = (False, False, True)
        myrobot.lock_rotation[0:3] = (True, True, False)
        myrobot.lock_scale[0:3] = (True, True, True)

    def activeCamera(self):
        bpy.context.scene.camera = bpy.data.objects[self.name + "_camera"]

    def __get_dim(self):
        return self.__dim

    def __get_margin(self):
        return self.__margin

    dim = property(__get_dim)
    margin = property(__get_margin)



"""
Operadores
"""


class SelectRobotProps(bpy.types.PropertyGroup):
    prop_robot_id: bpy.props.IntProperty(default=-1)

class SelectRobotOperator(bpy.types.Operator):
    bl_idname = "scene.select_robot"
    bl_label = "Select active robot"
    bl_description = "Choose current active robot"

    @classmethod
    def poll(cls, context):
        # begin local import:
        import robotCommunicationOperator as co
        # end local import:
        in_rob_mode = bpy.context.scene.com_props.prop_mode == co.robot_modes_summary.index("ROBOT_MODE")
        return not in_rob_mode and len(RobotSet()) > 0 and not bpy.context.scene.is_cursor_active

    def draw(self, context):
        scene = context.scene

        for item in scene.select_robot_collection:
            self.layout.prop(item, "selected", text=item.name)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):

        scene = context.scene
        for item in scene.select_robot_collection:
            if item.selected:
                idn = item.idn
                scene.selected_robot_props.prop_robot_id = idn

                robot = RobotSet().getRobot(idn)
                robot.activeCamera()

                break
        if 'idn' not in locals():
            scene.selected_robot_props.prop_robot_id = -1
        for item in scene.select_robot_collection:
            item.selected = False
        return {'FINISHED'}


def selectUpdate(self, context):
    if self.selected:
        for item in context.scene.select_robot_collection:
            if item.idn != self.idn:
                item.selected = False


class RobotItemForSelect(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Unknown")
    idn: bpy.props.IntProperty(name="Id", default=22)
    selected: bpy.props.BoolProperty(name="Selected", update=selectUpdate)

class RobotItemForDelete(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Unknown")
    idn: bpy.props.IntProperty(name="Id", default=22)
    selected: bpy.props.BoolProperty(name="Delete")

class AddRobotOperator(bpy.types.Operator):
    bl_idname = "scene.add_robot"
    bl_label = "Add Robot"
    bl_description = "Add Robot"

    @classmethod
    def poll(cls, context):
        # begin local import
        import robotCommunicationOperator as co
        # end local import
        in_rob_mode = bpy.context.scene.com_props.prop_mode == co.robot_modes_summary.index("ROBOT_MODE")
        return not in_rob_mode

    def draw(self, context):
        props = bpy.context.scene.robot_props
        self.layout.prop(props, "prop_robot_name", text="Name")
        self.layout.prop(props, "prop_robot_loc", text="Location")

        self.layout.prop(props, "prop_ip", text="Ip")
        self.layout.prop(props, "prop_port", text="Port")

        self.layout.prop(props, "prop_robot_type", text="Type")

        type = bpy.context.scene.robot_props.prop_robot_type
        if type == "ROBOMAP":
            props = bpy.context.scene.myrobot_props
            self.layout.prop(props, "prop_myrobot_rotation")
            self.layout.prop(props, "prop_myrobot_dim")
            self.layout.prop(props, "prop_myrobot_margin")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

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
            myitemselect = scene.select_robot_collection.add()
            myitemselect.name = robot.name
            myitemselect.idn = robot.idn

            myitemdelete = scene.delete_robot_collection.add()
            myitemdelete.name = robot.name
            myitemdelete.idn = robot.idn

        return {'FINISHED'}

class DeleteRobotOperator(bpy.types.Operator):
    bl_idname = "scene.delete_robot"
    bl_label = "Delete robot"
    bl_description = "Delete Robot"

    @classmethod
    def poll(cls, context):
        # begin local import:
        import robotCommunicationOperator as co
        import cursorListener as cl
        # end local import:
        in_rob_mode = bpy.context.scene.com_props.prop_mode == co.robot_modes_summary.index("ROBOT_MODE")
        return not in_rob_mode and len(RobotSet()) > 0 and not cl.isListenerActive()

    def execute(self, context):
        scene = context.scene
        for item in scene.delete_robot_collection:
            if item.selected:
                idn = item.idn
                RobotSet().deleteRobot(idn)
                idx = scene.select_robot_collection.find(item.name)
                scene.select_robot_collection.remove(idx)
                idx = scene.delete_robot_collection.find(item.name)
                scene.delete_robot_collection.remove(idx)

                # Deseleccionar robot
                if bpy.context.scene.selected_robot_props.prop_robot_id == idn:
                    bpy.context.scene.selected_robot_props.prop_robot_id = -1
        return {'FINISHED'}
