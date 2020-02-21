import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

from math import pi, radians

def autoregister():
    bpy.utils.register_class(BeaconProps)
    bpy.types.Scene.beacon_props = bpy.props.PointerProperty(type=BeaconProps)
    bpy.utils.register_class(AddBeaconOperator)

    bpy.types.Scene.bluetooth_beacon_props = bpy.props.PointerProperty(type=BluetoothBeaconProps)
    bpy.utils.register_class(BluetoothBeaconProps)

    bpy.types.Scene.infrared_beacon_props = bpy.props.PointerProperty(type=InfraredBeaconProps)
    bpy.utils.register_class(InfraredBeaconProps)

def autounregister():
    bpy.utils.unregister_class(BeaconProps)
    del bpy.types.Scene.beacon_props
    bpy.utils.unregister_class(AddBeaconOperator)

    del bpy.types.Scene.bluetooth_beacon_props
    bpy.utils.unregister_class(BluetoothBeaconProps)

    del bpy.types.Scene.infrared_beacon_props
    bpy.utils.unregister_class(InfraredBeaconProps)

beacon_types = [("BLUETOOTH", "Bluetooth", "", 1),
                ("INFRARED", "Infrared", "", 2)]


def add_beacon(self, context):
    beacon_props = bpy.context.scene.beacon_props
    name = beacon_props.prop_beacon_name
    loc = beacon_props.prop_position.xyz
    type = beacon_props.prop_type_beacon

    if type == "BLUETOOTH":
        add_bluetooth_beacon(self, context)
    elif type == "INFRARED":
        add_infrared_beacon(self, context)

    """
    bpy.ops.object.light_add(type='POINT', location=(loc.x, loc.y, loc.z))
    beacon = bpy.context.object
    beacon.object_type = "BEACON"
    beacon.name = name

    #beacon_props.prop_rotation.x
    """

class BeaconProps(bpy.types.PropertyGroup):
    # Propiedades comunes
    prop_beacon_name: bpy.props.StringProperty(name="Name", description="Beacon name",default="Beacon", maxlen=20)
    prop_position: bpy.props.FloatVectorProperty(name="Position", description="Beacon position", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)
    prop_type_beacon: bpy.props.EnumProperty(items = beacon_types)


class BluetoothBeaconProps(bpy.types.PropertyGroup):
    prop_distance: bpy.props.FloatProperty(name="Distance", description="Distance", default=2.0, min=0.0)

def add_bluetooth_beacon(self, context):
    beacon_props = bpy.context.scene.beacon_props
    bluetooth_beacon_props = bpy.context.scene.bluetooth_beacon_props

    bpy.ops.object.light_add(type='POINT', location=(loc.x, loc.y, loc.z))
    beacon = bpy.context.object
    beacon.object_type = "BEACON"
    beacon.name = name


class InfraredBeaconProps(bpy.types.PropertyGroup):
    prop_rotation: bpy.props.FloatVectorProperty(name="Rotation", description="Beacon rotation", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3, min=-360, max=360)
    prop_distance: bpy.props.FloatProperty(name="Distance", description="Distance", default=2.0, min=0.0)
    prop_spot_size: bpy.props.FloatProperty(name="Spot size", description="Spot size", default=4.0, min=0.0, max=180)

def add_infrared_beacon(self, context):
    beacon_props = bpy.context.scene.beacon_props
    infrared_beacon_props = bpy.context.scene.infrared_beacon_props

    bpy.ops.object.light_add(type='SPOT', location=(loc.x, loc.y, loc.z))
    beacon = bpy.context.object
    beacon.object_type = "BEACON"
    beacon.name = name


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
