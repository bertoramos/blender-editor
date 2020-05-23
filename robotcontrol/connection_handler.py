
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

    def __recv_ack_packet(self, pid):
        start_time = time.time()
        while abs(time.time() - start_time) < 3.0:
            try:
                msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
                ack_packet = ms.MsgPackSerializator.unpack(msgFromServer[0])
                if type(ack_packet) == dp.AckPacket:
                    if ack_packet.pid > bpy.context.scene.com_props.prop_last_recv_packet and ack_packet.ack_packet == pid:
                        bpy.context.scene.com_props.prop_last_recv_packet = ack_packet.pid
                        return ack_packet.status
            except Exception as e:
                pass
        raise exc.NotReceivedPacket(dp.AckPacket)

    def send_mode_packet(self, pid, mode):
        """
        Send a mode packet
        :raise: NotReceivedPacket if not receive an AckPacket or recognized_packet != pid
        :returns: ack status
        """
        mode_packet = dp.ModePacket(pid, mode)

        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(mode_packet), ConnectionHandler.serverAddr)

        status = self.__recv_ack_packet(mode_packet.pid)
        return status

    def receive_trace_packet(self):
        """
        Receive a trace packet or reached pose
        :raise: NotReceivedPacket if not receive a TracePacket
        :returns: (pid, pose)
        """
        start_time = time.time()
        while abs(time.time() - start_time) < 10.0:
            try:
                msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
                trace_packet = ms.MsgPackSerializator.unpack(msgFromServer[0])
                print(trace_packet)
                if trace_packet.pid > bpy.context.scene.com_props.prop_last_recv_packet and type(trace_packet) in {dp.TracePacket, dp.ReachedPosePacket}:
                    bpy.context.scene.com_props.prop_last_recv_packet = trace_packet.pid
                    return trace_packet.pose
            except Exception as e:
                pass
        raise exc.NotReceivedPacket(dp.TracePacket)

    def send_plan(self, pid_start, poses):
        """
        Send a plan to robot
        :raise: NotReceivedPacket if not receive some AckPacket
        :returns: 0 if plan was sent correctly
                    -1: fail open_plan
                    -2: fail send pose
                    -3: fail close_plan
        """
        pid = pid_start
        open_plan_packet = dp.OpenPlanPacket(pid, len(poses))

        bpy.context.scene.com_props.prop_last_sent_packet = pid
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(open_plan_packet), ConnectionHandler.serverAddr)

        status = self.__recv_ack_packet(open_plan_packet.pid)
        if status != 1:
            return -1

        for pose in poses:
            pid += 1
            bpy.context.scene.com_props.prop_last_sent_packet = pid
            add_pose_packet = dp.AddPosePlanPacket(pid, pose)
            ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(add_pose_packet), ConnectionHandler.serverAddr)
            status = self.__recv_ack_packet(add_pose_packet.pid)
            if status != 1:
                return -2

        pid += 1
        bpy.context.scene.com_props.prop_last_sent_packet = pid
        close_plan_packet = dp.ClosePlanPacket(pid)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(close_plan_packet), ConnectionHandler.serverAddr)
        status = self.__recv_ack_packet(close_plan_packet.pid)
        if status != 1:
            return -3

        return 0

    def send_start_plan_packet(self, pid):
        """
        Send a start plan packet
        :raise: NotReceivedPacket if not receive an AckPacket
        :returns: tuple ack (status, recognized_packet)
        """
        start_packet = dp.StartPlanPacket(pid)

        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(start_packet), ConnectionHandler.serverAddr)
        start_time = time.time()
        return self.__recv_ack_packet(start_packet.pid)

    def send_pause_plan_packet(self, pid):
        """
        Send a pause plan packet
        :raise: NotReceivedPacket if not receive an AckPacket
        :returns: tuple ack (status, recognized_packet)
        """
        pause_packet = dp.PausePlanPacket(pid)

        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(start_packet), ConnectionHandler.serverAddr)
        start_time = time.time()
        while abs(time.time() - start_time) < 3.0:
            try:
                msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
                ack_packet = ms.MsgPackSerializator.unpack(msgFromServer[0])
                if type(ack_packet) == dp.AckPacket:
                    if ack_packet.pid > bpy.context.scene.com_props.prop_last_recv_packet and ack_packet.ack_packet == pause_packet.pid:
                        bpy.context.scene.com_props.prop_last_recv_packet = ack_packet.pid
                        return (ack_packet.status, ack_packet.ack_packet)
            except Exception as e:
                pass
        raise exc.NotReceivedPacket(dp.AckPacket)

    def send_resume_plan_packet(self, pid):
        """
        Send resume plan packet
        :raise: NotReceivedPacket if not receive an AckPacket
        :returns: tuple ack (status, recognized_packet)
        """
        resume_packet = dp.ResumePlanPacket(pid)

        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(start_packet), ConnectionHandler.serverAddr)
        start_time = time.time()
        while abs(time.time() - start_time) < 3.0:
            try:
                msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
                ack_packet = ms.MsgPackSerializator.unpack(msgFromServer[0])
                if type(ack_packet) == dp.AckPacket:
                    if ack_packet.pid > bpy.context.scene.com_props.prop_last_recv_packet and ack_packet.ack_packet == resume_packet.pid:
                        bpy.context.scene.com_props.prop_last_recv_packet = ack_packet.pid
                        return (ack_packet.status, ack_packet.ack_packet)
            except Exception as e:
                pass
        raise exc.NotReceivedPacket(dp.AckPacket)

    def send_stop_plan_packet(self, pid):
        """
        Send stop plan packet
        :raise: NotReceivedPacket if not receive an AckPacket
        :returns: tuple ack (status, recognized_packet)
        """
        stop_packet = dp.StopPlanPacket(pid)

        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(start_packet), ConnectionHandler.serverAddr)
        start_time = time.time()
        while abs(time.time() - start_time) < 3.0:
            try:
                msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
                ack_packet = ms.MsgPackSerializator.unpack(msgFromServer[0])
                if type(ack_packet) == dp.AckPacket:
                    if ack_packet.pid > bpy.context.scene.com_props.prop_last_recv_packet and ack_packet.ack_packet == stop_packet.pid:
                        bpy.context.scene.com_props.prop_last_recv_packet = ack_packet.pid
                        return (ack_packet.status, ack_packet.ack_packet)
            except Exception as e:
                pass
        raise exc.NotReceivedPacket(dp.AckPacket)
