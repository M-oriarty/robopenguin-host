import os
import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import sensor_data_canvas

### 子界面类
class AHRSShowBtnWin(QtWidgets.QWidget):
    _signal = QtCore.pyqtSignal(str)

    ## 初始化函数
    def __init__(self, parent=None):
        super(AHRSShowBtnWin, self).__init__(parent)
        self.init_ui()

    ## 初始化串口UI界面
    def init_ui(self):

        # 窗口设置
        self.setFixedSize(1900, 1000)  # 设置窗体大小
        self.setWindowTitle('航姿信息曲线显示')  # 设置窗口标题

        # 布局
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        # 传感器数据显示区
        #AHRS_ANGLEX
        self.ahrs_anglex_datashow_frame = QtWidgets.QFrame()
        self.ahrs_anglex_datashow_layout = QtWidgets.QGridLayout()
        self.ahrs_anglex_datashow_frame.setLayout(self.ahrs_anglex_datashow_layout)
        self.ahrs_anglex_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ahrs_anglex_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ahrs_anglex_datashow_frame.setLineWidth(1)
        #AHRS_ANGLEY
        self.ahrs_angley_datashow_frame = QtWidgets.QFrame()
        self.ahrs_angley_datashow_layout = QtWidgets.QGridLayout()
        self.ahrs_angley_datashow_frame.setLayout(self.ahrs_angley_datashow_layout)
        self.ahrs_angley_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ahrs_angley_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ahrs_angley_datashow_frame.setLineWidth(1)
        #AHRS_ANGLEZ
        self.ahrs_anglez_datashow_frame = QtWidgets.QFrame()
        self.ahrs_anglez_datashow_layout = QtWidgets.QGridLayout()
        self.ahrs_anglez_datashow_frame.setLayout(self.ahrs_anglez_datashow_layout)
        self.ahrs_anglez_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ahrs_anglez_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ahrs_anglez_datashow_frame.setLineWidth(1)
        #AHRS_ACCELERATIONX
        self.ahrs_accx_datashow_frame = QtWidgets.QFrame()
        self.ahrs_accx_datashow_layout = QtWidgets.QGridLayout()
        self.ahrs_accx_datashow_frame.setLayout(self.ahrs_accx_datashow_layout)
        self.ahrs_accx_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ahrs_accx_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ahrs_accx_datashow_frame.setLineWidth(1)
        #AHRS_ACCELERATIONY
        self.ahrs_accy_datashow_frame = QtWidgets.QFrame()
        self.ahrs_accy_datashow_layout = QtWidgets.QGridLayout()
        self.ahrs_accy_datashow_frame.setLayout(self.ahrs_accy_datashow_layout)
        self.ahrs_accy_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ahrs_accy_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ahrs_accy_datashow_frame.setLineWidth(1)
        #AHRS_ACCELERATIONZ
        self.ahrs_accz_datashow_frame = QtWidgets.QFrame()
        self.ahrs_accz_datashow_layout = QtWidgets.QGridLayout()
        self.ahrs_accz_datashow_frame.setLayout(self.ahrs_accz_datashow_layout)
        self.ahrs_accz_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ahrs_accz_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ahrs_accz_datashow_frame.setLineWidth(1)
        #AHRS_ANGLESPEEDX
        self.ahrs_anglespeedx_datashow_frame = QtWidgets.QFrame()
        self.ahrs_anglespeedx_datashow_layout = QtWidgets.QGridLayout()
        self.ahrs_anglespeedx_datashow_frame.setLayout(self.ahrs_anglespeedx_datashow_layout)
        self.ahrs_anglespeedx_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ahrs_anglespeedx_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ahrs_anglespeedx_datashow_frame.setLineWidth(1)
        #AHRS_ANGLESPEEDY
        self.ahrs_anglespeedy_datashow_frame = QtWidgets.QFrame()
        self.ahrs_anglespeedy_datashow_layout = QtWidgets.QGridLayout()
        self.ahrs_anglespeedy_datashow_frame.setLayout(self.ahrs_anglespeedy_datashow_layout)
        self.ahrs_anglespeedy_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ahrs_anglespeedy_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ahrs_anglespeedy_datashow_frame.setLineWidth(1)
        #AHRS_ANGLESPEEDZ
        self.ahrs_anglespeedz_datashow_frame = QtWidgets.QFrame()
        self.ahrs_anglespeedz_datashow_layout = QtWidgets.QGridLayout()
        self.ahrs_anglespeedz_datashow_frame.setLayout(self.ahrs_anglespeedz_datashow_layout)
        self.ahrs_anglespeedz_datashow_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ahrs_anglespeedz_datashow_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ahrs_anglespeedz_datashow_frame.setLineWidth(1)

        self.main_layout.addWidget(self.ahrs_anglex_datashow_frame, 0, 0, 2, 2)
        self.main_layout.addWidget(self.ahrs_angley_datashow_frame, 0, 2, 2, 2)
        self.main_layout.addWidget(self.ahrs_anglez_datashow_frame, 0, 4, 2, 2)
        self.main_layout.addWidget(self.ahrs_accx_datashow_frame, 2, 0, 2, 2)
        self.main_layout.addWidget(self.ahrs_accy_datashow_frame, 2, 2, 2, 2)
        self.main_layout.addWidget(self.ahrs_accz_datashow_frame, 2, 4, 2, 2)
        self.main_layout.addWidget(self.ahrs_anglespeedx_datashow_frame, 4, 0, 2, 2)
        self.main_layout.addWidget(self.ahrs_anglespeedy_datashow_frame, 4, 2, 2, 2)
        self.main_layout.addWidget(self.ahrs_anglespeedz_datashow_frame, 4, 4, 2, 2)

        self.init_ahrs_anglex_datashow_frame_panel()
        self.init_ahrs_angley_datashow_frame_panel()
        self.init_ahrs_anglez_datashow_frame_panel()
        self.init_ahrs_accx_datashow_frame_panel()
        self.init_ahrs_accy_datashow_frame_panel()
        self.init_ahrs_accz_datashow_frame_panel()
        self.init_ahrs_anglespeedx_datashow_frame_panel()
        self.init_ahrs_anglespeedy_datashow_frame_panel()
        self.init_ahrs_anglespeedz_datashow_frame_panel()
        
        # 定义UI界面，这里由用户自己定义
        self.AHRS_Show_start_button = QtWidgets.QPushButton('开启显示')
        self.main_layout.addWidget(self.AHRS_Show_start_button, 6, 2, 1, 1, QtCore.Qt.AlignCenter)
        # 这里需要给按钮设置一个名字，因为之后需要将这个按钮与一个函数链接起来，那个函数会根据这个名字给下位机发送指令
        # 所以这个按钮的名字，应该作为一条指令添加到RFLink的Command中
        self.AHRS_Show_start_button.setObjectName("SET_AHRS_SHOW_STAR") 

        self.AHRS_Show_stop_button = QtWidgets.QPushButton('关闭显示')
        self.main_layout.addWidget(self.AHRS_Show_stop_button, 6, 3, 1, 1, QtCore.Qt.AlignCenter)
        self.AHRS_Show_stop_button.setObjectName("SET_AHRS_SHOW_STOP")

    def handle_click(self):
        if not self.isVisible():
            self.show()


    def handle_close(self):
        self.close()

    def init_ahrs_anglex_datashow_frame_panel(self):
        """
        初始化AHRS的x轴向角度（横滚）信息显示区面板
        :return:
        """

        # 图像显示部分
        self.ahrs_anglex_canvas_frame = QtWidgets.QFrame()
        self.ahrs_anglex_canvas_frame.setObjectName('ahrs_anglex_canvas_frame')
        self.ahrs_anglex_canvas_layout = QtWidgets.QVBoxLayout()
        self.ahrs_anglex_canvas_frame.setLayout(self.ahrs_anglex_canvas_layout)

        self.ahrs_anglex_datashow_layout.addWidget(self.ahrs_anglex_canvas_frame, 0, 0, 10, 12)

        self.ahrs_anglex_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.ahrs_anglex_sensor_data_canvas,self.ahrs_anglex_canvas_frame)
        self.ahrs_anglex_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.ahrs_anglex_canvas_layout.addWidget(self.ahrs_anglex_sensor_data_canvas)
        self.ahrs_anglex_sensor_data_canvas.ax.set_ylabel('AHRS Thetax')

    def init_ahrs_angley_datashow_frame_panel(self):
        """
        初始化AHRS的y轴向角度（俯仰）信息显示区面板
        :return:
        """

        # 图像显示部分
        self.ahrs_angley_canvas_frame = QtWidgets.QFrame()
        self.ahrs_angley_canvas_frame.setObjectName('ahrs_angley_canvas_frame')
        self.ahrs_angley_canvas_layout = QtWidgets.QVBoxLayout()
        self.ahrs_angley_canvas_frame.setLayout(self.ahrs_angley_canvas_layout)

        self.ahrs_angley_datashow_layout.addWidget(self.ahrs_angley_canvas_frame, 0, 0, 10, 12)

        self.ahrs_angley_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.ahrs_angley_sensor_data_canvas,self.ahrs_angley_canvas_frame)
        self.ahrs_angley_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.ahrs_angley_canvas_layout.addWidget(self.ahrs_angley_sensor_data_canvas)
        self.ahrs_angley_sensor_data_canvas.ax.set_ylabel('AHRS Thetay')

    def init_ahrs_anglez_datashow_frame_panel(self):
        """
        初始化AHRS的z轴向角度（偏航）信息显示区面板
        :return:
        """

        # 图像显示部分
        self.ahrs_anglez_canvas_frame = QtWidgets.QFrame()
        self.ahrs_anglez_canvas_frame.setObjectName('ahrs_anglez_canvas_frame')
        self.ahrs_anglez_canvas_layout = QtWidgets.QVBoxLayout()
        self.ahrs_anglez_canvas_frame.setLayout(self.ahrs_anglez_canvas_layout)

        self.ahrs_anglez_datashow_layout.addWidget(self.ahrs_anglez_canvas_frame, 0, 0, 10, 12)

        self.ahrs_anglez_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.ahrs_anglez_sensor_data_canvas,self.ahrs_anglez_canvas_frame)
        self.ahrs_anglez_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.ahrs_anglez_canvas_layout.addWidget(self.ahrs_anglez_sensor_data_canvas)
        self.ahrs_anglez_sensor_data_canvas.ax.set_ylabel('AHRS Thetaz')

    def init_ahrs_accx_datashow_frame_panel(self):
        """
        初始化AHRS的x轴向加速度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.ahrs_accx_canvas_frame = QtWidgets.QFrame()
        self.ahrs_accx_canvas_frame.setObjectName('ahrs_accx_canvas_frame')
        self.ahrs_accx_canvas_layout = QtWidgets.QVBoxLayout()
        self.ahrs_accx_canvas_frame.setLayout(self.ahrs_accx_canvas_layout)

        self.ahrs_accx_datashow_layout.addWidget(self.ahrs_accx_canvas_frame, 0, 0, 10, 12)

        self.ahrs_accx_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.ahrs_accx_sensor_data_canvas,self.ahrs_accx_canvas_frame)
        self.ahrs_accx_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.ahrs_accx_canvas_layout.addWidget(self.ahrs_accx_sensor_data_canvas)
        self.ahrs_accx_sensor_data_canvas.ax.set_ylabel('AHRS ax')

    def init_ahrs_accy_datashow_frame_panel(self):
        """
        初始化AHRS的y轴向加速度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.ahrs_accy_canvas_frame = QtWidgets.QFrame()
        self.ahrs_accy_canvas_frame.setObjectName('ahrs_accy_canvas_frame')
        self.ahrs_accy_canvas_layout = QtWidgets.QVBoxLayout()
        self.ahrs_accy_canvas_frame.setLayout(self.ahrs_accy_canvas_layout)

        self.ahrs_accy_datashow_layout.addWidget(self.ahrs_accy_canvas_frame, 0, 0, 10, 12)

        self.ahrs_accy_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.ahrs_accy_sensor_data_canvas,self.ahrs_accy_canvas_frame)
        self.ahrs_accy_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.ahrs_accy_canvas_layout.addWidget(self.ahrs_accy_sensor_data_canvas)
        self.ahrs_accy_sensor_data_canvas.ax.set_ylabel('AHRS ay')

    def init_ahrs_accz_datashow_frame_panel(self):
        """
        初始化AHRS的z轴向加速度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.ahrs_accz_canvas_frame = QtWidgets.QFrame()
        self.ahrs_accz_canvas_frame.setObjectName('ahrs_accz_canvas_frame')
        self.ahrs_accz_canvas_layout = QtWidgets.QVBoxLayout()
        self.ahrs_accz_canvas_frame.setLayout(self.ahrs_accz_canvas_layout)

        self.ahrs_accz_datashow_layout.addWidget(self.ahrs_accz_canvas_frame, 0, 0, 10, 12)

        self.ahrs_accz_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.ahrs_accz_sensor_data_canvas,self.ahrs_accz_canvas_frame)
        self.ahrs_accz_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.ahrs_accz_canvas_layout.addWidget(self.ahrs_accz_sensor_data_canvas)
        self.ahrs_accz_sensor_data_canvas.ax.set_ylabel('AHRS az')

    def init_ahrs_anglespeedx_datashow_frame_panel(self):
        """
        初始化AHRS的x轴向角速度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.ahrs_anglespeedx_canvas_frame = QtWidgets.QFrame()
        self.ahrs_anglespeedx_canvas_frame.setObjectName('ahrs_anglespeedx_canvas_frame')
        self.ahrs_anglespeedx_canvas_layout = QtWidgets.QVBoxLayout()
        self.ahrs_anglespeedx_canvas_frame.setLayout(self.ahrs_anglespeedx_canvas_layout)

        self.ahrs_anglespeedx_datashow_layout.addWidget(self.ahrs_anglespeedx_canvas_frame, 0, 0, 10, 12)

        self.ahrs_anglespeedx_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.ahrs_anglespeedx_sensor_data_canvas,self.ahrs_anglespeedx_canvas_frame)
        self.ahrs_anglespeedx_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.ahrs_anglespeedx_canvas_layout.addWidget(self.ahrs_anglespeedx_sensor_data_canvas)
        self.ahrs_anglespeedx_sensor_data_canvas.ax.set_ylabel('AHRS wx')

    def init_ahrs_anglespeedy_datashow_frame_panel(self):
        """
        初始化AHRS的y轴向角速度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.ahrs_anglespeedy_canvas_frame = QtWidgets.QFrame()
        self.ahrs_anglespeedy_canvas_frame.setObjectName('ahrs_anglespeedy_canvas_frame')
        self.ahrs_anglespeedy_canvas_layout = QtWidgets.QVBoxLayout()
        self.ahrs_anglespeedy_canvas_frame.setLayout(self.ahrs_anglespeedy_canvas_layout)

        self.ahrs_anglespeedy_datashow_layout.addWidget(self.ahrs_anglespeedy_canvas_frame, 0, 0, 10, 12)

        self.ahrs_anglespeedy_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.ahrs_anglespeedy_sensor_data_canvas,self.ahrs_anglespeedy_canvas_frame)
        self.ahrs_anglespeedy_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.ahrs_anglespeedy_canvas_layout.addWidget(self.ahrs_anglespeedy_sensor_data_canvas)
        self.ahrs_anglespeedy_sensor_data_canvas.ax.set_ylabel('AHRS wy')

    def init_ahrs_anglespeedz_datashow_frame_panel(self):
        """
        初始化AHRS的z轴向角速度信息显示区面板
        :return:
        """

        # 图像显示部分
        self.ahrs_anglespeedz_canvas_frame = QtWidgets.QFrame()
        self.ahrs_anglespeedz_canvas_frame.setObjectName('ahrs_anglespeedz_canvas_frame')
        self.ahrs_anglespeedz_canvas_layout = QtWidgets.QVBoxLayout()
        self.ahrs_anglespeedz_canvas_frame.setLayout(self.ahrs_anglespeedz_canvas_layout)

        self.ahrs_anglespeedz_datashow_layout.addWidget(self.ahrs_anglespeedz_canvas_frame, 0, 0, 10, 12)

        self.ahrs_anglespeedz_sensor_data_canvas = sensor_data_canvas.SensorDataCanvas()
        self.navigationbar = NavigationToolbar(self.ahrs_anglespeedz_sensor_data_canvas,self.ahrs_anglespeedz_canvas_frame)
        self.ahrs_anglespeedz_canvas_layout.addWidget(self.navigationbar, QtCore.Qt.AlignCenter)
        self.ahrs_anglespeedz_canvas_layout.addWidget(self.ahrs_anglespeedz_sensor_data_canvas)
        self.ahrs_anglespeedz_sensor_data_canvas.ax.set_ylabel('AHRS wz')