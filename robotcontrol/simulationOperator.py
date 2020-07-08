
import bpy
from mathutils import Vector, Euler
from math import pi, copysign

import pathContainer as pc
import robot
import path
import robotCommunicationOperator as rco

def autoregister():
    global classes
    classes = [SimulationOperator, PauseResumeSimulation, SimulationProps, ChangeSpeedSimulationOperator]
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.sim_props = bpy.props.PointerProperty(type=SimulationProps)

def autounregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.sim_props

def is_loc_reached(start_loc, end_loc, current_loc):
    current_dir = (end_loc - current_loc).normalized()
    running_dir = (end_loc - start_loc).normalized()
    print("Reached : ", current_dir.dot(running_dir), "Current_dir:", current_dir, "Running_dir:", running_dir)
    return current_dir.dot(running_dir) <= 0.0

class SimulationProps(bpy.types.PropertyGroup):
    prop_simulated_speed: bpy.props.FloatProperty(name="Speed", default=100.0, min=0.0, max=100.0)


max_speed = 1/5 # m/s
angle_speed = 0.05 # %

class SimulationOperator(bpy.types.Operator):
    bl_idname = "wm.simulate_plan"
    bl_label = "Simulate plan"
    bl_description = "Simulate plan"

    start_pose = None
    poses = []
    last_reached = -1
    current_pose = None
    direction = Vector((0.0,0.0,0.0))

    loc_reached = False
    rot_reached = False

    ang_dist = None

    active = False

    pause = False


    update_speed: bpy.props.FloatProperty(name="Speed",
                                          min=0.0,
                                          max=100.0,
                                          default=0.0)

    def invoke(self, context, event):
        self.update_speed = context.scene.sim_props.prop_simulated_speed
        wm = context.window_manager
        return wm.invoke_props_dialog(self)



    @classmethod
    def poll(cls, context):
        robot_mode = context.scene.com_props.prop_mode == rco.robot_modes_summary.index("ROBOT_MODE")
        #running_plan = context.scene.com_props.prop_running_nav
        selected_robot = context.scene.selected_robot_props.prop_robot_id >= 0
        active_editor = context.scene.is_cursor_active
        return not robot_mode and selected_robot and not active_editor and not SimulationOperator.active

    def cancel(self, context):
        sel_rob_id = context.scene.selected_robot_props.prop_robot_id
        if sel_rob_id < 0:
            return
        r = robot.RobotSet().getRobot(sel_rob_id)
        r.loc = SimulationOperator.start_pose.loc
        r.rotation = SimulationOperator.start_pose.rotation
        SimulationOperator.poses.clear()
        SimulationOperator.last_reached = -1
        SimulationOperator.start_pose = None
        SimulationOperator.current_pose = None
        SimulationOperator.direction = Vector((0,0,0))

        SimulationOperator.loc_reached = False
        SimulationOperator.rot_reached = False

        SimulationOperator.pause = False

        SimulationOperator.active = False

    def modal(self, context, event):
        if event.type == 'ESC':
            sel_rob_id = context.scene.selected_robot_props.prop_robot_id
            if sel_rob_id < 0:
                return
            r = robot.RobotSet().getRobot(sel_rob_id)
            r.loc = SimulationOperator.start_pose.loc
            r.rotation = SimulationOperator.start_pose.rotation
            SimulationOperator.poses.clear()
            SimulationOperator.last_reached = -1
            SimulationOperator.start_pose = None
            SimulationOperator.current_pose = None
            SimulationOperator.direction = Vector((0,0,0))

            SimulationOperator.loc_reached = False
            SimulationOperator.rot_reached = False

            SimulationOperator.pause = False

            SimulationOperator.active = False
            return {'FINISHED'}

        if event.type == 'TIMER':

            if SimulationOperator.pause:
                return {'PASS_THROUGH'}

            sel_rob_id = context.scene.selected_robot_props.prop_robot_id
            if sel_rob_id < 0:
                self.report({'ERROR'}, "Can not simulate plan: There is not a selected robot")
                return {'CANCELLED'}

            r = robot.RobotSet().getRobot(sel_rob_id)
            start_pose = SimulationOperator.poses[SimulationOperator.last_reached] if SimulationOperator.last_reached >= 0 else SimulationOperator.start_pose
            end_pose = SimulationOperator.poses[SimulationOperator.last_reached + 1]

            if SimulationOperator.loc_reached and SimulationOperator.rot_reached:

                SimulationOperator.loc_reached = False
                SimulationOperator.rot_reached = False

                if SimulationOperator.last_reached + 1 == len(SimulationOperator.poses) - 1:
                    r.loc = SimulationOperator.start_pose.loc
                    r.rotation = SimulationOperator.start_pose.rotation
                    SimulationOperator.poses.clear()
                    SimulationOperator.last_reached = -1
                    SimulationOperator.start_pose = None
                    SimulationOperator.current_pose = None
                    SimulationOperator.direction = Vector((0.0,0.0,0.0))

                    SimulationOperator.active = False
                    self.report({'INFO'}, "Finish simulation")
                    return {'FINISHED'}
                else:
                    r.loc = end_pose.loc
                    r.rot = end_pose.rotation
                    SimulationOperator.last_reached += 1

                    #self.report({'INFO'}, "New direction : " + str(SimulationOperator.last_reached) + "/" + str(len(SimulationOperator.poses)))
                    SimulationOperator.direction = (SimulationOperator.poses[SimulationOperator.last_reached+1].loc - \
                                                        SimulationOperator.poses[SimulationOperator.last_reached].loc).normalized()
                    start_pose = SimulationOperator.poses[SimulationOperator.last_reached] if SimulationOperator.last_reached >= 0 else SimulationOperator.start_pose
                    end_pose = SimulationOperator.poses[SimulationOperator.last_reached + 1]

            if not SimulationOperator.loc_reached:
                global max_speed
                speed = max_speed * context.scene.sim_props.prop_simulated_speed/100.0
                loc = SimulationOperator.current_pose.loc + speed * SimulationOperator.direction
                p = path.Pose.fromVector(loc, SimulationOperator.current_pose.rotation)
                SimulationOperator.current_pose = p
                r.loc = loc

                SimulationOperator.loc_reached = is_loc_reached(start_pose.loc, end_pose.loc, loc)
            else:
                SimulationOperator.current_pose = path.Pose.fromVector(end_pose.loc, SimulationOperator.current_pose.rotation)
                r.loc = end_pose.loc
            #print(start_pose.loc, end_pose.loc, SimulationOperator.direction, SimulationOperator.loc_reached)

            if not SimulationOperator.rot_reached:
                global angle_speed
                SimulationOperator.rot_reached = True
                current_z = SimulationOperator.current_pose.rotation.z
                target_z = end_pose.rotation.z

                error = target_z - current_z
                error = min(error, 2*pi - error)

                update_z = SimulationOperator.current_pose.rotation.z + angle_speed*error
                rot = Euler((SimulationOperator.current_pose.rotation.x, SimulationOperator.current_pose.rotation.y, update_z))
                SimulationOperator.current_pose = path.Pose.fromVector(SimulationOperator.current_pose.loc, rot)
                r.rotation = rot

                SimulationOperator.rot_reached = abs(error) < context.scene.TOL*10
            else:
                rot = Euler((SimulationOperator.current_pose.rotation.x, SimulationOperator.current_pose.rotation.y, end_pose.rotation.z))
                SimulationOperator.current_pose = path.Pose.fromVector(SimulationOperator.current_pose.loc, rot)
                r.rotation = rot

        return {'PASS_THROUGH'}

    def execute(self, context):


        sel_rob_id = context.scene.selected_robot_props.prop_robot_id
        if sel_rob_id < 0:
            self.report({'ERROR'}, "Can not simulate plan: There is not a selected robot")
            return {'FINISHED'}
        if len(pc.PathContainer()) <= 0:
            self.report({'ERROR'}, "Can not simulate plan: There is not a created plan")
            return {'FINISHED'}
        r = robot.RobotSet().getRobot(sel_rob_id)
        context.scene.sim_props.prop_simulated_speed = self.update_speed

        SimulationOperator.poses.extend(pc.PathContainer().poses)

        dist = (r.pose.loc - SimulationOperator.poses[0].loc).length

        current_z = r.rotation.z
        target_z = SimulationOperator.poses[0].rotation.z

        error = target_z - current_z
        error = min(error, 2*pi - error)

        if dist >= context.scene.TOL or abs(error) >= 10*context.scene.TOL:
            if dist < context.scene.TOL:
                SimulationOperator.loc_reached = True
            if abs(error) < 10*context.scene.TOL:
                SimulationOperator.rot_reached = True

            SimulationOperator.last_reached = -1
            SimulationOperator.current_pose = r.pose
            SimulationOperator.direction = (SimulationOperator.poses[0].loc - r.pose.loc).normalized()
        else:
            SimulationOperator.last_reached = 0
            SimulationOperator.current_pose = SimulationOperator.poses[0]
            SimulationOperator.direction = (SimulationOperator.poses[1].loc - SimulationOperator.poses[0].loc).normalized()

        SimulationOperator.start_pose = r.pose

        wm = context.window_manager
        self._timer = wm.event_timer_add(1, window=context.window)
        wm.modal_handler_add(self)

        SimulationOperator.active = True
        return {'RUNNING_MODAL'}

class PauseResumeSimulation(bpy.types.Operator):
    bl_idname = "wm.pause_simulation"
    bl_label = "Pause/Resume simulation"
    bl_description = "Pause/Resume simulation"

    @classmethod
    def poll(cls, context):
        return SimulationOperator.active

    def execute(self, context):
        SimulationOperator.pause = not SimulationOperator.pause
        return {'FINISHED'}

class ChangeSpeedSimulationOperator(bpy.types.Operator):
    bl_idname = "wm.change_speed_simulation"
    bl_label = "Change speed simulation"
    bl_description = "Change speed in simulation"

    update_speed: bpy.props.FloatProperty(name="Speed",
                                          min=0.0,
                                          max=100.0,
                                          default=0.0)

    @classmethod
    def poll(cls, context):
        return SimulationOperator.active

    def invoke(self, context, event):
        self.update_speed = context.scene.sim_props.prop_simulated_speed
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        self.report({'INFO'}, str(self.update_speed))
        context.scene.sim_props.prop_simulated_speed = self.update_speed
        return {'FINISHED'}
