
import bpy
import time
from mathutils import Vector, Euler
from math import radians

import connection_handler as cnh
import datapacket as dp
import robot

keymaps = []

def autoregister():
    bpy.utils.register_class(CommunicationProps)
    bpy.types.Scene.com_props = bpy.props.PointerProperty(type=CommunicationProps)

    bpy.utils.register_class(SocketModalOperator)
    bpy.utils.register_class(ChangeModeOperator)
    bpy.utils.register_class(PlayPauseOperator)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new(ChangeModeOperator.bl_idname, type='M', value='PRESS', ctrl=True)
        keymaps.append((km, kmi))

        kmi = km.keymap_items.new(PlayPauseOperator.bl_idname, type='P', value='PRESS', ctrl=True, alt=True, shift=False)
        keymaps.append((km, kmi))


def autounregister():
    bpy.utils.unregister_class(CommunicationProps)
    del bpy.types.Scene.com_props

    bpy.utils.unregister_class(SocketModalOperator)
    bpy.utils.unregister_class(ChangeModeOperator)
    bpy.utils.unregister_class(PlayPauseOperator)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()


robot_modes_summary = ["EDITOR_MODE", # 0
                       "ROBOT_MODE" # 1
                      ]

class CommunicationProps(bpy.types.PropertyGroup):
    prop_playing: bpy.props.BoolProperty(name="Playing", default=False)

    prop_mode : bpy.props.IntProperty(name="mode", default=0, min=0, max=len(robot_modes_summary)-1)
    prop_last_recv_packet : bpy.props.IntProperty(name="last_recv_packet", default=-1, min=-1)
    prop_last_sent_packet : bpy.props.IntProperty(name="last_sent_packet", default=-1, min=-1)

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

            if self.thread is None:
                cnh.ConnectionHandler().remove_socket()

                update_gui()
                toggle_deactivate_options(robot_modes_summary.index("EDITOR_MODE"))

                if SocketModalOperator.error != "":
                    self.report({'ERROR'}, SocketModalOperator.error)
                else:
                    self.report({'INFO'}, "socket closed")

                return {'FINISHED'}

            if not self.thread.isAlive():
                """
                Change mode : editor
                    if fails close socket and change to editor mode too -> exit with error (server not connecting)
                Close socket
                """
                SocketModalOperator.switching = True

                mode_packet = dp.ModePacket(bpy.context.scene.com_props.prop_last_sent_packet, robot_modes_summary.index("EDITOR_MODE"))
                try:
                    ack_packet = cnh.ConnectionHandler().send_mode_packet(mode_packet)
                    if ack_packet.status != 1:
                        raise Exception("status != 1")
                except Exception as e:
                    self.report({'INFO'}, "can't change to editor mode : caused by {0}".format(e))
                    self.report({'INFO'}, "it has been switched to editor mode but not in server")
                bpy.context.scene.com_props.prop_mode = robot_modes_summary.index("EDITOR_MODE")
                cnh.ConnectionHandler().remove_socket()
                self.report({'INFO'}, "socket closed")

                SocketModalOperator.switching = False

                update_gui()
                toggle_deactivate_options(robot_modes_summary.index("EDITOR_MODE"))
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def run(operator):
        n_fail_recv = 0
        # change mode : robomap
        SocketModalOperator.running = True
        while SocketModalOperator.running:
            """
            receive a trace packet
                if no receive packets close thread
            """
            try:
                trace_packet = cnh.ConnectionHandler().receive_trace_packet()
                n_fail_recv = 0 # Reset no received trace packets count

                if bpy.context.scene.com_props.prop_playing:
                    # get selected robot
                    # place in current position if playing is active
                    sel_rob_id = bpy.context.scene.selected_robot_props.prop_robot_id
                    if sel_rob_id < 0:
                        continue
                    pose = trace_packet.pose
                    x = pose.x
                    y = pose.y
                    g = pose.gamma

                    r = robot.RobotSet().getRobot(sel_rob_id)
                    r.loc = Vector((x, y, 0))
                    r.rotation = Euler((0,0, radians(g)))


            except Exception as e:
                n_fail_recv += 1
                operator.report({'ERROR'}, "No receive trace packet : {0}".format(e))
                if n_fail_recv > 5:
                    SocketModalOperator.running = False

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        """
        Open socket
        Change mode : robomap
            if fails close socket -> exit with errors (cannot connect)
        Create thread
        """
        SocketModalOperator.switching = True

        sel_rob_id = bpy.context.scene.selected_robot_props.prop_robot_id
        if sel_rob_id < 0:
            return
        r = robot.RobotSet().getRobot(sel_rob_id)

        cnh.ConnectionHandler().create_socket(("127.0.0.1", 1500), (r.ip, r.port))
        self.report({'INFO'}, "Socket created")

        current_mode = bpy.context.scene.com_props.prop_mode
        if current_mode == robot_modes_summary.index("ROBOT_MODE"):
            #self.report({'INFO'}, "already in RoboMap mode")
            SocketModalOperator.error = "already in RoboMap mode"
            return {'RUNNING_MODAL'}

        bpy.context.scene.com_props.prop_last_sent_packet += 1
        mode_packet = dp.ModePacket(bpy.context.scene.com_props.prop_last_sent_packet, robot_modes_summary.index("ROBOT_MODE"))
        try:
            ack_packet = cnh.ConnectionHandler().send_mode_packet(mode_packet)
            if ack_packet.status != 1:
                raise Exception("status != 1")
            bpy.context.scene.com_props.prop_mode = robot_modes_summary.index("ROBOT_MODE")
        except Exception as e:
            SocketModalOperator.error = "server unavailable"

            SocketModalOperator.switching = False
            return {'RUNNING_MODAL'}

        import threading
        self.thread = threading.Thread(target=SocketModalOperator.run, args=(self,))
        self.thread.start()

        SocketModalOperator.switching = False

        toggle_deactivate_options(robot_modes_summary.index("ROBOT_MODE"))

        SocketModalOperator.error = ""
        return {'RUNNING_MODAL'}


class ChangeModeOperator(bpy.types.Operator):
    bl_idname = "wm.change_mode"
    bl_label = "Change mode"
    bl_description = "Change between robot / editor"

    def __init__(self):
        pass

    def __del__(self):
        pass

    @classmethod
    def poll(cls, context):
        return context.scene.selected_robot_props.prop_robot_id >= 0 and not SocketModalOperator.switching

    def execute(self, context):
        if not SocketModalOperator.running:
            bpy.ops.wm.socket_modal('INVOKE_DEFAULT')
        else:
            SocketModalOperator.running = False
        return {'FINISHED'}

class PlayPauseOperator(bpy.types.Operator):
    bl_idname = "wm.play_pause"
    bl_label = "Play/Pause robot movement"
    bl_description = "Play/Pause"

    @classmethod
    def poll(cls, context):
        return context.scene.selected_robot_props.prop_robot_id >= 0 and not SocketModalOperator.switching and SocketModalOperator.running

    def execute(self, context):
        context.scene.com_props.prop_playing = not context.scene.com_props.prop_playing
        return {'FINISHED'}
