import bpy
import time
from mathutils import Vector, Euler
from math import radians

import connectionHandler as cnh
import datapacket as dp
import robot

import pathContainer as pc
import path

import pathEditor

keymaps = []

def autoregister():
    global classes
    classes = [CommunicationProps, SocketModalOperator, ChangeModeOperator,
                ToggleRenderingOperator, StartPauseResumePlanOperator, StopPlanOperator,
                ChangeSpeedOperator, SeeBufferOperator]
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.com_props = bpy.props.PointerProperty(type=CommunicationProps)


    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new(ChangeModeOperator.bl_idname, type='M', value='PRESS', ctrl=True, shift=True)
        keymaps.append((km, kmi))

        kmi = km.keymap_items.new(ToggleRenderingOperator.bl_idname, type='R', value='PRESS', ctrl=True, shift=True)
        keymaps.append((km, kmi))

        kmi = km.keymap_items.new(StartPauseResumePlanOperator.bl_idname, type='P', value='PRESS', ctrl=True, shift=True)
        keymaps.append((km, kmi))

        kmi = km.keymap_items.new(StopPlanOperator.bl_idname, type='C', value='PRESS', ctrl=True, shift=True)
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

    prop_last_path_update: bpy.props.IntProperty(name="last_path_update", default=-1, min=-1)

    prop_running_nav: bpy.props.BoolProperty(name="Running nav", default=False)
    prop_paused_nav: bpy.props.BoolProperty(name="Paused nav", default=False)

    prop_speed: bpy.props.FloatProperty(name="Speed", default=100.0, min=0.0, max=100.0)

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

    # active redrawing when a change occurs
    def check(self, context):
        return True

    def cancel(self, context):
        """
        Se ejecuta al cerrar la aplicación sin salir de modo robot
        """
        if context.scene.com_props.prop_running_nav:
            context.scene.com_props.prop_last_sent_packet += 1
            pid = context.scene.com_props.prop_last_sent_packet
            if not cnh.ConnectionHandler().send_stop_plan(pid):
                self.report({'ERROR'}, "Can not stop plan : no ack received")
            else:
                context.scene.com_props.prop_running_nav = False
                context.scene.com_props.prop_paused_nav = False

        if context.scene.com_props.prop_mode == robot_modes_summary.index("ROBOT_MODE"):
            context.scene.com_props.prop_last_sent_packet += 1
            new_pid = context.scene.com_props.prop_last_sent_packet
            new_mode = robot_modes_summary.index("EDITOR_MODE")
            initial_speed = context.scene.com_props.prop_speed
            context.scene.com_props.prop_mode = robot_modes_summary.index("EDITOR_MODE")

            if not cnh.ConnectionHandler().send_change_mode(new_pid, new_mode, initial_speed):
                self.report({'ERROR'}, "Changed to editor mode but not in server : ack not received")
                SocketModalOperator.running = False

        cnh.ConnectionHandler().remove_socket()

        if context.scene.is_cursor_active:
            bpy.ops.scene.stop_cursor_listener()


    def modal(self, context, event):
        if event.type == "TIMER":

            if context.scene.com_props.prop_running_nav and not context.scene.com_props.prop_paused_nav:
                last_pose = pc.PathContainer().poses[-1]
                reached_poses = cnh.Buffer().get_reached_poses()
                #self.report({'INFO'}, "Poses" + str(reached_poses))
                for pose in reached_poses:
                    if last_pose == pose:
                        context.scene.com_props.prop_running_nav = False
                        context.scene.com_props.prop_paused_nav = False

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
                        r.rotation = Euler((0, 0, pose.gamma))


            if SocketModalOperator.closed:
                SocketModalOperator.switching = True

                if SocketModalOperator.error != "":
                    self.report({'ERROR'}, self.error)
                    SocketModalOperator.running = False
                    cnh.ConnectionHandler().remove_socket()
                else:
                    bpy.context.scene.com_props.prop_last_sent_packet += 1
                    new_pid = bpy.context.scene.com_props.prop_last_sent_packet
                    new_mode = robot_modes_summary.index("EDITOR_MODE")
                    initial_speed = context.scene.com_props.prop_speed
                    bpy.context.scene.com_props.prop_mode = robot_modes_summary.index("EDITOR_MODE")

                    if not cnh.ConnectionHandler().send_change_mode(new_pid, new_mode, initial_speed):
                        self.report({'ERROR'}, "Changed to editor mode but not in server : ack not received")
                        SocketModalOperator.switching = False
                        SocketModalOperator.running = False
                        cnh.ConnectionHandler().remove_socket()
                        return {'FINISHED'}

                    #update_gui()
                    toggle_deactivate_options(robot_modes_summary.index("EDITOR_MODE"))
                    cnh.ConnectionHandler().remove_socket()
                    SocketModalOperator.running = False

                    if context.scene.is_cursor_active:
                        bpy.ops.scene.stop_cursor_listener()

                SocketModalOperator.switching = False
                self.report({'INFO'}, "Socket closed")

                context.scene.com_props.prop_running_nav = False
                context.scene.com_props.prop_paused_nav = False

                return {'FINISHED'}

        return {'PASS_THROUGH'}

    # THREAD EXECUTION
    def run(operator):
        limit = 10
        n_rcv = limit
        SocketModalOperator.running = True
        while SocketModalOperator.running:
            if cnh.ConnectionHandler().hasSocket():
                rcv = cnh.ConnectionHandler().receive_packet(operator)
                if rcv:
                    n_rcv = limit
                else:
                    operator.report({'INFO'}, 'No communication')
                    n_rcv-=1
            if n_rcv == 0:
                operator.report({'ERROR'}, 'Unavailable server: changing mode')
                bpy.ops.wm.change_mode()

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)

        SocketModalOperator.switching = True

        sel_rob_id = context.scene.selected_robot_props.prop_robot_id
        if sel_rob_id < 0:
            SocketModalOperator.error = "Robot not selected"
            return {'RUNNING_MODAL'}
        r = robot.RobotSet().getRobot(sel_rob_id)
        try:
            cnh.ConnectionHandler().create_socket(("127.0.0.1", 1500), (r.ip, r.port))
        except:
            SocketModalOperator.error = "error in socket creation"
            return {'RUNNING_MODAL'}

        import threading
        self.thread = threading.Thread(target=SocketModalOperator.run, args=(self,))
        self.thread.start()

        context.scene.com_props.prop_last_sent_packet += 1
        new_pid = context.scene.com_props.prop_last_sent_packet
        new_mode = robot_modes_summary.index("ROBOT_MODE")
        initial_speed = context.scene.com_props.prop_speed
        if not cnh.ConnectionHandler().send_change_mode(new_pid, new_mode, initial_speed):
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

    update_speed: bpy.props.FloatProperty(name="Set initial speed",
                                          min=0.0,
                                          max=100.0,
                                          default=0.0)

    def invoke(self, context, event):
        if SocketModalOperator.closed:
            self.update_speed = bpy.context.scene.com_props.prop_speed
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)

    @classmethod
    def poll(cls, context):
        running_plan = context.scene.com_props.prop_running_nav
        selected_robot = context.scene.selected_robot_props.prop_robot_id >= 0
        changing_mode = SocketModalOperator.switching
        active_editor = context.scene.is_cursor_active
        return not active_editor and not running_plan and selected_robot and not changing_mode

    def execute(self, context):
        if SocketModalOperator.closed:
            bpy.ops.wm.socket_modal('INVOKE_DEFAULT')
        else:
            SocketModalOperator.closed = True
        bpy.context.scene.com_props.prop_speed = self.update_speed
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
        return context.scene.com_props.prop_mode == robot_modes_summary.index("ROBOT_MODE") and not context.scene.is_cursor_active

    def execute(self, context):
        com_props = context.scene.com_props

        path_changed = com_props.prop_last_path_update < pc.PathContainer().getLastUpdate()

        def send_plan():
            cnh.Buffer().clear_reached_poses()
            # send plan
            if len(pc.PathContainer()) > 0:
                sel_robot_id = bpy.context.scene.selected_robot_props.prop_robot_id
                r = robot.RobotSet().getRobot(sel_robot_id)
                pose_robot = r.pose

                p = pc.PathContainer().poses

                if pose_robot != p[0]:
                    robot_obj = bpy.data.objects[r.name]
                    area_robot_obj = bpy.data.objects[r.area_name]
                    collide = pathEditor.is_colliding(sel_robot_id, robot_obj, area_robot_obj, pose_robot, p[0])
                    if collide:
                        self.report({"ERROR"}, "Collision : robot cannot be moved to the indicated start position")
                        return

                bpy.context.scene.com_props.prop_last_sent_packet += 1
                pid = bpy.context.scene.com_props.prop_last_sent_packet
                status = cnh.ConnectionHandler().send_plan(pid, p)

                self.report({"INFO"}, "Plan was sent" if status == len(p) else "Plan fail {0}".format(status))

                if status == len(p):
                    com_props.prop_last_sent_packet += 1
                    pid = com_props.prop_last_sent_packet
                    cnh.ConnectionHandler().send_start_plan(pid)

                    com_props.prop_running_nav = True
                    com_props.prop_paused_nav = False

            else:
                self.report({"ERROR"}, "There is not plan created : Please, design a plan to execute")
            # update path status
            context.scene.com_props.prop_last_path_update = pc.PathContainer().getLastUpdate()

        if com_props.prop_running_nav:
            if com_props.prop_paused_nav:
                if path_changed:
                    send_plan()
                    self.report({'INFO'}, "Paused plan: cancel current plan and start a new plan")
                else:
                    com_props.prop_last_sent_packet += 1
                    pid = com_props.prop_last_sent_packet

                    cnh.ConnectionHandler().send_resume_plan(pid)
                    com_props.prop_running_nav = True
                    com_props.prop_paused_nav = False
                    self.report({'INFO'}, "Paused plan: resume current plan")
            else:
                com_props.prop_last_sent_packet += 1
                pid = com_props.prop_last_sent_packet

                cnh.ConnectionHandler().send_pause_plan(pid)
                com_props.prop_running_nav = True
                com_props.prop_paused_nav = True
                self.report({'INFO'}, "Running plan: pause current plan")
        else:
            if com_props.prop_paused_nav:
                self.report({'ERROR'}, "not running and paused")
                com_props.prop_running_nav = False
                com_props.prop_paused_nav = False
            else:
                send_plan()
                #self.report({'INFO'}, "No plan: start a new plan")
        return {'FINISHED'}

