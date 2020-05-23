
import bpy
import time
from mathutils import Vector, Euler
from math import radians

import connection_handler as cnh
import datapacket as dp
import robot

import pathContainer as pc
import path

keymaps = []

def autoregister():
    global classes
    classes = [CommunicationProps, SocketModalOperator, ChangeModeOperator, PlayPauseRenderOperator, StartNavegationOperator, StopNavegationOperator,
                ShowTimeStamp, StartOperatorTmp, SendPathOperatorTmp]
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.com_props = bpy.props.PointerProperty(type=CommunicationProps)


    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new(ChangeModeOperator.bl_idname, type='M', value='PRESS', ctrl=True)
        keymaps.append((km, kmi))

        kmi = km.keymap_items.new(PlayPauseRenderOperator.bl_idname, type='P', value='PRESS', ctrl=True, alt=True, shift=False)
        keymaps.append((km, kmi))


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
    last_reached_pose = None

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

                bpy.context.scene.com_props.prop_last_sent_packet += 1
                new_pid = bpy.context.scene.com_props.prop_last_sent_packet
                new_mode = robot_modes_summary.index("EDITOR_MODE")
                try:
                    status = cnh.ConnectionHandler().send_mode_packet(new_pid, new_mode)
                    if status != 1:
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

                if context.scene.is_cursor_active:
                    bpy.ops.scene.stop_cursor_listener() # Paramos el editor de rutas si está activo
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
                pose = cnh.ConnectionHandler().receive_trace_packet()
                n_fail_recv = 0 # Reset no received trace packets count

                if bpy.context.scene.com_props.prop_rendering:
                    # get selected robot
                    # place in current position if playing is active
                    sel_rob_id = bpy.context.scene.selected_robot_props.prop_robot_id
                    if sel_rob_id < 0:
                        continue
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
        new_pid = bpy.context.scene.com_props.prop_last_sent_packet
        new_mode = robot_modes_summary.index("ROBOT_MODE")
        try:
            status = cnh.ConnectionHandler().send_mode_packet(new_pid, new_mode)
            if status != 1:
                raise Exception("status != 1")
            bpy.context.scene.com_props.prop_mode = robot_modes_summary.index("ROBOT_MODE")
        except Exception as e:
            SocketModalOperator.error = "server unavailable : " + str(e)

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

class PlayPauseRenderOperator(bpy.types.Operator):
    bl_idname = "wm.play_pause_render"
    bl_label = "Play/Pause rendering position"
    bl_description = "Play/Pause"

    @classmethod
    def poll(cls, context):
        return context.scene.selected_robot_props.prop_robot_id >= 0 and not SocketModalOperator.switching and SocketModalOperator.running

    def execute(self, context):
        context.scene.com_props.prop_rendering = not context.scene.com_props.prop_rendering
        return {'FINISHED'}

class StartNavegationOperator(bpy.types.Operator):
    bl_idname = "wm.start_navegation"
    bl_label = "Start navegation operator"
    bl_description = "Start - Pause/Resume navegation plan"

    @classmethod
    def poll(cls, context):
        active_com = context.scene.selected_robot_props.prop_robot_id >= 0 and not SocketModalOperator.switching and SocketModalOperator.running
        path_exists = len(pc.PathContainer()) > 0
        editing_path = context.scene.is_cursor_active
        return active_com and path_exists and not editing_path

    def execute(self, context):
        # context.scene.com_props.prop_running_nav
        # context.scene.com_props.prop_paused_nav
        change_path_status = False
        if context.scene.com_props.prop_running_nav:
            if context.scene.com_props.prop_paused_nav:
                if change_path_status:
                    # send plan
                    # update path status
                    # start plan
                    context.scene.com_props.prop_running_nav = True
                    context.scene.com_props.prop_paused_nav = False
                else:
                    # continue plan
                    context.scene.com_props.prop_running_nav = True
                    context.scene.com_props.prop_paused_nav = False
            else:
                # pause plan
                context.scene.com_props.prop_running_nav = True
                context.scene.com_props.prop_paused_nav = True
        else:
            if context.scene.com_props.prop_paused_nav:
                # Error
                self.report({"ERROR"}, "A plan that is not being executed cannot be paused")
            else:
                # send plan
                # update path status
                # start plan
                context.scene.com_props.prop_running_nav = True
                context.scene.com_props.prop_paused_nav = False
        return {'FINISHED'}

class StopNavegationOperator(bpy.types.Operator):
    bl_idname = "wm.stop_navegation"
    bl_label = "Stop navegation"
    bl_description = "Stop navegation"

    @classmethod
    def poll(cls, context):
        active_com = context.scene.selected_robot_props.prop_robot_id >= 0 and not SocketModalOperator.switching and SocketModalOperator.running
        path_exists = len(pc.PathContainer()) > 0
        editing_path = context.scene.is_cursor_active
        running_nav = context.scene.com_props.prop_running_nav
        return active_com and path_exists and not editing_path and running_nav

    def execute(self, context):
        context.scene.com_props.prop_running_nav = False
        context.scene.com_props.last_sent_packet += 1
        cnh.ConnectionHandler().send_stop_plan_packet(context.scene.com_props.prop_last_sent_packet)
        if status != 1:
            self.report({'ERROR'}, "Plan can't be started")
        return {'FINISHED'}


# TEMPORALES

class ShowTimeStamp(bpy.types.Operator):
    bl_idname = "wm.show_timestamp"
    bl_label = "Show timestamp"
    bl_description = "Show timestamp"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print(pc.PathContainer().get_last_timestamp())
        return {'FINISHED'}

class StartOperatorTmp(bpy.types.Operator):
    bl_idname = "wm.start_tmp"
    bl_label = "Start operator temporal"
    bl_description = "Start operator temporal"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.scene.com_props.prop_last_sent_packet += 1
        status = cnh.ConnectionHandler().send_start_plan_packet(context.scene.com_props.prop_last_sent_packet)
        if status != 1:
            self.report({'ERROR'}, "Plan can't be started")
        return {'FINISHED'}

class SendPathOperatorTmp(bpy.types.Operator):
    bl_idname = "wm.send_path_tmp"
    bl_label = "Send path operator temporal"
    bl_description = "Send path operator temporal"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        l = []
        l.append(path.Pose(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        l.append(path.Pose(1.0, 1.0, 0.0, 0.0, 0.0, 45.0))
        l.append(path.Pose(2.0, 2.0, 0.0, 0.0, 0.0, 90.0))
        l.append(path.Pose(3.0, 3.0, 0.0, 0.0, 0.0, 180.0))
        l.append(path.Pose(4.0, 4.0, 0.0, 0.0, 0.0, 270.0))
        l.append(path.Pose(5.0, 5.0, 0.0, 0.0, 0.0, 0.0))
        l.append(path.Pose(6.0, 6.0, 0.0, 0.0, 0.0, 45.0))
        l.append(path.Pose(7.0, 7.0, 0.0, 0.0, 0.0, 90.0))
        l.append(path.Pose(8.0, 8.0, 0.0, 0.0, 0.0, 180.0))
        l.append(path.Pose(9.0, 9.0, 0.0, 0.0, 0.0, 270.0))
        l.append(path.Pose(-10.0, -10.0, 0.0, 0.0, 0.0, 0.0))

        context.scene.com_props.prop_last_sent_packet += 1
        status = cnh.ConnectionHandler().send_plan(context.scene.com_props.prop_last_sent_packet, l)
        if status < 0:
            self.report({'ERROR'}, "Plan can't be load")
        return {'FINISHED'}
