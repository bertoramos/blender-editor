
import bpy

import socket
import time
import msgpack_serialization as ms
import datapacket as dp

import connection_exceptions as exc


class Buffer:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__buffer = []
            cls.__last_trace = None
        return cls.__instance

    def set_packet(self, packet):
        if type(packet) == dp.TracePacket:
            self.__last_trace = packet
        else:
            self.__buffer.append(packet)

    def get_last_trace_packet(self):
        return self.__last_trace

    def get_ack_packet(self, ack_packet):
        """
        :param ack_packet: recognized packet
        """
        ret_packet = None
        for p in self.__buffer:
            if type(p) == dp.AckPacket and p.ack_packet == ack_packet:
                ret_packet = p
                break
        if ret_packet is not None:
            self.__buffer.remove(ret_packet)
        return ret_packet

    def clear(self):
        self.__buffer.clear()


bufferSize = 128

class ConnectionHandler:
    __instance = None
    running = False

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.client_socket = None
        return cls.__instance

    def create_socket(self, clientAddr=("127.0.0.1", 1500), serverAddr=("127.0.0.1", 1999)):
        """
        Create a socket
        """
        ConnectionHandler.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        ConnectionHandler.client_socket.bind(clientAddr)
        ConnectionHandler.client_socket.settimeout(3)
        ConnectionHandler.serverAddr = serverAddr

    def remove_socket(self):
        ConnectionHandler.client_socket.close()
        ConnectionHandler.client_socket = None
        #bpy.context.scene.com_props.prop_last_recv_packet = -1

    def hasSocket(self):
        return ConnectionHandler.client_socket is not None

    def receive_packet(self):
        try:
            msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
            packet = ms.MsgPackSerializator.unpack(msgFromServer[0])
            if packet.pid > bpy.context.scene.com_props.prop_last_recv_packet:
                if type(packet) == dp.TracePacket:
                    Buffer().set_trace_packet(packet)
                else:
                    Buffer().set_packet(packet)
        except Exception as e:
            pass

    def send_mode_packet(self, pid, mode):
        """
        Send a mode packet
        :returns: False if send mode operation fails or status != 1
        """
        mode_packet = dp.ModePacket(pid, mode)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(mode_packet), ConnectionHandler.serverAddr)
        start_time = time.time()
        ack_packet = None
        while abs(time.time() - start_time) < 10.0 and ack_packet is None:
            ack_packet = Buffer().get_ack_packet(pid)
        print(ack_packet)
        return ack_packet.status == 1 if ack_packet is not None else False

    def send_plan(self, start_pid, pose):
        pass

    def send_start_plan(self, pid):
        pass

    def send_stop_plan(self, pid):
        pass

    def send_pause_plan(self, pid):
        pass

    def send_resume_plan(self, pid):
        pass
