
import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from math import sin, cos, asin, atan, radians, degrees, sqrt, pi

# begin local import: Change to from . import MODULE
import geom_math as gm
# end local import: Change to from . import MODULE

def autoregister():
    global classes
    classes = [WallProps, RoomProps, CreateAbsoluteWallOperator, CreateRelativeWallOperator, CreateAbsoluteRoomOperator]
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.wall_props = bpy.props.PointerProperty(type=WallProps)
    bpy.types.Scene.room_props = bpy.props.PointerProperty(type=RoomProps)

def autounregister():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)

    del bpy.types.Scene.wall_props
    del bpy.types.Scene.room_props


def create_wall(self, context, cursor):
    """
    cursor : cursor location
    :return mesh name
    """
    saved_location = bpy.context.scene.cursor.location.xyz
    bpy.context.scene.cursor.location.xyz = cursor

    scene = bpy.context.scene

    ox = scene.wall_props.prop_o.x
    oy = scene.wall_props.prop_o.y
    dx = scene.wall_props.prop_d.x
    dy = scene.wall_props.prop_d.y
    W = scene.wall_props.prop_width
    H = scene.wall_props.prop_height

    L = gm.dist(Vector((ox, oy, 0)), Vector((dx, dy, 0)))

    if abs(dx-ox) < context.scene.TOL and abs(dy-oy) < context.scene.TOL:
        self.report({'ERROR'}, "The wall could not be created, the start and end points must be different")
        return

    if dx - ox == 0:
        if dy - oy > 0:
            alpha = 90
        elif dy - oy < 0:
            alpha = 270
    else:
        alpha = degrees(atan((dy - oy)/(dx - ox)))


    if dx-ox < 0:
        th = 180 + alpha
    elif dy - oy == 0:
        if dx - ox > 0:
            th = 0
        elif dx - ox < 0:
            th = 180
    else:
        th = alpha
    # Vertex
    lfd = Vector((0, 0, 0))
    lbd = Vector((0, W, 0))
    rfd = Vector((L, 0, 0))
    rbd = Vector((L, W, 0))
    lfu = Vector((0, 0, H))
    lbu = Vector((0, W, H))
    rfu = Vector((L, 0, H))
    rbu = Vector((L, W, H))

    verts = [lfd, lbd, rfd, rbd, lfu, lbu, rfu, rbu]

    edges = []

    foreground = [verts.index(lfd), verts.index(lfu), verts.index(rfu), verts.index(rfd)]
    background = [verts.index(lbd), verts.index(lbu), verts.index(rbu), verts.index(rbd)]
    bottom = [verts.index(lfd), verts.index(lbd), verts.index(rbd), verts.index(rfd)]
    top = [verts.index(lbu), verts.index(rbu), verts.index(rfu), verts.index(lfu)]
    left = [verts.index(lfu), verts.index(lbu), verts.index(lbd), verts.index(lfd)]
    right = [verts.index(rfd), verts.index(rbd), verts.index(rbu), verts.index(rfu)]

    faces = [foreground, background, bottom, top, left, right]

    # Ponemos el origen del objeto en el cursor
    #bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    mesh = bpy.data.meshes.new(name="Wall")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(context, mesh, operator=self)

    wall_loc = Vector((cursor.x + ox, cursor.y + oy, 0))

    bpy.data.objects[mesh.name].location = wall_loc
    bpy.data.objects[mesh.name].rotation_euler.z = radians(th)

    # Colocar origen en uno de los vertices (lfd)
    # Colocar objeto en ox
    # Girar th grados
    save_cursor_loc = bpy.context.scene.cursor.location.xyz
    bpy.context.scene.cursor.location = wall_loc
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.scene.cursor.location = save_cursor_loc

    bpy.data.objects[mesh.name].object_type = 'WALL'

    bpy.context.scene.cursor.location.xyz = saved_location

    return mesh.name

class WallProps(bpy.types.PropertyGroup):
    prop_o: bpy.props.FloatVectorProperty(default=(0.0, 0.0), subtype='XYZ', size=2)
    prop_d: bpy.props.FloatVectorProperty(default=(10.0,0), subtype='XYZ', size=2)
    prop_width: bpy.props.FloatProperty(min=0.0, default=0.2)
    prop_height: bpy.props.FloatProperty(min=0.0, default=2.4)

class CreateAbsoluteWallOperator(Operator, AddObjectHelper):
    bl_idname = "mesh.create_absolute_wall"
    bl_label = 'Create wall (absolute position)'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add wall in an absolute location"

    def execute(self, context):
        name = create_wall(self, context, Vector((0,0,0)))
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.wall_props
        self.layout.prop(props, "prop_o", text="Start point (m)")
        self.layout.prop(props, "prop_d", text="End point (m)")
        self.layout.label(text="Wall properties")
        self.layout.prop(props, "prop_height", text="Height (m)")
        self.layout.prop(props, "prop_width", text="Width (m)")

