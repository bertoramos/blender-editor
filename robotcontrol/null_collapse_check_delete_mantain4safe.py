
import bpy
import bmesh

from mathutils import Vector
from math import sqrt, acos, degrees, radians
from mathutils.bvhtree import BVHTree

TOL = 0.0001

def dist(p0, p1):
    return sqrt((p1.x - p0.x)**2 + (p1.y - p0.y)**2 + (p1.z - p0.z)**2)

def cuadrante(x, y):

    if x >= 0 and y >= 0:
        # primer cuadrante
        return 1
    elif x <= 0 and y >= 0:
        # segundo cuadrante
        return 2
    elif x <= 0 and y <= 0:
        # tercer cuadrante
        return 3
    elif x >= 0 and y <= 0:
        # cuarto cuadrante
        return 4

def get_angles(p0, p1):
    l = dist(p0, p1)
    lp = sqrt((p1.x - p0.x)**2 + (p1.y - p0.y)**2)

    lx = p1.x - p0.x
    ly = p1.y - p0.y
    lz = p1.z - p0.z

    if l == 0:
        ay = 0
    else:
        ay = degrees(acos(float(lp / l)))

    if cuadrante(lp, lz) in {1, 2}:
        tetha_y = ay
    elif cuadrante(lp, lz) in {3, 4}:
        tetha_y = 360 - ay

    if lp == 0:
        az = 0
    else:
        az = degrees(acos(float(lx/lp)))

    if cuadrante(lx, ly) in {1, 2}:
        tetha_z = az
    elif cuadrante(lx, ly) in {3, 4}:
        tetha_z = 360 - az

    return -radians(tetha_y), radians(tetha_z)

def generate_area(p0, p1, w, h):
    """
    input:
        p0
        - start point - Vector
        p1
        - end point - Vector
        w
        - area width - float
        h
        - area height - float
    :returns area mesh name
    """
    l = dist(p0, p1)

    bpy.ops.mesh.primitive_cube_add()
    area_obj = bpy.context.object

    area_obj.dimensions = Vector((l, w, h))

    # origin set 0,0,0
    area_obj.location += Vector((l/2, 0, h/2))

    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    loc = Vector((p0.x, p0.y, p0.z))
    area_obj.location = loc

    # rotate
    dy, dz = get_angles(p0, p1)

    area_obj.rotation_euler.y = dy
    area_obj.rotation_euler.z = dz
    return area_obj.name

def is_overlapping(o1_name, o2_name):
    """
    Input:
        - o1 : object 1 name
        - o2 : object 2 name
    returns:
        - True if o1 overlap o2
    """
    obj1 = bpy.data.objects[o1_name]
    obj2 = bpy.data.objects[o2_name]

    if obj1 == obj2:
        return True

    tmp1 = obj1.copy()
    tmp1.data = obj1.data.copy()
    bpy.context.scene.collection.objects.link(tmp1)

    tmp2 = obj2.copy()
    tmp2.data = obj2.data.copy()
    bpy.context.scene.collection.objects.link(tmp2)

    [o.select_set(False) for o in bpy.data.objects]
    tmp1.select_set(True)
    tmp2.select_set(True)
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
    tmp1.select_set(False)
    tmp2.select_set(False)

    bmesh_tmp1 = bmesh.new()
    bmesh_tmp1.from_mesh(tmp1.data)
    bmesh_tmp1.transform(tmp1.matrix_world)

    bmesh_tmp2 = bmesh.new()
    bmesh_tmp2.from_mesh(tmp2.data)
    bmesh_tmp2.transform(tmp2.matrix_world)

    # Check overlap
    bool_res = True
    bvh_tmp1 = BVHTree.FromBMesh(bmesh_tmp1)
    bvh_tmp2 = BVHTree.FromBMesh(bmesh_tmp2)

    res = bvh_tmp1.overlap(bvh_tmp2)
    bool_res = (len(res) != 0)

    # Remove
    bpy.data.objects.remove(tmp1, do_unlink=True)
    bpy.data.objects.remove(tmp2, do_unlink=True)

    bmesh_tmp1.free()
    bmesh_tmp2.free()

    return bool_res

def points_inside(points, bm):
    """
    https://blender.stackexchange.com/questions/31693/how-to-find-if-a-point-is-inside-a-mesh
    input:
        points
        - a list of vectors (can also be tuples/lists)
        bm
        - a manifold bmesh with verts and (edge/faces) for which the
          normals are calculated already. (add bm.normal_update() otherwise)
    returns:
        a list
        - a mask lists with True if the point is inside the bmesh, False otherwise
    """

    rpoints = []
    addp = rpoints.append
    bvh = BVHTree.FromBMesh(bm, epsilon=0.0001)

    # return points on polygons
    for point in points:
        fco, normal, _, _ = bvh.find_nearest(point)
        # calcula vector
        #p2 = fco - Vector(point)
        p2 = Vector(point) - fco
        # Si el producto escalar es negativo, "están en direccion opuesta"
        v = p2.dot(normal)
        addp(v < 0.0)  # addp(v >= 0.0) ?

    return rpoints

def is_inside(obj1_name, obj2_name):
    """
    input:
        o1
        - name of first mesh
        o2
        - name of second mesh
    returns:
        if any vertex of o2 is inside o1
    """
    obj1 = bpy.data.objects[obj1_name]
    obj2 = bpy.data.objects[obj2_name]
    if obj1 == obj2:
        return True
    # Temporal copy
    tmp1 = obj1.copy()
    tmp1.data = obj1.data.copy()
    bpy.context.scene.collection.objects.link(tmp1)

    tmp2 = obj2.copy()
    tmp2.data = obj2.data.copy()
    bpy.context.scene.collection.objects.link(tmp2)

    [o.select_set(False) for o in bpy.data.objects]
    tmp1.select_set(True)
    tmp2.select_set(True)
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
    tmp1.select_set(False)
    tmp2.select_set(False)

    bmesh_tmp1 = bmesh.new()
    bmesh_tmp1.from_mesh(tmp1.data)

    # Check inside
    vertex_tmp2 = [vertex.co for vertex in tmp2.data.vertices]

    bool_res = points_inside(vertex_tmp2, bmesh_tmp1)

    # Remove
    bpy.data.objects.remove(tmp1, do_unlink=True)
    bpy.data.objects.remove(tmp2, do_unlink=True)

    bmesh_tmp1.free()

    return any(bool_res)

def collapse_check(p0, p1, w, h):
    """
    input:
        p0: Vector
        - first point
        p1: Vector
        - second point
        w: double
        - width area
        h: double
        - height area
    :returns: True if any object is into area
    """
    area_obj = generate_area(p0, p1, w, h)
    area_obj = bpy.data.objects[area_obj]

    collapse = False
    for obj in bpy.data.objects:
        # bpy.data.objects[mesh.name][common_options.OBJECT_TYPE.prop_name.value] = common_options.OBJECT_TYPE.WALL.value
        if obj != area_obj and obj.object_type in {'WALL', 'OBSTACLE'}:
            bool_inside = is_inside(area_obj.name, obj.name)
            bool_overlap = is_overlapping(area_obj.name, obj.name)
            inv_bool_inside = is_inside(area_obj.name, obj.name)
            inv_bool_overlap = is_overlapping(area_obj.name, obj.name)
            collapse = bool_inside or bool_overlap or inv_bool_inside or inv_bool_overlap
    bpy.data.objects.remove(area_obj, do_unlink=True)
    return collapse
