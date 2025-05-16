

import json
from pathlib import Path
import sys
import ctypes
ctypes.CDLL(str(Path(sys.executable).parent / Path('hidapi.dll')))
import hid

import numpy as np

import bpy
import mathutils
import math

import copy

# begin local import: Change to from . import MODULE
import connectionHandler as ch
import robotCommunicationOperator as rco
# end local import: Change to from . import MODULE

from collections import namedtuple
EventContainer = namedtuple("EventContainer", "type value")

def autoregister():
    global classes
    classes = [ManualControlEventsOperator, ToggleManualControlOperator]
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.manual_control_selected_device = bpy.props.StringProperty(name="manual_control_selected_device_name", description="Manual Control Selected Device", default="{}")
    
def autounregister():
    global classes
    for c in classes:
        bpy.utils.unregister_class(c)
    
    del bpy.types.Scene.manual_control_selected_device

##################################################################
# GAMEPAD
##################################################################

def _maprange(a, b, s):
        (a1, a2), (b1, b2) = a, b
        return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def _normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
        return v
    return v / norm

def _remap_joy(rx, ry, precision=0):
    x, y = rx, ry
    x = _maprange((0, 255), (-1, 1), x)
    y = _maprange((0, 255), (1, -1), y)
    direction = np.array([x, y])
    if np.linalg.norm(direction) < precision:
        return 0, 0
    [x, y] = _normalize(direction)
    return x, y

class Gamepad:

    def __init__(self, vid, pid):
        self.__dev = hid.Device(vid, pid)
        self.__dev.nonblocking = True
        self.__last_report = {
            "joyL": (0.0, 0.0),
            "joyR": (0.0, 0.0),
            "A": False,
            "B": False,
            "X": False,
            "Y": False,
            "L": False,
            "R": False,
            "START": False,
            "BACK": False
        }

    def read(self):
        new_report = copy.deepcopy(self.__last_report)
        data = list(self.__dev.read(3200))
        if data:
            # joystick
            jl_y, jl_x = data[3], data[1]
            jr_y, jr_x = data[7], data[5]
            new_report["joyL"] = _remap_joy(jl_x, jl_y, precision=0.5)
            new_report["joyR"] = _remap_joy(jr_x, jr_y, precision=0.5)

            # buttons
            buttons_byte = data[10]
            new_report["A"]     = ( buttons_byte & 0b0000_0001 ) > 0
            new_report["B"]     = ( buttons_byte & 0b0000_0010 ) > 0
            new_report["X"]     = ( buttons_byte & 0b0000_0100 ) > 0
            new_report["Y"]     = ( buttons_byte & 0b0000_1000 ) > 0
            new_report["L"]     = ( buttons_byte & 0b0001_0000 ) > 0
            new_report["R"]     = ( buttons_byte & 0b0010_0000 ) > 0
            new_report["START"] = ( buttons_byte & 0b0100_0000 ) > 0
            new_report["BACK"]  = ( buttons_byte & 0b1000_0000 ) > 0
        
        last_report = copy.deepcopy(self.__last_report)

        self.__last_report = new_report
        
        return new_report, last_report
    
    def close(self):
        self.__dev.close()


##################################################################

