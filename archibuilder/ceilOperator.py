
import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

def autoregister():
    bpy.utils.register_class(CeilProps)
    bpy.types.Scene.ceil_props = bpy.props.PointerProperty(type=CeilProps)
    bpy.utils.register_class(CreateAbsoluteCeilOperator)
    bpy.utils.register_class(CreateRelativeCeilOperator)

def autounregister():
    bpy.utils.unregister_class(CeilProps)
    del bpy.types.Scene.ceil_props
    bpy.utils.unregister_class(CreateAbsoluteCeilOperator)
    bpy.utils.unregister_class(CreateRelativeCeilOperator)

def create_ceil(cursor):
    scene = bpy.context.scene

    # Create plane
    bpy.ops.mesh.primitive_plane_add(location=Vector((cursor.x + 1, cursor.y + 1, cursor.z + 0.0)))
    ceil = bpy.context.object

    save_cursor_loc = bpy.context.scene.cursor.location.xyz
    bpy.context.scene.cursor.location = cursor
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    # Location
    x = scene.ceil_props.prop_loc.x
    y = scene.ceil_props.prop_loc.y
    z = scene.ceil_props.prop_loc.z
    # Dimension
    w = scene.ceil_props.prop_width
    h = scene.ceil_props.prop_height

    ceil.name = "Ceil"
    ceil.location = Vector((cursor.x + x, cursor.y + y, cursor.z + z))
    ceil.dimensions = Vector((w, h, 0))

    bpy.context.scene.cursor.location = save_cursor_loc

    if ceil.active_material is None:
        mat = bpy.data.materials.new("Material_cursor")
        ceil.active_material = mat
    mat.diffuse_color = Vector((1, 1, 1, 0.5))
    ceil.object_type = "CEIL"

class CeilProps(bpy.types.PropertyGroup):
    prop_loc: bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)
    prop_width: bpy.props.FloatProperty(min=0.0, default=2.0)
    prop_height: bpy.props.FloatProperty(min=0.0, default=2.0)

class CreateAbsoluteCeilOperator(Operator, AddObjectHelper):
    bl_idname = "mesh.create_absolute_ceil"
    bl_label = 'Create ceil (absolute position)'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add ceil in an absolute location"

    def execute(self, context):
        create_ceil(Vector((0,0,0)))
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.ceil_props
        self.layout.prop(props, "prop_loc", text="Ceil location")
        self.layout.label(text="Ceil properties")
        self.layout.prop(props, "prop_width", text="Width (x) (m)")
        self.layout.prop(props, "prop_height", text="Height (y) (m)")

class CreateRelativeCeilOperator(Operator, AddObjectHelper):
    bl_idname = "mesh.create_relative_ceil"
    bl_label = 'Create ceil (relative position)'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add ceil in a relative location"

    def execute(self, context):
        create_ceil(bpy.context.scene.cursor.location.xyz)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.ceil_props
        self.layout.prop(props, "prop_loc", text="Ceil location")
        self.layout.label(text="Ceil properties")
        self.layout.prop(props, "prop_width", text="Width (x) (m)")
        self.layout.prop(props, "prop_height", text="Height (y) (m)")
