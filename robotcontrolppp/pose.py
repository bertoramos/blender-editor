
import bpy
from mathutils import Vector

TOL = 0.0001

class Pose:

    def __init__(self, x, y, z, alpha, beta, gamma):
        self._x = x
        self._y = y
        self._z = z
        self._a = alpha
        self._b = beta
        self._g = gamma

    @classmethod
    def fromVector(cls, loc, angle):
        return cls(loc.x, loc.y, loc.z, angle.x, angle.y, angle.z)

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_z(self):
        return self._z

    def get_a(self):
        return self._a

    def get_b(self):
        return self._b

    def get_g(self):
        return self._g

    def get_loc(self):
        return Vector((self.x, self.y, self.z))

    def get_rotation(self):
        return Vector((self._a, self._b, self._g))

    def __eq__(self, other):
        return abs(self._x - other.x) <= TOL and abs(self._y - other.y) <= TOL and abs(self._z - other.z) <= TOL and \
                abs(self.alpha - other.alpha) <= TOL and abs(self.beta - other.beta) <= TOL and abs(self.gamma - other.gamma) <= TOL

    def __str__(self):
        return "Location(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ") " + \
            "Angle(" + str(self.alpha) + ", " + str(self.beta) + ", " + str(self.gamma) + ")"

    x = property(get_x)
    y = property(get_y)
    z = property(get_z)
    alpha = property(get_a)
    beta = property(get_b)
    gamma = property(get_g)
    loc = property(get_loc)
    rotation = property(get_rotation)
