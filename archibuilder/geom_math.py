
import bpy
from mathutils import Vector
from math import sqrt

def dist(a: Vector, b: Vector):
    return sqrt((b.x - a.x)**2 + (b.y - a.y)**2 + (b.z - a.z)**2)
