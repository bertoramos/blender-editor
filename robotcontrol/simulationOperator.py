
import bpy
from mathutils import Vector

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


def reached_pose(start_pose, end_pose, current_pose):
    current_dir = (end_pose.loc - current_pose.loc).normalized()
    running_dir = (end_pose.loc - start_pose.loc).normalized()
    return current_dir.dot(running_dir) < 0

speed = 1/1000

class SimulationOperator(bpy.types.Operator):
    bl_idname = "wm.simulate_plan"
    bl_label = "Simulate plan"
    bl_description = "Simulate plan"

    start_pose = None
    poses = []
    last_reached = -1
    current_pose = None
    direction = Vector((0,0,0))

    def cancel(self, context):
        sel_rob_id = context.scene.selected_robot_props.prop_robot_id
        if sel_rob_id < 0:
            return
        r = robot.RobotSet().getRobot(sel_rob_id)
        r.loc = SimulationOperator.start_pose.loc
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
            if reached_pose(start_pose, end_pose, r.pose):#r.pose == SimulationOperator.poses[SimulationOperator.last_reached + 1]:
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
                    SimulationOperator.last_reached += 1

                    self.report({'INFO'}, "New direction : " + str(SimulationOperator.last_reached) + "/" + str(len(SimulationOperator.poses)))
                    SimulationOperator.direction = (SimulationOperator.poses[SimulationOperator.last_reached+1].loc - SimulationOperator.poses[SimulationOperator.last_reached].loc).normalized()
            global speed
            loc = SimulationOperator.current_pose.loc + speed * SimulationOperator.direction
            p = path.Pose.fromVector(loc, SimulationOperator.current_pose.rotation)
            SimulationOperator.current_pose = p
            r.loc = loc

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
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