class StopPlanOperator(bpy.types.Operator):
    bl_idname = "wm.stop_plan"
    bl_label = "Stop plan"
    bl_description = "Stop plan"

    @classmethod
    def poll(cls, context):
        return context.scene.com_props.prop_running_nav

    def execute(self, context):
        context.scene.com_props.prop_last_sent_packet += 1
        pid = context.scene.com_props.prop_last_sent_packet
        cnh.ConnectionHandler().send_stop_plan(pid)

        context.scene.com_props.prop_running_nav = False
        context.scene.com_props.prop_paused_nav = False

        context.scene.com_props.prop_last_path_update = -1
        return {'FINISHED'}

class ChangeSpeedOperator(bpy.types.Operator):
    bl_idname = "wm.change_speed"
    bl_label = "Change speed"
    bl_description = "Send speed"

    update_speed: bpy.props.FloatProperty(name="Speed",
                                          min=0.0,
                                          max=100.0,
                                          default=0.0)

    @classmethod
    def poll(cls, context):
        return SocketModalOperator.running

    def invoke(self, context, event):
        self.update_speed = bpy.context.scene.com_props.prop_speed
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        self.report({'INFO'}, str(self.update_speed))

        older_speed = context.scene.com_props.prop_speed
        curre_speed = self.update_speed
        context.scene.com_props.prop_last_sent_packet += 1
        pid = context.scene.com_props.prop_last_sent_packet
        if not cnh.ConnectionHandler().send_change_speed(pid, curre_speed):
            self.report({"ERROR", "Speed can not be changed"})
        else:
            context.scene.com_props.prop_speed = curre_speed
        return {'FINISHED'}


# TEMPORAL

class SeeBufferOperator(bpy.types.Operator):
    bl_idname = "wm.see_buffer"
    bl_label = "See buffer"
    bl_description = "See buffer"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        s = "Buffer"
        for packet in iter(cnh.Buffer()):
            s += "\t" + str(packet) + "\n"
        s += "----------\n\t Last trace: " + str(cnh.Buffer().get_last_trace_packet()) + "\n----------"
        self.report({'INFO'}, s)
        return {'FINISHED'}
