
import bpy

import wallOperator as wo
import ceilOperator as co

def autoregister():
    bpy.utils.register_class(EnvironmentBuildPanel)

def autounregister():
    bpy.utils.unregister_class(EnvironmentBuildPanel)

class EnvironmentBuildPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_EnvironmentBuildPanel"
    bl_label = "Environment Builder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Archibuilder" # Add new tab to N-Panel

    def draw(self, context):
        layout = self.layout
        row0 = layout.row()
        row0.label(text="Absolute")
        row0.label(text="Relative")
        row1 = layout.row()
        row1.operator(wo.CreateAbsoluteWallOperator.bl_idname, icon='MOD_BUILD', text="Create wall (absolute position)")
        row1.operator(wo.CreateRelativeWallOperator.bl_idname, icon='MOD_BUILD', text="Create wall (relative position)")
        row2 = layout.row()
        row2.operator(co.CreateAbsoluteCeilOperator.bl_idname, icon='MESH_PLANE', text="Create ceil (absolute position)")
        row2.operator(co.CreateRelativeCeilOperator.bl_idname, icon='MESH_PLANE', text="Create ceil (relative position)")
        row3 = layout.row()
        layout.operator(wo.CreateAbsoluteRoomOperator.bl_idname, icon='AXIS_TOP', text="Create room")
