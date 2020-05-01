
import abc

class Packet(abc.ABC):

    def __init__(self, pid, ptype):
        self.__pid = pid
        self.__ptype = ptype

    def __get_pid(self):
        return self.__pid

    def __get_ptype(self):
        return self.__ptype

    pid = property(__get_pid)
    ptype = property(__get_ptype)


class Serialization:
    """
    Defines an algorithm to cipher-decipher a packet
    """

    @staticmethod
    @abc.abstractmethod
    def cipher(cls, packet):
        """
        Apply a serialization method to packet to cipher
        """
        raise NotImplementedError("Cipher not implemented. Use subclasses")

    @staticmethod
    @abc.abstractmethod
    def decipher(cls, byte_packet):
        """
        Apply a deserialization method to packet to decipher
        """
        raise NotImplementedError("Decipher not implemented. Use subclasses")

class Serializator:
    """
    Choose an Serialization method to cipher-decipher a received packet
    """

    @staticmethod
    @abc.abstractmethod
    def cipher(cls, packet):
        """
        Convert Packet to byte using __bytes__ magic method
        """
        raise NotImplementedError("Cipher not implemented. Use subclasses")

    @staticmethod
    @abc.abstractmethod
    def decipher(cls, byte_packet):
        """
        Convert a bytes to Packet, selecting a serialization method
        """
        raise NotImplementedError("Decipher not implemented. Use subclasses")
