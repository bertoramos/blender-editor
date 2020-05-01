
import serialization as st
import datapacket
import path

class ModePacketPipeSerialization(st.Serialization):
    """
    Defines an algorithm to cipher-decipher a packet
    """

    @staticmethod
    def cipher(packet):
        """
        Apply a serialization method to packet to cipher
        """
        s = str(packet.pid) + '|' + str(packet.ptype) + '|' + str(packet.mode)
        return bytes(s, encoding='utf-8')

    @staticmethod
    def decipher(byte_packet):
        """
        Apply a deserialization method to packet to decipher
        """
        values = byte_packet.decode().split("|")
        assert len(values) == 3, "Error: No valid mode packet"
        assert int(values[1]) == 2, "Error: byte_packet is not a mode packet"
        return datapacket.ModePacket(int(values[0]), int(values[2]))

class AckPacketPipeSerialization(st.Serialization):
    """
    Defines an algorithm to cipher-decipher a packet
    """

    @staticmethod
    def cipher(packet):
        """
        Apply a serialization method to packet to cipher
        """
        s = str(packet.pid) + '|' + str(packet.ptype) + '|' + str(packet.ack_packet) + '|' + str(packet.status)
        return bytes(s, encoding='utf-8')

    @staticmethod
    def decipher(byte_packet):
        """
        Apply a deserialization method to packet to decipher
        """
        values = byte_packet.decode().split("|")
        assert len(values) == 4, "Error: No valid ack packet"
        assert int(values[1]) == 1, "Error: byte_packet is not a ack packet"
        return datapacket.AckPacket(int(values[0]), int(values[2]), int(values[3]))

class TracePacketPipeSerialization(st.Serialization):
    """
    Defines an algorithm to cipher-decipher a packet
    """

    @staticmethod
    def cipher(packet):
        """
        Apply a serialization method to packet to cipher
        """
        s = str(packet.pid) + '|' + str(packet.ptype) + '|' + str(packet.pose.x) + '|' + str(packet.pose.y) + '|' + str(packet.pose.gamma)
        return bytes(s, encoding='utf-8')

    @staticmethod
    def decipher(byte_packet):
        """
        Apply a deserialization method to packet to decipher
        """
        values = byte_packet.decode().split("|")
        assert len(values) == 5, "Error: No valid trace packet"
        assert int(values[1]) == 3, "Error: byte_packet is not a ack packet"
        pose = path.Pose(float(values[2]), float(values[3]), 0, 0, 0, float(values[4]))
        return datapacket.TracePacket(int(values[0]), pose)



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
    def cipher(packet: st.Packet) -> bytes:
        ptype = packet.ptype
        cipher_method = choose_serialization.get(ptype)
        if cipher_method is None:
            raise "Error: Serialization method not found (cipher). Check packet type identification"
        return cipher_method.cipher(packet)

    @staticmethod
    def decipher(byte_packet: bytes) -> st.Packet:
        bpacket = clear(byte_packet)
        values = bpacket.decode().split("|")
        ptype = int(values[1])
        decipher_method = choose_serialization.get(ptype)
        if decipher_method is None:
            raise "Error: Serialization method not found (decipher). Check packet type identification"
        return decipher_method.decipher(bpacket)
