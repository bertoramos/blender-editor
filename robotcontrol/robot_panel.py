
import bpy

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
        self.layout.prop(props, "prop_robot_type", text="Type")
        type = bpy.context.scene.robot_props.prop_robot_type
        if type == "MYROBOT":
            props = bpy.context.scene.myrobot_props
            self.layout.prop(props, "prop_myrobot_dim")
            self.layout.prop(props, "prop_myrobot_margin")
