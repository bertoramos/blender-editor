
import serialization as st
import datapacket
import path
import msgpack

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
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 3, "Error: No valid mode packet"
        assert list_packet[1] == 2, "Error: list_packet is not a mode packet"
        return datapacket.ModePacket(list_packet[0], list_packet[2])

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
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

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
        return msgpack.packb(l, use_bin_type=True)

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 5, "Error: No valid trace packet"
        assert list_packet[1] == 3, "Error: list_packet is not a trace packet"
        pose = path.Pose(list_packet[2], list_packet[3], 0.0, 0.0, 0.0, list_packet[4])
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
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

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
        res = [l[0], l[1], l[2].x, l[2].y, degrees(l[2].gamma)]
        return msgpack.packb(res, use_bin_type=True)

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 5, "Error: No valid add pose plan packet"
        assert list_packet[1] == 5, "Error: list_packet is not a add pose plan packet"
        pose = path.Pose(list_packet[2], list_packet[3], 0.0, 0.0, 0.0, list_packet[4])
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
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

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
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

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
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

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
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

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
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

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
        return msgpack.packb(l, use_bin_type=True)

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 2, "Error: No valid reached pose packet"
        assert list_packet[1] == 11, "Error: list_packet is not a reached pose packet"
        return datapacket.TracePacket(list_packet[0])


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
                        11: ReachedPosePacketMsgPackSerialization
                       }

class MsgPackSerializator(st.Serializator):

    @staticmethod
    def pack(packet: st.Packet) -> bytes:
        ptype = packet.ptype
        cipher_method = choose_serialization.get(ptype)
        if cipher_method is None:
            raise "Error: Serialization method not found (pack). Check packet type identification"
        return cipher_method.pack(packet)

    @staticmethod
    def unpack(byte_packet: bytes) -> st.Packet:
        values = msgpack.unpackb(byte_packet)
        ptype = values[1]
        decipher_method = choose_serialization.get(ptype)
        if decipher_method is None:
            raise "Error: Serialization method not found (unpack). Check packet type identification"
        return decipher_method.unpack(values)
