import bpy
import time
from mathutils import Vector, Euler
from math import radians

import connectionHandler as cnh
import datapacket as dp
import robot

import pathContainer as pc
import path

keymaps = []

def autoregister():
    global classes
    classes = [CommunicationProps, SocketModalOperator, ChangeModeOperator]
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.com_props = bpy.props.PointerProperty(type=CommunicationProps)


    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new(ChangeModeOperator.bl_idname, type='M', value='PRESS', ctrl=True)
        keymaps.append((km, kmi))

        #kmi = km.keymap_items.new(PlayPauseRenderOperator.bl_idname, type='P', value='PRESS', ctrl=True, alt=True, shift=False)
        #keymaps.append((km, kmi))


def autounregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.com_props

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()


robot_modes_summary = ["EDITOR_MODE", # 0
                       "ROBOT_MODE" # 1
                      ]

class CommunicationProps(bpy.types.PropertyGroup):
    prop_rendering: bpy.props.BoolProperty(name="Rendering", default=True)

    prop_mode : bpy.props.IntProperty(name="mode", default=0, min=0, max=len(robot_modes_summary)-1)
    prop_last_recv_packet : bpy.props.IntProperty(name="last_recv_packet", default=-1, min=-1)
    prop_last_sent_packet : bpy.props.IntProperty(name="last_sent_packet", default=-1, min=-1)

    prop_running_nav: bpy.props.BoolProperty(name="Running nav", default=False)
    prop_paused_nav: bpy.props.BoolProperty(name="Paused nav", default=False)

# SOLUTION BUG: Create and drop a cube to update gui buttons
def update_gui():
    bpy.ops.mesh.primitive_cube_add()
    bpy.data.objects.remove(bpy.context.active_object, do_unlink=True)

def toggle_deactivate_options(mode):
    sel_rob_id = bpy.context.scene.selected_robot_props.prop_robot_id

    if sel_rob_id < 0:
        return

    r = robot.RobotSet().getRobot(sel_rob_id)
    if mode == robot_modes_summary.index("ROBOT_MODE"):
        r.lock()

    if mode == robot_modes_summary.index("EDITOR_MODE"):
        r.unlock()


class SocketModalOperator(bpy.types.Operator):
    bl_idname = "wm.socket_modal"
    bl_label = "Modal Socket Operator"
    bl_description = "Create/Close robot communication link"

    _timer = None
    thread = None
    running = False

    switching = False
    error = ""

    def modal(self, context, event):
        if event.type == "TIMER":

            if self.thread is None or bpy.context.scene.com_props.prop_mode != robot_modes_summary.index("ROBOT_MODE"):
                cnh.ConnectionHandler().remove_socket()

                update_gui()
                toggle_deactivate_options(robot_modes_summary.index("EDITOR_MODE"))

                if SocketModalOperator.error != "":
                    self.report({'ERROR'}, SocketModalOperator.error)
                else:
                    self.report({'INFO'}, "socket closed")

                return {'FINISHED'}

            if not self.thread.isAlive():
                SocketModalOperator.switching = True

                context.scene.com_props.prop_last_sent_packet += 1
                new_pid = context.scene.com_props.prop_last_sent_packet
                new_mode = robot_modes_summary.index("EDITOR_MODE")
                try:
                    if not cnh.ConnectionHandler().send_mode_packet(new_pid, new_mode):
                        raise Exception("status != 1")
                    bpy.context.scene.com_props.prop_mode = robot_modes_summary.index("EDITOR_MODE")
                except Exception as e:
                    self.report({'INFO'}, "can't change to editor mode : caused by {0}".format(e))
                    self.report({'ERROR'}, "it has been switched to editor mode but not in server")
                    cnh.ConnectionHandler().remove_socket()
                    self.report({'INFO'}, "socket closed")

                SocketModalOperator.switching = False

                update_gui()
                toggle_deactivate_options(robot_modes_summary.index("EDITOR_MODE"))

                if context.scene.is_cursor_active:
                    bpy.ops.scene.stop_cursor_listener() # Paramos el editor de rutas si está activo
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    # THREAD EXECUTION
    def run(operator):
        SocketModalOperator.running = True
        while SocketModalOperator.running:
            cnh.ConnectionHandler().receive_packet()
            operator.report({'INFO'}, "THREAD")

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        SocketModalOperator.switching = True

        sel_rob_id = bpy.context.scene.selected_robot_props.prop_robot_id
        if sel_rob_id < 0:
            self.report({'ERROR'}, "No robot available")
            SocketModalOperator.switching = False
            return
        r = robot.RobotSet().getRobot(sel_rob_id)
        if r is None:
            self.report({'ERROR'}, "Robot id={0} not exists".format(sel_rob_id))
            SocketModalOperator.switching = False
            return

        cnh.ConnectionHandler().create_socket(("127.0.0.1", 1500), (r.ip, r.port))
        self.report({'INFO'}, "Socket open")

        import threading
        self.thread = threading.Thread(target=SocketModalOperator.run, args=(self,))
        self.thread.start()

        current_mode = bpy.context.scene.com_props.prop_mode
        if current_mode == robot_modes_summary.index("ROBOT_MODE"):
            #self.report({'INFO'}, "already in RoboMap mode")
            SocketModalOperator.error = "already in RoboMap mode"
            return {'RUNNING_MODAL'}

        bpy.context.scene.com_props.prop_last_sent_packet += 1
        new_pid = bpy.context.scene.com_props.prop_last_sent_packet
        new_mode = robot_modes_summary.index("ROBOT_MODE")

        try:
            if not cnh.ConnectionHandler().send_mode_packet(new_pid, new_mode):
                raise Exception("status != 1")
            bpy.context.scene.com_props.prop_mode = robot_modes_summary.index("ROBOT_MODE")
            self.report({"INFO"}, "Entered to robomap mode")
        except Exception as e:
            SocketModalOperator.error = "server unavailable {0}".format(e)
            SocketModalOperator.switching = False
            SocketModalOperator.running = False
            return {'RUNNING_MODAL'}

        SocketModalOperator.switching = False

        toggle_deactivate_options(robot_modes_summary.index("ROBOT_MODE"))

        SocketModalOperator.error = ""
        return {'RUNNING_MODAL'}


class ChangeModeOperator(bpy.types.Operator):
    bl_idname = "wm.change_mode"
    bl_label = "Change mode"
    bl_description = "Change between robot / editor"

    @classmethod
    def poll(cls, context):
        return context.scene.selected_robot_props.prop_robot_id >= 0 and not SocketModalOperator.switching

    def execute(self, context):
        if not SocketModalOperator.running:
            bpy.ops.wm.socket_modal('INVOKE_DEFAULT')
        else:
            SocketModalOperator.running = False
        return {'FINISHED'}