class CreateRelativeWallOperator(Operator, AddObjectHelper):
    bl_idname = "mesh.create_relative_wall"
    bl_label = 'Create wall (relative position)'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add wall in a relative location"

    def execute(self, context):
        name = create_wall(self, context, bpy.context.scene.cursor.location)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.wall_props
        self.layout.prop(props, "prop_o", text="Start point (m)")
        self.layout.prop(props, "prop_d", text="End point (m)")
        self.layout.label(text="Wall properties")
        self.layout.prop(props, "prop_height", text="Alto (m)")
        self.layout.prop(props, "prop_width", text="Ancho (m)")

def create_room(self, context, cursor):
    saved_location = bpy.context.scene.cursor.location.xyz
    bpy.context.scene.cursor.location.xyz = cursor

    scene = bpy.context.scene

    # Save wall props
    save_prop_o = scene.wall_props.prop_o.xy
    save_prop_d = scene.wall_props.prop_d.xy
    save_W = scene.wall_props.prop_width
    save_H = scene.wall_props.prop_height

    point_x = scene.room_props.prop_point.x
    point_y = scene.room_props.prop_point.y
    dim_x = scene.room_props.prop_dim.x
    dim_y = scene.room_props.prop_dim.y
    width_n = scene.room_props.prop_width_north
    width_s = scene.room_props.prop_width_south
    width_e = scene.room_props.prop_width_east
    width_w = scene.room_props.prop_width_west
    height = scene.room_props.prop_height

    if dim_x < context.scene.TOL or dim_y < context.scene.TOL:
        self.report({'ERROR'}, "Room could not be created, room dimensions must be larger than 0")
        return


    # South wall
    scene.wall_props.prop_o = Vector((point_x - width_w, point_y - width_s))
    scene.wall_props.prop_d = Vector((point_x + dim_x + width_e, point_y - width_s))
    scene.wall_props.prop_width = width_s
    scene.wall_props.prop_height = height
    create_wall(self, context, cursor)

    # West wall
    scene.wall_props.prop_o = Vector((point_x, point_y))
    scene.wall_props.prop_d = Vector((point_x, point_y + dim_y))
    scene.wall_props.prop_width = width_w
    scene.wall_props.prop_height = height
    create_wall(self, context, cursor)

    # North wall
    scene.wall_props.prop_o = Vector((point_x - width_w, point_y + dim_y))
    scene.wall_props.prop_d = Vector((point_x + dim_x + width_e, point_y + dim_y))
    scene.wall_props.prop_width = width_n
    scene.wall_props.prop_height = height
    create_wall(self, context, cursor)

    # East wall
    scene.wall_props.prop_o = Vector((point_x + dim_x + width_e, point_y))
    scene.wall_props.prop_d = Vector((point_x + dim_x + width_e, point_y + dim_y))
    scene.wall_props.prop_width = width_e
    scene.wall_props.prop_height = height
    create_wall(self, context, cursor)

    # Restore wall props
    scene.wall_props.prop_o = save_prop_o
    scene.wall_props.prop_d = save_prop_d
    scene.wall_props.prop_width = save_W
    scene.wall_props.prop_height = save_H

    bpy.context.scene.cursor.location.xyz = saved_location

class RoomProps(bpy.types.PropertyGroup):
    prop_point: bpy.props.FloatVectorProperty(default=(0.0, 0.0), subtype='XYZ', size=2)
    prop_dim: bpy.props.FloatVectorProperty(default=(5.0, 5.0), subtype='XYZ', size=2, min=0.0)
    prop_width_north: bpy.props.FloatProperty(min=0.0, default=0.2)
    prop_width_east: bpy.props.FloatProperty(min=0.0, default=0.2)
    prop_width_west: bpy.props.FloatProperty(min=0.0, default=0.2)
    prop_width_south: bpy.props.FloatProperty(min=0.0, default=0.2)
    prop_height: bpy.props.FloatProperty(min=0.0, default=2.4)

class CreateAbsoluteRoomOperator(Operator, AddObjectHelper):
    bl_idname = "mesh.create_absolute_room"
    bl_label = "Create room (absolute position)"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add room in a absolute location"

    def execute(self, context):
        create_room(self, context, Vector((0, 0, 0)))
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.room_props
        self.layout.prop(props, "prop_point", text="Point (m)")
        self.layout.prop(props, "prop_dim", text="Dimensions (m)")
        self.layout.prop(props, "prop_height", text="Wall height (m)")
        box = self.layout.box()
        box.label(text="Walls width (m)")
        row1 = box.row()
        row1.prop(props, "prop_width_north", text="N")
        row2 = box.row()
        row2.prop(props, "prop_width_west", text="W")
        row2.prop(props, "prop_width_east", text="E")
        row3 = box.row()
        row3.prop(props, "prop_width_south", text="S")
