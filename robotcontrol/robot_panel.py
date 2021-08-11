
import bpy

# begin local import: Change to from . import MODULE
import robot
# end local import: Change to from . import MODULE

def autoregister():
    bpy.utils.register_class(RobotPropsPanel)

def autounregister():
    bpy.utils.unregister_class(RobotPropsPanel)

class RobotPropsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_RobotPanel"
    bl_label = "Add Robot"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Robot Control"

    def draw(self, context):
        props = bpy.context.scene.robot_props
        
        self.layout.operator(robot.AddRobotOperator.bl_idname, icon="SYSTEM", text="Add robot")
        if len(robot.RobotSet()) > 0:
            box = self.layout.box()
            scene = context.scene

            box.label(text="Available robots")
            for item in scene.delete_robot_collection:
                box.prop(item, "selected", text=item.name)
            box.operator(robot.DeleteRobotOperator.bl_idname, icon="TRASH", text = "Delete robot")

        box = self.layout.box()

        idx = context.scene.selected_robot_props.prop_robot_id
        txt = "Robot selected : " + str(robot.RobotSet().getRobot(idx).name) if idx >= 0 else "No robot selected"
        txt = txt if len(robot.RobotSet()) > 0 else "No robot available"

        box.label(text=txt)
        box.operator(robot.SelectRobotOperator.bl_idname, icon="CURVE_PATH", text="Select robot")
