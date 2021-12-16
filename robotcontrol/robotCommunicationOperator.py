import bpy
import time
from mathutils import Vector, Euler
from math import radians

# begin local import: Change to from . import MODULE
import connectionHandler as cnh
import datapacket as dp
import robot
import pathContainer as pc
import path
import pathEditor
import hudWriter
# end local import: Change to from . import MODULE


APP_STATUS = "APP_STATUS"
RUNNING_STATUS = "RUNNING_STATUS"
CAPTURE_STATUS = "CAPTURE_STATUS"

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

    hudWriter.HUDWriterOperator._textos[APP_STATUS] = SocketModalOperator.EDITOR_MODE #hudWriter.Texto(text="EDITOR mode")

def autounregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.com_props

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()

    if APP_STATUS in hudWriter.HUDWriterOperator._textos:
        del hudWriter.HUDWriterOperator._textos[APP_STATUS]


robot_modes_summary = ["EDITOR_MODE", # 0
                       "ROBOT_MODE" # 1
                      ]

#def update_func(self, context):
#    ip = context.scene.com_props.prop_client_ip
#    p = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
#    if not p.match(ip):
#        context.scene.com_props.prop_client_ip = "127.0.0.1"

class CommunicationProps(bpy.types.PropertyGroup):
    #prop_client_ip: bpy.props.StringProperty(name="Ip", default = "127.0.0.1", update=update_func)
    #prop_client_port : bpy.props.IntProperty(name="Port", default=1500, min=0)

    prop_rendering: bpy.props.BoolProperty(name="Rendering", default=True)

    prop_mode : bpy.props.IntProperty(name="mode", default=0, min=0, max=len(robot_modes_summary)-1)
    prop_last_recv_packet : bpy.props.IntProperty(name="last_recv_packet", default=-1, min=-1)
    prop_last_sent_packet : bpy.props.IntProperty(name="last_sent_packet", default=-1, min=-1)

    prop_last_path_update: bpy.props.IntProperty(name="last_path_update", default=-1, min=-1)

    prop_running_nav: bpy.props.BoolProperty(name="Running nav", default=False)
    prop_paused_nav: bpy.props.BoolProperty(name="Paused nav", default=False)

    prop_speed: bpy.props.FloatProperty(name="Speed", default=100.0, min=0.0, max=100.0)

    prop_capture_running: bpy.props.BoolProperty(name="Capture running", default=False)

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

    ROBOT_MODE = hudWriter.Texto(text="ROBOT mode", x=15, y=30)
    EDITOR_MODE = hudWriter.Texto(text="EDITOR mode", x=15, y=30)

    RUNNING_PLAN = hudWriter.Texto(text="RUNNING plan", x=15, y=90)
    PAUSED_PLAN = hudWriter.Texto(text="PAUSED plan", x=15, y=90)

    CAPTURE_ON = hudWriter.Texto(text="CAPTURE ON", x=15, y=150)


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

        if RUNNING_STATUS in hudWriter.HUDWriterOperator._textos:
            del hudWriter.HUDWriterOperator._textos[RUNNING_STATUS]

        if CAPTURE_STATUS in hudWriter.HUDWriterOperator._textos:
            del hudWriter.HUDWriterOperator._textos[CAPTURE_STATUS]

        context.scene.com_props.prop_capture_running = False


    def clear_hud(self, context):
        if RUNNING_STATUS in hudWriter.HUDWriterOperator._textos:
            del hudWriter.HUDWriterOperator._textos[RUNNING_STATUS]

        if CAPTURE_STATUS in hudWriter.HUDWriterOperator._textos:
            del hudWriter.HUDWriterOperator._textos[CAPTURE_STATUS]

        context.scene.com_props.prop_capture_running = False

    def modal(self, context, event):
        if event.type == "TIMER":

            if context.scene.com_props.prop_running_nav and not context.scene.com_props.prop_paused_nav:
                last_pose = pc.PathContainer().poses[-1]
                reached_poses = cnh.Buffer().get_reached_poses()
                num_reached_poses = len(reached_poses)
                num_path_poses = len(pc.PathContainer().poses)
                end_reached = cnh.Buffer().end_reached()

                if num_reached_poses == num_path_poses and end_reached:
                    context.scene.com_props.prop_running_nav = False
                    context.scene.com_props.prop_paused_nav = False

                    if RUNNING_STATUS in hudWriter.HUDWriterOperator._textos:
                        del hudWriter.HUDWriterOperator._textos[RUNNING_STATUS]

                if num_reached_poses != num_path_poses and end_reached:
                    self.report({'ERROR'}, "End reached not expected")
                    context.scene.com_props.prop_running_nav = False
                    context.scene.com_props.prop_paused_nav = False

                capture_started = cnh.Buffer().capture_started()
                capture_ended = cnh.Buffer().capture_ended()

                if capture_started:
                    prop_capture_running = context.scene.com_props.prop_capture_running
                    if prop_capture_running:
                        self.report({'ERROR'}, "Capture is already started")
                    else:
                        context.scene.com_props.prop_capture_running = True
                        self.report({'INFO'}, "Capture started")
                    hudWriter.HUDWriterOperator._textos[CAPTURE_STATUS] = SocketModalOperator.CAPTURE_ON

                if capture_ended:
                    prop_capture_running = context.scene.com_props.prop_capture_running
                    if not prop_capture_running:
                        self.report({'ERROR'}, "Capture was not started")
                    else:
                        context.scene.com_props.prop_capture_running = False
                        self.report({'INFO'}, "Capture ended")

                    if CAPTURE_STATUS in hudWriter.HUDWriterOperator._textos:
                        del hudWriter.HUDWriterOperator._textos[CAPTURE_STATUS]

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

                        self.thread.join() # se espera a que acabe el hilo

                        cnh.ConnectionHandler().remove_socket()

                        self.clear_hud(context)
                        return {'FINISHED'}

                    #update_gui()
                    toggle_deactivate_options(robot_modes_summary.index("EDITOR_MODE"))

                    SocketModalOperator.running = False
                    self.thread.join() # se espera a que acabe el hilo

                    cnh.ConnectionHandler().remove_socket()

                    if context.scene.is_cursor_active:
                        bpy.ops.scene.stop_cursor_listener()

                cnh.Buffer().clear_reached_poses()
                SocketModalOperator.switching = False
                self.report({'INFO'}, "Socket closed")

                context.scene.com_props.prop_running_nav = False
                context.scene.com_props.prop_paused_nav = False

                self.clear_hud(context)
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    # THREAD EXECUTION
    def run(operator):

        hudWriter.HUDWriterOperator._textos[APP_STATUS] = SocketModalOperator.ROBOT_MODE

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
                n_rcv = limit
                operator.report({'ERROR'}, 'Unavailable server: changing mode')
                bpy.ops.wm.change_mode()

        hudWriter.HUDWriterOperator._textos[APP_STATUS] = SocketModalOperator.EDITOR_MODE # hudWriter.Texto(text="EDITOR mode")

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


        client_ip = r.client_ip
        client_port = r.client_port

        try:
            cnh.ConnectionHandler().create_socket((client_ip, client_port), (r.ip, r.port))
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

                poses_list = pc.PathContainer().poses


                robot_obj = bpy.data.objects[r.name]
                area_robot_obj = bpy.data.objects[r.area_name]

                if pose_robot != poses_list[0]:
                    collide = pathEditor.is_colliding(sel_robot_id, robot_obj, area_robot_obj, pose_robot, poses_list[0])
                    if collide:
                        self.report({"ERROR"}, "Collision : robot cannot be moved to the indicated start position")
                        return

                # Comprobar colision para el resto de poses de la ruta
                for pose_index in range(len(poses_list)-1):
                    collide = pathEditor.is_colliding(sel_robot_id, robot_obj, area_robot_obj, poses_list[pose_index], poses_list[pose_index + 1])
                    if collide:
                        self.report({"ERROR"}, "Collision: robot cannot execute current path")
                        return

                bpy.context.scene.com_props.prop_last_sent_packet += 1
                pid = bpy.context.scene.com_props.prop_last_sent_packet
                status = cnh.ConnectionHandler().send_plan(pid, poses_list)

                self.report({"INFO"}, "Plan was sent" if status == len(poses_list) else "Plan fail {0}".format(status))

                if status == len(poses_list):
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

                    hudWriter.HUDWriterOperator._textos[RUNNING_STATUS] = SocketModalOperator.RUNNING_PLAN
                else:
                    com_props.prop_last_sent_packet += 1
                    pid = com_props.prop_last_sent_packet

                    cnh.ConnectionHandler().send_resume_plan(pid)
                    com_props.prop_running_nav = True
                    com_props.prop_paused_nav = False
                    self.report({'INFO'}, "Paused plan: resume current plan")

                    hudWriter.HUDWriterOperator._textos[RUNNING_STATUS] = SocketModalOperator.RUNNING_PLAN
            else:
                com_props.prop_last_sent_packet += 1
                pid = com_props.prop_last_sent_packet

                cnh.ConnectionHandler().send_pause_plan(pid)
                com_props.prop_running_nav = True
                com_props.prop_paused_nav = True
                self.report({'INFO'}, "Running plan: pause current plan")

                hudWriter.HUDWriterOperator._textos[RUNNING_STATUS] = SocketModalOperator.PAUSED_PLAN
        else:
            if com_props.prop_paused_nav:
                self.report({'ERROR'}, "not running and paused")
                com_props.prop_running_nav = False
                com_props.prop_paused_nav = False
            else:
                send_plan()

                hudWriter.HUDWriterOperator._textos[RUNNING_STATUS] = SocketModalOperator.RUNNING_PLAN
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
        cnh.Buffer().clear_reached_poses()

        if RUNNING_STATUS in hudWriter.HUDWriterOperator._textos:
            del hudWriter.HUDWriterOperator._textos[RUNNING_STATUS]

        return {'FINISHED'}

class ChangeSpeedOperator(bpy.types.Operator):
    bl_idname = "wm.change_speed"
    bl_label = "Change speed"
    bl_description = "Send speed"

    update_speed: bpy.props.FloatProperty(name="Speed",
                                          min=0.0,
                                          max=100.0,
                                          default=100.0)

    @classmethod
    def poll(cls, context):
        return SocketModalOperator.running

    def invoke(self, context, event):
        self.update_speed = bpy.context.scene.com_props.prop_speed
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):

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
        from datetime import datetime
        self.report({'INFO'}, "(" + str(datetime.now()) + ")\nBuffer:\n-------------------\n" + str(cnh.Buffer()) + "\n-------------------------")
        return {'FINISHED'}
