
import serialization as st
import datapacket
import path
import msgpack

class ModePacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to cipher-decipher a packet
    """

    @staticmethod
    def cipher(packet):
        """
        Apply a serialization method to packet to cipher
        """
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

    @staticmethod
    def decipher(list_packet):
        """
        Apply a deserialization method to packet to decipher
        """
        assert len(list_packet) == 3, "Error: No valid mode packet"
        assert int(list_packet[1]) == 2, "Error: byte_packet is not a mode packet"
        return datapacket.ModePacket(int(list_packet[0]), int(list_packet[2]))

class AckPacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to cipher-decipher a packet
    """

    @staticmethod
    def cipher(packet):
        """
        Apply a serialization method to packet to cipher
        """
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

    @staticmethod
    def decipher(list_packet):
        """
        Apply a deserialization method to packet to decipher
        """
        assert len(list_packet) == 4, "Error: No valid ack packet"
        assert int(list_packet[1]) == 1, "Error: byte_packet is not a ack packet"
        return datapacket.AckPacket(int(list_packet[0]), int(list_packet[2]), int(list_packet[3]))

class TracePacketMsgPackSerialization(st.Serialization):
    """
    Defines an algorithm to cipher-decipher a packet
    """

    @staticmethod
    def cipher(packet):
        """
        Apply a serialization method to packet to cipher
        """
        l = list(iter(packet))
        return msgpack.packb(l, use_bin_type=True)

    @staticmethod
    def decipher(list_packet):
        """
        Apply a deserialization method to packet to decipher
        """
        assert len(list_packet) == 5, "Error: No valid trace packet"
        assert int(list_packet[1]) == 3, "Error: byte_packet is not a ack packet"
        pose = path.Pose(float(list_packet[2]), float(list_packet[3]), 0, 0, 0, float(list_packet[4]))
        return datapacket.TracePacket(int(list_packet[0]), pose)

choose_serialization = {1: AckPacketMsgPackSerialization,
                        2: ModePacketMsgPackSerialization,
                        3: TracePacketMsgPackSerialization}

class MsgPackSerializator(st.Serializator):

    @staticmethod
    def cipher(packet: st.Packet) -> bytes:
        ptype = packet.ptype
        cipher_method = choose_serialization.get(ptype)
        if cipher_method is None:
            raise "Error: Serialization method not found (cipher). Check packet type identification"
        return cipher_method.cipher(packet)

    @staticmethod
    def decipher(byte_packet: bytes) -> st.Packet:
        values = msgpack.unpackb(byte_packet)
        ptype = values[1]
        decipher_method = choose_serialization.get(ptype)
        if decipher_method is None:
            raise "Error: Serialization method not found (decipher). Check packet type identification"
        return decipher_method.decipher(values)
