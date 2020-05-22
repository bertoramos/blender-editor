
import bpy

import socket
import time
import msgpack_serialization as ms
import datapacket as dp

import connection_exceptions as exc

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
        bpy.context.scene.com_props.prop_last_recv_packet = -1

    def hasSocket(self):
        return ConnectionHandler.client_socket is not None

    def send_mode_packet(self, mode_packet):
        """
        Send a mode packet
        :raise: NotReceivedPacket if not receive an AckPacket
        :returns: AckPacket associated to mode_packet
        """
        print("pre sendto")
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.cipher(mode_packet), ConnectionHandler.serverAddr)
        print("post sendto")
        start_time = time.time()
        while abs(time.time() - start_time) < 3.0:
            try:
                msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
                ack_packet = ms.MsgPackSerializator.decipher(msgFromServer[0])
                if type(ack_packet) == dp.AckPacket:
                    if ack_packet.pid > bpy.context.scene.com_props.prop_last_recv_packet and ack_packet.ack_packet == mode_packet.pid:
                        bpy.context.scene.com_props.prop_last_recv_packet = ack_packet.pid
                        return ack_packet
            except Exception as e:
                pass
        raise exc.NotReceivedPacket(dp.AckPacket)

    def receive_trace_packet(self):
        """
        Receive a trace packet
        :raise: NotReceivedPacket if not receive a TracePacket
        :returns: TracePacket
        """
        start_time = time.time()
        while abs(time.time() - start_time) < 3.0:
            try:
                msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
                trace_packet = ms.MsgPackSerializator.decipher(msgFromServer[0])
                if trace_packet.pid > bpy.context.scene.com_props.prop_last_recv_packet and type(trace_packet) == dp.TracePacket:
                    bpy.context.scene.com_props.prop_last_recv_packet = trace_packet.pid
                    return trace_packet
            except Exception as e:
                pass
        raise exc.NotReceivedPacket(dp.TracePacket)