class ManualControlEventsOperator(bpy.types.Operator):
    bl_idname = "wm.manual_control_events_operator"
    bl_label = "Manual Control Events Operator"
    bl_description = "Manual Control Events Operator"

    _open = False
    _last_processed_event = None

    _timer = None

    _vid = None
    _pid = None

    # Running globals
    _direction = mathutils.Vector((0, 1))
    _rotation_displacement = 0
    _gear = False
    _prev_gear = False
    _prev_timer_gear = False
    _gamepad = None

    def _send_translation(self, context, vx, vy, speed):        
        pid = context.scene.com_props.prop_last_sent_packet + 1
        rescode = ch.ConnectionHandler().send_manual_translation_packet(pid, vx, vy, speed)

        context.scene.com_props.prop_last_sent_packet = pid

        return rescode is not None and rescode
    
    def _send_rotation(self, context, rotation, speed):
        pid = context.scene.com_props.prop_last_sent_packet + 1
        rescode = ch.ConnectionHandler().send_manual_rotation_packet(pid, rotation, speed)

        context.scene.com_props.prop_last_sent_packet = pid

        return rescode is not None and rescode
    
    def _send_stop(self, context):
        pid = context.scene.com_props.prop_last_sent_packet + 1
        rescode = ch.ConnectionHandler().send_manual_stop_packet(pid)

        context.scene.com_props.prop_last_sent_packet = pid

        return rescode is not None and rescode
    
    def _timer_handler(self, context):

        if self._gamepad is not None: # Esta activo el gamepad
            report, prev_report = self._gamepad.read()
            joyL = report["joyL"]
            self._direction = mathutils.Vector(joyL)
            
            self._gear = self._direction.length > 0 # Para si el joystick está suelto

            if report["L"]: # L está presionado
                self._rotation_displacement = -1
                self._gear = True
            elif report["L"] != prev_report["L"]: # Se soltó L (L no está presionado y antes lo estaba)
                self._rotation_displacement = 0
                self._gear = False
            
            if report["R"]: # R está presionado
                self._rotation_displacement = +1
                self._gear = True
            elif report["R"] != prev_report["R"]: # Se soltó R (R no está presionado y antes lo estaba)
                self._rotation_displacement = 0
                self._gear = False
            
            if report["A"] or report["B"] or report["X"] or report["Y"]:
                self._gear = False
        
        speed = context.scene.com_props.prop_speed

        rescode = True
        # Update pose
        if self._gear == False and self._prev_timer_gear != self._gear: # Si se ha solicitado pararlo y anteriormente no se paró
            rescode = self._send_stop(context)
            print("PARADA")
        rotation_sent = False
        if self._gear == True:
            if self._rotation_displacement != 0: # Si el desplazamiento a realizar es mayor a 0
                rescode = self._send_rotation(context, self._rotation_displacement, speed)
                rotation_sent = True
                print(f"ROTACION {self._rotation_displacement}")
            
            if self._direction.length > 0: # Si el vector de direccion tiene longitud mayor a 0
                if not rotation_sent:
                    rescode = self._send_translation(context, self._direction[0], self._direction[1], speed)
                    print(f"MOVIMIENTO {self._direction[0]}, {self._direction[1]}")
            else: # Si no se para el robot
                rescode = self._send_stop(context)
                print("PARADA")
        self._prev_timer_gear = self._gear
        #print(rescode)
    
    def _event_handler(self, context, event):
        # Lambda utils
        def set_direction(vx, vy): self._direction = mathutils.Vector((vx, vy))
        def set_rotation_displacement(angle): self._rotation_displacement=angle
        def set_gear(value): self._gear=value
        rotation_matrix = lambda angle : mathutils.Matrix([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])

        value, type = event.value, event.type
        
        angle_inc = 1
        keyboard_action = {('PRESS','W'): lambda : [set_direction(+0, +1)],
                  ('PRESS','S'): lambda : [set_direction(+0, -1)],
                  ('PRESS','D'): lambda : [set_direction(+1, +0)],
                  ('PRESS','A'): lambda : [set_direction(-1, +0)],
                  ('PRESS', 'K'): lambda : [self._direction.rotate(rotation_matrix(math.radians(angle_inc)))],
                  ('PRESS', 'L'): lambda : [self._direction.rotate(rotation_matrix(math.radians(-angle_inc)))],
                  ('PRESS', 'V'): lambda : [set_gear(False if self._gear else True)],
                  ('PRESS','RIGHT_ARROW'): lambda : [set_rotation_displacement(+1), set_gear(True)],
                  ('PRESS','LEFT_ARROW'): lambda : [set_rotation_displacement(-1), set_gear(True)],
                  ('RELEASE', 'RIGHT_ARROW'): lambda: [set_rotation_displacement(+0), set_gear(False)],
                  ('RELEASE', 'LEFT_ARROW'): lambda: [set_rotation_displacement(+0), set_gear(False)],
                 }

        last_processed_event = ManualControlEventsOperator._last_processed_event

        if event.type!="TIMER": # ** TIMER se procesa siempre
            # Si ya ha sido procesado no se procesa de nuevo (**Excepto TIMER)
            if last_processed_event is not None and \
                last_processed_event.value == value and last_processed_event.type == type: return {'RUNNING_MODAL'}
            # Se ignoran los eventos no utilizados (**Excepto TIMER)
            if (value,type) not in keyboard_action: return {'PASS_THROUGH'}
        
        self._prev_gear = self._gear
        if self._gamepad is None and (value, type) in keyboard_action:
            keyboard_action[(value, type)]()
        
        if event.type == "TIMER":
            self._timer_handler(context) # Handle gamepad and/or update pose

        ManualControlEventsOperator._last_processed_event = EventContainer(type=event.type, value=event.value)

        return {"RUNNING_MODAL"}
    
    def modal(self, context, event):
        if not ManualControlEventsOperator._open:
            if self._gamepad:
                try:
                    self._gamepad.close()
                except:
                    pass
            return {'FINISHED'}
        context.scene.com_props.prop_running_nav
        if ManualControlEventsOperator._open:
            if context.scene.com_props.prop_mode != rco.robot_modes_summary.index("ROBOT_MODE") or \
                context.scene.com_props.prop_running_nav:

                ManualControlEventsOperator._open = False

                if self._gamepad:
                    try:
                        self._gamepad.close()
                    except:
                        pass
                return {'FINISHED'}

        return self._event_handler(context, event)

    def execute(self, context):        
        
        selected_device = json.loads(context.scene.manual_control_selected_device)
        self._vid = selected_device["vendor_id"]
        self._pid = selected_device["product_id"]
        
        if self._vid is not None and self._pid is not None:
            # open gamepad
            self._gamepad = Gamepad(self._vid, self._pid)
        else:
            self._gamepad = None
        
        # Run timer
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.3, window=context.window) # 300ms
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        if self._timer is not None:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)


