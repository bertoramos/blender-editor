
import bpy
from mathutils import Vector
import time

# begin local import: Change to from . import MODULE
import path
import utils
# end local import: Change to from . import MODULE


class PathContainer:
    """
    Save actions
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__list = []
            cls.__instance = object.__new__(cls)
            cls.__instance.__last_update = -1
        return cls.__instance

    def getLastAction(self):
        return PathContainer.__instance.__list[-1] if len(PathContainer.__instance.__list) > 0 else None

    def removeLastAction(self):
        self.__last_update = int(time.time())
        return PathContainer.__instance.__list.pop() if len(PathContainer.__instance.__list) > 0 else None

    def clear(self):
        PathContainer.__instance.__list.clear()
        self.__last_update = int(time.time())

    def extendActions(self, actions):
        idx = len(PathContainer.__instance.__list)
        PathContainer.__instance.__list.extend(actions)
        self.__last_update = int(time.time())

    def addAllActions(self, actions):
        PathContainer.__instance.__list = actions
        self.__last_update = int(time.time())

    def getAllActions(self):
        return PathContainer.__instance.__list

    def getLastUpdate(self):
        return int(self.__last_update)

    def loadPoses(self, poses_list, context=None):
        self.clear()
        for pose_index in range(len(poses_list)-1):
            action = path.Action(poses_list[pose_index], poses_list[pose_index+1])
            if context is not None:
                action.draw_annotation(context)
            if pose_index == 0:
                action.set_first_action()
            PathContainer.__instance.__list.append(action)
        self.__last_update = int(time.time())

    def _get_poses(self):
        poses = []
        for action in PathContainer.__instance.__list:
            poses.append(action.p0)
        last_action = self.getLastAction()
        if last_action is not None:
            poses.append(last_action.p1)
        return poses

    def __iter__(self):
        return iter(PathContainer.__instance.__list)

    def __str__(self):
        return str(PathContainer.__instance.__list)

    def __len__(self):
        return len(PathContainer.__instance.__list)

    poses = property(_get_poses)

class TempPathContainer:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__list = []
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def appendAction(self, action):
        id = len(TempPathContainer.__instance.__list)
        TempPathContainer.__instance.__list.append(action)

    def removeLast(self):
        assert len(TempPathContainer.__instance.__list) > 0
        action = TempPathContainer.__instance.__list.pop()
        return action

    def remove(self, action_index):
        if action_index < len(TempPathContainer.__instance.__list):
            action = TempPathContainer.__instance.__list.pop(action_index)
            del action

    def insert(self, action_index, action):
        TempPathContainer.__instance.__list.insert(action_index, action)

    def getLastAction(self):
        return TempPathContainer.__instance.__list[-1] if len(TempPathContainer.__instance.__list) > 0 else None

    def clear(self):
        TempPathContainer.__instance.__list.clear()

    def loadActions(self):
        if len(PathContainer()) > 0:
            TempPathContainer.__instance.__list = PathContainer().getAllActions()

    def pushActions(self):
        if len(TempPathContainer.__instance.__list) > 0:
            # Move elements in __list
            sent_list = []
            for i in range(len(TempPathContainer.__instance.__list)):
                a = TempPathContainer.__instance.__list.pop(0)
                sent_list.append(a)
            PathContainer().addAllActions(sent_list)
            self.clear()

    def __iter__(self):
        return iter(TempPathContainer.__instance.__list)

    def __getitem__(self, item_index):
        return TempPathContainer.__instance.__list[item_index]

    def __str__(self):
        return str(TempPathContainer.__instance.__list)

    def __len__(self):
        return len(TempPathContainer.__instance.__list)
