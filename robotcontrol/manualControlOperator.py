

from pathlib import Path
import sys
import ctypes
ctypes.CDLL(str(Path(sys.executable).parent / Path('hidapi.dll')))
import hid

import numpy as np

class Gamepad:

    def __init__(self, vendor=0x0079, product=0x0006):
        self.gamepad = hid.Device(vendor, product)
        self.gamepad.nonblocking = True

    
    def read(self):
        report = list(self.gamepad.read(3200))
        if not report:
            return {}

        x_button = ((report[5] & 0b10000000) >> 7) == 1
        a_button = ((report[5] & 0b01000000) >> 6) == 1
        b_button = ((report[5] & 0b00100000) >> 5) == 1
        y_button = ((report[5] & 0b00010000) >> 4) == 1

        x_left, y_left = self.__remap_joy(report[0], report[1], precision=0.5)
        x_right, y_right = self.__remap_joy(report[3], report[4], precision=0.5)

        return {
            'x_button': x_button,
            'y_button': y_button,
            'a_button': a_button,
            'b_button': b_button,
            'left_joystick': (x_left, y_left),
            'right_joystick': (x_right, y_right)
        }

    def __maprange(self, a, b, s):
        (a1, a2), (b1, b2) = a, b
        return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

    def __normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: 
            return v
        return v / norm

    def __remap_joy(self, rx, ry, precision=0):
        x, y = rx, ry
        x = self.__maprange((0, 255), (-1, 1), x)
        y = self.__maprange((0, 255), (1, -1), y)
        direction = np.array([x, y])
        if np.linalg.norm(direction) < precision:
            return 0, 0
        [x, y] = self.__normalize(direction)
        return x, y

########################################################################################

