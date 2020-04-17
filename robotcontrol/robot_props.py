
import bpy
import re

def autoregister():
    bpy.utils.register_class(RobotProps)
    bpy.utils.register_class(MyRobotProps)
    bpy.types.Scene.robot_props = bpy.props.PointerProperty(type=RobotProps)
    bpy.types.Scene.myrobot_props = bpy.props.PointerProperty(type=MyRobotProps)

def autounregister():
    bpy.utils.unregister_class(RobotProps)
    bpy.utils.unregister_class(MyRobotProps)
    del bpy.types.Scene.robot_props
    del bpy.types.Scene.myrobot_props

robot_types = [("ROBOMAP", "RoboMap", "", 1)]

def update_func(self, context):
    ip = context.scene.robot_props.prop_ip
    p = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if not p.match(ip):
        context.scene.robot_props.prop_ip = "127.0.0.1"
        #self.report({'ERROR'}, "No valid ip")

class RobotProps(bpy.types.PropertyGroup):
    # Propiedades comunes
    prop_robot_name: bpy.props.StringProperty(name="Name", description="Robot name",default="Robot", maxlen=20)
    prop_robot_loc: bpy.props.FloatVectorProperty(name="Location", description="Robot dimensions", default=(0,0,0), subtype='XYZ', size=3)
    prop_robot_type: bpy.props.EnumProperty(items = robot_types)
    prop_ip: bpy.props.StringProperty(name="Ip", update=update_func)
    prop_port : bpy.props.IntProperty(name="Port", min=0)

class MyRobotProps(bpy.types.PropertyGroup):
    prop_myrobot_rotation: bpy.props.FloatProperty(name="Rotation", description="Rotation angle [degree]", default=0, min=0, max=359)
    prop_myrobot_dim: bpy.props.FloatVectorProperty(name="Dimension", description="Robot dimension", default=(1.0, 1.0, 1.0), subtype='XYZ', size=3)
    prop_myrobot_margin: bpy.props.FloatVectorProperty(name="Margin", description="Robot margin", default=(1.0, 1.0, 1.0), subtype='XYZ', size=3)
