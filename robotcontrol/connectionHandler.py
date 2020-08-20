
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
            cls.__reached_poses = []
            cls.__calibration_packets = []
            cls.__last_trace = None
        return cls.__instance

    def set_packet(self, packet):

        if type(packet) == dp.TracePacket:
            self.__last_trace = packet
            bpy.context.scene.com_props.prop_last_recv_packet = packet.pid
        elif type(packet) == dp.ReachedPosePacket:
            self.__reached_poses.append(packet)
            bpy.context.scene.com_props.prop_last_recv_packet = packet.pid
        elif type(packet) in {dp.CalibrationRequestPacket, dp.StartCalibrationPacket, dp.CloseCalibrationPacket, dp.AddUltrasoundBeaconPacket}:
            self.__calibration_packets.append(packet)
        else:
            self.__buffer.append(packet)
            bpy.context.scene.com_props.prop_last_recv_packet = packet.pid

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

    def get_reached_poses(self):
        return [e.pose for e in self.__reached_poses]

    def get_calibration_packets(self):
        return self.__calibration_packets

    def rmv_from_calibration_packets(self, packet):
        self.__calibration_packets.remove(packet)

    def clear_calibration_packets(self):
        self.__calibration_packets.clear()

    def clear_reached_poses(self):
        self.__reached_poses.clear()

    def clear(self):
        self.__buffer.clear()
        self.__last_trace = None

    def __str__(self):
        s = ""

        s += "General buffer: \n"
        for p in self.__buffer:
            s += "\t" + str(p) + "\n"

        s += "Reached poses buffer: \n"
        for p in self.__reached_poses:
            s += "\t" + str(p) + "\n"

        s += "Calibration packets buffer: \n"
        for p in self.__calibration_packets:
            s += "\t" + str(p) + "\n"

        s += "-------------\nLast trace : " + str(self.__last_trace)
        return s

    def __iter__(self):
        return iter(self.__buffer)


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

    def hasSocket(self):
        return ConnectionHandler.client_socket is not None

    def receive_packet(self, op):

        try:
            msgFromServer = ConnectionHandler.client_socket.recvfrom(bufferSize)
            packet = ms.MsgPackSerializator.unpack(msgFromServer[0])
            if type(packet) != dp.TracePacket:
                op.report({'INFO'}, "Receive: " + str(packet) + " " + str(type(packet)))

            if packet.pid > bpy.context.scene.com_props.prop_last_recv_packet:
                Buffer().set_packet(packet)

            # acknowledge reached pose packet
            if type(packet) == dp.ReachedPosePacket:
                bpy.context.scene.com_props.prop_last_sent_packet += 1
                ack_pid = bpy.context.scene.com_props.prop_last_sent_packet
                status = 1
                ack_packet = dp.AckPacket(ack_pid, packet.pid, status)
                ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(ack_packet), ConnectionHandler.serverAddr)
        except Exception as e:
            import sys
            op.report({'INFO'}, str(e) + " line "+ str(sys.exc_info()[-1].tb_lineno))
            return False
        return True


    def receive_ack_packet(self, pid):
        start_time = time.time()
        ack_packet = None
        while abs(time.time() - start_time) < 3.0 and ack_packet is None:
            ack_packet = Buffer().get_ack_packet(pid)
        return ack_packet.status == 1 if ack_packet is not None else False

    def send_change_mode(self, pid, mode, initial_speed):
        """
        Send a mode packet
        :returns: False if send mode operation fails or status != 1
        """
        mode_packet = dp.ModePacket(pid, mode, initial_speed)
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

    def send_change_speed(self, pid, speed):
        """
        Send a change speed packet
        :returns: False if status != 1 or not ack is received
        """
        change_speed_packet = dp.ChangeSpeedPacket(pid, speed)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(change_speed_packet), ConnectionHandler.serverAddr)
        return self.receive_ack_packet(pid)

    def receive_start_calibration_packet(self):
        """
        Receive start calibration packet
        :returns: StartCalibrationPacket
        """
        start_time = time.time()
        start_calibration_packet = None
        while abs(time.time() - start_time) < 10.0 and start_calibration_packet is None:
            for p in Buffer().get_calibration_packets():
                if type(p) == dp.StartCalibrationPacket:
                    start_calibration_packet = p
                    Buffer().rmv_from_calibration_packets(p)
                    break
        if start_calibration_packet is not None:
            bpy.context.scene.com_props.prop_last_recv_packet = start_calibration_packet.pid

            bpy.context.scene.com_props.prop_last_sent_packet += 1
            pid = bpy.context.scene.com_props.prop_last_sent_packet
            ack_packet = dp.AckPacket(pid, start_calibration_packet.pid, 1)
            ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(ack_packet), ConnectionHandler.serverAddr)
        return start_calibration_packet

    def receive_calibration_data(self):
        """
        Send a calibration request packet and returns calibration information
        :returns: calibration information or None
        """

        # REQUEST PACKET
        bpy.context.scene.com_props.prop_last_sent_packet += 1
        pid = bpy.context.scene.com_props.prop_last_sent_packet

        request_calibration_packet = dp.CalibrationRequestPacket(pid)
        ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(request_calibration_packet), ConnectionHandler.serverAddr)

        if not self.receive_ack_packet(pid):
            return None

        # START CALIBRATION
        start_cal_packet = self.receive_start_calibration_packet()
        if start_cal_packet is None:
            return None

        nbeacons = start_cal_packet.nbeacons
        n_nochanges = 0
        close_recv = False

        prev_dim = 0
        while n_nochanges < 10 and not close_recv:
            cal_data = Buffer().get_calibration_packets()
            if len(cal_data) == prev_dim:
                n_nochanges += 1
            else:
                n_nochanges = 0
            for p in cal_data:
                if type(p) == dp.CloseCalibrationPacket:
                    close_recv = True
            prev_dim = len(cal_data)

        calibration_data = []
        cal_data = Buffer().get_calibration_packets()
        for p in cal_data:
            bpy.context.scene.com_props.prop_last_sent_packet += 1
            pid = bpy.context.scene.com_props.prop_last_sent_packet

            ack_packet = dp.AckPacket(pid, p.pid, 1)
            ConnectionHandler.client_socket.sendto(ms.MsgPackSerializator.pack(ack_packet), ConnectionHandler.serverAddr)

            if type(p) == dp.CloseCalibrationPacket:
                bpy.context.scene.com_props.prop_last_recv_packet = p.pid
            if type(p) == dp.AddUltrasoundBeaconPacket:
                calibration_data.append(p)
        Buffer().clear_calibration_packets()

        return calibration_data
