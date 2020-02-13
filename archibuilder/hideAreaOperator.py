import bpy
from bpy.types import Operator

def autoregister():
    bpy.utils.register_class(HideAreaOperator)
    bpy.utils.register_class(OptionsPanel)

def autounregister():
    bpy.utils.unregister_class(HideAreaOperator)
    bpy.utils.unregister_class(OptionsPanel)

is_hide = False

class HideAreaOperator(Operator):
    bl_idname = "scene.hide_margin_area"
    bl_label = 'Toggle secure margin area'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Toggle secure margin area"

    @classmethod
    def poll(cls, context):
        # Any obstacle in scene?
        return any([obj.object_type=='OBSTACLE' for obj in bpy.data.objects])

    def execute(self, context):
        global is_hide
        for obj in bpy.data.objects:
            if obj.object_type in {'OBSTACLE_MARGIN'}:
                is_hide = obj.hide_get()
                obj.hide_set(not is_hide)
        return {'FINISHED'}

class OptionsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_OptionsPanel"
    bl_label = "View"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Options" # Add new tab to N-Panel

    def draw(self, context):
        global is_hide
        layout = self.layout
        if is_hide:
            icon = 'HIDE_OFF'
            text = "Hide secure margin"
        else:
            icon = 'HIDE_ON'
            text = "Show secure margin"
        layout.operator("scene.hide_margin_area", icon=icon, text=text)
