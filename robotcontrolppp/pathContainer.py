
import bpy
import pose

from collections import namedtuple

Node = namedtuple('Node', 'id pose mesh_line mesh_arrow')

class PathContainer:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__list = []
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def removeLast(self):
        assert len(PathContainer.__instance.__list) > 0
        nodo = PathContainer.__instance.__list.pop()
        return nodo.pose, nodo.mesh_line, nodo.mesh_arrow

    def clear(self):
        PathContainer.__instance.__list.clear()

    def extendPoses(self, poses):
        PathContainer.__instance.__list.extend(poses)

    def __str__(self):
        return str(PathContainer.__instance.__list)

    def __len__(self):
        return len(PathContainer.__instance.__list)

class TempPathContainer:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__list = []
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def appendPose(self, pose, mesh_line_name, mesh_arrow_name):
        id = len(TempPathContainer.__instance.__list)
        nodo = Node(id, pose, mesh_line_name, mesh_arrow_name)
        TempPathContainer.__instance.__list.append(nodo)

    def removeLast(self):
        assert len(TempPathContainer.__instance.__list) > 0
        nodo = TempPathContainer.__instance.__list.pop()
        return nodo.pose, nodo.mesh_line, nodo.mesh_arrow

    def clear(self):
        TempPathContainer.__instance.__list.clear()

    def pushPoses(self):
        pc = PathContainer()
        pc.extendPoses(TempPathContainer.__instance.__list)
        self.clear()

    def __str__(self):
        return str(TempPathContainer.__instance.__list)

    def __len__(self):
        return len(TempPathContainer.__instance.__list)
