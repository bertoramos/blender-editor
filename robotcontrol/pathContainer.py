
import bpy

import path
import utils
from mathutils import Vector

def draw_path_id(context, loc, name, txt, color, font, font_align):
    # Draw notes
    hint_space = 10
    rotation = 0

    path_note_name = utils.draw_text(context, name, txt, loc, color, hint_space, font, font_align, rotation)
    bpy.data.objects[path_note_name].protected = True
    return path_note_name

class Path:
    def __init__(self, idx, robot_id, actions):
        self.__idx = idx
        self.__robot_id = robot_id
        self.__actions = actions
        loc = actions[0].p0.loc # Indicates start of path
        loc.z += 0.5
        self.__note_name = draw_path_id(bpy.context, loc, "note_path" + str(idx), "ID" + str(idx) + " for " + str(robot_id), Vector((1,0,0,1)), 14, 'C')

    def delete_last_action(self):
        v = self.__actions[-1]
        self.__actions.remove(v)
        return v

    def get(self, key):
        return self.__actions[key]

    def __len__(self):
        return len(self.__actions)

    def __del__(self):
        note = bpy.data.objects[self.__note_name]
        bpy.data.objects.remove(note, do_unlink=True)

    def __get_idx(self):
        return self.__idx

    idx = property(__get_idx)


class PathContainer:

    """
    Save many paths
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__list = []
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def removeLastPath(self):
        assert len(PathContainer.__instance.__list) > 0
        path = PathContainer.__instance.__list.pop()
        del path

    def getLastPath(self):
        assert len(PathContainer.__instance.__list) > 0
        return PathContainer.__instance.__list[-1]

    def getLastAction(self):
        return PathContainer.__instance.__list[-1].get(-1)

    def getLastActionOfRobot(self, idx):
        for p in PathContainer.__instance.__list:
            if p.idx == idx:
                return p.get(-1)
        return None

    def removeLastAction(self):
        a = self.getLastPath().delete_last_action() # removeLast
        if len(self.getLastPath()) == 0:
            self.removeLastPath()
        return a

    def clear(self):
        PathContainer.__instance.__list.clear()

    def extendActions(self, robot_id, actions):
        idx = len(PathContainer.__instance.__list)
        PathContainer.__instance.__list.append(Path(idx, robot_id, actions))

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

    def appendAction(self, action):
        id = len(TempPathContainer.__instance.__list)
        TempPathContainer.__instance.__list.append(action)

    def removeLast(self):
        assert len(TempPathContainer.__instance.__list) > 0
        action = TempPathContainer.__instance.__list.pop()
        return action

    def clear(self):
        TempPathContainer.__instance.__list.clear()

    def pushActions(self, id_robot):
        if len(TempPathContainer.__instance.__list) > 0:
            # Move elements in __list
            sent_list = []
            for i in range(len(TempPathContainer.__instance.__list)):
                a = TempPathContainer.__instance.__list.pop(0)
                sent_list.append(a)
            PathContainer().extendActions(id_robot, sent_list)
            self.clear()

    def __str__(self):
        return str(TempPathContainer.__instance.__list)

    def __len__(self):
        return len(TempPathContainer.__instance.__list)
