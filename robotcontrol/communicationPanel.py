
import bpy

import communicationOperator

def autoregister():
    bpy.utils.register_class(CommunicationPanel)

def autounregister():
    bpy.utils.unregister_class(CommunicationPanel)


class CommunicationPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_CommunicationPanel"
    bl_label = "Control Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CommunicationPanel"

    def draw(self, context):
        props = bpy.context.scene.mode_props

        icon_mode = ""
        mode = props.prop_mode
        if mode == "EDITOR_MODE":
            icon_mode = "FILE_BLEND"
        elif mode == "ROBOMAP_MODE":
            icon_mode = "SYSTEM"

        self.layout.operator(communicationOperator.ChangeModeOperator.bl_idname, icon=icon_mode, text="Change mode")
        #self.layout.prop(props, "prop_speed", text="Name")
        #self.layout.operator(UpdateSpeedOperator.bl_idname, text = "Update speed")
