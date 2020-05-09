
import bpy

items = [("OTHER", "Other", "", 0),
         ("WALL", "Wall", "", 1),
         ("CEIL", "Ceil", "", 2),
         ("OBSTACLE", "Obstacle", "", 3),
         ("OBSTACLE_MARGIN", "Obstacle margin", "", 4),
         ("BLUETOOTH_BEACON", "Bluetooth_Beacon", "", 5),
         ("ULTRASOUND_BEACON", "Ultrasound_Beacon", "", 6),
         ("ROBOT", "Robot", "", 7),
         ("ROBOT_MARGIN", "Robot_margin", "", 8),
         ("TEMPORAL", "Temporal", "", 9)]

bpy.types.Object.object_type = bpy.props.EnumProperty(items=items, default="OTHER")
