
import bpy
import beaconOperator as bo

def autoregister():
    bpy.utils.register_class(AddBeaconPanel)

def autounregister():
    bpy.utils.unregister_class(AddBeaconPanel)

def add_bluetooth_panel(layout):
    props = bpy.context.scene.bluetooth_beacon_props
    layout.prop(props, "prop_distance", text="Distance")

def add_ultrasound_panel(layout):
    props = bpy.context.scene.ultrasound_beacon_props
    layout.prop(props, "prop_rotation", text="Rotation")
    layout.prop(props, "prop_distance", text="Distance")
    layout.prop(props, "prop_spot_size", text="Spot size")

"""
def add_type_panel(layout):
    "" "
    Add beacon props panel
    "" "
    pass

"""

class AddBeaconPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_BeaconPanel"
    bl_label = "Beacon"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Archibuilder" # Add new tab to N-Panel

    def draw(self, context):
        props = bpy.context.scene.beacon_props
        self.layout.prop(props, "prop_beacon_name", text="Name")
        self.layout.prop(props, "prop_position", text="Position")
        self.layout.prop(props, "prop_type_beacon", text="Type")
        if props.prop_type_beacon == "BLUETOOTH":
            add_bluetooth_panel(self.layout)
        elif props.prop_type_beacon == "ULTRASOUND":
            add_ultrasound_panel(self.layout)
        """
        elif props.prop_type_beacon == "TYPE":
            add_type_panel(layout)
        """
        self.layout.operator(bo.AddBeaconOperator.bl_idname, icon='LIGHT_POINT', text="Create beacon")
