import bpy
from bpy.types import Operator

def autoregister():
    bpy.utils.register_class(HideAreaOperator)
    bpy.utils.register_class(HideCeilOperator)
    bpy.utils.register_class(OptionsPanel)

def autounregister():
    bpy.utils.unregister_class(HideAreaOperator)
    bpy.utils.register_class(HideCeilOperator)
    bpy.utils.unregister_class(OptionsPanel)

is_hide_area = False

class HideAreaOperator(Operator):
    bl_idname = "scene.hide_margin_area"
    bl_label = 'Toggle secure margin area view'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Toggle secure margin area"

    @classmethod
    def poll(cls, context):
        # Any obstacle in scene?
        return any([obj.object_type=='OBSTACLE_MARGIN' for obj in bpy.data.objects])

    def execute(self, context):
        global is_hide_area
        for obj in bpy.data.objects:
            if obj.object_type in {'OBSTACLE_MARGIN'}:
                is_hide_area = obj.hide_get()
                obj.hide_set(not is_hide_area)
                is_hide_area = not is_hide_area
        return {'FINISHED'}

is_hide_ceil = False

class HideCeilOperator(Operator):
    bl_idname = "scene.hide_ceil"
    bl_label = 'Toggle ceil view'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Toggle ceil view"

    @classmethod
    def poll(cls, context):
        # Any obstacle in scene?
        return any([obj.object_type=='CEIL' for obj in bpy.data.objects])

    def execute(self, context):
        global is_hide_ceil
        for obj in bpy.data.objects:
            if obj.object_type in {'CEIL'}:
                is_hide_ceil = obj.hide_get()
                obj.hide_set(not is_hide_ceil)
                is_hide_ceil = not is_hide_ceil
        return {'FINISHED'}

class OptionsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_OptionsPanel"
    bl_label = "View"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Options" # Add new tab to N-Panel

    def draw(self, context):
        global is_hide_area
        layout = self.layout
        if not is_hide_area:
            icon = 'HIDE_OFF'
            text = "Hide secure margin"
        else:
            icon = 'HIDE_ON'
            text = "Show secure margin"
        layout.operator("scene.hide_margin_area", icon=icon, text=text)

        global is_hide_ceil
        if not is_hide_ceil:
            icon = 'HIDE_OFF'
            text = "Hide ceil"
        else:
            icon = 'HIDE_ON'
            text = "Show ceil"
        layout.operator("scene.hide_ceil", icon=icon, text=text)
