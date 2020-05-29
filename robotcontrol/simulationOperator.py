
import bpy
from mathutils import Vector, Euler
from math import pi, copysign

import pathContainer as pc
import robot
import path

def autoregister():
    global classes
    classes = [SimulationOperator]
    for cls in classes:
        bpy.utils.register_class(cls)

def autounregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)


def reached_rot(start_rot, end_rot, current_rot):

    start_z = start_rot.z % 2*pi
    end_z   = end_rot.z % 2*pi
    curr_z  = current_rot.z % 2*pi
    curr_ang_dist = min(abs(end_z - curr_z), 2*pi - abs(end_z - curr_z))
    print("\t", start_rot.z, end_rot.z, current_rot.z)
    print(start_z, end_z, curr_z, (end_z-curr_z), curr_ang_dist)

    return curr_ang_dist <= 0.01
    #curr_ang_dist = min(end_z - curr_z, 360 - (end_z - curr_z))
    #return prev_ang_dist < curr_ang_dist, curr_ang_dist

def reached_loc(start_loc, end_loc, current_loc):
    current_dir = (end_loc - current_loc).normalized()
    running_dir = (end_loc - start_loc).normalized()
    return current_dir.dot(running_dir) <= 0

speed = 1/1 # m/s
angle_speed = 2*pi/(100*2*pi) # m/s

class SimulationOperator(bpy.types.Operator):
    bl_idname = "wm.simulate_plan"
    bl_label = "Simulate plan"
    bl_description = "Simulate plan"

    start_pose = None
    poses = []
    last_reached = -1
    current_pose = None
    direction = Vector((0,0,0))
    rot_dir = +1

    ang_dist = None

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
            return {'FINISHED'}

        if event.type == 'TIMER':
            sel_rob_id = context.scene.selected_robot_props.prop_robot_id
            if sel_rob_id < 0:
                self.report({'ERROR'}, "Can not simulate plan: There is not a selected robot")
                return {'CANCELLED'}

            r = robot.RobotSet().getRobot(sel_rob_id)
            start_pose = SimulationOperator.poses[SimulationOperator.last_reached]
            end_pose = SimulationOperator.poses[SimulationOperator.last_reached + 1]

            res_reached_loc = reached_loc(start_pose.loc, end_pose.loc, r.pose.loc)
            res_reached_rot = reached_rot(start_pose.rotation, end_pose.rotation, r.pose.rotation)

            if res_reached_loc and res_reached_rot:

                if SimulationOperator.last_reached + 1 == len(SimulationOperator.poses) - 1:
                    r.loc = SimulationOperator.start_pose.loc
                    SimulationOperator.poses.clear()
                    SimulationOperator.last_reached = -1
                    SimulationOperator.start_pose = None
                    SimulationOperator.current_pose = None
                    SimulationOperator.direction = Vector((0,0,0))
                    self.report({'INFO'}, "Finish simulation")
                    return {'FINISHED'}
                else:
                    r.loc = end_pose.loc
                    r.rot = end_pose.rotation
                    SimulationOperator.last_reached += 1

                    self.report({'INFO'}, "New direction : " + str(SimulationOperator.last_reached) + "/" + str(len(SimulationOperator.poses)))
                    SimulationOperator.direction = (SimulationOperator.poses[SimulationOperator.last_reached+1].loc - \
                                                        SimulationOperator.poses[SimulationOperator.last_reached].loc).normalized()

            if not res_reached_loc:
                global speed
                loc = SimulationOperator.current_pose.loc + speed * SimulationOperator.direction
                p = path.Pose.fromVector(loc, SimulationOperator.current_pose.rotation)
                SimulationOperator.current_pose = p
                r.loc = loc
            else:
                p = path.Pose.fromVector(end_pose.loc, SimulationOperator.current_pose.rotation)
                SimulationOperator.current_pose = p
                r.loc = p.loc

            if not res_reached_rot:
                cur_rotz = SimulationOperator.current_pose.rotation.z
                end_rotz = SimulationOperator.poses[SimulationOperator.last_reached + 1].rotation.z
                dist = min(abs(cur_rotz-end_rotz), 2*pi - abs(cur_rotz-end_rotz))

                cur_rotz += 0.05 * dist

                rot = Euler((SimulationOperator.current_pose.rotation.x, SimulationOperator.current_pose.rotation.y, cur_rotz))
                SimulationOperator.current_pose = path.Pose.fromVector(SimulationOperator.current_pose.loc, rot)
                r.rotation = rot
            else:
                p = path.Pose.fromVector(SimulationOperator.current_pose.loc, end_pose.rotation)
                SimulationOperator.current_pose = p
                r.rotation = p.rotation

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

        SimulationOperator.poses.extend(pc.PathContainer().poses)
        SimulationOperator.last_reached = -1
        SimulationOperator.current_pose = r.pose
        SimulationOperator.direction = (SimulationOperator.poses[0].loc - r.pose.loc).normalized()

        SimulationOperator.start_pose = r.pose

        wm = context.window_manager
        self._timer = wm.event_timer_add(1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
