
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
        return cls.__instance

    def getLastAction(self):
        return PathContainer.__instance.__list[-1] if len(PathContainer.__instance.__list) > 0 else None

    def removeLastAction(self):
        return PathContainer.__instance.__list.pop() if len(PathContainer.__instance.__list) > 0 else None

    def getActionByTimestamp(self, timestamp):
        for a in PathContainer.__instance.__list:
            if a.timestamp == timestamp:
                return a

    def findPose(self, pose):
        """
        incoming_action ----> pose ----> outgoing_action
            if incoming_action is None -> 'pose' is first pose
            if outgoing_action is None -> 'pose' is last pose
            if incoming_action and outgoing_action is not None -> incoming_action.p1 == outgoing_action.p0 == pose
            if incoming_action and outgoing_action is None -> pose not in PathContainer
        """
        incoming_action = None
        outgoing_action = None

        action_tmp = None
        index_action = -1
        for i, a in enumerate(PathContainer.__instance.__list):
            if a.p0 == pose or a.p1 == pose:
                index_action = i # action location in list
                action_tmp = a
                break
        if action_tmp is None:
            return None, None # pose not found
        if action_tmp.p0 == pose:
            return None, action_tmp # First pose
        if action_tmp.p1 == pose:
            if index_action == len(PathContainer.__instance.__list)-1:
                return action_tmp, None # Last pose
            return action_tmp, PathContainer.__instance.__list[index_action] # midpoint
        return None, None

    def clear(self):
        PathContainer.__instance.__list.clear()

    def extendActions(self, actions):
        idx = len(PathContainer.__instance.__list)
        PathContainer.__instance.__list.extend(actions)

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
