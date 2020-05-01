
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
    bl_label = "Create path"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Robot Control"

    def draw(self, context):

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
        self.layout.operator(pe.MoveCursorToLastPoseOperator.bl_idname, icon="REW")
