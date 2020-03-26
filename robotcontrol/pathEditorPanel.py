
import bpy
import cursorListener as cl
import pathEditor as pe
import robot as robot_tools

def autoregister():
    bpy.utils.register_class(PathCreationPanel)
    bpy.utils.register_class(ToolsPanel)

def autounregister():
    bpy.utils.unregister_class(PathCreationPanel)
    bpy.utils.unregister_class(ToolsPanel)

class PathCreationPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_PathCreationPanel"
    bl_label = "Create Path"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Robot Control"

    def draw(self, context):
        box = self.layout.box()

        idx = context.scene.selected_robot_props.prop_robot_id
        txt = "Robot selected : " + str(idx) if idx >= 0 else "No robot selected"
        txt = txt if len(robot_tools.RobotSet()) > 0 else "No robot available"

        box.label(text=txt)
        box.operator(pe.SelectRobotForPathOperator.bl_idname, icon="CURVE_PATH", text="Select robot")
        self.layout.operator(cl.StartPosesListener.bl_idname, icon="CURVE_PATH", text="Start editor")
        self.layout.operator(cl.StopPosesListener.bl_idname, icon="DISK_DRIVE", text="Stop editor (Save poses)")
        self.layout.operator(pe.RemoveLastSavedPoseOperator.bl_idname, icon="GPBRUSH_ERASE_STROKE")

class ToolsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_ToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Path creation tools"

    @classmethod
    def poll(cls, context):
        # Cursor active?
        return any([scene.is_cursor_active for scene in bpy.data.scenes])

    def draw(self, context):
        self.layout.operator(pe.SavePoseOperator.bl_idname, icon="IMPORT")
        self.layout.operator(pe.UndoPoseOperator.bl_idname, icon="LOOP_BACK")
        box = self.layout.box()
        props = bpy.context.scene.pose_props
        box.prop(props, "prop_speed", text="Speed")
        self.layout.operator(pe.MoveCursorToLastPoseOperator.bl_idname, icon="REW")

"""
class RobotPropsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_RobotPropsPanel"
    bl_label = "Robot Props"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Robot Control"

    def draw(self, context):
        props = bpy.context.scene.robot_props
        self.layout.label(text="Robot size")
        self.layout.prop(props, "prop_height", text="Height")
        self.layout.prop(props, "prop_margin_height", text="Safety height margin")
        self.layout.prop(props, "prop_width", text="Width")
        self.layout.prop(props, "prop_margin_width", text="Safety width margin")
        self.layout.prop(props, "prop_length", text="Length")
        self.layout.prop(props, "prop_margin_length", text="Safety length margin")
"""
