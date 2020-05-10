
import bpy

import communicationOperator as co
import robot as r

def autoregister():
    bpy.utils.register_class(CommunicationPanel)

def autounregister():
    bpy.utils.unregister_class(CommunicationPanel)


class CommunicationPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_CommunicationPanel"
    bl_label = "Control Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Robot Control"

    def draw(self, context):

        icon_mode = ""
        mode = context.scene.com_props.prop_mode

        if mode == co.robot_modes_summary.index("EDITOR_MODE"):
            icon_mode = "FILE_BLEND"
        if mode == co.robot_modes_summary.index("ROBOT_MODE"):
            icon_mode = "SYSTEM"

        box = self.layout.box()

        idx = context.scene.selected_robot_props.prop_robot_id
        txt = "Robot selected : " + str(r.RobotSet().getRobot(idx).name) if idx >= 0 else "No robot selected"
        txt = txt if len(r.RobotSet()) > 0 else "No robot available"

        box.label(text=txt)
        box.operator(r.SelectRobotOperator.bl_idname, icon="CURVE_PATH", text="Select robot")

        self.layout.operator(co.ChangeModeOperator.bl_idname, icon = icon_mode, text="Change mode")

        rendering = context.scene.com_props.prop_rendering
        rendering_txt = "Rendering active" if rendering else "Rendering inactive"
        icon_play = "RESTRICT_RENDER_OFF" if rendering else "RESTRICT_RENDER_ON"

        box2 = self.layout.box()
        box2.operator(co.PlayPauseRenderOperator.bl_idname, icon = icon_play, text=rendering_txt)
