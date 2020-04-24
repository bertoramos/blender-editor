
import bpy

def autoregister():
    bpy.utils.register_class(ModeProgram)
    bpy.types.Scene.mode_props = bpy.props.PointerProperty(type=ModeProgram)
    bpy.utils.register_class(ChangeModeOperator)
    bpy.utils.register_class(PlayOperator)

def autounregister():
    bpy.utils.unregister_class(ModeProgram)
    del bpy.types.Scene.mode_props
    bpy.utils.unregister_class(ChangeModeOperator)
    bpy.utils.unregister_class(PlayOperator)

robot_types = [("EDITOR_MODE", "EditorMode", "", 0),
               ("ROBOMAP_MODE", "RoboMapMode", "", 1)]

class ModeProgram(bpy.types.PropertyGroup):
    prop_mode: bpy.props.EnumProperty(items = robot_types, default="EDITOR_MODE")
    prop_playing: bpy.props.BoolProperty(name="Playing", default=False)

class ChangeModeOperator(bpy.types.Operator):
    bl_idname = "scene.change_mode"
    bl_label = "Change mode"
    bl_description = "Change mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        current_mode = context.scene.mode_props.prop_mode
        current_id = 0

        for MODE, mode, _, id in robot_types:
            if current_mode == MODE:
                current_id = id
        current_id += 1
        current_id = current_id % len(robot_types)

        for MODE, mode, _, id in robot_types:
            if current_id == id:
                context.scene.mode_props.prop_mode = MODE
        return {'FINISHED'}

class PlayOperator(bpy.types.Operator):
    bl_idname = "scene.play_pause_operation"
    bl_label = "Play/Pause"
    bl_description = "Play/Pause robot"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        props = context.scene.mode_props
        playing = props.prop_playing
        props.prop_playing = not playing

        return {'FINISHED'}

class StopOperator(bpy.types.Operator):
    bl_idname = "scene.stop_operation"
    bl_label = "Stop"
    bl_description = "Stop robot"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

class CurrentSpeed(bpy.types.PropertyGroup):
    speed: bpy.props.FloatProperty(name="Speed", default=25.0, min=0.0, max=100.0)

class UpdateSpeedOperator(bpy.types.Operator):
    bl_idname = "scene.update_speed"
    bl_label = "Update speed"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}
