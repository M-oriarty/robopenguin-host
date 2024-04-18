# python3
# @Time    : 2021.05.18
# @Author  : 张鹏飞
# @FileName: robotstate.py
# @Software: 机器鲨鱼上位机
# version: 机器海豚上位机    author: Sijie Li    data: 2022.04.06

from enum import Enum
import struct

class SwimState(Enum):
    """
    游动状态枚举类型
    """
    SWIM_FORCESTOP = 0
    SWIM_STOP = 1
    SWIM_RUN = 2
    SWIM_INIT = 3


class RobotState:
    """
    机器人状态类
    """
    def __init__(self):
        #机器海豚工作状态指示
        self.swim_state = SwimState.SWIM_FORCESTOP.value
        #胸鳍数据
        self.lpect_flap_amp = 0.0
        self.lpect_flap_freq = 0.0
        self.lpect_flap_offset = 0.0
        self.rpect_flap_amp = 0.0
        self.rpect_flap_freq = 0.0
        self.rpect_flap_offset = 0.0

        self.lpect_feather_amp = 0.0
        self.lpect_feather_freq = 0.0
        self.lpect_feather_offset = 0.0
        self.rpect_feather_amp = 0.0
        self.rpect_feather_freq = 0.0
        self.rpect_feather_offset = 0.0

        self.lpect_pitch_amp = 0.0
        self.lpect_pitch_freq = 0.0
        self.lpect_pitch_offset = 0.0
        self.rpect_pitch_amp = 0.0
        self.rpect_pitch_freq = 0.0
        self.rpect_pitch_offset = 0.0

        self.tail_amp = 0.0
        self.tail_freq = 0.0
        self.tail_offset = 0.0
        #IMU测量数据
        self.imu_roll = 0.0
        self.imu_pitch = 0.0
        self.imu_yaw = 0.0
        self.imu_accelx = 0.0
        self.imu_accely = 0.0
        self.imu_accelz = 0.0
        self.imu_gyrox = 0.0
        self.imu_gyroy = 0.0
        self.imu_gyroz = 0.0
        #深度传感器测量
        self.underwater_depth = 0.0
        #限位状态数据
        self.mass_limit = 0    #限位
        self.pump_limit = 0    #限位

        self.mass_distance = 0
        self.pump_distance = 0

if __name__ == "__main__":
    databytes = b'\xfc\x00'
    print(databytes)
    n = len(databytes).to_bytes(2,'big')
    # n = len(databytes)
    # print(n)
    # print(n[1])
    print(round(2.2123,2))
