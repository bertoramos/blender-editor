
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

    def getLastPath(self):
        assert len(PathContainer.__instance.__list) > 0
        return PathContainer.__instance.__list[-1]

    def getLastAction(self):
        return PathContainer.__instance.__list[-1].get(-1) if len(PathContainer.__instance.__list) > 0 else None

    def removeLastAction(self):
        return PathContainer.__instance.__list.pop() if len(PathContainer.__instance.__list) > 0 else None

    def clear(self):
        PathContainer.__instance.__list.clear()

    def extendActions(self, actions):
        idx = len(PathContainer.__instance.__list)
        PathContainer.__instance.__list.extend(actions)

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
