
import bpy

import path
import utils
from mathutils import Vector

import time

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

    def getLastUpdate(self):
        return int(self.__last_update)

    def _get_poses(self):
        poses = []
        for action in PathContainer.__instance.__list:
            poses.append(action.p0)
        last_action = self.getLastAction()
        if last_action is not None:
            poses.append(last_action.p1)
        return poses

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

    def clear(self):
        TempPathContainer.__instance.__list.clear()

    def pushActions(self):
        if len(TempPathContainer.__instance.__list) > 0:
            # Move elements in __list
            sent_list = []
            for i in range(len(TempPathContainer.__instance.__list)):
                a = TempPathContainer.__instance.__list.pop(0)
                sent_list.append(a)
            PathContainer().extendActions(sent_list)
            self.clear()

    def __str__(self):
        return str(TempPathContainer.__instance.__list)

    def __len__(self):
        return len(TempPathContainer.__instance.__list)