import bpy
import mathutils
import math

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
    
        pid = context.scene.com_props.prop_last_sent_packet + 1
        
        action = {('PRESS','W'): lambda : ch.ConnectionHandler().send_manual_translation_packet(pid, 0, +displacement, speed),
                  ('PRESS','S'): lambda : ch.ConnectionHandler().send_manual_translation_packet(pid, 0, -displacement, speed),
                  ('PRESS','D'): lambda : ch.ConnectionHandler().send_manual_translation_packet(pid, +displacement, 0, speed),
                  ('PRESS','A'): lambda : ch.ConnectionHandler().send_manual_translation_packet(pid, -displacement, 0, speed),
                  ('PRESS','RIGHT_ARROW'): lambda : ch.ConnectionHandler().send_manual_rotation_packet(pid, +displacement, speed),
                  ('PRESS','LEFT_ARROW'): lambda : ch.ConnectionHandler().send_manual_rotation_packet(pid, -displacement, speed),
                  ('RELEASE', 'W'): lambda: ch.ConnectionHandler().send_manual_stop_packet(pid),
                  ('RELEASE', 'S'): lambda: ch.ConnectionHandler().send_manual_stop_packet(pid),
                  ('RELEASE', 'D'): lambda: ch.ConnectionHandler().send_manual_stop_packet(pid),
                  ('RELEASE', 'A'): lambda: ch.ConnectionHandler().send_manual_stop_packet(pid),
                  ('RELEASE', 'RIGHT_ARROW'): lambda: ch.ConnectionHandler().send_manual_stop_packet(pid),
                  ('RELEASE', 'LEFT_ARROW'): lambda: ch.ConnectionHandler().send_manual_stop_packet(pid)
                 }
    
        last_sent = ManualControlEventsOperator._last_sent
        if last_sent is not None and last_sent[0] == value and last_sent[1] == type: return {'RUNNING_MODAL'}
        if (value,type) not in action: return {'PASS_THROUGH'}
    
        # Send message
        rescode = action[(value,type)]()
        print("ACK rescode from send translation ", rescode)
        context.scene.com_props.prop_last_sent_packet = pid
        ManualControlEventsOperator._last_sent = (value, type)
        if rescode is not None and rescode:
            return {'RUNNING_MODAL'} # is correct
        else:
            self.report({'ERROR'}, f"WARNING: Robot could not be stopped")
            return {'RUNNING_MODAL'}

    def _send_translation(self, context, x, y):
        speed = context.scene.com_props.prop_speed
        pid = context.scene.com_props.prop_last_sent_packet + 1

        rescode = ch.ConnectionHandler().send_manual_translation_packet(pid, x, y, speed)

        context.scene.com_props.prop_last_sent_packet = pid

        if rescode is not None and rescode:
            return {'RUNNING_MODAL'} # is correct
        else:
            self.report({'ERROR'}, f"WARNING: Robot could not be translated")
            return {'RUNNING_MODAL'}
    
    def _send_rotation(self, context, rotation):
        speed = context.scene.com_props.prop_speed
        pid = context.scene.com_props.prop_last_sent_packet + 1

        rescode = ch.ConnectionHandler().send_manual_rotation_packet(pid, rotation, speed)
        
        context.scene.com_props.prop_last_sent_packet = pid

        if rescode is not None and rescode:
            return {'RUNNING_MODAL'} # is correct
        else:
            self.report({'ERROR'}, f"WARNING: Robot could not be rotated")
            return {'RUNNING_MODAL'}
    
    def _send_stop(self, context):
        pid = context.scene.com_props.prop_last_sent_packet + 1

        rescode = ch.ConnectionHandler().send_manual_stop_packet(pid)
        
        context.scene.com_props.prop_last_sent_packet = pid

        if rescode is not None and rescode:
            return {'RUNNING_MODAL'} # is correct
        else:
            self.report({'ERROR'}, f"WARNING: Robot could not be stopped")
            return {'RUNNING_MODAL'}

    def _update_pose(self, context, event):

        rotation_matrix = lambda angle : mathutils.Matrix([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
        

        if not self.gamepad_on:
            if event.value == "PRESS":
                angle_inc = 1
                if event.type == "K":
                    self.direction.rotate(rotation_matrix(math.radians(angle_inc)))
                if event.type == "L":
                    self.direction.rotate(rotation_matrix(math.radians(-angle_inc)))
            
            if event.value == "PRESS":
                if event.type == "W":
                    self.direction = mathutils.Vector((+0, +1))
                if event.type == "S":
                    self.direction = mathutils.Vector((+0, -1))
                if event.type == "A":
                    self.direction = mathutils.Vector((-1, +0))
                if event.type == "D":
                    self.direction = mathutils.Vector((+1, +0))
        
            if event.value == "PRESS":
                if event.type == "V":
                    self.gear = not self.gear
            
            if event.value == "PRESS":
                if event.type == "LEFT_ARROW":
                    self.gear = False
                    self._send_rotation(context, -1)
                if event.type == "RIGHT_ARROW":
                    self.gear = False
                    self._send_rotation(context, +1)
            if event.value == "RELEASE":
                if event.type in {"LEFT_ARROW", "RIGHT_ARROW"}:
                    self.gear = False
                    self._send_stop(context)
                
        if event.value == "PRESS":
            if event.type == "P":
                self.gear = False
                self.gamepad_on = not self.gamepad_on
                self._send_stop(context)

                self.direction = mathutils.Vector((+0, +1))

        if event.type == 'TIMER':

            if self.gamepad_on:
                # Gamepad direction
                report = self.gamepad.read()
                if report:
                    self.direction = mathutils.Vector(report["left_joystick"])
                    if self.direction.length > 0:
                        self.gear = True
                    else:
                        self.gear = False
                    
                    if report['x_button'] == True:
                        self.gear = False
                        self._send_rotation(context, -1)
                    if report['b_button'] == True:
                        self.gear = False
                        self._send_rotation(context, +1)

                    if self.prev_report is not None:
                        # Release button
                        if report['x_button'] == False and self.prev_report["x_button"] == True:
                            self._send_stop(context)
                        if report['y_button'] == False and self.prev_report["y_button"] == True:
                            self._send_stop(context)

                    self.prev_report = report
            
            # Update
            if self.gear:
                self._send_translation(context, self.direction[0], self.direction[1])
            else:
                self._send_stop(context)

            return {"RUNNING_MODAL"}

        # Ensure modal return
        if event.value in {"PRESS", "RELEASE"}:
            if event.type in {"P", 'LEFT_ARROW', 'RIGHT_ARROW', "V", "A", "W", "S", "D", "K", "L"}:
                return {"RUNNING_MODAL"}
        
        return {'PASS_THROUGH'}
    

    def modal(self, context, event):
        if not ManualControlEventsOperator._open:
            return {'FINISHED'}
        context.scene.com_props.prop_running_nav
        if ManualControlEventsOperator._open:
            if context.scene.com_props.prop_mode != rco.robot_modes_summary.index("ROBOT_MODE") or \
                context.scene.com_props.prop_running_nav:

                ManualControlEventsOperator._open = False
                return {'FINISHED'}

        return self._update_pose(context, event)
        #return self._apply_move(context, event.value, event.type)

    def execute(self, context):
        self.gamepad = Gamepad(0x0079, 0x0006)
        self.direction = mathutils.Vector((0, 1))
        self.gear = False
        self.gamepad_on = True
        self.prev_report = None

        self.robot = context.object

        self.report({'INFO'}, "JOYSTICK " + "ON" if self.gamepad_on else "OFF")

        #context.window_manager.modal_handler_add(self)
        millis_to_sec = lambda t : t / 1000

        wm = context.window_manager
        self._timer = wm.event_timer_add(millis_to_sec(300), window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


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
