# python3
# @Time    : 2021.05.18
# @Author  : 张鹏飞
# @FileName: robosharkhost.py
# @Software: 机器鲨鱼上位机
# @修改历史:
# version: 机器海豚上位机    author: Sijie Li    data: 2022.04.06

from ctypes.wintypes import SIZE
from math import radians
import sys
import time
from xml.etree.ElementTree import PI

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette
from numpy import short
import serial
import struct
import copy
import platform

from PyQt5 import QtCore,QtGui,QtWidgets

from PyQt5.QtSerialPort import QSerialPortInfo

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from openpyxl import Workbook

###
### 自定义模块
import childwindows.analysis_btn_win # 解析数据窗口
import childwindows.storage_btn_win # 储存数据窗口
import childwindows.sendback_btn_win # 回传数据窗口
import childwindows.depth_control_btn_win # 深度控制窗口
import childwindows.yaw_control_btn_win #偏航控制窗口
import childwindows.AHRS_show_btn_win #航姿信息显示窗口
import childwindows.DVL_Infrared_Depth_show_btn_win #DVL、红外和深度信息显示窗口
import childwindows.pect_oscillating_control_btn_win #胸鳍拍动控制子窗口
import childwindows.identify_swimpara_control_btn_win #参数辨识游动参数控制子窗口

import rflink # Robotic Fish 通讯协议
import serctl # 串口控制工具
import robotstate # 机器人状态
import sensor_data_canvas

import ctypes
if(platform.system()=='Windows'):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

###
### 类对象
# 机器人状态
robosharkstate = robotstate.RobotState()
# 串口类
send_sertool = serctl.RobotSerial()
recv_sertool = serctl.RobotSerial()
# rf通讯协议类
rftool = rflink.RFLink()

###
### 多线程变量
# 机器人状态线程锁
rm_mutex = QtCore.QMutex()
# 串口线程锁
ser_mutex = QtCore.QMutex()
# 通讯线程锁
rf_mutex = QtCore.QMutex()
rf_cond = QtCore.QWaitCondition()
# 绘图线程锁
plt_mutex = QtCore.QMutex()

def append_variable_to_txt(variable, filename):
    with open(filename, 'a') as file:
        file.write(str(variable) + '\n')


#########################################################################################################
def analysis_data(databytes,datalen): # 分析串口接收到的rflink数据,更新robosharkstate的状态
    """
    本函数将串口接收到的rflink数据进行分析,解码出收到的Command,更新robosharkstate的状态
    :param databytes: byte类型数据串
    :param datalen: 数据串长度
    :return: 收到Command的ID
    """
    global robosharkstate

    # print('进入数据包分析函数')
    try:
        command_id = databytes[0]
    except IndexError:
        return rflink.Command.LAST_COMMAND_FLAG.value

    command = rflink.Command(command_id)
    print('数据包分析函数解析后的指令为：',command)
    if command is rflink.Command.READ_ROBOT_STATUS:
        robosharkstate.swim_state = robotstate.SwimState((databytes[1]>>6)&3) # 取一个字节的第7位和第6位（从高往低）
        robosharkstate.mass_limit = ((databytes[1]>>5) & 1) #取一个字节的第4位（从高往低），纵向滑块限位状态
        robosharkstate.pump_limit = ((databytes[1]>>4) & 1) #取一个字节的第3位（从高往低），水泵限位状态
        print(databytes)
        print(robosharkstate.mass_limit)
        print(robosharkstate.pump_limit)


    elif command is rflink.Command.READ_FLAP:
        datatuple = struct.unpack('ffffff', databytes[1:])
        robosharkstate.lpect_flap_amp = datatuple[0]
        robosharkstate.lpect_flap_freq = datatuple[1]
        robosharkstate.lpect_flap_offset = datatuple[2] * 3.1415926535
        robosharkstate.rpect_flap_amp = datatuple[3]
        robosharkstate.rpect_flap_freq = datatuple[4]
        robosharkstate.rpect_flap_offset = datatuple[5] * 3.1415926535

    elif command is rflink.Command.READ_FEATHER:
        datatuple = struct.unpack('ffffff', databytes[1:])
        robosharkstate.lpect_feather_amp = datatuple[0]
        robosharkstate.lpect_feather_freq = datatuple[1]
        robosharkstate.lpect_feather_offset = datatuple[2] * 3.1415926535
        robosharkstate.rpect_feather_amp = datatuple[3]
        robosharkstate.rpect_feather_freq = datatuple[4]
        robosharkstate.rpect_feather_offset = datatuple[5] * 3.1415926535

    elif command is rflink.Command.READ_PITCH:
        datatuple = struct.unpack('ffffff', databytes[1:])
        robosharkstate.lpect_pitch_amp = datatuple[0]
        robosharkstate.lpect_pitch_freq = datatuple[1]
        robosharkstate.lpect_pitch_offset = datatuple[2] * 3.1415926535
        robosharkstate.rpect_pitch_amp = datatuple[3]
        robosharkstate.rpect_pitch_freq = datatuple[4]
        robosharkstate.rpect_pitch_offset = datatuple[5] * 3.1415926535

    elif command is rflink.Command.READ_TAIL:
        datatuple = struct.unpack('fff', databytes[1:])
        robosharkstate.tail_amp = datatuple[0]
        robosharkstate.tail_freq = datatuple[1]
        robosharkstate.tail_offset = datatuple[2] * 3.1415926535

    return command_id

#########################################################################################################
class PollingStateThread(QtCore.QThread): # 轮询线程
    """
    本类创建一个轮询线程,每隔一段时间,通过串口发送获取机器人状态的指令
    """
    def __init__(self,parent=None):
        super(PollingStateThread, self).__init__(parent)
        self.is_running = False
        self.is_pause = False
        self._sync = QtCore.QMutex()
        self._pause_cond = QtCore.QWaitCondition()
        self._count = 0

    def run(self):
        """
        本线程运行的主要循环
        """
        self.is_running = True
        while self.is_running == True:

            self._sync.lock()
            if self.is_pause:
                self._pause_cond.wait(self._sync)
            self._sync.unlock()

            # # 这段代码就是在轮询,获取下位机信息,注释掉就没有了
            # datapack = rftool.RFLink_packdata(rflink.Command.CMD_READ_SINE_MOTION_PARAM.value, 0)

            # # 通过串口发送数据
            # ser_mutex.lock()
            # send_sertool.write_cmd(datapack)
            # ser_mutex.unlock()

            # # 间隔1s,轮询一次
            # self.sleep(1)

    def pause(self):
        """
        暂停线程
        """
        self._sync.lock()
        self.is_pause = True
        self._sync.unlock()

    def resume(self):
        """
        恢复线程
        """
        self._sync.lock()
        self.is_pause = False
        self._sync.unlock()
        self._pause_cond.wakeAll()

    def stop(self):
        """
        终止线程,一旦调用,本线程将无法再打开
        """
        self.is_running = False
        self.terminate()

#########################################################################################################
class ReceiveDataThread(QtCore.QThread): # 数据接收线程
    """
    本类创建一个数据接收线程
    通过串口等待数据,每接收到一个数据,就使用RFLink的接收状态机RFLink_receivedata进行分析
    每次接收到一帧完整的消息后,唤醒AnalysisDataThread线程
    """
    def __init__(self,parent=None):
        super(ReceiveDataThread, self).__init__(parent)
        self.is_running = False
        self.is_pause = False
        self._sync = QtCore.QMutex()
        self._pause_cond = QtCore.QWaitCondition()

    def run(self):
        """
        本线程运行的主要循环
        """
        print('数据接收线程成功启动!')
        self.is_running = True
        global rftool
        while self.is_running == True:

            self._sync.lock()
            if self.is_pause:
                self._pause_cond.wait(self._sync)
            self._sync.unlock()

            # 接收数据
            rx_data = recv_sertool.read_data()
            # print('单次接收到的数据：',rx_data)
            # 数据送入状态机
            rf_mutex.lock()
            if rftool.RFLink_receivedata(rx_data): # 如果返回True,那么通知数据分析线程
                # print('唤醒分析线程')
                rf_cond.wakeAll() # 通知等待rf_cond的线程
            rf_mutex.unlock()

    def pause(self):
        """
        暂停线程
        """
        self._sync.lock()
        self.is_pause = True
        self._sync.unlock()

    def resume(self):
        """
        恢复线程
        """
        self._sync.lock()
        self.is_pause = False
        self._sync.unlock()
        self._pause_cond.wakeAll()

    def stop(self):
        """
        终止线程,一旦调用,本线程将无法再打开
        """
        self.is_running = False
        self.terminate()

#########################################################################################################
class AnalysisDataThread(QtCore.QThread): # 数据分析线程
    """
    本类创建一个数据分析线程
    每当ReceiveDataThread接收到一帧完整消息后,本线程被唤醒
    本线程分析消息中的Command以及机器人的数据
    """
    # 信号量,用于传递Command的ID
    command_id_out = QtCore.pyqtSignal(int)

    def __init__(self,parent=None):
        super(AnalysisDataThread, self).__init__(parent)
        self.command_id = 0
        self.is_running = False
        self.is_pause = False
        self._sync = QtCore.QMutex()
        self._pause_cond = QtCore.QWaitCondition()

    def run(self):
        """
        本线程运行的主要循环
        """
        print('数据分析线程成功启动!')
        self.is_running = True
        global rftool
        while self.is_running == True:

            self._sync.lock()
            if self.is_pause:
                self._pause_cond.wait(self._sync)
            self._sync.unlock()

            # 获取消息
            rf_mutex.lock()
            rf_cond.wait(rf_mutex) # 等待数据接收线程唤醒,一旦唤醒,说明rftool已经接收到了一帧完整的消息
            # 拿到数据
            databytes = rftool.message
            datalen = rftool.length
            rf_mutex.unlock()

            # 分析消息,更新机器人状态
            rm_mutex.lock()
            # print('分析消息开始，调用数据包分析函数')
            self.command_id = analysis_data(databytes,datalen)
            rm_mutex.unlock()

            # 通知Main Window
            self.command_id_out.emit(self.command_id)

    def pause(self):
        """
        暂停线程
        """
        self._sync.lock()
        self.is_pause = True
        self._sync.unlock()

    def resume(self):
        """
        恢复线程
        """
        self._sync.lock()
        self.is_pause = False
        self._sync.unlock()
        self._pause_cond.wakeAll()

    def stop(self):
        """
        终止线程,一旦调用,本线程将无法再打开
        """
        self.is_running = False
        self.terminate()

