# python3
# @Time    : 2021.05.18
# @Author  : 张鹏飞
# @FileName: rflink.py
# @Software: 机器鲨鱼上位机
# @修改历史:
# version: 机器海豚上位机    author: Sijie Li    data: 2022.04.06

from enum import Enum

FishID = Enum('Fish_id',({\
    'FISH_ALL':b'\x00',\
	'Fish_1':b'\x33'}))

# Recstate枚举类型
Recstate = Enum('Recstate',(\
	'WAITING_FF',\
    'SENDER_ID',\
	'RECEIVER_ID',\
    'RECEIVE_LEN',\
	'RECEIVE_PACKAGE',\
	'RECEIVE_CHECK'))




# Command枚举类型(set:3-28,read:29-40,goto:41-43)
Command = Enum('Command',(\
    'SHAKING_HANDS',\
    'SYNCHRONIZE_CLOCK',\
    'SET_SWIM_RUN',\
    'SET_SWIM_START',\
    'SET_SWIM_STOP',\
    'SET_SWIM_FORCESTOP',\
    'SET_LPECT_FLAP',\
    'SET_LPECT_FEATHER',\
    'SET_LPECT_PITCH', \
    'SET_RPECT_FLAP', \
    'SET_RPECT_FEATHER', \
    'SET_RPECT_PITCH', \
    "SET_DATASHOW_OVER", \
    'SET_TAIL', \
    'SET_PUMP_OFF',\
    'SET_PUMP_IN',\
    'SET_PUMP_OUT',\
    'SET_LONGITUDINAL_MASS_FMOVE',\
    'SET_LONGITUDINAL_MASS_BMOVE',\
    'SET_LONGITUDINAL_MASS_STOP',\
    'SET_FREQ_ADD',\
    'SET_FREQ_SUB',\
    'READ_ROBOT_STATUS',\
    'READ_ROBOT_DATA',\
    "READ_IMU_ATTITUDE", \
    "READ_IMU_ACCEL", \
    "READ_IMU_GYRO", \
    "READ_DEPTH",\
    "READ_CURRENT", \
    "READ_VOLTAGE", \
    "READ_POWER", \
    "READ_FLAP", \
    "READ_FEATHER", \
    "READ_PITCH", \
    "READ_TAIL", \
    "DEPTH_CONTROL", \
    "DEPTH_CONTROL_START", \
    "DEPTH_CONTROL_OVER", \
    "SET_DEPTH_PID", \
    "SET_ANGLE_PID", \
    "CENTER_CONTROL", \
    "TURN_LEFT", \
    "TURN_RIGHT", \
    "ANGLE_CONTROL", \
    "ANGLE_CONTROL_END", \
    "GLIDE_RISE", \
    "GLIDE_DIVE"))


class RFLink():
    """
    Robotic Fish 通讯协议类
    通讯协议规范:(一帧完整数据如下:)
    2022.04.06自定义修改后:
    0xFF, SENDER_ID, RECEIVER_ID, RECEIVE_LEN, RECEIVE_PACKAGE, RECEIVE_CHECK

    2021.10.11自定义修改后:
    :arg length: 消息长度
    :arg message: 消息(byte类型)

    :attributes RFLink_receivedata:接收状态机,解码RFLink通讯协议
    :attributes RFLink_packdata:将待发送数据按RFLink通讯协议打包
    """
    def __init__(self):
        self.sender_id = b''
        self.receiver_id = b''
        self.length = 0
        self.message = b''
        self._receive_state = Recstate.WAITING_FF
        self._checksum = 0
        self._byte_count = 0
        self.MY_ID = b'\x11'
        self.FRIEND_ID = b'\x33'

    def RFLink_receivedata(self, rx_data):
        """
        RFLink接收状态机
        :param rx_data: 串口接收到的数据
        :return: 当接收到一帧完整数据时,返回1;否则,返回0.
        """

        if self._receive_state==Recstate.WAITING_FF:
            if rx_data==b'\xff':
                self._receive_state = Recstate.SENDER_ID
                self._checksum = ord(rx_data) # 转换为ASCII码
                self.message = b''
                self.length = 0
                self._byte_count = 0
        
        elif self._receive_state == Recstate.SENDER_ID:
            # print('进入SENDER_ID')
            if rx_data == self.FRIEND_ID:
                self._receive_state = Recstate.RECEIVER_ID
                self._checksum += ord(rx_data)
            else:
                self._receive_state = Recstate.WAITING_FF

        elif self._receive_state == Recstate.RECEIVER_ID:
            # print('进入RECEIVER_ID')
            if rx_data == self.MY_ID:
                self._receive_state = Recstate.RECEIVE_LEN
                self._checksum += ord(rx_data)
            else:
                self._receive_state = Recstate.WAITING_FF

        elif self._receive_state == Recstate.RECEIVE_LEN:
            # print('进入RECEIVE_LEN')
            self._receive_state = Recstate.RECEIVE_PACKAGE
            self._checksum += ord(rx_data)
            self.length = ord(rx_data)

        elif self._receive_state == Recstate.RECEIVE_PACKAGE:
            # print('进入RECEIVE_PACKAGE')
            self._checksum += ord(rx_data)
            self.message = self.message + rx_data
            self._byte_count += 1
            if self._byte_count > self.length:#这里实际上多了1主要是command原本不计算1个长度
                self._receive_state = Recstate.RECEIVE_CHECK
                self._checksum  = self._checksum % 255

        elif self._receive_state == Recstate.RECEIVE_CHECK:
            if rx_data == self._checksum.to_bytes(1,'big'):
                # print('成功收到1帧数据')
                # print(rx_data)
                # print(self._checksum.to_bytes(1,'big'))
                # print(self.message)
                self._checksum = 0
                self._receive_state = Recstate.WAITING_FF
                return 1
            else:
                self._receive_state = Recstate.WAITING_FF

        else:
            self._receive_state = Recstate.WAITING_FF

        return 0



    def RFLink_packdata(self, cmd, databyte):
        """
        RFLink数据与指令打包函数
        :param cmd:Command
        :param data:待发送数据
        :return:符合RFLink通讯协议的消息包
        """
        first_byte = b'\xff'
        second_byte = self.MY_ID
        third_byte = self.FRIEND_ID

        cmdbyte = cmd.to_bytes(1,'big')
        if databyte != 0 and databyte is not None:
            datalenbyte = len(databyte).to_bytes(1,'big')
        else:
            databyte = b''
            datalenbyte = b'\x00'

        check_num = ord(first_byte) + ord(second_byte) + ord(third_byte)
        check_num = check_num + datalenbyte[0] + ord(cmdbyte)
        for data in databyte:
            check_num = check_num + data
        check_num = (check_num%255).to_bytes(1,'big')

        datapack = first_byte + second_byte + third_byte + datalenbyte + cmdbyte + databyte + check_num

        return datapack





if __name__ == "__main__":
    #print(RFLink_packdata(Command.SET_CPG_AMP.value,0.0))
    p=[0,1,2,3]
    data = 1
    rf = RFLink()
    rf.RFLink_receivedata(b'\xff')
    rf.RFLink_receivedata(b'\x33')
    rf.RFLink_receivedata(b'\x11')
    rf.RFLink_receivedata(b'\x00')
    rf.RFLink_receivedata(b'\x2D')
    rf.RFLink_receivedata(b'\x71')
    print(Command['READ_AHRS_ATTITUDE'].value)
    print(data.to_bytes)
    print(p[0:])
        