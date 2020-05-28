
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
        self.__last_trace = None


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
        if ConnectionHandler.client_socket is not None:
            ConnectionHandler.client_socket.close()
            ConnectionHandler.client_socket = None
            Buffer().clear()
        #bpy.context.scene.com_props.prop_last_recv_packet = -1

    def hasSocket(self):
        return ConnectionHandler.client_socket is not None

    def receive_packet(self):
        try:
            msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
            packet = ms.MsgPackSerializator.unpack(msgFromServer[0])
            if packet.pid > bpy.context.scene.com_props.prop_last_recv_packet:
                Buffer().set_packet(packet)
        except Exception as e:
            pass

    def receive_ack_packet(self, pid):
        start_time = time.time()
        ack_packet = None
        while abs(time.time() - start_time) < 3.0 and ack_packet is None:
            ack_packet = Buffer().get_ack_packet(pid)
        return ack_packet.status == 1 if ack_packet is not None else False

    def send_change_mode(self, pid, mode):
        """
        Send a mode packet
        :returns: False if send mode operation fails or status != 1
        """
        mode_packet = dp.ModePacket(pid, mode)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(mode_packet), ConnectionHandler.serverAddr)
        return self.receive_ack_packet(pid)

    def send_plan(self, start_pid, poses):
        """
        Send a plan to robot
        :params start_pid: pid for open plan packet
        :returns: len(poses) if the plan was sent successfully
                  -1 if open plan fails
                  -2 if close plan fails
                  { 0 <= n < len(poses) } if n pose was not add
        """
        pid = start_pid

        # Open plan packet
        open_plan_packet = dp.OpenPlanPacket(pid, len(poses))
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(open_plan_packet), ConnectionHandler.serverAddr)
        if not self.receive_ack_packet(pid):
            return -1

        # Add pose
        for n, pose in enumerate(poses):
            print("Sent : " , str(pose))
            pid += 1
            bpy.context.scene.com_props.prop_last_sent_packet = pid
            add_pose_packet = dp.AddPosePlanPacket(pid, pose)
            ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(add_pose_packet), ConnectionHandler.serverAddr)
            if not self.receive_ack_packet(pid):
                return n

        pid += 1
        bpy.context.scene.com_props.prop_last_sent_packet = pid

        # Close plan packet
        close_plan_packet = dp.ClosePlanPacket(pid)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(close_plan_packet), ConnectionHandler.serverAddr)
        if not self.receive_ack_packet(pid):
            return -2

        return len(poses)

    def send_start_plan(self, pid):
        """
        Send a start plan packet
        :returns: False if send start plan operation fails or status != 1
        """
        start_plan_packet = dp.StartPlanPacket(pid)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(start_plan_packet), ConnectionHandler.serverAddr)
        return self.receive_ack_packet(pid)

    def send_stop_plan(self, pid):
        """
        Send a stop plan packet
        :returns: False if send stop plan operation fails or status != 1
        """
        stop_plan_packet = dp.StopPlanPacket(pid)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(stop_plan_packet), ConnectionHandler.serverAddr)
        return self.receive_ack_packet(pid)

    def send_pause_plan(self, pid):
        """
        Send pause plan packet
        :returns: False if send pause plan operation fails or status != 1
        """
        pause_plan_packet = dp.PausePlanPacket(pid)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(pause_plan_packet), ConnectionHandler.serverAddr)
        return self.receive_ack_packet(pid)

    def send_resume_plan(self, pid):
        """
        Send resume plan packet
        :returns: False if send resume plan operation fails or status != 1
        """
        resume_plan_packet = dp.ResumePlanPacket(pid)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(resume_plan_packet), ConnectionHandler.serverAddr)
        return self.receive_ack_packet(pid)