#########################################################################################################
class RoboPenguinWindow(QtWidgets.QMainWindow): # 主窗口
    """
    robosharkstate Qt 主窗口
    函数大致分为四块:
    第一部分:关于UI定义
    第二部分:关于Slot和Signal的(slot是槽的意思)
    第三部分:下位机数据处理
    """
    close_signal = QtCore.pyqtSignal() # 同步关闭主窗口和子窗口
    
    # 初始化
    def __init__(self):
        """
        初始化
        创建三大线程
        初始化UI
        初始化信号和槽的连接
        """
        super(RoboPenguinWindow, self).__init__()
        # 创建线程
        self.receive_data_thread = ReceiveDataThread()
        self.polling_state_thread = PollingStateThread()
        self.analysis_data_thread = AnalysisDataThread()
        
        # 初始化UI
        self.button_height = 35  #所有按钮的高度，也可以后期自己定义
        self.init_ui()

        # 初始化控件间信号和槽的连接
        self.widgets_connect() #按下按钮之后对应什么反应，会有一个对应的函数处理
        self.analysis_data_thread.command_id_out.connect(self.newdata_comming_slot) # 处理下位机数据

        # 绘图部分变量初始化
        self.showtime = 0
        self.timelist = []  # x轴数据,时间
        self.datalist = []  # y轴数据,传感器数据
        self.yaxis_lowbound = -1
        self.yaxis_upbound = 1
        self.datashow_running_flag = False
        self.update_bound_cnt = 0

        self.datashow_sensor_id = 1
        self.datashow_sensor_datatype = 1
        self.datashow_sensor_dataaxis = 1
        self.datashow_sensor_module = 1

        ## 深度控制子窗口
        self.DCBW = childwindows.depth_control_btn_win.DepthControlBtnWin()  # 初始化子窗口类
        self.depth_control_button.clicked.connect(self.DCBW.handle_click)  # 将按钮与子窗口的开启函数关联起来
        self.DCBW.depthctl_start_button.clicked.connect(self.console_button_clicked)  # 将子窗口中的按钮与console_button_clicked函数关联起来
        self.DCBW.depthctl_stop_button.clicked.connect(self.console_button_clicked)  # 将子窗口中的按钮与console_button_clicked函数关联起来
        self.DCBW.depthctl_writeparam_button.clicked.connect(self.console_button_clicked)  # 将子窗口中的按钮与console_button_clicked函数关联起来
        self.DCBW.anglectl_writeparam_button.clicked.connect(self.console_button_clicked)  # 将子窗口中的按钮与console_button_clicked函数关联起来
        self.close_signal.connect(self.DCBW.handle_close)  # 将主窗口关闭信号与子窗口关闭函数关联起来，这样只要主窗口关闭，子窗口也会关闭


    #####################################################################################################
    #####################################################################################################
    ## 第一部分:关于UI定义
    #####################################################################################################
    #####################################################################################################
    # 初始化UI界面
    def init_ui(self):
        """
        初始化UI
        :return:
        """
        self.init_layout()
        self.statusBar().showMessage('串口未打开') #状态栏
        self.setFixedSize(1920,1080)# 设置窗体大小
        self.setWindowTitle('Robotic Penguin Host')  # 设置窗口标题
        self.setWindowOpacity(0.95) #透明度
        self.setWindowIcon(QtGui.QIcon('icon/my/dolphin_black.ico')) #图标
        self.show()  # 窗口显示


    # 初始化layout界面
    def init_layout(self):
        """
        初始化UI界面布局
        UI界面主要分为三个部分:
        self.stateshow_frame:状态显示区
        self.datashow_frame:传感器数据显示区
        self.console_frame:控制台
        self.cmdshell_frame:指令shell区
        :return:
        """

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setObjectName('main_widget')
        self.main_layout = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        # shell区
        self.cmdshell_frame = QtWidgets.QFrame()
        self.cmdshell_layout = QtWidgets.QGridLayout()
        self.cmdshell_frame.setLayout(self.cmdshell_layout)
        self.cmdshell_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.cmdshell_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.cmdshell_frame.setLineWidth(1)

        # 状态显示区
        self.stateshow_frame = QtWidgets.QFrame()
        self.stateshow_frame.setObjectName('stateshow_frame')
        self.stateshow_layout = QtWidgets.QGridLayout()
        self.stateshow_frame.setLayout(self.stateshow_layout)
        self.stateshow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.stateshow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.stateshow_frame.setLineWidth(1)

        # 传感器数据显示区
        self.datashow_frame = QtWidgets.QFrame()
        self.datashow_layout = QtWidgets.QGridLayout()
        self.datashow_frame.setLayout(self.datashow_layout)
        self.datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.datashow_frame.setLineWidth(1)

        # 控制台
        self.console_frame = QtWidgets.QFrame()
        self.console_layout = QtWidgets.QGridLayout()
        self.console_frame.setLayout(self.console_layout)
        self.console_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.console_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.console_frame.setLineWidth(1)

        #布局，16:9
        self.main_layout.addWidget(self.stateshow_frame, 0, 0, 5, 4)
        self.main_layout.addWidget(self.console_frame, 5, 0, 4, 4)
        self.main_layout.addWidget(self.datashow_frame, 0, 4, 9, 8)
        self.main_layout.addWidget(self.cmdshell_frame, 0, 12, 9, 4)

        self.setCentralWidget(self.main_widget)  # 设置窗口主部件

        self.init_stateshow_panel()
        self.init_datashow_panel()
        self.init_console_panel()
        self.init_cmdshell_panel()

    # 初始化状态显示区面板
    def init_stateshow_panel(self):
        """
        初始化状态显示区面板
        :return:
        """
        self.stateshow_title_label = QtWidgets.QLabel('状态显示区')
        self.stateshow_title_label.setObjectName('stateshow_title_label')
        self.stateshow_layout.addWidget(self.stateshow_title_label, 0, 0, 1, 4, QtCore.Qt.AlignCenter)

        # 图像显示部分
        self.stateshow_subframe = QtWidgets.QFrame()
        self.stateshow_subframe.setObjectName('stateshow_subframe')
        self.stateshowsubframe_layout = QtWidgets.QGridLayout()
        self.stateshow_subframe.setLayout(self.stateshowsubframe_layout)
        self.stateshow_layout.addWidget(self.stateshow_subframe, 1, 0, 10, 4)

        self.swimstate_fixed_label = QtWidgets.QLabel('游动状态')
        self.swimstate_fixed_label.setObjectName('swimstate_fixed_label')
        self.stateshowsubframe_layout.addWidget(self.swimstate_fixed_label, 1, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.swimstate_label = QtWidgets.QLabel('停止')
        self.swimstate_label.setObjectName('swimstate_label')
        self.stateshowsubframe_layout.addWidget(self.swimstate_label, 1, 1, 1, 3, QtCore.Qt.AlignCenter)

        # self.communicatestate_fixed_label = QtWidgets.QLabel('通讯状态')
        # self.communicatestate_fixed_label.setObjectName('communicatestate_fixed_label')
        # self.stateshowsubframe_layout.addWidget(self.communicatestate_fixed_label, 2, 0, 1, 1, QtCore.Qt.AlignCenter)
        #
        # self.communicatestate_label = QtWidgets.QLabel('中断')
        # self.communicatestate_label.setObjectName('communicatestate_label')
        # self.stateshowsubframe_layout.addWidget(self.communicatestate_label, 2, 1, 1, 3, QtCore.Qt.AlignCenter)

        #尾部数据
        self.tail_data_label = QtWidgets.QLabel('tail')
        self.tail_data_label.setObjectName('tail_data_label')
        self.stateshowsubframe_layout.addWidget(self.tail_data_label, 3, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.tail_amp_label = QtWidgets.QLabel('0.0')
        self.tail_amp_label.setObjectName('tail_amp_label')
        self.stateshowsubframe_layout.addWidget(self.tail_amp_label, 3, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.tail_freq_label = QtWidgets.QLabel('0.0')
        self.tail_freq_label.setObjectName('tail_freq_label')
        self.stateshowsubframe_layout.addWidget(self.tail_freq_label, 3, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.tail_offset_label = QtWidgets.QLabel('0.0')
        self.tail_offset_label.setObjectName('tail_offset_label')
        self.stateshowsubframe_layout.addWidget(self.tail_offset_label, 3, 3, 1, 1, QtCore.Qt.AlignCenter)

        #左胸鳍flap数据
        self.lpect_flap_data_label = QtWidgets.QLabel('lp-flap')
        self.lpect_flap_data_label.setObjectName('lpect_flap_data_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_flap_data_label, 4, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_flap_amp_label = QtWidgets.QLabel('0.0')
        self.lpect_flap_amp_label.setObjectName('lpect_flap_amp_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_flap_amp_label, 4, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_flap_freq_label = QtWidgets.QLabel('0.0')
        self.lpect_flap_freq_label.setObjectName('lpect_flap_freq_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_flap_freq_label, 4, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_flap_offset_label = QtWidgets.QLabel('0.0')
        self.lpect_flap_offset_label.setObjectName('lpect_flap_offset_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_flap_offset_label, 4, 3, 1, 1, QtCore.Qt.AlignCenter)

        # 左胸鳍feather数据
        self.lpect_feather_data_label = QtWidgets.QLabel('lp-feather')
        self.lpect_feather_data_label.setObjectName('lpect_feather_data_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_feather_data_label, 5, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_feather_amp_label = QtWidgets.QLabel('0.0')
        self.lpect_feather_amp_label.setObjectName('lpect_feather_amp_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_feather_amp_label, 5, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_feather_freq_label = QtWidgets.QLabel('0.0')
        self.lpect_feather_freq_label.setObjectName('lpect_feather_freq_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_feather_freq_label, 5, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_feather_offset_label = QtWidgets.QLabel('0.0')
        self.lpect_feather_offset_label.setObjectName('lpect_feather_offset_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_feather_offset_label, 5, 3, 1, 1, QtCore.Qt.AlignCenter)

        # 左胸鳍pitch数据
        self.lpect_pitch_data_label = QtWidgets.QLabel('lp-pitch')
        self.lpect_pitch_data_label.setObjectName('lpect_pitch_data_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_pitch_data_label, 6, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_pitch_amp_label = QtWidgets.QLabel('0.0')
        self.lpect_pitch_amp_label.setObjectName('lpect_pitch_amp_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_pitch_amp_label, 6, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_pitch_freq_label = QtWidgets.QLabel('0.0')
        self.lpect_pitch_freq_label.setObjectName('lpect_pitch_freq_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_pitch_freq_label, 6, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_pitch_offset_label = QtWidgets.QLabel('0.0')
        self.lpect_pitch_offset_label.setObjectName('lpect_pitch_offset_label')
        self.stateshowsubframe_layout.addWidget(self.lpect_pitch_offset_label, 6, 3, 1, 1, QtCore.Qt.AlignCenter)

        # 右胸鳍flap数据
        self.rpect_flap_data_label = QtWidgets.QLabel('rp-flap')
        self.rpect_flap_data_label.setObjectName('rpect_flap_data_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_flap_data_label, 7, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_flap_amp_label = QtWidgets.QLabel('0.0')
        self.rpect_flap_amp_label.setObjectName('rpect_flap_amp_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_flap_amp_label, 7, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_flap_freq_label = QtWidgets.QLabel('0.0')
        self.rpect_flap_freq_label.setObjectName('rpect_flap_freq_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_flap_freq_label, 7, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_flap_offset_label = QtWidgets.QLabel('0.0')
        self.rpect_flap_offset_label.setObjectName('rpect_flap_offset_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_flap_offset_label, 7, 3, 1, 1, QtCore.Qt.AlignCenter)

        # 右胸鳍feather数据
        self.rpect_feather_data_label = QtWidgets.QLabel('rp-feather')
        self.rpect_feather_data_label.setObjectName('rpect_feather_data_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_feather_data_label, 8, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_feather_amp_label = QtWidgets.QLabel('0.0')
        self.rpect_feather_amp_label.setObjectName('rpect_feather_amp_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_feather_amp_label, 8, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_feather_freq_label = QtWidgets.QLabel('0.0')
        self.rpect_feather_freq_label.setObjectName('rpect_feather_freq_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_feather_freq_label, 8, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_feather_offset_label = QtWidgets.QLabel('0.0')
        self.rpect_feather_offset_label.setObjectName('rpect_feather_offset_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_feather_offset_label, 8, 3, 1, 1, QtCore.Qt.AlignCenter)

        # 左胸鳍pitch数据
        self.rpect_pitch_data_label = QtWidgets.QLabel('rp-pitch')
        self.rpect_pitch_data_label.setObjectName('rpect_pitch_data_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_pitch_data_label, 9, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_pitch_amp_label = QtWidgets.QLabel('0.0')
        self.rpect_pitch_amp_label.setObjectName('rpect_pitch_amp_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_pitch_amp_label, 9, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_pitch_freq_label = QtWidgets.QLabel('0.0')
        self.rpect_pitch_freq_label.setObjectName('rpect_pitch_freq_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_pitch_freq_label, 9, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_pitch_offset_label = QtWidgets.QLabel('0.0')
        self.rpect_pitch_offset_label.setObjectName('rpect_pitch_offset_label')
        self.stateshowsubframe_layout.addWidget(self.rpect_pitch_offset_label, 9, 3, 1, 1, QtCore.Qt.AlignCenter)

        self.read_robot_state_button = QtWidgets.QPushButton('读取状态')
        self.stateshowsubframe_layout.addWidget(self.read_robot_state_button, 10, 0, 1, 2, QtCore.Qt.AlignCenter)
        self.read_robot_state_button.setObjectName("READ_ROBOT_STATUS")
        self.read_robot_state_button.setFixedSize(140, self.button_height)

        self.read_robot_data_button = QtWidgets.QPushButton('读取参数')
        self.stateshowsubframe_layout.addWidget(self.read_robot_data_button, 10, 2, 1, 2, QtCore.Qt.AlignCenter)
        self.read_robot_data_button.setObjectName("READ_ROBOT_DATA")
        self.read_robot_data_button.setFixedSize(140, self.button_height)

    # 初始化传感器数据显示区面板
    def init_datashow_panel(self):
        """
        初始化传感器数据显示区面板
        :return:...........................
        """
        self.datashow_title_label = QtWidgets.QLabel('传感器数据显示区')
        self.datashow_title_label.setObjectName('datashow_title_label')
        self.datashow_layout.addWidget(self.datashow_title_label, 0, 0, 1, 16, QtCore.Qt.AlignCenter)

        # 图像显示部分
        self.canvas_frame = QtWidgets.QFrame()
        self.canvas_frame.setObjectName('canvas_frame')
        self.canvas_layout = QtWidgets.QVBoxLayout()
        self.canvas_frame.setLayout(self.canvas_layout)
        self.datashow_layout.addWidget(self.canvas_frame, 1, 0, 11, 16)

        self.sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.sensor_data_canvas, self.canvas_frame)
        self.canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.canvas_layout.addWidget(self.sensor_data_canvas)

        self.datasc_frame = QtWidgets.QFrame()
        self.datasc_frame.setObjectName('datasc_frame')
        self.datasc_layout = QtWidgets.QGridLayout()
        self.datasc_frame.setLayout(self.datasc_layout)
        self.datashow_layout.addWidget(self.datasc_frame,12, 7, 6, 9)

        self.datasw_frame = QtWidgets.QFrame()
        self.datasw_frame.setObjectName('datasw_frame')
        self.datasw_layout = QtWidgets.QGridLayout()
        self.datasw_frame.setLayout(self.datasw_layout)
        self.datashow_layout.addWidget(self.datasw_frame, 12, 0, 6, 7)

        #参数设置
        self.datasw_label = QtWidgets.QLabel("参数设置")
        self.datasw_label.setObjectName('datasw_label')
        self.datasw_layout.addWidget(self.datasw_label, 11, 0, 1, 8, QtCore.Qt.AlignCenter)

        self.motor_chose_fixed_label = QtWidgets.QLabel('舵机选择')
        self.motor_chose_fixed_label.setObjectName('motor_chose_fixed_label')
        self.datasw_layout.addWidget(self.motor_chose_fixed_label, 12, 0, 1, 2, QtCore.Qt.AlignLeft)

        self.motor_chose_combo = QtWidgets.QComboBox()
        self.motor_chose_combo.addItem('lpect_flap')
        self.motor_chose_combo.addItem('lpect_feather')
        self.motor_chose_combo.addItem('lpect_pitch')
        self.motor_chose_combo.addItem('rpect_flap')
        self.motor_chose_combo.addItem('rpect_feather')
        self.motor_chose_combo.addItem('rpect_pitch')
        self.motor_chose_combo.addItem('tail')
        self.motor_chose_combo.setFixedSize(180, self.button_height)
        self.datasw_layout.addWidget(self.motor_chose_combo, 12, 2, 1, 2, QtCore.Qt.AlignCenter)

        self.cpgcc_amp_label = QtWidgets.QLabel('幅度')
        self.cpgcc_amp_label.setObjectName('cpgcc_amp_label')
        self.cpgcc_amp_label.setFixedSize(50, self.button_height)
        self.datasw_layout.addWidget(self.cpgcc_amp_label, 13, 0, 1, 2, QtCore.Qt.AlignCenter)

        self.cpgcc_amp_edit = QtWidgets.QLineEdit()
        self.cpgcc_amp_edit.setFixedSize(100, self.button_height)
        self.cpgcc_amp_edit.setPlaceholderText('0~22')
        double_validator1 = QtGui.QDoubleValidator()
        double_validator1.setRange(0, 100)
        double_validator1.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator1.setDecimals(3)
        self.cpgcc_amp_edit.setValidator(double_validator1)
        self.datasw_layout.addWidget(self.cpgcc_amp_edit, 13, 2, 1, 2, QtCore.Qt.AlignCenter)

        self.cpgcc_freq_label = QtWidgets.QLabel('频率')
        self.cpgcc_freq_label.setObjectName('cpgcc_freq_label')
        self.cpgcc_freq_label.setFixedSize(50, self.button_height)
        self.datasw_layout.addWidget(self.cpgcc_freq_label, 14, 0, 1, 2, QtCore.Qt.AlignCenter)

        self.cpgcc_freq_edit = QtWidgets.QLineEdit()
        self.cpgcc_freq_edit.setFixedSize(100, self.button_height)
        self.cpgcc_freq_edit.setPlaceholderText('0~3.0')
        double_validator2 = QtGui.QDoubleValidator()
        double_validator2.setRange(0, 100)
        double_validator2.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator2.setDecimals(2)
        self.cpgcc_freq_edit.setValidator(double_validator2)
        self.datasw_layout.addWidget(self.cpgcc_freq_edit, 14, 2, 1, 2, QtCore.Qt.AlignCenter)

        self.cpgcc_offset_label = QtWidgets.QLabel('偏移')
        self.cpgcc_offset_label.setObjectName('cpgcc_offset_label')
        self.cpgcc_offset_label.setFixedSize(50, self.button_height)
        self.datasw_layout.addWidget(self.cpgcc_offset_label, 15, 0, 1, 2, QtCore.Qt. AlignCenter)

        self.cpgcc_offset_edit = QtWidgets.QLineEdit()
        self.cpgcc_offset_edit.setFixedSize(100, self.button_height)
        self.cpgcc_offset_edit.setPlaceholderText('-20~20')
        double_validator3 = QtGui.QDoubleValidator()
        double_validator3.setRange(0, 100)
        double_validator3.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator3.setDecimals(2)
        self.cpgcc_offset_edit.setValidator(double_validator3)
        self.datasw_layout.addWidget(self.cpgcc_offset_edit, 15, 2, 1, 2, QtCore.Qt.AlignCenter)

        self.cpgcc_set_button = QtWidgets.QPushButton('写入')
        self.datasw_layout.addWidget(self.cpgcc_set_button, 16, 0, 1, 4, QtCore.Qt.AlignCenter)
        self.cpgcc_set_button.setObjectName("SET_CPG_DATA")
        self.cpgcc_set_button.setFixedSize(100, self.button_height)

        # 数据显示控制台
        self.datasc_label = QtWidgets.QLabel("数据控制台")
        self.datasc_label.setObjectName('datasc_label')
        self.datasc_layout.addWidget(self.datasc_label, 11, 8, 1, 8, QtCore.Qt.AlignCenter)

        self.imu_checkbox = QtWidgets.QCheckBox("IMU")
        self.imu_checkbox.setObjectName('imu_checkbox')
        self.imu_checkbox.setChecked(True)
        self.datasc_layout.addWidget(self.imu_checkbox, 12, 8, 1, 2, QtCore.Qt.AlignLeft)

        self.angle_checkbox = QtWidgets.QCheckBox("角度")
        self.angle_checkbox.setObjectName('angle_checkbox')
        self.angle_checkbox.setChecked(True)
        self.datasc_layout.addWidget(self.angle_checkbox, 12, 10, 1, 2, QtCore.Qt.AlignLeft)

        self.accel_checkbox = QtWidgets.QCheckBox("加速度")
        self.accel_checkbox.setObjectName('accel_checkbox')
        self.datasc_layout.addWidget(self.accel_checkbox, 12, 12, 1, 2, QtCore.Qt.AlignLeft)

        self.gyro_checkbox = QtWidgets.QCheckBox("角速度")
        self.gyro_checkbox.setObjectName('gyro_checkbox')
        self.datasc_layout.addWidget(self.gyro_checkbox, 12, 14, 1, 2, QtCore.Qt.AlignLeft)

        self.x_checkbox = QtWidgets.QCheckBox("X轴")
        self.x_checkbox.setObjectName('x_checkbox')
        self.x_checkbox.setChecked(True)
        self.datasc_layout.addWidget(self.x_checkbox, 13, 10, 1, 2, QtCore.Qt.AlignLeft)

        self.y_checkbox = QtWidgets.QCheckBox("Y轴")
        self.y_checkbox.setObjectName('y_checkbox')
        self.datasc_layout.addWidget(self.y_checkbox, 13, 12, 1, 2, QtCore.Qt.AlignLeft)

        self.z_checkbox = QtWidgets.QCheckBox("Z轴")
        self.z_checkbox.setObjectName('z_checkbox')
        self.datasc_layout.addWidget(self.z_checkbox, 13, 14, 1, 2, QtCore.Qt.AlignLeft)

        self.depthsensor_checkbox = QtWidgets.QCheckBox("深度传感器")
        self.depthsensor_checkbox.setObjectName('depthsensor_checkbox')
        self.datasc_layout.addWidget(self.depthsensor_checkbox, 14, 8, 1, 2, QtCore.Qt.AlignLeft)

        self.depth_checkbox = QtWidgets.QCheckBox("深度")
        self.depth_checkbox.setObjectName('depth_checkbox')
        self.datasc_layout.addWidget(self.depth_checkbox, 14, 10, 1, 2, QtCore.Qt.AlignLeft)

        self.depthsensor_checkbox.setChecked(False)
        self.depth_checkbox.setEnabled(False)

        self.powersensor_checkbox = QtWidgets.QCheckBox("功率传感器")
        self.powersensor_checkbox.setObjectName('powersensor_checkbox')
        self.datasc_layout.addWidget(self.powersensor_checkbox, 15, 8, 1, 2, QtCore.Qt.AlignLeft)

        self.current_checkbox = QtWidgets.QCheckBox("电流")
        self.current_checkbox.setObjectName('current_checkbox')
        self.datasc_layout.addWidget(self.current_checkbox, 15, 10, 1, 2, QtCore.Qt.AlignLeft)

        self.voltage_checkbox = QtWidgets.QCheckBox("电压")
        self.voltage_checkbox.setObjectName('voltage_checkbox')
        self.datasc_layout.addWidget(self.voltage_checkbox, 15, 12, 1, 2, QtCore.Qt.AlignLeft)

        self.power_checkbox = QtWidgets.QCheckBox("功率")
        self.power_checkbox.setObjectName('power_checkbox')
        self.datasc_layout.addWidget(self.power_checkbox, 15, 14, 1, 2, QtCore.Qt.AlignLeft)

        self.pect_checkbox = QtWidgets.QCheckBox("PECT")
        self.pect_checkbox.setObjectName('x_checkbox')
        self.pect_checkbox.setChecked(True)
        self.datasc_layout.addWidget(self.pect_checkbox, 16, 10, 1, 2, QtCore.Qt.AlignLeft)


        self.glide_checkbox = QtWidgets.QCheckBox("GLIDE")
        self.glide_checkbox.setObjectName('z_checkbox')
        self.datasc_layout.addWidget(self.glide_checkbox, 16, 12, 1, 2, QtCore.Qt.AlignLeft)

        self.powersensor_checkbox.setChecked(False)
        self.current_checkbox.setEnabled(False)
        self.voltage_checkbox.setEnabled(False)
        self.power_checkbox.setEnabled(False)
        self.pect_checkbox.setEnabled(False)
        self.glide_checkbox.setEnabled(False)

        self.datashow_start_button = QtWidgets.QPushButton('开始显示')
        self.datashow_start_button.setFixedSize(80, self.button_height)
        self.datasc_layout.addWidget(self.datashow_start_button, 17, 8, 1, 2, QtCore.Qt.AlignCenter)

        self.datashow_stop_button = QtWidgets.QPushButton('停止显示')
        self.datashow_stop_button.setFixedSize(80, self.button_height)
        self.datasc_layout.addWidget(self.datashow_stop_button, 17, 11, 1, 2, QtCore.Qt.AlignCenter)
        self.datashow_stop_button.setObjectName("SET_DATASHOW_OVER")

        self.datashow_clear_button = QtWidgets.QPushButton('清空界面')
        self.datashow_clear_button.setFixedSize(80, self.button_height)
        self.datasc_layout.addWidget(self.datashow_clear_button, 17, 14, 1, 2, QtCore.Qt.AlignCenter)

        self.datashow_storage_button = QtWidgets.QPushButton('记录数据')
        self.datashow_storage_button.setFixedSize(80, self.button_height)
        self.datasc_layout.addWidget(self.datashow_storage_button, 18, 8, 1, 2, QtCore.Qt.AlignCenter)
        self.datashow_storage_button.setObjectName("GOTO_STORAGE_DATA")

        self.datashow_stopstorage_button = QtWidgets.QPushButton('停止记录')
        self.datashow_stopstorage_button.setFixedSize(80, self.button_height)
        self.datasc_layout.addWidget(self.datashow_stopstorage_button, 18, 11, 1, 2, QtCore.Qt.AlignCenter)
        self.datashow_stopstorage_button.setObjectName("GOTO_STOP_STORAGE")

        self.datashow_save_button = QtWidgets.QPushButton('回传数据')
        self.datashow_save_button.setFixedSize(80, self.button_height)
        self.datasc_layout.addWidget(self.datashow_save_button, 18, 14, 1, 2, QtCore.Qt.AlignCenter)
        self.datashow_save_button.setObjectName("GOTO_SEND_DATA")
        self.datashow_save_button.setEnabled(True)

    # 初始化控制台面板
    def init_console_panel(self):
        """
                初始化控制台面板
                控制台面板分为五大板块
                self.swimcc_frame:游动控制
                self.cpgcc_frame:CPG参数控制
                self.advancedcc_frame:高级控制
                :return:
                """
        self.console_title_label = QtWidgets.QLabel('机器企鹅控制台')
        self.console_title_label.setObjectName('console_title_label')
        self.console_layout.addWidget(self.console_title_label, 0, 0, 1, 8, QtCore.Qt.AlignCenter)

        # 游动控制
        self.swimcc_frame = QtWidgets.QFrame()
        self.swimcc_frame.setObjectName('swimcc_frame')
        self.swimcc_layout = QtWidgets.QGridLayout()
        self.swimcc_frame.setLayout(self.swimcc_layout)
        self.console_layout.addWidget(self.swimcc_frame, 1, 0, 7, 8)

        self.swimcc_fixed_label = QtWidgets.QLabel('基础运动控制')
        self.swimcc_fixed_label.setObjectName('swimcc_fixed_label')
        self.swimcc_layout.addWidget(self.swimcc_fixed_label, 1, 0, 1, 8, QtCore.Qt.AlignCenter)

        self.swimcc_start_button = QtWidgets.QPushButton('初始化(q)')
        self.swimcc_layout.addWidget(self.swimcc_start_button, 2, 0, 1, 2, QtCore.Qt.AlignCenter)
        self.swimcc_start_button.setObjectName("SET_SWIM_RUN")
        self.swimcc_start_button.setShortcut('q')
        self.swimcc_start_button.setFixedSize(110, self.button_height)

        self.swimcc_stop2start_button = QtWidgets.QPushButton('开始(w)')
        self.swimcc_layout.addWidget(self.swimcc_stop2start_button, 2, 2, 1, 2, QtCore.Qt.AlignCenter)
        self.swimcc_stop2start_button.setObjectName("SET_SWIM_START")
        self.swimcc_stop2start_button.setShortcut('w')
        self.swimcc_stop2start_button.setFixedSize(110, self.button_height)

        self.swimcc_stop_button = QtWidgets.QPushButton('暂停(e)')
        self.swimcc_layout.addWidget(self.swimcc_stop_button, 2, 4, 1, 2, QtCore.Qt.AlignCenter)
        self.swimcc_stop_button.setObjectName("SET_SWIM_STOP")
        self.swimcc_stop_button.setShortcut('e')
        self.swimcc_stop_button.setFixedSize(110, self.button_height)

        self.swimcc_forcestop_button = QtWidgets.QPushButton('停止(r)')
        self.swimcc_layout.addWidget(self.swimcc_forcestop_button, 2, 6, 1, 2, QtCore.Qt.AlignCenter)
        self.swimcc_forcestop_button.setObjectName("SET_SWIM_FORCESTOP")
        self.swimcc_forcestop_button.setShortcut('r')
        self.swimcc_forcestop_button.setFixedSize(110, self.button_height)

        self.pump_off_button = QtWidgets.QPushButton('水泵停止(b)')
        self.swimcc_layout.addWidget(self.pump_off_button, 3, 0, 1, 2, QtCore.Qt.AlignCenter)
        self.pump_off_button.setObjectName("SET_PUMP_OFF")
        self.pump_off_button.setShortcut('b')
        self.pump_off_button.setFixedSize(110, self.button_height)

        self.pump_in_button = QtWidgets.QPushButton('水泵抽水(n)')
        self.swimcc_layout.addWidget(self.pump_in_button, 3, 2, 1, 2, QtCore.Qt.AlignCenter)
        self.pump_in_button.setObjectName("SET_PUMP_IN")
        self.pump_in_button.setShortcut('n')
        self.pump_in_button.setFixedSize(110, self.button_height)

        self.pump_out_button = QtWidgets.QPushButton('水泵排水(m)')
        self.swimcc_layout.addWidget(self.pump_out_button, 3, 4, 1, 2, QtCore.Qt.AlignCenter)
        self.pump_out_button.setObjectName("SET_PUMP_OUT")
        self.pump_out_button.setShortcut('m')
        self.pump_out_button.setFixedSize(110, self.button_height)

        self.longitudinalmass_stop_button = QtWidgets.QPushButton('滑块停(i)')
        self.swimcc_layout.addWidget(self.longitudinalmass_stop_button, 4, 0, 1, 2, QtCore.Qt.AlignCenter)
        self.longitudinalmass_stop_button.setObjectName("SET_LONGITUDINAL_MASS_STOP")
        # self.longitudinalmass_stop_button.setObjectName("SET_LATERAL_MASS_STOP")
        self.longitudinalmass_stop_button.setShortcut('i')
        self.longitudinalmass_stop_button.setFixedSize(110, self.button_height)

        self.longitudinalmass_forward_button = QtWidgets.QPushButton('滑块↑(o)')
        self.swimcc_layout.addWidget(self.longitudinalmass_forward_button, 4, 2, 1, 2, QtCore.Qt.AlignCenter)
        self.longitudinalmass_forward_button.setObjectName("SET_LONGITUDINAL_MASS_FMOVE")
        # self.longitudinalmass_forward_button.setObjectName("SET_LATERAL_MASS_FMOVE")
        self.longitudinalmass_forward_button.setShortcut('o')
        self.longitudinalmass_forward_button.setFixedSize(110, self.button_height)

        self.longitudinalmaa_backward_button = QtWidgets.QPushButton('滑块↓(p)')
        self.swimcc_layout.addWidget(self.longitudinalmaa_backward_button, 4, 4, 1, 2, QtCore.Qt.AlignCenter)
        self.longitudinalmaa_backward_button.setObjectName("SET_LONGITUDINAL_MASS_BMOVE")
        # self.longitudinalmaa_backward_button.setObjectName("SET_LATERAL_MASS_BMOVE")
        self.longitudinalmaa_backward_button.setShortcut('p')
        self.longitudinalmaa_backward_button.setFixedSize(110, self.button_height)

        self.freq_sub_button = QtWidgets.QPushButton('freq-')
        self.swimcc_layout.addWidget(self.freq_sub_button, 4, 6, 1, 2, QtCore.Qt.AlignCenter)
        self.freq_sub_button.setObjectName("SET_FREQ_SUB")
        self.freq_sub_button.setFixedSize(110, self.button_height)

        self.freq_add_button = QtWidgets.QPushButton('freq+')
        self.swimcc_layout.addWidget(self.freq_add_button, 3, 6, 1, 2, QtCore.Qt.AlignCenter)
        self.freq_add_button.setObjectName("SET_FREQ_ADD")
        self.freq_add_button.setFixedSize(110, self.button_height)

        self.depth_control_button = QtWidgets.QPushButton('定深')
        self.swimcc_layout.addWidget(self.depth_control_button, 5, 0, 1, 2, QtCore.Qt.AlignCenter)
        self.depth_control_button.setObjectName("DEPTH_CONTROL")
        self.depth_control_button.setFixedSize(110, self.button_height)

        self.center_control_button = QtWidgets.QPushButton('回中')
        self.swimcc_layout.addWidget(self.center_control_button, 5, 2, 1, 2, QtCore.Qt.AlignCenter)
        self.center_control_button.setObjectName("CENTER_CONTROL")
        self.center_control_button.setFixedSize(110, self.button_height)

        self.turn_left_button = QtWidgets.QPushButton('左转')
        self.swimcc_layout.addWidget(self.turn_left_button, 5, 4, 1, 2, QtCore.Qt.AlignCenter)
        self.turn_left_button.setObjectName("TURN_LEFT")
        self.turn_left_button.setFixedSize(110, self.button_height)

        self.turn_right_button = QtWidgets.QPushButton('右转')
        self.swimcc_layout.addWidget(self.turn_right_button, 5, 6, 1, 2, QtCore.Qt.AlignCenter)
        self.turn_right_button.setObjectName("TURN_RIGHT")
        self.turn_right_button.setFixedSize(110, self.button_height)

        self.angle_control_button = QtWidgets.QPushButton('俯仰调节')
        self.swimcc_layout.addWidget(self.angle_control_button, 6, 0, 1, 2, QtCore.Qt.AlignCenter)
        self.angle_control_button.setObjectName("ANGLE_CONTROL")
        self.angle_control_button.setFixedSize(110, self.button_height)

        self.angle_end_button = QtWidgets.QPushButton('俯仰结束')
        self.swimcc_layout.addWidget(self.angle_end_button, 6, 2, 1, 2, QtCore.Qt.AlignCenter)
        self.angle_end_button.setObjectName("ANGLE_CONTROL_END")
        self.angle_end_button.setFixedSize(110, self.button_height)

        self.glide_rise_button = QtWidgets.QPushButton('上浮')
        self.swimcc_layout.addWidget(self.glide_rise_button, 6, 4, 1, 2, QtCore.Qt.AlignCenter)
        self.glide_rise_button.setObjectName("GLIDE_RISE")
        self.glide_rise_button.setFixedSize(110, self.button_height)

        self.glide_dive_button = QtWidgets.QPushButton('下潜')
        self.swimcc_layout.addWidget(self.glide_dive_button, 6, 6, 1, 2, QtCore.Qt.AlignCenter)
        self.glide_dive_button.setObjectName("GLIDE_DIVE")
        self.glide_dive_button.setFixedSize(110, self.button_height)

        # self.switch_button = QtWidgets.QPushButton('切换到第二个界面')
        # self.swimcc_layout.addWidget(self.switch_button, 4, 6, 1, 2, QtCore.Qt.AlignCenter)
        # self.switch_button.setFixedSize(110, self.button_height)
        # self.switch_button.clicked.connect(self.switch_window)


    # 初始化command shell面板
    def init_cmdshell_panel(self):
        """
        初始化command shell面板
        主要分为:输出窗口,输入命令和串口控制部分
        :return:
        """
        self.cmdshell_title_label = QtWidgets.QLabel('Command Shell')
        self.cmdshell_title_label.setObjectName('cmdshell_title_label')
        self.cmdshell_layout.addWidget(self.cmdshell_title_label,0,0,1,8)

        # 输出窗口和输入命令
        self.cmdshell_text_frame = QtWidgets.QFrame()
        self.cmdshell_text_frame.setObjectName('cmdshell_text_frame')
        self.cmdshell_text_layout = QtWidgets.QGridLayout()
        self.cmdshell_text_frame.setLayout(self.cmdshell_text_layout)
        self.cmdshell_layout.addWidget(self.cmdshell_text_frame, 1, 0, 10, 8)

        self.cmdshell_browser_label = QtWidgets.QLabel('输出窗口')
        self.cmdshell_browser_label.setObjectName('cmdshell_browser_label')
        self.cmdshell_text_layout.addWidget(self.cmdshell_browser_label, 0, 0, 1, 8, QtCore.Qt.AlignCenter)

        self.cmdshell_text_browser = QtWidgets.QTextBrowser()
        self.cmdshell_text_browser.setObjectName('cmdshell_text_browser')
        self.cmdshell_text_browser.setFixedSize(320, 300)
        self.cmdshell_text_layout.addWidget(self.cmdshell_text_browser, 1, 0, 8, 8, QtCore.Qt.AlignCenter)
        self.cmdshell_text_browser.append("<font color='Cyan'>robosharkstate-host:~$&nbsp;</font> ")

        self.cmdshell_editor_label = QtWidgets.QLabel('输入命令')
        self.cmdshell_editor_label.setObjectName('cmdshell_editor_label')
        self.cmdshell_text_layout.addWidget(self.cmdshell_editor_label, 9, 0, 1, 3, QtCore.Qt.AlignLeft)

        self.cmdshell_text_editor = QtWidgets.QLineEdit()
        self.cmdshell_text_editor.setObjectName('cmdshell_text_editor')
        self.cmdshell_text_editor.setFixedSize(200, 30)
        self.cmdshell_text_layout.addWidget(self.cmdshell_text_editor, 9, 2, 1, 6, QtCore.Qt.AlignCenter)

        # 串口控制
        self.serial_frame = QtWidgets.QFrame()
        self.serial_frame.setObjectName('serial_frame')
        self.serial_layout = QtWidgets.QGridLayout()
        self.serial_frame.setLayout(self.serial_layout)
        self.cmdshell_layout.addWidget(self.serial_frame, 11, 0, 4, 8)

        self.serial_fixed_label = QtWidgets.QLabel('串口控制')
        self.serial_fixed_label.setObjectName('serial_fixed_label')
        self.serial_layout.addWidget(self.serial_fixed_label, 0, 0, 1, 4, QtCore.Qt.AlignCenter)

        # 串口1--发送串口
        self.serial1_com_label = QtWidgets.QLabel('发送COM')
        self.serial1_com_label.setObjectName('serial1_com_label')
        self.serial_layout.addWidget(self.serial1_com_label, 1, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.serial1_com_combo = QtWidgets.QComboBox()
        serial1_available_ports = QSerialPortInfo.availablePorts()
        for port in serial1_available_ports:
            self.serial1_com_combo.addItem(port.portName())
        # self.serial1_com_combo.addItem('COM3')
        # self.serial1_com_combo.addItem('COM4')
        # self.serial1_com_combo.addItem('COM5')
        # self.serial1_com_combo.addItem('COM6')
        # self.serial1_com_combo.addItem('COM7')
        # self.serial1_com_combo.addItem('COM8')
        # self.serial1_com_combo.addItem('COM9')
        # self.serial1_com_combo.addItem('COM10')
        self.serial1_com_combo.setFixedSize(80, 30)
        self.serial_layout.addWidget(self.serial1_com_combo, 2, 0, 1, 1, QtCore.Qt.AlignLeft)

        self.serial1_bps_label = QtWidgets.QLabel('BPS')
        self.serial1_bps_label.setObjectName('serial1_bps_label')
        self.serial_layout.addWidget(self.serial1_bps_label, 1, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.serial1_bps_combo = QtWidgets.QComboBox()
        self.serial1_bps_combo.addItem('9600')
        self.serial1_bps_combo.addItem('14400')
        self.serial1_bps_combo.addItem('19200')
        self.serial1_bps_combo.addItem('38400')
        self.serial1_bps_combo.addItem('56000')
        self.serial1_bps_combo.addItem('57600')
        self.serial1_bps_combo.addItem('115200')
        self.serial1_bps_combo.setFixedSize(80, self.button_height)
        self.serial_layout.addWidget(self.serial1_bps_combo, 2, 1, 1, 1, QtCore.Qt.AlignLeft)

        self.serial1_open_button = QtWidgets.QPushButton('打开')
        self.serial1_open_button.setFixedSize(60, self.button_height)
        self.serial_layout.addWidget(self.serial1_open_button, 2, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.serial1_close_button = QtWidgets.QPushButton('关闭')
        self.serial1_close_button.setFixedSize(60, self.button_height)
        self.serial_layout.addWidget(self.serial1_close_button, 2, 3, 1, 1, QtCore.Qt.AlignCenter)

        # 串口2--接收串口
        self.serial2_com_label = QtWidgets.QLabel('接收COM')
        self.serial2_com_label.setObjectName('serial2_com_label')
        self.serial_layout.addWidget(self.serial2_com_label, 3, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.serial2_com_combo = QtWidgets.QComboBox()
        serial2_available_ports = QSerialPortInfo.availablePorts()
        for port in serial2_available_ports:
            self.serial2_com_combo.addItem(port.portName())
        # self.serial2_com_combo.addItem('COM3')
        # self.serial2_com_combo.addItem('COM4')
        # self.serial2_com_combo.addItem('COM5')
        # self.serial2_com_combo.addItem('COM7')
        # self.serial2_com_combo.addItem('COM6')
        # self.serial2_com_combo.addItem('COM8')
        # self.serial2_com_combo.addItem('COM9')
        # self.serial2_com_combo.addItem('COM10')
        # self.serial2_com_combo.addItem('COM11')
        # self.serial2_com_combo.addItem('COM12')
        # self.serial2_com_combo.addItem('COM13')
        # self.serial2_com_combo.addItem('COM14')
        # self.serial2_com_combo.addItem('COM16')
        self.serial2_com_combo.setFixedSize(80, self.button_height)
        self.serial_layout.addWidget(self.serial2_com_combo, 4, 0, 1, 1, QtCore.Qt.AlignLeft)

        self.serial2_bps_label = QtWidgets.QLabel('BPS')
        self.serial2_bps_label.setObjectName('serial2_bps_label')
        self.serial_layout.addWidget(self.serial2_bps_label, 3, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.serial2_bps_combo = QtWidgets.QComboBox()
        self.serial2_bps_combo.addItem('9600')
        self.serial2_bps_combo.addItem('14400')
        self.serial2_bps_combo.addItem('19200')
        self.serial2_bps_combo.addItem('38400')
        self.serial2_bps_combo.addItem('56000')
        self.serial2_bps_combo.addItem('57600')
        self.serial2_bps_combo.addItem('115200')
        self.serial2_bps_combo.setFixedSize(80, self.button_height)
        self.serial_layout.addWidget(self.serial2_bps_combo, 4, 1, 1, 1, QtCore.Qt.AlignLeft)

        self.serial2_open_button = QtWidgets.QPushButton('打开')
        self.serial2_open_button.setFixedSize(60, self.button_height)
        self.serial_layout.addWidget(self.serial2_open_button, 4, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.serial2_close_button = QtWidgets.QPushButton('关闭')
        self.serial2_close_button.setFixedSize(60, self.button_height)
        self.serial_layout.addWidget(self.serial2_close_button, 4, 3, 1, 1, QtCore.Qt.AlignCenter)

        self.fishid_label = QtWidgets.QLabel('编号:')
        self.fishid_label.setObjectName('fishid_label')
        self.serial_layout.addWidget(self.fishid_label, 5, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.fishid_combo = QtWidgets.QComboBox()
        for robot_id in rflink.FishID:
            self.fishid_combo.addItem(robot_id.name)
        self.fishid_combo.setCurrentText('Fish_1')
        self.fishid_combo.setFixedSize(120, self.button_height)
        self.serial_layout.addWidget(self.fishid_combo, 5, 1, 1, 1, QtCore.Qt.AlignLeft)

        self.serial_shakehand_button = QtWidgets.QPushButton('握手')
        self.serial_shakehand_button.setFixedSize(60, self.button_height)
        self.serial_shakehand_button.setObjectName("SHAKING_HANDS")
        self.serial_layout.addWidget(self.serial_shakehand_button, 5, 2, 1, 2, QtCore.Qt.AlignCenter)

        # self.pid_p_button = QtWidgets.QPushButton('P修改')
        # self.serial_layout.addWidget(self.pid_p_button, 6, 3, 1, 1, QtCore.Qt.AlignCenter)
        # self.pid_p_button.setObjectName("PID_P")
        # self.pid_p_button.setFixedSize(100, self.button_height)
        #
        # self.pid_i_button = QtWidgets.QPushButton('I修改')
        # self.serial_layout.addWidget(self.pid_i_button, 7, 3, 1, 1, QtCore.Qt.AlignCenter)
        # self.pid_i_button.setObjectName("PID_I")
        # self.pid_i_button.setFixedSize(100, self.button_height)
        #
        # self.pid_d_button = QtWidgets.QPushButton('D修改')
        # self.serial_layout.addWidget(self.pid_d_button, 8, 3, 1, 1, QtCore.Qt.AlignCenter)
        # self.pid_d_button.setObjectName("PID_D")
        # self.pid_d_button.setFixedSize(100, self.button_height)

        # self.cpgcc_offset_label = QtWidgets.QLabel('偏移')
        # self.cpgcc_offset_label.setObjectName('cpgcc_offset_label')
        # self.cpgcc_offset_label.setFixedSize(50, self.button_height)
        # self.datasw_layout.addWidget(self.cpgcc_offset_label, 15, 0, 1, 2, QtCore.Qt.AlignCenter)
        #
        # self.pid_p_edit = QtWidgets.QLineEdit()
        # self.pid_p_edit.setFixedSize(100, self.button_height)
        # double_validator3 = QtGui.QDoubleValidator()
        # double_validator3.setRange(-20, 20)
        # double_validator1.setNotation(QtGui.QDoubleValidator.StandardNotation)
        # double_validator1.setDecimals(2)
        # self.cpgcc_offset_edit.setValidator(double_validator3)
        # self.datasw_layout.addWidget(self.cpgcc_offset_edit, 15, 2, 1, 2, QtCore.Qt.AlignCenter)
        #
        # self.cpgcc_set_button = QtWidgets.QPushButton('写入')
        # self.datasw_layout.addWidget(self.cpgcc_set_button, 16, 0, 1, 4, QtCore.Qt.AlignCenter)
        # self.cpgcc_set_button.setObjectName("SET_CPG_DATA")
        # self.cpgcc_set_button.setFixedSize(100, self.button_height)


    def closeEvent(self, event):
        self.close_signal.emit()
        self.close()

    #####################################################################################################
    #####################################################################################################
    ## 第二部分:关于Slot和Signal的
    #####################################################################################################
    #####################################################################################################
    #信号连接
    def widgets_connect(self):
        """
        本函数将按钮发送信号与对应槽函数构建连接
        :return:
        """
        #状态显示
        self.read_robot_state_button.clicked.connect(self.stateshow_button_clicked)
        self.read_robot_data_button.clicked.connect(self.stateshow_button_clicked)

        #控制台
        self.swimcc_start_button.clicked.connect(self.console_button_clicked)
        self.swimcc_stop2start_button.clicked.connect(self.console_button_clicked)
        self.swimcc_stop_button.clicked.connect(self.console_button_clicked)
        self.swimcc_forcestop_button.clicked.connect(self.console_button_clicked)
        self.pump_off_button.clicked.connect(self.console_button_clicked)
        self.pump_in_button.clicked.connect(self.console_button_clicked)
        self.pump_out_button.clicked.connect(self.console_button_clicked)
        self.longitudinalmass_stop_button.clicked.connect(self.console_button_clicked)
        self.longitudinalmass_forward_button.clicked.connect(self.console_button_clicked)
        self.longitudinalmaa_backward_button.clicked.connect(self.console_button_clicked)
        self.freq_add_button.clicked.connect(self.console_button_clicked)
        self.freq_sub_button.clicked.connect(self.console_button_clicked)
        # self.depth_control_button.clicked.connect(self.console_button_clicked)
        self.center_control_button.clicked.connect(self.console_button_clicked)
        self.turn_left_button.clicked.connect(self.console_button_clicked)
        self.turn_right_button.clicked.connect(self.console_button_clicked)
        self.angle_control_button.clicked.connect(self.console_button_clicked)
        self.angle_end_button.clicked.connect(self.console_button_clicked)
        self.glide_dive_button.clicked.connect(self.console_button_clicked)
        self.glide_rise_button.clicked.connect(self.console_button_clicked)

        #参数设置
        self.cpgcc_set_button.clicked.connect(self.cpgcc_set_button_clicked)

        #数据显示
        self.datashow_start_button.clicked.connect(self.datashow_start_button_clicked)
        self.datashow_stop_button.clicked.connect(self.datashow_stop_button_clicked)
        self.datashow_clear_button.clicked.connect(self.datashow_clear_button_clicked)
        #记录数据的3个按钮 TODO
        ##IMU
        self.imu_checkbox.stateChanged.connect(self.imu_checkbox_ctl)
        self.angle_checkbox.stateChanged.connect(self.angle_checkbox_ctl)
        self.accel_checkbox.stateChanged.connect(self.accel_checkbox_ctl)
        self.gyro_checkbox.stateChanged.connect(self.gyro_checkbox_ctl)
        self.x_checkbox.stateChanged.connect(self.x_checkbox_ctl)
        self.y_checkbox.stateChanged.connect(self.y_checkbox_ctl)
        self.z_checkbox.stateChanged.connect(self.z_checkbox_ctl)
        ##深度传感器
        self.depthsensor_checkbox.stateChanged.connect(self.depthsensor_checkbox_ctl)
        self.depth_checkbox.stateChanged.connect(self.depth_checkbox_ctl)
        ##功率传感器
        self.powersensor_checkbox.stateChanged.connect(self.powersensor_checkbox_ctl)
        self.current_checkbox.stateChanged.connect(self.current_checkbox_ctl)
        self.voltage_checkbox.stateChanged.connect(self.voltage_checkbox_ctl)
        self.power_checkbox.stateChanged.connect(self.power_checkbox_ctl)
        self.pect_checkbox.stateChanged.connect(self.pect_checkbox_ctl)
        self.glide_checkbox.stateChanged.connect(self.glide_checkbox_ctl)

        #串口
        self.serial1_open_button.clicked.connect(self.serial1_open_button_clicked)
        self.serial1_close_button.clicked.connect(self.serial1_close_button_clicked)
        self.serial2_open_button.clicked.connect(self.serial2_open_button_clicked)
        self.serial2_close_button.clicked.connect(self.serial2_close_button_clicked)
        self.serial_shakehand_button.clicked.connect(self.shakehand_button_clicked)

        #Command Shell
        self.cmdshell_text_editor.returnPressed.connect(self.command_shell_backstage)

    #状态显示有关的按钮
    def stateshow_button_clicked(self):
        """
               状态读取按钮对应的槽函数
               :return:
               """
        sender_button = self.sender()
        cmd = rflink.Command[sender_button.objectName()].value
        data = 0
        if rflink.Command[sender_button.objectName()] is rflink.Command.READ_ROBOT_DATA:
            cmd1 = rflink.Command["READ_FLAP"].value
            cmd2 = rflink.Command["READ_FEATHER"].value
            cmd3 = rflink.Command["READ_PITCH"].value
            cmd4 = rflink.Command["READ_TAIL"].value
            # 数据打包
            datapack1 = rftool.RFLink_packdata(cmd1, data)
            datapack2 = rftool.RFLink_packdata(cmd2, data)
            datapack3 = rftool.RFLink_packdata(cmd3, data)
            datapack4 = rftool.RFLink_packdata(cmd4, data)
            # 数据发送
            with QtCore.QMutexLocker(ser_mutex):
                try:
                    send_sertool.write_cmd(datapack1)
                    time.sleep(0.1)
                    send_sertool.write_cmd(datapack2)
                    time.sleep(0.1)
                    send_sertool.write_cmd(datapack3)
                    time.sleep(0.1)
                    send_sertool.write_cmd(datapack4)
                except serial.serialutil.SerialException:
                    self.statusBar().showMessage('串口未打开,无法发送')
        else:
            #数据打包
            datapack = rftool.RFLink_packdata(cmd, data)
            #数据发送
            with QtCore.QMutexLocker(ser_mutex):
                try:
                    send_sertool.write_cmd(datapack)
                except serial.serialutil.SerialException:
                    self.statusBar().showMessage('串口未打开,无法发送')

    #参数设置有关的按钮
    def cpgcc_set_button_clicked(self):
        sender_button = self.sender()
        motor = self.motor_chose_combo.currentText()
        if motor == "lpect_flap":
            cmd = rflink.Command["SET_LPECT_FLAP"].value
            data = struct.pack('<f', float(self.cpgcc_amp_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_freq_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_offset_edit.text()))
        elif motor == "lpect_feather":
            cmd = rflink.Command["SET_LPECT_FEATHER"].value
            data = struct.pack('<f', float(self.cpgcc_amp_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_freq_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_offset_edit.text()))
        elif motor == "lpect_pitch":
            cmd = rflink.Command["SET_LPECT_PITCH"].value
            data = struct.pack('<f', float(self.cpgcc_amp_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_freq_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_offset_edit.text()))
        elif motor == "rpect_flap":
            cmd = rflink.Command["SET_RPECT_FLAP"].value
            data = struct.pack('<f', float(self.cpgcc_amp_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_freq_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_offset_edit.text()))
        elif motor == "rpect_feather":
            cmd = rflink.Command["SET_RPECT_FEATHER"].value
            data = struct.pack('<f', float(self.cpgcc_amp_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_freq_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_offset_edit.text()))
        elif motor == "rpect_pitch":
            cmd = rflink.Command["SET_RPECT_PITCH"].value
            data = struct.pack('<f', float(self.cpgcc_amp_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_freq_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_offset_edit.text()))
        elif motor == "tail":
            cmd = rflink.Command["SET_TAIL"].value
            data = struct.pack('<f', float(self.cpgcc_amp_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_freq_edit.text())) + \
                struct.pack('<f', float(self.cpgcc_offset_edit.text()))

        # 数据打包
        datapack = rftool.RFLink_packdata(cmd, data)
        # 数据发送
        with QtCore.QMutexLocker(ser_mutex):
            try:
                send_sertool.write_cmd(datapack)
            except serial.serialutil.SerialException:
                self.statusBar().showMessage('串口未打开,无法发送')

    #控制台有关的按钮
    def console_button_clicked(self):
        """
                本函数为控制台按钮按下时,关联的槽函数
                每个控制台的按钮都对应了RFLink通讯协议中的一条Command,所以可以统一用一个函数来处理
                每当按钮按下时,串口将Command发送出去,发给机器人
                :return:
                """
        sender_button = self.sender()
        cmd = rflink.Command[sender_button.objectName()].value
        if rflink.Command[sender_button.objectName()] is rflink.Command.SET_LONGITUDINAL_MASS_FMOVE:
            data = struct.pack('<h', short(1010))
        elif rflink.Command[sender_button.objectName()] is rflink.Command.SET_LONGITUDINAL_MASS_BMOVE:
            data = struct.pack('<h', short(1010))
        elif rflink.Command[sender_button.objectName()] is rflink.Command.SET_DEPTH_PID:  # 关于SET_DEPTHCTL_PARAM的处理
            data = struct.pack('<f', float(self.DCBW.depthctl_param_kp_edit.text())) + \
                   struct.pack('<f', float(self.DCBW.depthctl_param_ki_edit.text())) + \
                   struct.pack('<f', float(self.DCBW.depthctl_param_kd_edit.text()))  # data就是我们要发送的数据
        elif rflink.Command[sender_button.objectName()] is rflink.Command.SET_ANGLE_PID:  # 关于SET_DEPTHCTL_PARAM的处理
            data = struct.pack('<f', float(self.DCBW.anglectl_param_kp_edit.text())) + \
                   struct.pack('<f', float(self.DCBW.anglectl_param_ki_edit.text())) + \
                   struct.pack('<f', float(self.DCBW.anglectl_param_kd_edit.text()))  # data就是我们要发送的数据
        else:
            data = 0

        # 数据打包
        datapack = rftool.RFLink_packdata(cmd, data)
        # 数据发送
        with QtCore.QMutexLocker(ser_mutex):
            try:
                send_sertool.write_cmd(datapack)
            except serial.serialutil.SerialException:
                self.statusBar().showMessage('串口未打开,无法发送')

    #有关数据显示checkbox的一些列函数
    ##IMU
    def imu_checkbox_ctl(self):
        if self.imu_checkbox.isChecked():
            #IMU
            self.imu_checkbox.setChecked(True)
            self.angle_checkbox.setEnabled(True)
            self.accel_checkbox.setEnabled(True)
            self.gyro_checkbox.setEnabled(True)
            self.x_checkbox.setEnabled(True)
            self.y_checkbox.setEnabled(True)
            self.z_checkbox.setEnabled(True)
            #深度传感器
            self.depthsensor_checkbox.setChecked(False)
            self.depthsensor_checkbox.setEnabled(True)
            self.depth_checkbox.setEnabled(False)
            #功率传感器
            self.powersensor_checkbox.setChecked(False)
            self.powersensor_checkbox.setEnabled(True)
            self.current_checkbox.setEnabled(False)
            self.voltage_checkbox.setEnabled(False)
            self.power_checkbox.setEnabled(False)
            self.pect_checkbox.setEnabled(False)
            self.glide_checkbox.setEnabled(False)
            ##刷新datashow状态
            self.datashow_sensor_id = 1
            self.datashow_sensor_datatype = 0
            self.datashow_sensor_dataaxis = 0

    def angle_checkbox_ctl(self):
        if self.angle_checkbox.isChecked():
            self.accel_checkbox.setChecked(False)
            self.gyro_checkbox.setChecked(False)
            self.datashow_sensor_datatype = 1

    def accel_checkbox_ctl(self):
        if self.accel_checkbox.isChecked():
            self.angle_checkbox.setChecked(False)
            self.gyro_checkbox.setChecked(False)
            self.datashow_sensor_datatype = 2

    def gyro_checkbox_ctl(self):
        if self.gyro_checkbox.isChecked():
            self.angle_checkbox.setChecked(False)
            self.accel_checkbox.setChecked(False)
            self.datashow_sensor_datatype = 3

    def x_checkbox_ctl(self):
        if self.x_checkbox.isChecked():
            self.y_checkbox.setChecked(False)
            self.z_checkbox.setChecked(False)
            self.datashow_sensor_dataaxis = 1

    def y_checkbox_ctl(self):
        if self.y_checkbox.isChecked():
            self.x_checkbox.setChecked(False)
            self.z_checkbox.setChecked(False)
            self.datashow_sensor_dataaxis = 2

    def z_checkbox_ctl(self):
        if self.z_checkbox.isChecked():
            self.x_checkbox.setChecked(False)
            self.y_checkbox.setChecked(False)
            self.datashow_sensor_dataaxis = 3

    def depthsensor_checkbox_ctl(self):
        if self.depthsensor_checkbox.isChecked():
            # IMU
            self.imu_checkbox.setChecked(False)
            self.imu_checkbox.setEnabled(True)
            self.angle_checkbox.setEnabled(False)
            self.accel_checkbox.setEnabled(False)
            self.gyro_checkbox.setEnabled(False)
            self.x_checkbox.setEnabled(False)
            self.y_checkbox.setEnabled(False)
            self.z_checkbox.setEnabled(False)
            # 深度传感器
            self.depthsensor_checkbox.setChecked(True)
            self.depth_checkbox.setEnabled(True)
            # 功率传感器
            self.powersensor_checkbox.setChecked(False)
            self.powersensor_checkbox.setEnabled(True)
            self.current_checkbox.setEnabled(False)
            self.voltage_checkbox.setEnabled(False)
            self.power_checkbox.setEnabled(False)
            self.pect_checkbox.setEnabled(False)
            self.glide_checkbox.setEnabled(False)
            ##刷新datashow状态
            self.datashow_sensor_id = 2
            self.datashow_sensor_datatype = 0

    def depth_checkbox_ctl(self):
        if self.depth_checkbox.isChecked():
            self.depth_checkbox.setChecked(True)
            self.datashow_sensor_datatype = 1

    def powersensor_checkbox_ctl(self):
        if self.powersensor_checkbox.isChecked():
            # IMU
            self.imu_checkbox.setChecked(False)
            self.imu_checkbox.setEnabled(True)
            self.angle_checkbox.setEnabled(False)
            self.accel_checkbox.setEnabled(False)
            self.gyro_checkbox.setEnabled(False)
            self.x_checkbox.setEnabled(False)
            self.y_checkbox.setEnabled(False)
            self.z_checkbox.setEnabled(False)
            # 深度传感器
            self.depthsensor_checkbox.setChecked(False)
            self.depthsensor_checkbox.setEnabled(True)
            self.depth_checkbox.setEnabled(False)
            # 功率传感器
            self.powersensor_checkbox.setChecked(True)
            self.current_checkbox.setEnabled(True)
            self.voltage_checkbox.setEnabled(True)
            self.power_checkbox.setEnabled(True)
            self.pect_checkbox.setEnabled(True)
            self.glide_checkbox.setEnabled(True)
            ##刷新datashow状态
            self.datashow_sensor_id = 3
            self.datashow_sensor_datatype = 0
            self.datashow_sensor_module = 0

    def current_checkbox_ctl(self):
        if self.current_checkbox.isChecked():
            self.voltage_checkbox.setChecked(False)
            self.power_checkbox.setChecked(False)
            self.datashow_sensor_datatype = 1

    def voltage_checkbox_ctl(self):
        if self.voltage_checkbox.isChecked():
            self.current_checkbox.setChecked(False)
            self.power_checkbox.setChecked(False)
            self.datashow_sensor_datatype = 2

    def power_checkbox_ctl(self):
        if self.power_checkbox.isChecked():
            self.current_checkbox.setChecked(False)
            self.voltage_checkbox.setChecked(False)
            self.datashow_sensor_datatype = 3

    def pect_checkbox_ctl(self):
        if self.pect_checkbox.isChecked():
            self.glide_checkbox.setChecked(False)
            self.datashow_sensor_module = 1

    def glide_checkbox_ctl(self):
        if self.glide_checkbox.isChecked():
            self.pect_checkbox.setChecked(False)
            self.datashow_sensor_module = 2

    # 有关数据显示的一系列按钮
    def datashow_start_button_clicked(self):
        """
        开始显示数据
        每当输入命令栏,敲击回车键以后,会调用此函数
        :return:
        """
        cmd = None
        data = None
        #判断传感器类型
        ### IMU
        if self.datashow_sensor_id == 1:
            # 判断传感器ID和数据类型
            if self.datashow_sensor_datatype == 1:
                cmd = rflink.Command["READ_IMU_ATTITUDE"].value
            elif self.datashow_sensor_datatype ==2:
                cmd = rflink.Command["READ_IMU_ACCEL"].value
            elif self.datashow_sensor_datatype == 3:
                cmd = rflink.Command["READ_IMU_GYRO"].value
            else:
                self.statusBar().showMessage('未选定需要显示的数据')
                return
            # 判断数据的轴向
            if self.datashow_sensor_dataaxis == 1:
                data = 1
            elif self.datashow_sensor_dataaxis == 2:
                data = 2
            elif self.datashow_sensor_dataaxis == 3:
                data = 3
            else:
                self.statusBar().showMessage('未选定需要显示的数据')
                return

        ### 深度传感器
        elif self.datashow_sensor_id == 2:
            # 判断传感器ID和数据类型
            if self.datashow_sensor_datatype == 1:
                cmd = rflink.Command["READ_DEPTH"].value
                data = 0
            else:
                self.statusBar().showMessage('未选定需要显示的数据')
                return

        ###功率传感器
        elif self.datashow_sensor_id == 3:
            # 判断传感器ID和数据类型
            if self.datashow_sensor_datatype == 1:
                cmd = rflink.Command["READ_CURRENT"].value
                data = 0
            elif self.datashow_sensor_datatype == 2:
                cmd = rflink.Command["READ_VOLTAGE"].value
                data = 0
            elif self.datashow_sensor_datatype == 3:
                cmd = rflink.Command["READ_POWER"].value
                data = 0
            else:
                self.statusBar().showMessage('未选定需要显示的数据')
                return

            # 判断所需数据的模块
            if self.datashow_sensor_module == 1:
                data = 1
            elif self.datashow_sensor_module == 2:
                data = 2
            else:
                self.statusBar().showMessage('未选定需要显示的数据')
                return

        else:
            self.statusBar().showMessage('未选定需要显示的数据')
            return

        # 发送信号
        datapack = rftool.RFLink_packdata(cmd, struct.pack('B', data))
        with QtCore.QMutexLocker(ser_mutex):
            try:
                send_sertool.write_cmd(datapack)
            except serial.serialutil.SerialException:
                self.statusBar().showMessage('串口未打开,无法发送')
                return
        self.datashow_running_flag = True

        ## 一旦开始显示数据,全部checkbox都会停止
        #IMU
        self.imu_checkbox.setEnabled(False)
        self.angle_checkbox.setEnabled(False)
        self.accel_checkbox.setEnabled(False)
        self.gyro_checkbox.setEnabled(False)
        self.x_checkbox.setEnabled(False)
        self.y_checkbox.setEnabled(False)
        self.z_checkbox.setEnabled(False)
        #深度传感器
        self.depthsensor_checkbox.setEnabled(False)
        self.depth_checkbox.setEnabled(False)
        #功率传感器
        self.powersensor_checkbox.setEnabled(False)
        self.current_checkbox.setEnabled(False)
        self.voltage_checkbox.setEnabled(False)
        self.power_checkbox.setEnabled(False)
        self.pect_checkbox.setEnabled(False)
        self.glide_checkbox.setEnabled(False)

    def datashow_stop_button_clicked(self):
        datapack = rftool.RFLink_packdata(rflink.Command["SET_DATASHOW_OVER"].value, None)
        with QtCore.QMutexLocker(ser_mutex):
            try:
                send_sertool.write_cmd(datapack)
            except serial.serialutil.SerialException:
                self.statusBar().showMessage('串口未打开,无法发送')
                return
        self.datashow_running_flag = False

        ### 停止显示后使能Checkbox
        self.imu_checkbox.setEnabled(True)
        self.depthsensor_checkbox.setEnabled(True)
        self.powersensor_checkbox.setEnabled(True)
        if self.datashow_sensor_id == 1:
            self.angle_checkbox.setEnabled(True)
            self.accel_checkbox.setEnabled(True)
            self.gyro_checkbox.setEnabled(True)
            self.x_checkbox.setEnabled(True)
            self.y_checkbox.setEnabled(True)
            self.z_checkbox.setEnabled(True)
        elif self.datashow_sensor_id == 2:
            self.depth_checkbox.setEnabled(True)
        elif self.datashow_sensor_id == 3:
            self.current_checkbox.setEnabled(True)
            self.voltage_checkbox.setEnabled(True)
            self.power_checkbox.setEnabled(True)
            self.pect_checkbox.setEnabled(True)
            self.glide_checkbox.setEnabled(True)
        else:
            return

    def datashow_clear_button_clicked(self):
        if self.datashow_running_flag == False:
            # 停止绘制后的操作
            plt_mutex.lock()
            self.datalist = []
            self.timelist = []
            self.showtime = 0
            self.sensor_data_canvas.clear()
            plt_mutex.unlock()

    #记录数据的三个按钮 TODO


    # 有关串口开关的一系列按钮
    def serial1_open_button_clicked(self):
        """
        串口打开按钮对应的槽函数
        :return:
        """
        global send_sertool

        if (platform.system() == 'Windows'):
            port = self.serial1_com_combo.currentText()
        elif (platform.system() == 'Linux'):
            port = '/dev/' + self.serial1_com_combo.currentText()

        baud = int(self.serial1_bps_combo.currentText())
        try:
            send_sertool.init_serial(port, baud)
            self.statusBar().showMessage('发送串口已开启')
        except serial.serialutil.SerialException:
            self.statusBar().showMessage('该串口不存在')

    def serial1_close_button_clicked(self):
        """
        串口关闭对应的槽函数
        :return:
        """
        self.polling_state_thread.pause()
        send_sertool.close_serial()
        self.statusBar().showMessage('发送串口已关闭')

    def serial2_open_button_clicked(self):
        """
        接收串口打开按钮对应的槽函数
        :return:
        """
        global recv_sertool

        if(platform.system()=='Windows'):
            port = self.serial2_com_combo.currentText()
        elif(platform.system()=='Linux'):
            port = '/dev/'+self.serial2_com_combo.currentText()

        baud = int(self.serial2_bps_combo.currentText())
        try:
            recv_sertool.init_serial(port,baud)

            if self.receive_data_thread.is_running is False:
                self.receive_data_thread.start()
            else:
                self.receive_data_thread.resume()

            if self.analysis_data_thread.is_running is False:
                self.analysis_data_thread.start()
            else:
                self.analysis_data_thread.resume()

            self.statusBar().showMessage('接收串口已开启')
        except serial.serialutil.SerialException:
            self.statusBar().showMessage('该串口不存在')

    def serial2_close_button_clicked(self):
        """
        接收串口关闭对应的槽函数
        :return:
        """
        self.receive_data_thread.pause()
        self.analysis_data_thread.pause()
        recv_sertool.close_serial()
        self.statusBar().showMessage('接收串口已关闭')

    def shakehand_button_clicked(self):
        sender_button = self.sender()
        cmd = rflink.Command[sender_button.objectName()].value
        if rflink.Command[sender_button.objectName()] is rflink.Command.SHAKING_HANDS:
            if rflink.FishID[self.fishid_combo.currentText()] is rflink.FishID.FISH_ALL: #
                cmd = rflink.Command.SYNCHRONIZE_CLOCK.value
            data = 0
            # 数据打包
            datapack = rftool.RFLink_packdata(cmd, data)
            # 数据发送
            with QtCore.QMutexLocker(ser_mutex):
                try:
                    send_sertool.write_cmd(datapack)
                except serial.serialutil.SerialException:
                    self.statusBar().showMessage('串口未打开,无法发送')

    # Command Shell后端函数
    def command_shell_backstage(self):
        """
        本函数为Command Shell的后端函数
        每当输入命令栏,敲击回车键以后,会调用此函数
        :return:
        """
        # 获取用户输入的指令
        prefix = "<font color='Cyan'>robosharkstate-host:~$&nbsp;</font> "
        instr = self.cmdshell_text_editor.text()
        # self.cmdshell_text_editor.clear() # 清除编辑区的文字
        self.cmdshell_text_browser.append(prefix + instr)
        instrlist = instr.split()
        try:
            cmd = instrlist[0]
        except IndexError:
            return

        # 判断指令所属类型
        if cmd == "clear":  # 清除Shell显示区
            self.cmdshell_text_browser.clear()
            self.cmdshell_text_browser.append(prefix)

        elif cmd == "help":  # 打开帮助
            self.cmdshell_text_browser.append("<font color='DarkOrange'>Help&nbsp;Doc</font>")
            self.cmdshell_text_browser.append("<font color='DeepPink'>Basic&nbsp;operate&nbsp;commands&nbsp;including:</font>")
            self.cmdshell_text_browser.append("<font color='GreenYellow'>(1)&nbsp;ls</font>")
            self.cmdshell_text_browser.append("<font color='GreenYellow'>(1)&nbsp;clear</font>")
            self.cmdshell_text_browser.append("<font color='GreenYellow'>(2)&nbsp;help</font>")
            self.cmdshell_text_browser.append("<font color='GreenYellow'>(2)&nbsp;SET</font>")
            self.cmdshell_text_browser.append("<font color='GreenYellow'>(2)&nbsp;READ</font>")
            self.cmdshell_text_browser.append("<font color='GreenYellow'>(2)&nbsp;GOTO</font>")
            self.cmdshell_text_browser.append(
                "<font color='DeepPink'>Commands&nbsp;consist&nbsp;of&nbsp;four&nbsp;categories,&nbsp;including:</font>")
            self.cmdshell_text_browser.append(
                "<font color='GreenYellow'>(1)&nbsp;SHAKING_HANDS&nbsp;:&nbsp;build&nbsp;communication&nbsp;with&nbsp;slave</font>")
            self.cmdshell_text_browser.append(
                "<font color='GreenYellow'>(2)&nbsp;SET&nbsp;cmd:&nbsp;set&nbsp;parameters&nbsp;of&nbsp;slave</font>")
            self.cmdshell_text_browser.append(
                "<font color='GreenYellow'>(3)&nbsp;READ&nbsp;cmd:&nbsp;read&nbsp;parameters&nbsp;from&nbsp;slave</font>")
            self.cmdshell_text_browser.append(
                "<font color='GreenYellow'>(4)&nbsp;GOTO&nbsp;cmd:&nbsp;goto&nbsp;execute&nbsp;behaviors&nbsp;of&nbsp;slave</font>")
            self.cmdshell_text_browser.append(
                "<font color='DarkOrange'>Further&nbsp;explanation,&nbsp;please&nbsp;type&nbsp;'SET*'&nbsp;or&nbsp;'READ*'&nbsp;or&nbsp;'GOTO*'</font>")

        elif cmd == "SET": # 查询SET相关命令
            self.cmdshell_text_browser.append("<font color='DarkOrange'>" + "Usage&nbsp;:&nbsp;SET*&nbsp;[param1]&nbsp;[param2]&nbsp;..." + "</font>")
            self.cmdshell_text_browser.append("<font color='DeepPink'>" + "Example&nbsp;:&nbsp;SET_SINE_MOTION_AMP&nbsp;0.1" + "</font>")
            for i in range(28):
                self.cmdshell_text_browser.append("<font color='GreenYellow'>"+rflink.Command(i+2).name+"</font>")

        elif cmd == "READ": # 查询READ相关命令
            self.cmdshell_text_browser.append("<font color='DarkOrange'>" + "Usage&nbsp;:&nbsp;READ*" + "</font>")
            self.cmdshell_text_browser.append("<font color='DeepPink'>" + "Example&nbsp;:&nbsp;READ_ROBOT_STATUS" + "</font>")
            for i in range(12):
                self.cmdshell_text_browser.append("<font color='GreenYellow'>" + rflink.Command(i+30).name + "</font>")

        elif cmd == "GOTO": # 查询GOTO相关命令
            self.cmdshell_text_browser.append("<font color='DarkOrange'>" + "Usage&nbsp;:&nbsp;GOTO*" + "</font>")
            self.cmdshell_text_browser.append("<font color='DeepPink'>" + "Example&nbsp;:&nbsp;GOTO_SEND_DATA" + "</font>")
            for i in range(3):
                self.cmdshell_text_browser.append("<font color='GreenYellow'>" + rflink.Command(i+42).name + "</font>")

        elif cmd == "ls": # 显示下位机SD卡中的文件名
            # 发送一条读取文件列表的命令,等待下位机响应,并返回文件列表
            datapack = rftool.RFLink_packdata(rflink.Command.READ_FILE_LIST.value, None)
            with QtCore.QMutexLocker(ser_mutex):
                try:
                    send_sertool.write_cmd(datapack)
                except serial.serialutil.SerialException:
                    self.cmdshell_text_browser.append(
                        "<font color='red'>Warning&nbsp;:&nbsp;Serial&nbsp;port&nbsp;not&nbsp;open,&nbsp;false&nbsp;!</font>")

        elif cmd == "save":
            self.cmdshell_text_browser.append("<font color='orange'>(1)GOTO_STORAGE_DATA</font>")
            self.cmdshell_text_browser.append("<font color='orange'>(2)GOTO_SEND_DATA</font>")

        # else:  # 其他指令,也就是rflink中定义的指令 TODO

    #####################################################################################################
    #####################################################################################################
    ## 第三部分:下位机数据处理,就一个函数
    #####################################################################################################
    #####################################################################################################
    def newdata_comming_slot(self,command_id):
        """
        窗口更新槽函数
        每当接收到来自AnalysisDataThread的Command的ID,开始刷新窗口界面
        :param command_id:接收的Command的ID
        :return:
        """
        global robosharkstate
        global rftool

        if rflink.Command(command_id) is rflink.Command.SHAKING_HANDS:
            # 握手成功,打开轮询线程,不要采用轮询的方式
            # if self.polling_state_thread.is_running is False:
            #     self.polling_state_thread.start()
            # else:
            #     self.polling_state_thread.resume()
            # 刷新cmdshell
            prefix = "<font color='red'>slave:~$&nbsp;</font> "
            self.cmdshell_text_browser.append(prefix + "Shaking&nbsp;hands&nbsp;succeed&nbsp;!")

        elif rflink.Command(command_id) is rflink.Command.READ_ROBOT_STATUS:
            # 更新状态栏
            rm_mutex.lock()
            pal = QtGui.QPalette()
            self.swimstate_label.setAutoFillBackground(True)

            if robosharkstate.pump_limit == 0:
                if robosharkstate.mass_limit == 0:
                        if robosharkstate.swim_state is robotstate.SwimState.SWIM_FORCESTOP:
                            self.swimstate_label.setText('停止')
                            pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.red)
                            self.swimstate_label.setPalette(pal)
                        elif robosharkstate.swim_state is robotstate.SwimState.SWIM_STOP:
                            self.swimstate_label.setText('暂停')
                            pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.blue)
                            self.swimstate_label.setPalette(pal)
                        elif robosharkstate.swim_state is robotstate.SwimState.SWIM_RUN:
                            self.swimstate_label.setText('运行')
                            pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.green)
                            self.swimstate_label.setPalette(pal)
                        elif robosharkstate.swim_state is robotstate.SwimState.SWIM_INIT:
                            self.swimstate_label.setText('初始化')
                            pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.gray)
                            self.swimstate_label.setPalette(pal)
                else:
                    self.swimstate_label.setText('滑块限位')
                    pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.red)
                    self.swimstate_label.setPalette(pal)
            else:
                self.swimstate_label.setText('活塞限位')
                pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.red)
                self.swimstate_label.setPalette(pal)
            rm_mutex.unlock()

        elif rflink.Command(command_id) is rflink.Command.READ_FLAP:
            rm_mutex.lock()
            print('刷新FLAP对应的值')
            self.lpect_flap_amp_label.setText(str(round(robosharkstate.lpect_flap_amp,2)))
            self.lpect_flap_freq_label.setText(str(round(robosharkstate.lpect_flap_freq,2)))
            self.lpect_flap_offset_label.setText(str(round(robosharkstate.lpect_flap_offset,2)))
            self.rpect_flap_amp_label.setText(str(round(robosharkstate.rpect_flap_amp, 2)))
            self.rpect_flap_freq_label.setText(str(round(robosharkstate.rpect_flap_freq, 2)))
            self.rpect_flap_offset_label.setText(str(round(robosharkstate.rpect_flap_offset, 2)))
            rm_mutex.unlock()
            pal = QtGui.QPalette()
            pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.blue)
            self.lpect_flap_amp_label.setPalette(pal)
            self.lpect_flap_freq_label.setPalette(pal)
            self.lpect_flap_offset_label.setPalette(pal)
            self.rpect_flap_amp_label.setPalette(pal)
            self.rpect_flap_freq_label.setPalette(pal)
            self.rpect_flap_offset_label.setPalette(pal)

        elif rflink.Command(command_id) is rflink.Command.READ_FEATHER:
            rm_mutex.lock()
            print('刷新FEATHER对应的值')
            self.lpect_feather_amp_label.setText(str(round(robosharkstate.lpect_feather_amp,2)))
            self.lpect_feather_freq_label.setText(str(round(robosharkstate.lpect_feather_freq,2)))
            self.lpect_feather_offset_label.setText(str(round(robosharkstate.lpect_feather_offset,2)))
            self.rpect_feather_amp_label.setText(str(round(robosharkstate.rpect_feather_amp, 2)))
            self.rpect_feather_freq_label.setText(str(round(robosharkstate.rpect_feather_freq, 2)))
            self.rpect_feather_offset_label.setText(str(round(robosharkstate.rpect_feather_offset, 2)))
            rm_mutex.unlock()
            pal = QtGui.QPalette()
            pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.blue)
            self.lpect_feather_amp_label.setPalette(pal)
            self.lpect_feather_freq_label.setPalette(pal)
            self.lpect_feather_offset_label.setPalette(pal)
            self.rpect_feather_amp_label.setPalette(pal)
            self.rpect_feather_freq_label.setPalette(pal)
            self.rpect_feather_offset_label.setPalette(pal)

        elif rflink.Command(command_id) is rflink.Command.READ_PITCH:
            rm_mutex.lock()
            print('刷新PITCH对应的值')
            self.lpect_pitch_amp_label.setText(str(round(robosharkstate.lpect_pitch_amp,2)))
            self.lpect_pitch_freq_label.setText(str(round(robosharkstate.lpect_pitch_freq,2)))
            self.lpect_pitch_offset_label.setText(str(round(robosharkstate.lpect_pitch_offset,2)))
            self.rpect_pitch_amp_label.setText(str(round(robosharkstate.rpect_pitch_amp, 2)))
            self.rpect_pitch_freq_label.setText(str(round(robosharkstate.rpect_pitch_freq, 2)))
            self.rpect_pitch_offset_label.setText(str(round(robosharkstate.rpect_pitch_offset, 2)))
            rm_mutex.unlock()
            pal = QtGui.QPalette()
            pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.blue)
            self.lpect_pitch_amp_label.setPalette(pal)
            self.lpect_pitch_freq_label.setPalette(pal)
            self.lpect_pitch_offset_label.setPalette(pal)
            self.rpect_pitch_amp_label.setPalette(pal)
            self.rpect_pitch_freq_label.setPalette(pal)
            self.rpect_pitch_offset_label.setPalette(pal)

        elif rflink.Command(command_id) is rflink.Command.READ_TAIL:
            rm_mutex.lock()
            print('刷新TAIL对应的值')
            self.tail_amp_label.setText(str(round(robosharkstate.tail_amp,2)))
            self.tail_freq_label.setText(str(round(robosharkstate.tail_freq,2)))
            self.tail_offset_label.setText(str(round(robosharkstate.tail_offset,2)))
            rm_mutex.unlock()
            pal = QtGui.QPalette()
            pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.blue)
            self.tail_amp_label.setPalette(pal)
            self.tail_freq_label.setPalette(pal)
            self.tail_offset_label.setPalette(pal)

        elif command_id >= rflink.Command.READ_IMU_ATTITUDE.value and \
            command_id <= rflink.Command.READ_POWER.value:

            rf_mutex.lock()
            try:
                if rftool.length == 16:
                    # print(rftool.length)
                    # print('刷新窗口进入数据字节数为16')
                    print(rftool.message)
                    showdata = struct.unpack('ffff', rftool.message[1:])[0]
                    append_variable_to_txt(showdata, 'a_v_x.txt')
                    # savedata = struct.unpack('ffff', rftool.message[1:])
                elif rftool.length == 8:
                    # print(rftool.length)
                    # print('刷新窗口进入数据字节数为8')
                    print(rftool.message)
                    showdata = struct.unpack('ff', rftool.message[1:])[0]
                    append_variable_to_txt(showdata, 'a_v_x.txt')
                    # savedata = struct.unpack('ff', rftool.message[1:])
                elif rftool.length == 4:
                    print('刷新窗口进入数据字节数为4')
                    print(rftool.message)
                    showdata = struct.unpack('f', rftool.message[1:])[0]
                    # print(showdata)
                    append_variable_to_txt(showdata, 'a_v_x.txt')
                    # savedata = struct.unpack('f', rftool.message[1:])
                elif rftool.length == 2:
                    # print('刷新窗口进入数据字节数为2')
                    # print(rftool.message)
                    showdata = struct.unpack('h', rftool.message[1:])[0]
                    append_variable_to_txt(showdata, 'a_v_x.txt')
                    # savedata = struct.unpack('h', rftool.message[1:])
                elif rftool.length == 1:
                    # print('刷新窗口进入数据字节数为1')
                    # print(rftool.message)
                    showdata = struct.unpack('B', rftool.message[1:])[0]
                    append_variable_to_txt(showdata, 'a_v_x.txt')
                    # savedata = struct.unpack('B', rftool.message[1:])
                else:
                    showdata = 10
                    # savedata = [0,0,0,0]
            except:
                showdata = 10
                #  savedata = [0,0,0,0]
            rf_mutex.unlock()

            plt_mutex.lock()
            self.datalist.append(showdata)
            self.timelist.append(self.showtime)
            self.showtime = self.showtime + 1.0
            self.sensor_data_canvas.plot(self.timelist, self.datalist)
            _maxvalue = max(self.datalist[0:])
            _minvalue = min(self.datalist[0:])
            self.yaxis_upbound = _maxvalue + abs(_maxvalue) * 0.2
            self.yaxis_lowbound = _minvalue - abs(_minvalue) * 0.2
            self.sensor_data_canvas.set_ylim(self.yaxis_lowbound, self.yaxis_upbound)

            if len(self.datalist) > 100:
                self.timelist.pop(0)
                self.datalist.pop(0)
            plt_mutex.unlock()

        elif rflink.Command(command_id) is rflink.Command.PRINT_SYS_MSG:
            rf_mutex.lock()
            # 读取当前消息
            mes = rftool.message
            rf_mutex.unlock()
            # 刷新cmdshell
            self.cmdshell_text_browser.append("<font color='orange'>"+str(mes[1:],'ascii')+"</font>")

        # # 记录数据到文件中（还未完善？？？？）
        # elif rflink.Command(command_id) is rflink.Command.GOTO_SEND_DATA:
        #     # 读取当前消息
        #     rf_mutex.lock()
        #     mes = rftool.message
        #     meslen = rftool.length
        #     rf_mutex.unlock()
        #
        #     print("mes:")
        #     print(mes)
        #     print("meslen:")
        #     print(meslen)
        #
        #     if len(mes)==2:
        #         if mes[1]==1:
        #             self.SBBW.set_lineeditor_text('回传中，请耐心等待~~~')
        #             filename = 'data/' + self.savefile_name[9:]
        #             self.datafile = open(filename,'ab+')
        #             prefix = "<font color='red'>slave:~$&nbsp;</font> "
        #             self.cmdshell_text_browser.append(prefix + "Transfer Beginning!")
        #         elif mes[1]==0:
        #             self.SBBW.set_lineeditor_text('回传成功！')
        #             self.datafile.close()
        #             prefix = "<font color='red'>slave:~$&nbsp;</font> "
        #             self.cmdshell_text_browser.append(prefix + "Transfer Succeed!")
        #         else:
        #             self.datafile.write(mes[1:])




        elif rflink.Command(command_id) is not rflink.Command.LAST_COMMAND_FLAG:

            # 读取当前消息
            rf_mutex.lock()
            mes = rftool.message
            meslen = rftool.length
            rf_mutex.unlock()

            # 刷新cmdshell
            prefix = "<font color='red'>slave:~$&nbsp;</font> "
            self.cmdshell_text_browser.append(prefix + rflink.Command(command_id).name)
            # self.cmdshell_text_browser.append(str(mes))

        QtWidgets.QApplication.processEvents()

    def switch_window(self):
        second_window.show()
        self.hide()

class SecondWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('第二个界面')
        self.button = QtWidgets.QPushButton('切换到第一个界面')
        self.button.clicked.connect(self.switch_window)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

    def switch_window(self):
        RRW.show()
        self.hide()


if __name__ == '__main__':
     # 创建QApplication对象是必须，管理整个程序，参数可有可无，有的话可接收命令行参数
    app = QtWidgets.QApplication(sys.argv) 

    # 创建窗体对象
    RRW = RoboPenguinWindow()

    second_window = SecondWindow()
    
    # 美化窗体对象
    with open('robosharkhost.qss') as f:
        qss = f.read()
    RRW.setStyleSheet(qss)




    #
    sys.exit(app.exec_())
