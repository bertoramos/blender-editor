
import bpy

items = [("OTHER", "Other", "", 0),
         ("WALL", "Wall", "", 1),
         ("CEIL", "Ceil", "", 2),
         ("OBSTACLE", "Obstacle", "", 3),
         ("OBSTACLE_MARGIN", "Obstacle margin", "", 4),
         ("BEACON", "Beacon", "", 5),
         ("ROBOT", "Robot", "", 6)]

bpy.types.Object.object_type = bpy.props.EnumProperty(items=items, default="OTHER")
