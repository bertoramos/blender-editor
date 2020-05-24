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
    classes = [CommunicationProps, SocketModalOperator, ChangeModeOperator,
                ToggleRenderingOperator, StartPauseResumePlanOperator,
                SendPathTemporalOperator]
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
    closed = True
    error = ""

    def modal(self, context, event):
        if event.type == "TIMER":
            if not SocketModalOperator.closed and context.scene.com_props.prop_rendering:
                # Render robot position
                sel_robot_id = bpy.context.scene.selected_robot_props.prop_robot_id
                if sel_robot_id < 0:
                    self.report({'ERROR'}, "No robot selected")
                else:
                    r = robot.RobotSet().getRobot(sel_robot_id)
                    trace = cnh.Buffer().get_last_trace_packet()
                    if trace is not None:
                        pose = trace.pose
                        r.loc = Vector((pose.x, pose.y, 0))
                        r.rotation = Euler((0, 0, radians(pose.gamma)))

            if SocketModalOperator.closed:
                SocketModalOperator.switching = True

                if SocketModalOperator.error != "":
                    self.report({'ERROR'}, "mode could not be switched : " + self.error)
                    cnh.ConnectionHandler().remove_socket()
                    SocketModalOperator.running = False
                else:
                    bpy.context.scene.com_props.prop_last_sent_packet += 1
                    new_pid = bpy.context.scene.com_props.prop_last_sent_packet
                    new_mode = robot_modes_summary.index("EDITOR_MODE")
                    bpy.context.scene.com_props.prop_mode = robot_modes_summary.index("EDITOR_MODE")

                    if not cnh.ConnectionHandler().send_mode_packet(new_pid, new_mode):
                        self.report({'ERROR'}, "Changed to editor mode but not in server : ack not received")
                        SocketModalOperator.switching = False
                        cnh.ConnectionHandler().remove_socket()
                        SocketModalOperator.running = False
                        return {'FINISHED'}

                    update_gui()
                    toggle_deactivate_options(robot_modes_summary.index("EDITOR_MODE"))
                    cnh.ConnectionHandler().remove_socket()
                    SocketModalOperator.running = False

                    if context.scene.is_cursor_active:
                        bpy.ops.scene.stop_cursor_listener()

                SocketModalOperator.switching = False
                self.report({'INFO'}, "Socket closed")

                return {'FINISHED'}

        return {'PASS_THROUGH'}

    # THREAD EXECUTION
    def run(operator):
        SocketModalOperator.running = True
        while SocketModalOperator.running:
            if cnh.ConnectionHandler().hasSocket():
                cnh.ConnectionHandler().receive_packet()
            print("thread")
        print("thread dead")

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        SocketModalOperator.switching = True

        sel_rob_id = context.scene.selected_robot_props.prop_robot_id
        if sel_rob_id < 0:
            return
        r = robot.RobotSet().getRobot(sel_rob_id)
        cnh.ConnectionHandler().create_socket(("127.0.0.1", 1500), (r.ip, r.port))

        import threading
        self.thread = threading.Thread(target=SocketModalOperator.run, args=(self,))
        self.thread.start()

        context.scene.com_props.prop_last_sent_packet += 1
        new_pid = context.scene.com_props.prop_last_sent_packet
        new_mode = robot_modes_summary.index("ROBOT_MODE")
        if not cnh.ConnectionHandler().send_mode_packet(new_pid, new_mode):
            SocketModalOperator.error = "server not available : could not be switched to robot mode / no ack received"
            SocketModalOperator.switching = False
            self.closed = True
            return {'RUNNING_MODAL'}

        SocketModalOperator.switching = False

        toggle_deactivate_options(robot_modes_summary.index("ROBOT_MODE"))
        SocketModalOperator.error = ""
        SocketModalOperator.closed = False
        bpy.context.scene.com_props.prop_mode = robot_modes_summary.index("ROBOT_MODE")

        return {'RUNNING_MODAL'}


class ChangeModeOperator(bpy.types.Operator):
    bl_idname = "wm.change_mode"
    bl_label = "Change mode"
    bl_description = "Change between robot / editor"

    @classmethod
    def poll(cls, context):
        return context.scene.selected_robot_props.prop_robot_id >= 0 and not SocketModalOperator.switching

    def execute(self, context):
        if SocketModalOperator.closed:
            bpy.ops.wm.socket_modal('INVOKE_DEFAULT')
        else:
            SocketModalOperator.closed = True
        return {'FINISHED'}

class ToggleRenderingOperator(bpy.types.Operator):
    bl_idname = "wm.toggle_rendering"
    bl_label = "Toggle rendering"
    bl_description = "Toggle rendering"

    @classmethod
    def poll(cls, context):
        return not SocketModalOperator.closed

    def execute(self, context):
        context.scene.com_props.prop_rendering = not context.scene.com_props.prop_rendering
        return {'FINISHED'}

class StartPauseResumePlanOperator(bpy.types.Operator):
    bl_idname = "wm.start_pause_resume_plan"
    bl_label = "Start/Pause/Resume plan"
    bl_description = "Start/Pause/Resume plan"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.com_props.prop_last_sent_packet += 1
        pid = bpy.context.scene.com_props.prop_last_sent_packet
        status = cnh.ConnectionHandler().send_start_plan(pid)
        return {'FINISHED'}

class StopPlanOperator(bpy.types.Operator):
    bl_idname = "wm.stop_plan"
    bl_label = "Stop plan"
    bl_description = "Stop plan"

    @classmethod
    def poll(cls, context):
        return not SocketModalOperator.closed

    def execute(self, context):
        return {'FINISHED'}

# TEMPORAL

class SendPathTemporalOperator(bpy.types.Operator):
    bl_idname = "wm.send_path"
    bl_label = "Send path (temporal)"
    bl_description = "Send path (temporal)"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        p = []
        p.append(path.Pose(+0.0, +0.0, 0.0, 0.0, 0.0,  45.0))
        p.append(path.Pose(+4.0, +0.0, 0.0, 0.0, 0.0,  90.0))
        p.append(path.Pose(+3.0, +4.0, 0.0, 0.0, 0.0, 180.0))
        p.append(path.Pose(-5.0, +1.0, 0.0, 0.0, 0.0, 270.0))
        p.append(path.Pose(+0.0, -4.0, 0.0, 0.0, 0.0,   0.0))
        p.append(path.Pose(+0.0, +0.0, 0.0, 0.0, 0.0,  45.0))
        p.append(path.Pose(+0.0, +0.0, 0.0, 0.0, 0.0,   0.0))

        bpy.context.scene.com_props.prop_last_sent_packet += 1
        pid = bpy.context.scene.com_props.prop_last_sent_packet
        status = cnh.ConnectionHandler().send_plan(pid, p)

        self.report({"INFO"}, "Plan was sent" if status == len(p) else "Plan fail {0}".format(status))
        return {'FINISHED'}
