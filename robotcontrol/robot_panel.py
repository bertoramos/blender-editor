
import bpy
import robot

def autoregister():
    bpy.utils.register_class(RobotPropsPanel)

def autounregister():
    bpy.utils.unregister_class(RobotPropsPanel)

class RobotPropsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_RobotPanel"
    bl_label = "Robot Props"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Robot Control"

    def draw(self, context):
        props = bpy.context.scene.robot_props
        self.layout.prop(props, "prop_robot_name", text="Name")
        self.layout.prop(props, "prop_robot_loc", text="Location")
        self.layout.prop(props, "prop_robot_type", text="Type")
        type = bpy.context.scene.robot_props.prop_robot_type
        if type == "MYROBOT":
            props = bpy.context.scene.myrobot_props
            self.layout.prop(props, "prop_myrobot_rotation")
            self.layout.prop(props, "prop_myrobot_dim")
            self.layout.prop(props, "prop_myrobot_margin")
        self.layout.operator(robot.AddRobotOperator.bl_idname, icon="SYSTEM", text="Add robot")
        if len(robot.RobotSet()) > 0:
            box = self.layout.box()
            scene = context.scene

            box.label(text="Available robots")
            for item in scene.robot_collection:
                box.prop(item, "selected", text=item.name)
            box.operator(robot.DeleteRobotOperator.bl_idname, icon="TRASH", text = "Delete robot")