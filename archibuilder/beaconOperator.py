import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

from math import pi, radians

def autoregister():
    bpy.utils.register_class(BeaconProps)
    bpy.types.Scene.beacon_props = bpy.props.PointerProperty(type=BeaconProps)
    bpy.utils.register_class(AddBeaconOperator)

def autounregister():
    bpy.utils.unregister_class(BeaconProps)
    del bpy.types.Scene.beacon_props
    bpy.utils.unregister_class(AddBeaconOperator)

beacon_types = [("OMNIDIRECTIONAL", "Omnidirectional", "", 1),
                ("DIRECTIONAL", "Directional", "", 2)]


def add_beacon(self, context):
    beacon_props = bpy.context.scene.beacon_props
    name = beacon_props.prop_beacon_name
    loc = beacon_props.prop_position.xyz
    if beacon_props.prop_type_beacon == "OMNIDIRECTIONAL":
        bpy.ops.object.light_add(type='POINT', location=(loc.x, loc.y, loc.z))
    else:
        bpy.ops.object.light_add(type='SPOT', location=(loc.x, loc.y, loc.z))
        beacon = bpy.context.object

        beacon.rotation_euler.x = radians(beacon_props.prop_rotation.x)
        beacon.rotation_euler.y = radians(beacon_props.prop_rotation.y)
        beacon.rotation_euler.z = radians(beacon_props.prop_rotation.z)

        beacon.data.distance = beacon_props.prop_distance
        beacon.data.spot_size = radians(beacon_props.prop_spot_size)
    beacon = bpy.context.object
    beacon.name = name
    beacon.object_type = "BEACON"

class BeaconProps(bpy.types.PropertyGroup):
    # Propiedades comunes
    prop_beacon_name: bpy.props.StringProperty(name="Name", description="Beacon name",default="Beacon", maxlen=20)
    prop_position: bpy.props.FloatVectorProperty(name="Position", description="Beacon position", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)
    prop_type_beacon: bpy.props.EnumProperty(items = beacon_types)
    # Propiedades de beacon directional
    prop_rotation: bpy.props.FloatVectorProperty(name="Rotation", description="Beacon rotation", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3, min=-360, max=360)
    prop_distance: bpy.props.FloatProperty(name="Distance", description="Distance", default=2.0, min=0.0)
    prop_spot_size: bpy.props.FloatProperty(name="Spot size", description="Spot size", default=4.0, min=0.0, max=180)

class AddBeaconOperator(Operator, AddObjectHelper):
    bl_idname = "mesh.add_beacon"
    bl_label = 'Add a beacon'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add beacon"

    def execute(self, context):
        add_beacon(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.beacon_props
        self.layout.prop(props, "prop_beacon_name", text="Name")
        self.layout.prop(props, "prop_position", text="Position")
        self.layout.prop(props, "prop_type_beacon", text="Type")
        # Directional type props
        if bpy.context.scene.beacon_props.prop_type_beacon == "DIRECTIONAL":
            self.layout.prop(props, "prop_rotation", text="Rotation (degrees)")
            self.layout.prop(props, "prop_distance", text="Distance (m)")
            self.layout.prop(props, "prop_spot_size", text="Spot size (0-180º)")
