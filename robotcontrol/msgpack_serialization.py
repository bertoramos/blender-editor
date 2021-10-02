
from math import radians, degrees
import msgpack

# begin local import: Change to from . import MODULE
import serialization as st
import datapacket
import path
# end local import: Change to from . import MODULE

class ModePacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.ModePacket, "Error : packet is not a ModePacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 4, "Error: No valid mode packet"
        assert list_packet[1] == 2, "Error: list_packet is not a mode packet"
        return datapacket.ModePacket(list_packet[0], list_packet[2], list_packet[3])

class AckPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.AckPacket, "Error : packet is not a AckPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 4, "Error: No valid ack packet"
        assert list_packet[1] == 1, "Error: list_packet is not a ack packet"
        return datapacket.AckPacket(list_packet[0], list_packet[2], list_packet[3])

class TracePacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.TracePacket, "Error : packet is not a TracePacket"
        l = list(iter(packet))

        from math import degrees
        return [l[0], l[1], l[2].x, l[2].y, degrees(l[2].gamma)]

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 5, "Error: No valid trace packet"
        assert list_packet[1] == 3, "Error: list_packet is not a trace packet"

        from math import radians
        pose = path.Pose(list_packet[2], list_packet[3], 0.0, 0.0, 0.0, radians(list_packet[4]))
        return datapacket.TracePacket(list_packet[0], pose)

class OpenPlanPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.OpenPlanPacket, "Error : packet is not a ModePacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 3, "Error: No valid open plan packet"
        assert list_packet[1] == 4, "Error: list_packet is not a open plan packet"
        n_poses = list_packet[2]
        return datapacket.OpenPlanPacket(list_packet[0], n_poses)

class AddPosePlanPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.AddPosePlanPacket, "Error: packet is not an AddPosePlanPacket"
        l = list(iter(packet))

        from math import degrees
        return [l[0], l[1], l[2].x, l[2].y, degrees(l[2].gamma)]

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 5, "Error: No valid add pose plan packet"
        assert list_packet[1] == 5, "Error: list_packet is not a add pose plan packet"

        from math import radians
        pose = path.Pose(list_packet[2], list_packet[3], 0.0, 0.0, 0.0, radians(list_packet[4]))
        return datapacket.AddPosePlanPacket(list_packet[0], pose)

class ClosePlanPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.ClosePlanPacket, "Error: packet is not a ClosePlanPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 2, "Error: No valid trace packet"
        assert list_packet[1] == 6, "Error: list_packet is not a ack packet"
        return datapacket.ClosePlanPacket(list_packet[0])

class StartPlanPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.StartPlanPacket, "Error: packet is not a StartPlanPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 2, "Error: No valid start plan packet"
        assert list_packet[1] == 7, "Error: list_packet is not a start plan packet"
        return datapacket.StartPlanPacket(list_packet[0])

class PausePlanPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.PausePlanPacket, "Error: packet is not a PausePlanPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 2, "Error: No valid pause plan packet"
        assert list_packet[1] == 9, "Error: list_packet is not a pause plan packet"
        return datapacket.PausePlanPacket(list_packet[0])

class ResumePlanPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.ResumePlanPacket, "Error: packet is not a ResumePlanPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 2, "Error: No valid resume plan packet"
        assert list_packet[1] == 10, "Error: list_packet is not a resume plan packet"
        return datapacket.ResumePlanPacket(list_packet[0])

class StopPlanPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.StopPlanPacket, "Error: packet is not a stop plan packet"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 2, "Error: No valid stop plan packet"
        assert list_packet[1] == 8, "Error: list_packet is not a stop plan packet"
        return datapacket.StopPlanPacket(list_packet[0])

class ReachedPosePacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.ReachedPosePacket, "Error: packet is not a ReachedPosePacket"
        l = list(iter(packet))

        from math import degrees
        return [l[0], l[1], l[2].x, l[2].y, degrees(l[2].gamma)]

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 5, "Error: No valid reached pose packet " + "len= " + str(len(list_packet))
        assert list_packet[1] == 11, "Error: list_packet is not a reached pose packet"
        x = list_packet[2]
        y = list_packet[3]
        tetha = list_packet[4]
        from math import radians
        pose = path.Pose(x, y, 0, 0, 0, radians(tetha))
        return datapacket.ReachedPosePacket(list_packet[0], pose)

class ChangeSpeedPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.ChangeSpeedPacket, "Error: packet is not a ChangeSpeedPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 3, "Error: No valid change speed packet"
        assert list_packet[1] == 12, "Error: list_packet is not a change speed packet"
        return datapacket.ChangeSpeedPacket(list_packet[0], list_packet[2])

class CalibrationRequestPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """
    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.CalibrationRequestPacket, "Error: packet is not a CalibrationRequestPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        assert len(list_packet) == 2, "Error: no valid CalibrationRequestPacket"
        assert list_packet[1] == 13, "Error: packet is not a CalibrationRequestPacket"
        pid = list_packet[0]
        return datapacket.CalibrationRequestPacket(pid)

class StartCalibrationPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """
    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.StartCalibrationPacket, "Error: packet is not a StartCalibrationPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        assert len(list_packet) == 3, "Error: no valid StartCalibrationPacket"
        assert list_packet[1] == 14, "Error: packet is not a StartCalibrationPacket"
        pid = list_packet[0]
        nbeacons = list_packet[2]
        return datapacket.StartCalibrationPacket(pid, nbeacons)

class AddUltrasoundBeaconPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """
    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.AddUltrasoundBeaconPacket, "Error: packet is not an AddUltrasoundBeaconPacket"
        list_packet = list(iter(packet))
        pid = list_packet[0]
        ptype = list_packet[1]
        beacon_id = list_packet[2]
        x = list_packet[3].x
        y = list_packet[3].y
        z = list_packet[3].z
        a = radians(list_packet[3].alpha)
        b = radians(list_packet[3].beta)
        g = radians(list_packet[3].gamma)
        return [pid, ptype, beacon_id, x, y, z, a, b, g]

    @staticmethod
    def unpack(list_packet):
        assert len(list_packet) == 9, "Error: no valid AddUltrasoundBeaconPacket"
        assert list_packet[1] == 15, "Error: packet is not an AddUltrasoundBeaconPacket"
        pid = list_packet[0]
        ptype = list_packet[1]
        beacon_id = list_packet[2]
        x = list_packet[3]
        y = list_packet[4]
        z = list_packet[5]
        a = list_packet[6]
        b = list_packet[7]
        g = list_packet[8]
        pose_beacon = path.Pose(x, y, z, a, b, g)
        return datapacket.AddUltrasoundBeaconPacket(pid, beacon_id, pose_beacon)


class CloseCalibrationPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """
    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.CloseCalibrationPacket, "Error: packet is not a CloseCalibrationPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        assert len(list_packet) == 2, "Error: no valid CloseCalibrationPacket"
        assert list_packet[1] == 16, "Error: packet is not a CloseCalibrationPacket"
        pid = list_packet[0]
        return datapacket.CloseCalibrationPacket(pid)


class ManualTranslationPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """
    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.ManualTranslationPacket, "Error: packet is not a ManualTranslationPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        assert len(list_packet) == 5, "Error: no valid ManualTranslationPacket"
        assert list_packet[1] == 17, "Error: packet is not a ManualTranslationPacket"
        pid = list_packet[0]
        return datapacket.ManualTranslationPacket(pid)

class ManualRotationPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """
    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.ManualRotationPacket, "Error: packet is not a ManualRotationPacket"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        assert len(list_packet) == 5, "Error: no valid ManualRotationPacket"
        assert list_packet[1] == 18, "Error: packet is not a ManualRotationPacket"
        pid = list_packet[0]
        return datapacket.ManualRotationPacket(pid)

class ManualStopPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        assert type(packet) == datapacket.ManualStopPacket, "Error: packet is not a manual stop packet"
        return list(iter(packet))

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 2, "Error: No valid manual stop packet"
        assert list_packet[1] == 19, "Error: list_packet is not a manual stop packet"
        return datapacket.StopPlanPacket(list_packet[0])

class EndPlanReachedPacketMsgPackSerialization(st.Serialization):

    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.EndPlanReachedPacket, "Error: packet is not an end plan reached"
        return list(iter(packet))
    
    @staticmethod
    def unpack(cls, list_packet: list):
        assert len(list_packet) == 2, "Error: No valid end plan reached packet"
        assert list_packet[1] == 20, "Error: list_packet is not an end plan reached packet"
        return datapacket.EndPlanReachedPacket(list_packet[0])

class CaptureStartedPacketMsgPackSerialization(st.Serialization):
    
    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.CaptureStartedPacket, "Error: packet is not a capture started packet"
        return list(iter(packet))
    
    @staticmethod
    def unpack(cls, list_packet: list):
        assert len(list_packet) == 2, "Error: No valid capture started packet"
        assert list_packet[1] == 21, "Error: list_packet is not a capture started packet"
        return datapacket.EndPlanReachedPacket(list_packet[0])


class CaptureEndedPacketMsgPackSerialization(st.Serialization):
    
    @staticmethod
    def pack(packet):
        assert type(packet) == datapacket.CaptureStartedPacket, "Error: packet is not a capture ended packet"
        return list(iter(packet))
    
    @staticmethod
    def unpack(cls, list_packet: list):
        assert len(list_packet) == 2, "Error: No valid capture ended packet"
        assert list_packet[1] == 22, "Error: list_packet is not a capture ended packet"
        return datapacket.EndPlanReachedPacket(list_packet[0])


# { ptype : SerializationClass, ... }
# choose_serialization.get(ptype) -> return: ptype pack/unpack method
choose_serialization = {
                        1:  AckPacketMsgPackSerialization,
                        2:  ModePacketMsgPackSerialization,
                        3:  TracePacketMsgPackSerialization,
                        4:  OpenPlanPacketMsgPackSerialization,
                        5:  AddPosePlanPacketMsgPackSerialization,
                        6:  ClosePlanPacketMsgPackSerialization,
                        7:  StartPlanPacketMsgPackSerialization,
                        8:  StopPlanPacketMsgPackSerialization,
                        9:  PausePlanPacketMsgPackSerialization,
                        10: ResumePlanPacketMsgPackSerialization,
                        11: ReachedPosePacketMsgPackSerialization,
                        12: ChangeSpeedPacketMsgPackSerialization,
                        13: CalibrationRequestPacketMsgPackSerialization,
                        14: StartCalibrationPacketMsgPackSerialization,
                        15: AddUltrasoundBeaconPacketMsgPackSerialization,
                        16: CloseCalibrationPacketMsgPackSerialization,
                        17: ManualTranslationPacketMsgPackSerialization,
                        18: ManualRotationPacketMsgPackSerialization,
                        19: ManualStopPacketMsgPackSerialization,
                        20: EndPlanReachedPacketMsgPackSerialization,
                        21: CaptureStartedPacketMsgPackSerialization,
                        22: CaptureEndedPacketMsgPackSerialization
                       }

class MsgPackSerializator(st.Serializator):

    @staticmethod
    def pack(packet: st.Packet) -> bytes:
        ptype = packet.ptype
        cipher_method = choose_serialization.get(ptype)
        if cipher_method is None:
            raise "Error: Serialization method not found (pack). Check packet type identification"
        values = cipher_method.pack(packet)
        return msgpack.packb(values, use_bin_type=True)

    @staticmethod
    def unpack(byte_packet: bytes) -> st.Packet:
        values = msgpack.unpackb(byte_packet)
        ptype = values[1]
        decipher_method = choose_serialization.get(ptype)
        if decipher_method is None:
            raise "Error: Serialization method not found (unpack). Check packet type identification"
        return decipher_method.unpack(values)
