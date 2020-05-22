
import serialization as st

class ModePacket(st.Packet):

    def __init__(self, pid, mode, ptype=2):
        super().__init__(pid, ptype)
        self.__mode = mode

    def __get_mode(self):
        return self.__mode

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype) + "|" + str(self.__mode) + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__mode])

    mode = property(__get_mode)

class AckPacket(st.Packet):

    def __init__(self, pid, ack_packet, status, ptype=1):
        super().__init__(pid, ptype)
        self.__ack_packet = ack_packet
        self.__status = status

    def __get_ack_packet(self):
        return self.__ack_packet

    def __get_status(self):
        return self.__status

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype) + "|" + str(self.__ack_packet) + "|" + str(self.__status) + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__ack_packet, self.__status])

    ack_packet = property(__get_ack_packet)
    status = property(__get_status)

class TracePacket(st.Packet):

    def __init__(self, pid, pose, ptype=3):
        super().__init__(pid, ptype)
        self.__pose = pose

    def __get_pose(self):
        return self.__pose

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype) + "|" + str(self.__pose) + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__pose.x, self.__pose.y, self.__pose.gamma])

    pose = property(__get_pose)

class OpenPlanPacket(st.Packet):

    def __init__(self, pid, n_poses, ptype=4):
        super().__init__(pid, ptype)
        self.__n_poses = n_poses

    def __get_n_poses(self):
        return self.__n_poses

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype) + "|" + str(self.__n_poses) + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__n_poses])

class AddPosePacket(st.Packet):

    def __init__(self, pid, pose, ptype=5):
        super().__init__(pid, ptype)
        self.__pose = pose

    def __get_pose(self):
        return self.__pose

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype) + "|" + str(self.__pose) + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__pose])

class ClosePlanPacket(st.Packet):

    def __init__(self, pid, ptype=6):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype) + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype])

class StartPlanPacket(st.Packet):

    def __init__(self, pid, ptype=7):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype)  + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype])

class PausePlanPacket(st.Packet):

    def __init__(self, pid, ptype=9):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype)  + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype])

class ResumePlanPacket(st.Packet):

    def __init__(self, pid, ptype=10):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype)  + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype])

class StopPlanPacket(st.Packet):

    def __init__(self, pid, ptype=8):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype)  + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype])

class ReachedPosePacket(st.Packet):

    def __init__(self, pid, ptype=11):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype) + "]"

    def __iter__(self):
        return iter([self.pid, self.ptype])
