
import bpy

def autoregister():
    bpy.utils.register_class(PathCreationPanel)

def autounregister():
    bpy.utils.unregister_class(PathCreationPanel)

class PathCreationPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_PathCreationPanel"
    bl_label = "Create Path"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Create Path"

    def draw(self, context):
        self.layout.operator("scene.start_poses_listener", icon="CURVE_PATH")
        self.layout.operator("scene.stop_poses_listener", icon="DISK_DRIVE")
        self.layout.operator("scene.remove_last_saved_pose", icon="TRASH")

class ToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Path creation tools"

    def draw(self, context):
        self.layout.operator("scene.save_pose", icon="IMPORT")
        self.layout.operator("scene.undo_pose", icon="LOOP_BACK")
