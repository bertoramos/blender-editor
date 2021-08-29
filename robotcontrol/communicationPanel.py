
import bpy
import bpy.utils.previews
import os

# begin local import: Change to from . import MODULE
import robotCommunicationOperator as co
import robot as r
import simulationOperator as so
import calibrationOperator as cal_op
import manualControlOperator as mco
# end local import: Change to from . import MODULE

def autoregister():
    global preview_collections
    preview_collections = {}

    pcoll = bpy.utils.previews.new()
    # https://icons8.com/license
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pcoll.load("gamepad_line_icon", os.path.join(my_icons_dir, "gamepad_line.png"), 'IMAGE')
    pcoll.load("gamepad_filled_icon", os.path.join(my_icons_dir, "gamepad_filled.png"), 'IMAGE')

    preview_collections["main"] = pcoll

    bpy.utils.register_class(CommunicationPanel)

def autounregister():
    global preview_collections

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    bpy.utils.unregister_class(CommunicationPanel)


class CommunicationPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_CommunicationPanel"
    bl_label = "Control Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Robot Control"

    def draw(self, context):
        global preview_collections

        icon_mode = ""
        mode = context.scene.com_props.prop_mode

        if mode == co.robot_modes_summary.index("EDITOR_MODE"):
            icon_mode = "FILE_BLEND"
        if mode == co.robot_modes_summary.index("ROBOT_MODE"):
            icon_mode = "SYSTEM"

        self.layout.label(text="Communication")

        props = context.scene.com_props
        #self.layout.prop(props, "prop_client_ip", text="Client Ip")
        #self.layout.prop(props, "prop_client_port", text="Client Port")

        self.layout.operator(co.ChangeModeOperator.bl_idname, icon = icon_mode, text="Change mode")

        rendering = context.scene.com_props.prop_rendering
        rendering_txt = "Rendering active" if rendering else "Rendering inactive"
        icon_rendering = "RESTRICT_RENDER_OFF" if rendering else "RESTRICT_RENDER_ON"


        self.layout.operator(co.ToggleRenderingOperator.bl_idname, icon = icon_rendering, text=rendering_txt)
        self.layout.label(text="Control panel")

        self.layout.operator(cal_op.CalibrateOperator.bl_idname, icon="UV_SYNC_SELECT")
        self.layout.operator(cal_op.DropAllStaticBeacons.bl_idname, icon="TRASH")

        box_com = self.layout.box()
        icon_play = "PAUSE" if context.scene.com_props.prop_running_nav and not context.scene.com_props.prop_paused_nav else "PLAY"
        play_row = box_com.split()
        play_row.operator(co.StartPauseResumePlanOperator.bl_idname, icon=icon_play, text="")
        play_row.operator(co.StopPlanOperator.bl_idname, icon="CANCEL", text="")

        speed_lab = "Speed : " + "{0:.2f}".format(context.scene.com_props.prop_speed) + " %"
        box_com.label(text=speed_lab)
        box_com.operator(co.ChangeSpeedOperator.bl_idname, icon="ANIM_DATA", text="Change speed")


        manual_control_button_text = "Open manual control" if not mco.ManualControlEventsOperator._open else "Close manual control"

        pcoll = preview_collections["main"]
        gamepad_line_icon = pcoll["gamepad_line_icon"]
        gamepad_filled_icon = pcoll["gamepad_filled_icon"]

        icon_value = gamepad_line_icon.icon_id if not mco.ManualControlEventsOperator._open else gamepad_filled_icon.icon_id
        self.layout.operator(mco.ToggleManualControlOperator.bl_idname, text=manual_control_button_text, icon_value=icon_value)

        # SIMULATION:

        icon_sim = "PLAY"
        text_sim = "Simulate" if not so.SimulationOperator.active else "Press esc to stop"

        pause_icon = "PAUSE" if not so.SimulationOperator.pause else "PLAY"
        pause_text = "Pause" if not so.SimulationOperator.pause else "Resume"

        self.layout.label(text="Simulation panel")

        box_sim = self.layout.box()
        row_sim = box_sim.split()
        row_sim.operator(so.SimulationOperator.bl_idname, icon=icon_sim, text=text_sim)
        row_sim.operator(so.PauseResumeSimulation.bl_idname, icon=pause_icon, text=pause_text)

        speed_lab = "Speed : " + "{0:.2f}".format(context.scene.sim_props.prop_simulated_speed) + " %"
        box_sim.label(text=speed_lab)
        box_sim.operator(so.ChangeSpeedSimulationOperator.bl_idname, icon="ANIM_DATA", text="Change speed")
