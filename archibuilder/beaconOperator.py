import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from math import pi, radians

import utils

def autoregister():
    bpy.utils.register_class(BeaconProps)
    bpy.types.Scene.beacon_props = bpy.props.PointerProperty(type=BeaconProps)

    bpy.utils.register_class(BluetoothBeaconProps)
    bpy.types.Scene.bluetooth_beacon_props = bpy.props.PointerProperty(type=BluetoothBeaconProps)

    bpy.utils.register_class(UltrasoundBeaconProps)
    bpy.types.Scene.ultrasound_beacon_props = bpy.props.PointerProperty(type=UltrasoundBeaconProps)

    """
    bpy.utils.register_class(TypeBeaconProps)
    bpy.types.Scene.type_beacon_props = bpy.props.PointerProperty(type=TypeBeaconProps)
    """

    bpy.utils.register_class(AddBeaconOperator)

def autounregister():
    bpy.utils.unregister_class(BeaconProps)
    del bpy.types.Scene.beacon_props

    bpy.utils.unregister_class(BluetoothBeaconProps)
    del bpy.types.Scene.bluetooth_beacon_props

    bpy.utils.unregister_class(UltrasoundBeaconProps)
    del bpy.types.Scene.ultrasound_beacon_props

    bpy.utils.unregister_class(AddBeaconOperator)

beacon_types = [("BLUETOOTH", "Bluetooth", "", 1),
                ("ULTRASOUND", "Ultrasound", "", 2)]
            # ,("TYPE", "Type", "", 3)

class BeaconProps(bpy.types.PropertyGroup):
    # Propiedades comunes
    prop_beacon_name: bpy.props.StringProperty(name="Name", description="Beacon name",default="Beacon", maxlen=20)
    prop_position: bpy.props.FloatVectorProperty(name="Position", description="Beacon position", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3)
    prop_type_beacon: bpy.props.EnumProperty(items = beacon_types)


class BluetoothBeaconProps(bpy.types.PropertyGroup):
    prop_distance: bpy.props.FloatProperty(name="Distance", description="Distance", default=2.0, min=0.0)

def draw_bluetooth_note(context, name, loc, distance):
    color = Vector((1.0, 1.0, 1.0, 1.0))
    font = 14
    font_align = 'C'
    hint_space = 0.1
    font_rotation = 0
    text = "Distance : " + "{:.4}".format(distance) + " m "

    nota = utils.draw_text(context, name + "_note", text, loc, color, hint_space, font, font_align, font_rotation)

    bpy.data.objects[nota].lock_location[0:3] = (True, True, True)
    bpy.data.objects[nota].lock_rotation[0:3] = (True, True, True)
    bpy.data.objects[nota].lock_scale[0:3] = (True, True, True)

    return nota

def add_bluetooth_beacon(self, context):
    beacon_props = bpy.context.scene.beacon_props
    name = beacon_props.prop_beacon_name
    loc = beacon_props.prop_position.xyz

    bluetooth_beacon_props = bpy.context.scene.bluetooth_beacon_props

    bpy.ops.object.light_add(type='POINT', location=(loc.x, loc.y, loc.z))
    beacon = bpy.context.object
    beacon.object_type = "BLUETOOTH_BEACON"
    beacon.name = name

    beacon.data.distance = bluetooth_beacon_props.prop_distance

    #nota = draw_bluetooth_note(context, beacon.name, loc, beacon.data.distance)

    #bpy.data.objects[nota].parent = beacon
    #bpy.data.objects[nota].protected = True

class UltrasoundBeaconProps(bpy.types.PropertyGroup):
    prop_rotation: bpy.props.FloatVectorProperty(name="Rotation", description="Beacon rotation", default=(0.0, 0.0, 0.0), subtype='XYZ', size=3, min=-360, max=360)
    prop_distance: bpy.props.FloatProperty(name="Distance", description="Distance", default=2.0, min=0.0)
    prop_spot_size: bpy.props.FloatProperty(name="Spot size", description="Spot size", default=4.0, min=0.0, max=180)

def draw_ultrasound_note(context, name, loc, rotation, distance, spot_size):
    color = Vector((1.0, 1.0, 1.0, 1.0))
    font = 14
    font_align = 'C'
    hint_space = 0.1
    font_rotation = 0
    text = "({:.4}".format(rotation.x) + ", " + "{:.4}".format(rotation.x) + ", " + "{:.4}".format(rotation.x) + ") º|" + \
           "Distance : " + "{:.4}".format(distance) + " m |" + \
           "Spot : " + "{:.4}".format(spot_size) + " º"

    nota = utils.draw_text(context, name + "_note", text, loc, color, hint_space, font, font_align, font_rotation)

    bpy.data.objects[nota].lock_location[0:3] = (True, True, True)
    bpy.data.objects[nota].lock_rotation[0:3] = (True, True, True)
    bpy.data.objects[nota].lock_scale[0:3] = (True, True, True)

    return nota

def add_ultrasound_beacon(self, context):
    beacon_props = bpy.context.scene.beacon_props
    name = beacon_props.prop_beacon_name
    loc = beacon_props.prop_position.xyz

    ultrasound_beacon_props = bpy.context.scene.ultrasound_beacon_props

    bpy.ops.object.light_add(type='SPOT', location=(loc.x, loc.y, loc.z))
    beacon = bpy.context.object
    beacon.object_type = "ULTRASOUND_BEACON"
    beacon.name = name

    beacon.rotation_euler = ultrasound_beacon_props.prop_rotation
    beacon.data.distance = ultrasound_beacon_props.prop_distance
    beacon.data.spot_size = radians(ultrasound_beacon_props.prop_spot_size)

    #nota = draw_ultrasound_note(context, beacon.name, loc, beacon.rotation_euler, beacon.data.distance, ultrasound_beacon_props.prop_spot_size)

    #bpy.data.objects[nota].parent = beacon
    #bpy.data.objects[nota].protected = True

"""
class TypeBeaconProps(bpy.types.PropertyGroup):
    prop_1: ...
    prop_2: ...

def draw_type_beacon(data):
    " ""
    draw/update notes
    " ""

def add_type_beacon(self, context):
    " ""
    add beacon routine
    " ""
    pass

"""

beacon_add_function = {"BLUETOOTH": [add_bluetooth_beacon],
                       "ULTRASOUND": [add_ultrasound_beacon]}

class AddBeaconOperator(Operator, AddObjectHelper):
    bl_idname = "mesh.add_beacon"
    bl_label = 'Add a beacon'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add beacon"

    def execute(self, context):
        beacon_props = bpy.context.scene.beacon_props
        name = beacon_props.prop_beacon_name
        loc = beacon_props.prop_position.xyz
        type = beacon_props.prop_type_beacon

        beacon_add_function.get(type, lambda self, context: self.report({'ERROR'}, type + ' does not exist'))[0](self, context)
        return {'FINISHED'}
