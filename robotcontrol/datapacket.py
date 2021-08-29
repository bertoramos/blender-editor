# begin local import: Change to from . import MODULE
import serialization as st
# end local import: Change to from . import MODULE

"""
Paquete desconocido (0)
Paquete de reconocimiento (1)
Paquete de “modo” (2): Modo robomap ON (1) / Modo robomap OFF (0)
Paquete de seguimiento (3)
Paquete abrir plan (4)
Paquete agregar pose de ruta (5)
Paquete cerrar plan (6)
Paquete iniciar plan de navegación (7)
Paquete de detener (8)
Paquete de pausa (9)
Paquete continuar (10)
Paquete pose de ruta alcanzado (11)
Paquete de velocidad (12)
Paquete de solicitud de informacion de calibrado (13)
Paquete de abrir calibrado (14)
Paquete de agregar baliza ultrasónica (15)
Paquete de cerrar calibrado (16)
"""

class ModePacket(st.Packet):

    def __init__(self, pid, mode, initial_speed, ptype=2):
        super().__init__(pid, ptype)
        self.__mode = mode
        self.__initial_speed = initial_speed

    def __get_mode(self):
        return self.__mode

    def __get_initial_speed(self):
        return self.__initial_speed

    def __str__(self):
        return "[{}|{}|{}|{}]".format(self.pid, self.ptype, self.__mode, self.__initial_speed)

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__mode, self.__initial_speed])

    mode = property(__get_mode)
    initial_speed = property(__get_initial_speed)

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
        #return "[" + str(self.pid) + "|" + str(self.ptype) + "|" + str(self.__ack_packet) + "|" + str(self.__status) + "]"
        return "[{}|{}|{}|{}]".format(self.pid, self.ptype, self.__ack_packet, self.__status)

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
        return "[{}|{}|{}]".format(self.pid, self.ptype, self.__pose)

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
        return "[{}|{}|{}]".format(self.pid, self.ptype, self.__n_poses)

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__n_poses])

    n_poses = property(__get_n_poses)

class AddPosePlanPacket(st.Packet):

    def __init__(self, pid, pose, ptype=5):
        super().__init__(pid, ptype)
        self.__pose = pose

    def __get_pose(self):
        return self.__pose

    def __str__(self):
        return "[{}|{}|{}]".format(self.pid, self.ptype, self.__pose)

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__pose])

    pose = property(__get_pose)

class ClosePlanPacket(st.Packet):

    def __init__(self, pid, ptype=6):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[{}|{}]".format(self.pid, self.ptype)

    def __iter__(self):
        return iter([self.pid, self.ptype])


class StartPlanPacket(st.Packet):

    def __init__(self, pid, ptype=7):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[{}|{}]".format(self.pid, self.ptype)

    def __iter__(self):
        return iter([self.pid, self.ptype])

class PausePlanPacket(st.Packet):

    def __init__(self, pid, ptype=9):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[{}|{}]".format(self.pid, self.ptype)

    def __iter__(self):
        return iter([self.pid, self.ptype])

class ResumePlanPacket(st.Packet):

    def __init__(self, pid, ptype=10):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[{}|{}]".format(self.pid, self.ptype)

    def __iter__(self):
        return iter([self.pid, self.ptype])

class StopPlanPacket(st.Packet):

    def __init__(self, pid, ptype=8):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[{}|{}]".format(self.pid, self.ptype)

    def __iter__(self):
        return iter([self.pid, self.ptype])

class ReachedPosePacket(st.Packet):

    def __init__(self, pid, pose, ptype=11):
        super().__init__(pid, ptype)
        self.__pose = pose

    def __get_pose(self):
        return self.__pose

    def __str__(self):
        return "[{}|{}|{}]".format(self.pid, self.ptype, self.__pose)

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__pose])

    pose = property(__get_pose)

class ChangeSpeedPacket(st.Packet):

    def __init__(self, pid, speed, ptype=12):
        super().__init__(pid, ptype)
        self.__speed = speed

    def __get_speed(self):
        return self.__speed

    def __str__(self):
        return "[{}|{}|{}]".format(self.pid, self.ptype, self.__speed)

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__speed])

    speed = property(__get_speed)

class CalibrationRequestPacket(st.Packet):

    def __init__(self, pid, ptype=13):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[{}|{}]".format(self.pid, self.ptype)

    def __iter__(self):
        return iter([self.pid, self.ptype])

class StartCalibrationPacket(st.Packet):

    def __init__(self, pid, nbeacons, ptype=14):
        super().__init__(pid, ptype)
        self.__nbeacons = nbeacons

    def __str__(self):
        return "[{}|{}|{}]".format(self.pid, self.ptype, self.__nbeacons)

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__nbeacons])

    def __get_nbeacons(self):
        return self.__nbeacons

    nbeacons = property(__get_nbeacons)

class AddUltrasoundBeaconPacket(st.Packet):

    def __init__(self, pid, beacon_id, beacon_pose, ptype=15):
        super().__init__(pid, ptype)
        self.__beacon_id = beacon_id
        self.__beacon_pose = beacon_pose

    def __str__(self):
        return "[{}|{}|{}|{}]".format(self.pid, self.ptype, self.__beacon_id, self.__beacon_pose)

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__beacon_id, self.__beacon_pose])

    def __get_beacon_id(self):
        return self.__beacon_id

    def __get_beacon_pose(self):
        return self.__beacon_pose

    beacon_id = property(__get_beacon_id)
    beacon_pose = property(__get_beacon_pose)

class CloseCalibrationPacket(st.Packet):

    def __init__(self, pid, ptype=16):
        super().__init__(pid, ptype)

    def __str__(self):
        return "[{}|{}]".format(self.pid, self.ptype)

    def __iter__(self):
        return iter([self.pid, self.ptype])

class ManualTranslationPacket(st.Packet):

    def __init__(self, pid, dx, dy, speed, ptype=17):
        super().__init__(pid, ptype)
        self.__dx = dx
        self.__dy = dy
        self.__speed = speed

    def __str__(self):
        return '|'.join('{}'.format(e) for e in [self.pid, self.ptype, self.__dx, self.__dy, self.__speed])

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__dx, self.__dy, self.__speed])

    def __get_dx(self):
        return self.__dx

    def __get_dy(self):
        return self.__dy

    def __get_speed(self):
        return self.__speed

    dx = property(__get_dx)
    dy = property(__get_dy)
    speed = property(__get_speed)

class ManualRotationPacket(st.Packet):

    def __init__(self, pid, direction, speed, ptype=18):
        super().__init__(pid, ptype)
        self.__direction = direction
        self.__speed = speed

    def __str__(self):
        return '|'.join('{}'.format(e) for e in [self.pid, self.ptype, self.__direction, self.__speed])

    def __iter__(self):
        return iter([self.pid, self.ptype, self.__direction, self.__speed])

    def __get_direction(self):
        return self.__direction

    def __get_speed(self):
        return self.__speed

    direction = property(__get_direction)
    speed = property(__get_speed)
