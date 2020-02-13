
import bpy
import path

class PathContainer:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__list = []
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def removeLast(self):
        assert len(PathContainer.__instance.__list) > 0
        action = PathContainer.__instance.__list.pop()
        return action

    def getLast(self):
        assert len(PathContainer.__instance.__list) > 0
        return PathContainer.__instance.__list[-1]

    def clear(self):
        PathContainer.__instance.__list.clear()

    def extendActions(self, actions):
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
        pc = PathContainer()
        pc.extendActions(TempPathContainer.__instance.__list)
        self.clear()

    def __str__(self):
        return str(TempPathContainer.__instance.__list)

    def __len__(self):
        return len(TempPathContainer.__instance.__list)