class ToggleManualControlOperator(bpy.types.Operator):
    bl_idname = "wm.toggle_manual_control_operator"
    bl_label = "Toggle Manual Control Operator"
    bl_description = "Toggle Manual Control Operator"

    
    def get_available_devices(scene, context):
        available_devices = [
            (json.dumps({
                "product_string": e["product_string"],
                "vendor_id": e["vendor_id"],
                "product_id": e["product_id"]
            }), e["product_string"], "", i)
            for i, e in enumerate(hid.enumerate())
        ]

        keyboard_tag = json.dumps({"product_string": "Keyboard",
                                   "vendor_id": None,
                                   "product_id": None})
        available_devices += [(keyboard_tag, "Keyboard", "", len(available_devices) + 1)]
        return available_devices

    prop_available_devices: bpy.props.EnumProperty(items = get_available_devices)
    
    def invoke(self, context, event):
        if not ManualControlEventsOperator._open:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)

    @classmethod
    def poll(cls, context):
        return context.scene.com_props.prop_mode == rco.robot_modes_summary.index("ROBOT_MODE") and\
            not context.scene.com_props.prop_running_nav
    
    def execute(self, context):
        if ManualControlEventsOperator._open:
            ManualControlEventsOperator._open = False
            context.scene.manual_control_selected_device = "{}"
        else:
            ManualControlEventsOperator._open = True
            context.scene.manual_control_selected_device = self.prop_available_devices
            # print("Toggle says : ", str(self.available_devices), type(self.available_devices))
            bpy.ops.wm.manual_control_events_operator('INVOKE_DEFAULT')
        return {'FINISHED'}
