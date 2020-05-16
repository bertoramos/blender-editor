
import bpy
import bmesh
from mathutils.geometry import intersect_line_line
from mathutils import Vector
from math import sqrt, acos, degrees, radians, pi
from mathutils.bvhtree import BVHTree

TOL = 0.0001

"""
Check a mesh overlap other mesh
"""

def is_overlapping(bm1, bm2):
    """
    Input:
        - bm1 : bmesh 1st object
        - bm2 : bmesh 2nd object
    returns:
        - True if bm1 overlap bm2
    """

    # Check overlap
    bool_res = True
    bvh1 = BVHTree.FromBMesh(bm1)
    bvh2 = BVHTree.FromBMesh(bm2)
    res = bvh1.overlap(bvh2)

    del bvh1
    del bvh2

    return len(res) != 0

"""
Check mesh inside other mesh
"""

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

def is_inside(bm1, bm2):
    """
    input:
        bm1
        - bmesh 1st object
        bm2
        - bmesh 2nd object
    returns:
        if any vertex of bm2 is inside bm1
    """
    # Check inside
    vertex_tmp2 = [vertex.co for vertex in bm2.verts]
    bool_res = points_inside(vertex_tmp2, bm1)
    for v, r in zip(vertex_tmp2, bool_res):
        print(v, r)
    return any(bool_res)

"""
Check a face of a mesh overlap face other mesh
"""

def point_in_segment(point, line):
    dist = lambda p1, p2: (p2-p1).length
    D = dist(line[0], line[1])
    d1 = dist(line[0], point)
    d2 = dist(point, line[1])
    return abs(D - (d1 + d2)) <= TOL

def segments_intersect(line1, line2):
    """
    Check if two segments intersect
    line1: (Vector, Vector)
    line2: (Vector, Vector)
    :returns: True if line1 and line2 intersect
    """
    dist = lambda p0, p1: (p1 - p0).length

    x0, y0 = line1[0], line1[1]
    x1, y1 = line2[0], line2[1]

    res = intersect_line_line(x0, y0, x1, y1)
    if res is not None:
        r0 = res[0]
        r1 = res[1]
        # puntos mas cercanos de en una linea a otra linea deben ser iguales
        if dist(r0, r1) <= TOL:
            # comprobar que el punto de cruce pertenece a ambos segmentos
            if point_in_segment(r0, line1) and point_in_segment(r0, line2):
                return True
    return False

def point_inside_infinite_plane(point, plane):
    """
    Check if infinite plane contains point
    point: Vector((x,y,z))
    plane: BMFace
    """
    # plane
    normal = plane.normal.normalized()
    nx, ny, nz = normal.x, normal.y, normal.z
    q = plane.verts[0].co
    md = nx*q.x + ny*q.y + nz*q.z # constant: -d
    plane_f = lambda x, y, z : nx*x + ny*y + nz*z - md

    # point
    x0, y0, z0 = point.x, point.y, point.z

    return abs(plane_f(x0, y0, z0)) <= TOL

def point_inside_finite_plane(point, plane):
    """
    Check if finite plane contains point
    point: Vector((x,y,z))
    plane: BMFace
    """
    contain = point_inside_infinite_plane(point, plane) # Infinite plane contains point
    reflect = bmesh.geometry.intersect_face_point(plane, (point.x, point.y, point.z)) # Point reflects over plane
    any_vertex_equal = any([(v.co.xyz - point).length <= TOL for v in plane.verts]) # Any vertex equals point

    return (contain and reflect) or any_vertex_equal

def are_coplanar(plane1, plane2):
    """
    plane1 and plane2 are both infinite planes
    returns: plane1 and plane2 are coplanar
    """
    # Plano 1
    p1_norm = plane1.normal.normalized()
    points1 = plane1.verts
    # Plano 2
    p2_norm = plane2.normal.normalized()
    points2 = plane2.verts

    if p1_norm.length == 0 or p2_norm.length == 0:
        return False
    angle = p1_norm.angle(p2_norm) # acos(p1_norm.dot(p2_norm)/(p1_norm.length*p2_norm.length))

    are_parallel = abs(angle) <= TOL or abs(angle - pi) <= TOL # planes are parallel or coplanar (normal vector angle: 0 or pi)
    P = points1[0].co.xyz
    contains = point_inside_infinite_plane(P, plane2) # plane2 contains a point of plane1
    return are_parallel and contains

def infinite_plane_contains_line(plane, line):
    norm = plane.normal.normalized()
    v_line = (line[1] - line[0]).normalized()

    # Infinite plane contains line
    prod = norm.dot(v_line)
    parallel = prod == 0 or abs(prod) <= TOL
    contains_point = point_inside_infinite_plane(line[0], plane)
    return parallel and contains_point

def finite_plane_contains_line(plane, line):
    """
    Checks if plane contains line
    plane: BMFace
    line: (Vector, Vector)
    """
    if not infinite_plane_contains_line(plane, line):
        # infinite plane does not contains line
        return False

    # Any edge intersect
    for edge in plane.edges:
        e1 = edge.verts[0].co.xyz
        e2 = edge.verts[1].co.xyz
        # check intersect
        if segments_intersect(line, (e1, e2)):
            return True
    p1in = point_inside_finite_plane(line[0], plane)
    p2in = point_inside_finite_plane(line[1], plane)
    return p1in and p2in

def plane_inside(plane1, plane2):
    """
    Check if plane1 is inside plane2
    plane1 and plane2 are coplanar and overlap
    - plane1, plane2:
        BMFace
    """
    # Plano 1
    p1_norm = plane1.normal.normalized()
    points1 = plane1.verts
    # Plano 2
    p2_norm = plane2.normal.normalized()
    points2 = plane1.verts

    # Los planos infinitos que contienen a plane1 y plane2 son coplanares
    if not are_coplanar(plane1, plane2):
        return False
    # Se cruza algun edge o está uno dentro de otro
    for edge in plane1.edges:
        e1 = edge.verts[0].co.xyz
        e2 = edge.verts[1].co.xyz
        if finite_plane_contains_line(plane2, (e1, e2)):
            return True
    for edge in plane2.edges:
        e1 = edge.verts[0].co.xyz
        e2 = edge.verts[1].co.xyz
        if finite_plane_contains_line(plane1, (e1, e2)):
            return True
    return False

def face_overlap(bm1, bm2):
    """
    Check if any face of two bmesh overlap
    -
    """
    for face1 in bm1.faces:
        for face2 in bm2.faces:
            res_a = plane_inside(face1, face2)
            res_b = plane_inside(face2, face1)
            if res_a or res_b:
                return True
    return False

def check_overlap(bm0, bm1):
    """
    Check if two bmesh collides
    """
    # check overlap
    # check inside
    # check face_collision
    if is_overlapping(bm0, bm1):
        return True
    if face_overlap(bm0, bm1):
        return True
    return False
