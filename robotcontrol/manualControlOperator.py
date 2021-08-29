
import bpy

# begin local import: Change to from . import MODULE
import connectionHandler as ch
import robotCommunicationOperator as rco
# end local import: Change to from . import MODULE

def autoregister():
    global classes
    classes = [ManualControlEventsOperator, ToggleManualControlOperator]
    for c in classes:
        bpy.utils.register_class(c)

def autounregister():
    global classes
    for c in classes:
        bpy.utils.unregister_class(c)

class ManualControlEventsOperator(bpy.types.Operator):
    bl_idname = "wm.manual_control_events_operator"
    bl_label = "Manual Control Events Operator"
    bl_description = "Manual Control Events Operator"

    _open = False
    _last_sent = None

    def _apply_move(self, context, value, type):
        speed = context.scene.com_props.prop_speed
        displacement = 1

        context.scene.com_props.prop_last_sent_packet += 1
        pid = context.scene.com_props.prop_last_sent_packet

        action = {('PRESS','W'): lambda : ch.ConnectionHandler().send_manual_translation_packet(pid, 0, +displacement, speed),
                  ('PRESS','S'): lambda : ch.ConnectionHandler().send_manual_translation_packet(pid, 0, -displacement, speed),
                  ('PRESS','D'): lambda : ch.ConnectionHandler().send_manual_translation_packet(pid, +displacement, 0, speed),
                  ('PRESS','A'): lambda : ch.ConnectionHandler().send_manual_translation_packet(pid, -displacement, 0, speed),
                  ('PRESS','RIGHT_ARROW'): lambda : ch.ConnectionHandler().send_manual_rotation_mode(pid, +displacement, speed),
                  ('PRESS','LEFT_ARROW'): lambda : ch.ConnectionHandler().send_manual_rotation_mode(pid, -displacement, speed)
                 }

        last_sent = ManualControlEventsOperator._last_sent
        if last_sent is not None and last_sent[0] == value and last_sent[1] == type: return {'RUNNING_MODAL'}
        if (value,type) not in action: return {'PASS_THROUGH'}

        # Send message
        rescode = action[(value,type)]()
        if rescode is not None and rescode:
            ManualControlEventsOperator._last_sent = (value, type)
            return {'RUNNING_MODAL'} # is correct
        else:
            self.report({'ERROR'}, f"Ack not received {rescode}")
            return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if not ManualControlEventsOperator._open:
            return {'FINISHED'}
        context.scene.com_props.prop_running_nav
        if ManualControlEventsOperator._open:
            if context.scene.com_props.prop_mode != rco.robot_modes_summary.index("ROBOT_MODE") or \
                context.scene.com_props.prop_running_nav:

                ManualControlEventsOperator._open = False
                return {'FINISHED'}

        return self._apply_move(context, event.value, event.type)

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ToggleManualControlOperator(bpy.types.Operator):
    bl_idname = "wm.toggle_manual_control_operator"
    bl_label = "Toggle Manual Control Operator"
    bl_description = "Toggle Manual Control Operator"

    @classmethod
    def poll(cls, context):
        return context.scene.com_props.prop_mode == rco.robot_modes_summary.index("ROBOT_MODE") and not context.scene.com_props.prop_running_nav

    def execute(self, context):
        if ManualControlEventsOperator._open:
            ManualControlEventsOperator._open = False
        else:
            ManualControlEventsOperator._open = True
            bpy.ops.wm.manual_control_events_operator('INVOKE_DEFAULT')
        return {'FINISHED'}
