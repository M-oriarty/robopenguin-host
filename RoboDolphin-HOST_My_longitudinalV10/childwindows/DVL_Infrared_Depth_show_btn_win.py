import os
import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import sensor_data_canvas

### 子界面类
class DVLInfraredDepthShowBtnWin(QtWidgets.QWidget):
    _signal = QtCore.pyqtSignal(str)

    ## 初始化函数
    def __init__(self, parent=None):
        super(DVLInfraredDepthShowBtnWin, self).__init__(parent)
        self.init_ui()

    ## 初始化串口UI界面
    def init_ui(self):

        # 窗口设置
        self.setFixedSize(1900, 1000)  # 设置窗体大小
        self.setWindowTitle('距离速度信息曲线显示')  # 设置窗口标题

        # 布局
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        # 传感器数据显示区
        #DVL_VELOCITYX
        self.dvl_velx_datashow_frame = QtWidgets.QFrame()
        self.dvl_velx_datashow_layout = QtWidgets.QGridLayout()
        self.dvl_velx_datashow_frame.setLayout(self.dvl_velx_datashow_layout)
        self.dvl_velx_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.dvl_velx_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.dvl_velx_datashow_frame.setLineWidth(1)
        #DVL_VELOCITYY
        self.dvl_vely_datashow_frame = QtWidgets.QFrame()
        self.dvl_vely_datashow_layout = QtWidgets.QGridLayout()
        self.dvl_vely_datashow_frame.setLayout(self.dvl_vely_datashow_layout)
        self.dvl_vely_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.dvl_vely_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.dvl_vely_datashow_frame.setLineWidth(1)
        #DVL_VELOCITYZ
        self.dvl_velz_datashow_frame = QtWidgets.QFrame()
        self.dvl_velz_datashow_layout = QtWidgets.QGridLayout()
        self.dvl_velz_datashow_frame.setLayout(self.dvl_velz_datashow_layout)
        self.dvl_velz_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.dvl_velz_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.dvl_velz_datashow_frame.setLineWidth(1)
        #DVL_DISTANCEX
        self.dvl_disx_datashow_frame = QtWidgets.QFrame()
        self.dvl_disx_datashow_layout = QtWidgets.QGridLayout()
        self.dvl_disx_datashow_frame.setLayout(self.dvl_disx_datashow_layout)
        self.dvl_disx_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.dvl_disx_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.dvl_disx_datashow_frame.setLineWidth(1)
        #DVL_DISTANCEY
        self.dvl_disy_datashow_frame = QtWidgets.QFrame()
        self.dvl_disy_datashow_layout = QtWidgets.QGridLayout()
        self.dvl_disy_datashow_frame.setLayout(self.dvl_disy_datashow_layout)
        self.dvl_disy_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.dvl_disy_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.dvl_disy_datashow_frame.setLineWidth(1)
        #DVL_DISTANCEZ
        self.dvl_disz_datashow_frame = QtWidgets.QFrame()
        self.dvl_disz_datashow_layout = QtWidgets.QGridLayout()
        self.dvl_disz_datashow_frame.setLayout(self.dvl_disz_datashow_layout)
        self.dvl_disz_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.dvl_disz_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.dvl_disz_datashow_frame.setLineWidth(1)
        #DEPTH
        self.depth_datashow_frame = QtWidgets.QFrame()
        self.depth_datashow_layout = QtWidgets.QGridLayout()
        self.depth_datashow_frame.setLayout(self.depth_datashow_layout)
        self.depth_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.depth_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.depth_datashow_frame.setLineWidth(1)
        #INFRARED_PISTON
        self.infrared_piston_datashow_frame = QtWidgets.QFrame()
        self.infrared_piston_datashow_layout = QtWidgets.QGridLayout()
        self.infrared_piston_datashow_frame.setLayout(self.infrared_piston_datashow_layout)
        self.infrared_piston_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.infrared_piston_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.infrared_piston_datashow_frame.setLineWidth(1)
        #INFRARED_LONGITUDINAL
        self.infrared_longitudinal_datashow_frame = QtWidgets.QFrame()
        self.infrared_longitudinal_datashow_layout = QtWidgets.QGridLayout()
        self.infrared_longitudinal_datashow_frame.setLayout(self.infrared_longitudinal_datashow_layout)
        self.infrared_longitudinal_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.infrared_longitudinal_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.infrared_longitudinal_datashow_frame.setLineWidth(1)

        self.main_layout.addWidget(self.dvl_velx_datashow_frame, 0, 0, 2, 2)
        self.main_layout.addWidget(self.dvl_vely_datashow_frame, 0, 2, 2, 2)
        self.main_layout.addWidget(self.dvl_velz_datashow_frame, 0, 4, 2, 2)
        self.main_layout.addWidget(self.dvl_disx_datashow_frame, 2, 0, 2, 2)
        self.main_layout.addWidget(self.dvl_disy_datashow_frame, 2, 2, 2, 2)
        self.main_layout.addWidget(self.dvl_disz_datashow_frame, 2, 4, 2, 2)
        self.main_layout.addWidget(self.depth_datashow_frame, 4, 0, 2, 2)
        self.main_layout.addWidget(self.infrared_piston_datashow_frame, 4, 2, 2, 2)
        self.main_layout.addWidget(self.infrared_longitudinal_datashow_frame, 4, 4, 2, 2)

        self.init_dvl_velx_datashow_frame_panel()
        self.init_dvl_vely_datashow_frame_panel()
        self.init_dvl_velz_datashow_frame_panel()
        self.init_dvl_disx_datashow_frame_panel()
        self.init_dvl_disy_datashow_frame_panel()
        self.init_dvl_disz_datashow_frame_panel()
        self.init_depth_datashow_frame_panel()
        self.init_infrared_piston_datashow_frame_panel()
        self.init_infrared_longitudinal_datashow_frame_panel()

        # 定义UI界面，这里由用户自己定义
        self.DVL_Infrared_Depth_Show_start_button = QtWidgets.QPushButton('开启显示')
        self.main_layout.addWidget(self.DVL_Infrared_Depth_Show_start_button, 6, 2, 1, 1, QtCore.Qt.AlignCenter)
        # 这里需要给按钮设置一个名字，因为之后需要将这个按钮与一个函数链接起来，那个函数会根据这个名字给下位机发送指令
        # 所以这个按钮的名字，应该作为一条指令添加到RFLink的Command中
        self.DVL_Infrared_Depth_Show_start_button.setObjectName("SET_DISTANCE_VELOCITY_SHOW_STAR") 

        self.DVL_Infrared_Depth_Show_stop_button = QtWidgets.QPushButton('关闭显示')
        self.main_layout.addWidget(self.DVL_Infrared_Depth_Show_stop_button, 6, 3, 1, 1, QtCore.Qt.AlignCenter)
        self.DVL_Infrared_Depth_Show_stop_button.setObjectName("SET_DISTANCE_VELOCITY_SHOW_STOP")

    def handle_click(self):
        if not self.isVisible():
            self.show()


    def handle_close(self):
        self.close()


    def init_dvl_velx_datashow_frame_panel(self):
        """
        初始化DVL的x轴向速度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.dvl_velx_canvas_frame = QtWidgets.QFrame()
        self.dvl_velx_canvas_frame.setObjectName('dvl_velx_canvas_frame')
        self.dvl_velx_canvas_layout = QtWidgets.QVBoxLayout()
        self.dvl_velx_canvas_frame.setLayout(self.dvl_velx_canvas_layout)

        self.dvl_velx_datashow_layout.addWidget(self.dvl_velx_canvas_frame, 0, 0, 10, 12)

        self.dvl_velx_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.dvl_velx_sensor_data_canvas,self.dvl_velx_canvas_frame)
        self.dvl_velx_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.dvl_velx_canvas_layout.addWidget(self.dvl_velx_sensor_data_canvas)
        self.dvl_velx_sensor_data_canvas.ax.set_ylabel('DVL Vx m/s')

    def init_dvl_vely_datashow_frame_panel(self):
        """
        初始化DVL的y轴向速度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.dvl_vely_canvas_frame = QtWidgets.QFrame()
        self.dvl_vely_canvas_frame.setObjectName('dvl_vely_canvas_frame')
        self.dvl_vely_canvas_layout = QtWidgets.QVBoxLayout()
        self.dvl_vely_canvas_frame.setLayout(self.dvl_vely_canvas_layout)

        self.dvl_vely_datashow_layout.addWidget(self.dvl_vely_canvas_frame, 0, 0, 10, 12)

        self.dvl_vely_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.dvl_vely_sensor_data_canvas,self.dvl_vely_canvas_frame)
        self.dvl_vely_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.dvl_vely_canvas_layout.addWidget(self.dvl_vely_sensor_data_canvas)
        self.dvl_vely_sensor_data_canvas.ax.set_ylabel('DVL Vy m/s')

    def init_dvl_velz_datashow_frame_panel(self):
        """
        初始化DVL的z轴向速度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.dvl_velz_canvas_frame = QtWidgets.QFrame()
        self.dvl_velz_canvas_frame.setObjectName('dvl_velz_canvas_frame')
        self.dvl_velz_canvas_layout = QtWidgets.QVBoxLayout()
        self.dvl_velz_canvas_frame.setLayout(self.dvl_velz_canvas_layout)

        self.dvl_velz_datashow_layout.addWidget(self.dvl_velz_canvas_frame, 0, 0, 10, 12)

        self.dvl_velz_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.dvl_velz_sensor_data_canvas,self.dvl_velz_canvas_frame)
        self.dvl_velz_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.dvl_velz_canvas_layout.addWidget(self.dvl_velz_sensor_data_canvas)
        self.dvl_velz_sensor_data_canvas.ax.set_ylabel('DVL Vz m/s')

    def init_dvl_disx_datashow_frame_panel(self):
        """
        初始化DVL的x轴向距离信息显示区面板
        :return:
        """

        # 图像显示部分
        self.dvl_disx_canvas_frame = QtWidgets.QFrame()
        self.dvl_disx_canvas_frame.setObjectName('dvl_disx_canvas_frame')
        self.dvl_disx_canvas_layout = QtWidgets.QVBoxLayout()
        self.dvl_disx_canvas_frame.setLayout(self.dvl_disx_canvas_layout)

        self.dvl_disx_datashow_layout.addWidget(self.dvl_disx_canvas_frame, 0, 0, 10, 12)

        self.dvl_disx_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.dvl_disx_sensor_data_canvas,self.dvl_disx_canvas_frame)
        self.dvl_disx_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.dvl_disx_canvas_layout.addWidget(self.dvl_disx_sensor_data_canvas)
        self.dvl_disx_sensor_data_canvas.ax.set_ylabel('DVL Dx m')

    def init_dvl_disy_datashow_frame_panel(self):
        """
        初始化DVL的y轴向距离信息显示区面板
        :return:
        """

        # 图像显示部分
        self.dvl_disy_canvas_frame = QtWidgets.QFrame()
        self.dvl_disy_canvas_frame.setObjectName('dvl_disy_canvas_frame')
        self.dvl_disy_canvas_layout = QtWidgets.QVBoxLayout()
        self.dvl_disy_canvas_frame.setLayout(self.dvl_disy_canvas_layout)

        self.dvl_disy_datashow_layout.addWidget(self.dvl_disy_canvas_frame, 0, 0, 10, 12)

        self.dvl_disy_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.dvl_disy_sensor_data_canvas,self.dvl_disy_canvas_frame)
        self.dvl_disy_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.dvl_disy_canvas_layout.addWidget(self.dvl_disy_sensor_data_canvas)
        self.dvl_disy_sensor_data_canvas.ax.set_ylabel('DVL Dy m')

    def init_dvl_disz_datashow_frame_panel(self):
        """
        初始化DVL的z轴向距离信息显示区面板
        :return:
        """

        # 图像显示部分
        self.dvl_disz_canvas_frame = QtWidgets.QFrame()
        self.dvl_disz_canvas_frame.setObjectName('dvl_disz_canvas_frame')
        self.dvl_disz_canvas_layout = QtWidgets.QVBoxLayout()
        self.dvl_disz_canvas_frame.setLayout(self.dvl_disz_canvas_layout)

        self.dvl_disz_datashow_layout.addWidget(self.dvl_disz_canvas_frame, 0, 0, 10, 12)

        self.dvl_disz_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.dvl_disz_sensor_data_canvas,self.dvl_disz_canvas_frame)
        self.dvl_disz_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.dvl_disz_canvas_layout.addWidget(self.dvl_disz_sensor_data_canvas)
        self.dvl_disz_sensor_data_canvas.ax.set_ylabel('DVL Dz m')

    def init_depth_datashow_frame_panel(self):
        """
        初始化深度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.depth_canvas_frame = QtWidgets.QFrame()
        self.depth_canvas_frame.setObjectName('depth_canvas_frame')
        self.depth_canvas_layout = QtWidgets.QVBoxLayout()
        self.depth_canvas_frame.setLayout(self.depth_canvas_layout)

        self.depth_datashow_layout.addWidget(self.depth_canvas_frame, 0, 0, 10, 12)

        self.depth_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.depth_sensor_data_canvas,self.depth_canvas_frame)
        self.depth_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.depth_canvas_layout.addWidget(self.depth_sensor_data_canvas)
        self.depth_sensor_data_canvas.ax.set_ylabel('Depth')

    def init_infrared_piston_datashow_frame_panel(self):
        """
        初始化活塞高度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.infrared_piston_canvas_frame = QtWidgets.QFrame()
        self.infrared_piston_canvas_frame.setObjectName('infrared_piston_canvas_frame')
        self.infrared_piston_canvas_layout = QtWidgets.QVBoxLayout()
        self.infrared_piston_canvas_frame.setLayout(self.infrared_piston_canvas_layout)

        self.infrared_piston_datashow_layout.addWidget(self.infrared_piston_canvas_frame, 0, 0, 10, 12)

        self.infrared_piston_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.infrared_piston_sensor_data_canvas,self.infrared_piston_canvas_frame)
        self.infrared_piston_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.infrared_piston_canvas_layout.addWidget(self.infrared_piston_sensor_data_canvas)
        self.infrared_piston_sensor_data_canvas.ax.set_ylabel('Piston cm')

    def init_infrared_longitudinal_datashow_frame_panel(self):
        """
        初始化纵滑距离信息显示区面板
        :return:
        """

        # 图像显示部分
        self.infrared_longitudinal_canvas_frame = QtWidgets.QFrame()
        self.infrared_longitudinal_canvas_frame.setObjectName('infrared_longitudinal_canvas_frame')
        self.infrared_longitudinal_canvas_layout = QtWidgets.QVBoxLayout()
        self.infrared_longitudinal_canvas_frame.setLayout(self.infrared_longitudinal_canvas_layout)

        self.infrared_longitudinal_datashow_layout.addWidget(self.infrared_longitudinal_canvas_frame, 0, 0, 10, 12)

        self.infrared_longitudinal_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.infrared_longitudinal_sensor_data_canvas,self.infrared_longitudinal_canvas_frame)
        self.infrared_longitudinal_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.infrared_longitudinal_canvas_layout.addWidget(self.infrared_longitudinal_sensor_data_canvas)
        self.infrared_longitudinal_sensor_data_canvas.ax.set_ylabel('Logitudinal cm')