
import bpy

import robotCommunicationOperator as co
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

        self.layout.operator(co.ChangeModeOperator.bl_idname, icon = icon_mode, text="Change mode")

        rendering = context.scene.com_props.prop_rendering
        rendering_txt = "Rendering active" if rendering else "Rendering inactive"
        icon_rendering = "RESTRICT_RENDER_OFF" if rendering else "RESTRICT_RENDER_ON"

        box2 = self.layout.box()
        box2.operator(co.ToggleRenderingOperator.bl_idname, icon = icon_rendering, text=rendering_txt)


        icon_play = "PAUSE" if context.scene.com_props.prop_running_nav and not context.scene.com_props.prop_paused_nav else "PLAY"
        play_row = box2.split()
        play_row.operator(co.StartPauseResumePlanOperator.bl_idname, icon=icon_play, text="")
        play_row.operator(co.StopPlanOperator.bl_idname, icon="CANCEL", text="")
