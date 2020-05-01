
import serialization as st

class ModePacket(st.Packet):

    def __init__(self, pid, mode, ptype=2):
        super().__init__(pid, ptype)
        self.__mode = mode

    def __get_mode(self):
        return self.__mode

    def __str__(self):
        return "[" + str(self.pid) + "|" + str(self.ptype) + "|" + str(self.__mode) + "]"

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

    pose = property(__get_pose)
