
import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from math import sin, cos, atan, radians, degrees, sqrt, pi

def autoregister():
    bpy.utils.register_class(ObstacleProps)
    bpy.types.Scene.obstacle_props = bpy.props.PointerProperty(type=ObstacleProps)
    bpy.utils.register_class(AddObstacleOperator)

def autounregister():
    bpy.utils.unregister_class(ObstacleProps)
    del bpy.types.Scene.obstacle_props
    bpy.utils.unregister_class(AddObstacleOperator)

def add_obstacle(self, context, name, size, margin, r, g, b, a):
    bpy.ops.mesh.primitive_cube_add()
    obstacle = bpy.context.selected_objects[0]
    obstacle.name = name

    # Cambiar tamaño del objeto
    obstacle.dimensions = Vector((size.x, size.y, size.z))

    # Colocar objeto a ras de suelo teniendo en cuenta sus dimensiones
    inc_z_location = size.z/2
    obstacle.location.z += inc_z_location

    obstacle.object_type = 'OBSTACLE'

    if obstacle.active_material is None:
        mat = bpy.data.materials.new("Material_" + name)
        obstacle.active_material = mat
    mat.diffuse_color = Vector((r, g, b, a))

    # Añadimos margen de seguridad
    x_dim = size.x + 2.0 * margin.x/100.0 * size.x
    y_dim = size.y + 2.0 * margin.y/100.0 * size.y
    z_dim = size.z + 2.0 * margin.z/100.0 * size.z

    bpy.ops.mesh.primitive_cube_add()
    area = bpy.context.active_object
    area.name = 'margin' + name

    area.dimensions = Vector((x_dim, y_dim, z_dim))

    if area.active_material is None:
        mat = bpy.data.materials.new("Material_margin" + name)
        area.active_material = mat
    mat.diffuse_color = Vector((0, 0, 0, 0.2))

    # Centrar area al objeto
    # Parent set
    area.location.z += inc_z_location
    area.object_type = 'OBSTACLE_MARGIN'

    area.select_set(True)
    obstacle.select_set(True)

    bpy.context.view_layer.objects.active = obstacle

    bpy.ops.object.parent_set()

    area.select_set(False)
    obstacle.select_set(False)

    area.hide_select = True


class ObstacleProps(bpy.types.PropertyGroup):
    prop_obstacle_name: bpy.props.StringProperty(name="Name", description="Object name",default="Object", maxlen=20)
    prop_type: bpy.props.IntProperty(name="type", default=0)
    prop_size: bpy.props.FloatVectorProperty(name="Dimensions", description="Object dimensions", default=(1.0, 1.0, 1.0), subtype='XYZ', size=3, min=0.0)
    prop_margin: bpy.props.FloatVectorProperty(name="Secure margin", description="Object secure margin", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3, min=0.0)
    prop_color: bpy.props.FloatVectorProperty(name="myColor", subtype="COLOR", size=4, min=0.0, max=1.0, default=(1.0, 1.0, 1.0, 1.0))

class AddObstacleOperator(Operator, AddObjectHelper):
    bl_idname = "mesh.add_obstacle"
    bl_label = 'Add an object'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add an obstacle into scenario"

    def execute(self, context):
        scene = bpy.context.scene
        name = scene.obstacle_props.prop_obstacle_name
        size = scene.obstacle_props.prop_size.xyz
        margin = scene.obstacle_props.prop_margin.xyz
        r = scene.obstacle_props.prop_color[0]
        g = scene.obstacle_props.prop_color[1]
        b = scene.obstacle_props.prop_color[2]
        a = scene.obstacle_props.prop_color[3]
        add_obstacle(self, context, name, size, margin, r, g, b, a)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.obstacle_props
        self.layout.prop(props, "prop_obstacle_name", text="Name")
        self.layout.label(text="Object properties")
        self.layout.prop(props, "prop_size", text="Dimensions (m)")
        self.layout.prop(props, "prop_margin", text="Margin (%)")
        self.layout.prop(props, "prop_color", text="Color")
