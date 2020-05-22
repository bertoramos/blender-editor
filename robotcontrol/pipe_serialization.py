
import serialization as st
import datapacket
import path

class ModePacketPipeSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """ 

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        l = list(iter(packet))
        s = "|".join(map(str, l))
        return bytes(s, encoding='utf-8')

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 3, "Error: No valid mode packet"
        assert int(list_packet[1]) == 2, "Error: byte_packet is not a mode packet"
        return datapacket.ModePacket(int(list_packet[0]), int(list_packet[2]))

class AckPacketPipeSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        l = list(iter(packet))
        s = "|".join(map(str, l))
        return bytes(s, encoding='utf-8')

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 4, "Error: No valid ack packet"
        assert int(list_packet[1]) == 1, "Error: byte_packet is not a ack packet"
        return datapacket.AckPacket(int(list_packet[0]), int(list_packet[2]), int(list_packet[3]))

class TracePacketPipeSerialization(st.Serialization):
    """
    Defines an algorithm to pack-unpack a packet
    """

    @staticmethod
    def pack(packet):
        """
        Apply a serialization method to pack
        """
        l = list(iter(packet))
        s = "|".join(map(str, l))
        return bytes(s, encoding='utf-8')

    @staticmethod
    def unpack(list_packet):
        """
        Apply a deserialization method to unpack
        """
        assert len(list_packet) == 5, "Error: No valid trace packet"
        assert int(list_packet[1]) == 3, "Error: byte_packet is not a ack packet"
        pose = path.Pose(float(list_packet[2]), float(list_packet[3]), 0, 0, 0, float(list_packet[4]))
        return datapacket.TracePacket(int(list_packet[0]), pose)



choose_serialization = {1: AckPacketPipeSerialization,
                        2: ModePacketPipeSerialization,
                        3: TracePacketPipeSerialization}

def clear(sbyte: bytes) -> bytes:
    r = bytes()
    i = 0
    while i < len(sbyte) and sbyte[i] != 0:
        r += bytes([sbyte[i]])
        i+=1
    return r

class PipeSerializator(st.Serializator):

    @staticmethod
    def pack(packet: st.Packet) -> bytes:
        ptype = packet.ptype
        cipher_method = choose_serialization.get(ptype)
        if cipher_method is None:
            raise "Error: Serialization method not found (pack). Check packet type identification"
        return cipher_method.pack(packet)

    @staticmethod
    def unpack(byte_packet: bytes) -> st.Packet:
        bpacket = clear(byte_packet)
        values = bpacket.decode().split("|")
        ptype = int(values[1])
        decipher_method = choose_serialization.get(ptype)
        if decipher_method is None:
            raise "Error: Serialization method not found (unpack). Check packet type identification"
        return decipher_method.unpack(values)
