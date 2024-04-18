import os
import sys
from PyQt5 import QtCore,QtGui,QtWidgets

### 子界面类
class IdentifySwimparaControlBtnWin(QtWidgets.QWidget):
    _signal = QtCore.pyqtSignal(str)

    ## 初始化函数
    def __init__(self, parent=None):
        super(IdentifySwimparaControlBtnWin, self).__init__(parent)
        self.init_ui()

    ## 初始化串口UI界面
    def init_ui(self):

        # 窗口设置
        self.setFixedSize(780, 500)  # 设置窗体大小
        self.setWindowTitle('参数辨识游动参数控制')  # 设置窗口标题

        # 布局
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.button_height = 30
        
        # 定义UI界面，这里由用户自己定义
        self.identify_freq_fixed_label = QtWidgets.QLabel('频率变化函数设置')
        self.identify_freq_fixed_label.setObjectName('identify_freq_fixed_label')
        self.main_layout.addWidget(self.identify_freq_fixed_label, 0, 0, 1, 3, QtCore.Qt.AlignCenter)



        self.identify_freq_amp_label = QtWidgets.QLabel('变化幅度')
        self.identify_freq_amp_label.setObjectName('identify_freq_amp_label')
        self.identify_freq_amp_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.identify_freq_amp_label, 1, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.identify_freq_amp_edit = QtWidgets.QLineEdit()
        self.identify_freq_amp_edit.setFixedSize(100, self.button_height)
        self.identify_freq_amp_edit.setPlaceholderText('0~2')
        double_validator1 = QtGui.QDoubleValidator()
        double_validator1.setRange(0, 20)
        double_validator1.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator1.setDecimals(3)
        self.identify_freq_amp_edit.setValidator(double_validator1)
        self.main_layout.addWidget(self.identify_freq_amp_edit, 1, 1, 1, 1, QtCore.Qt.AlignCenter)



        self.identify_freq_freq_label = QtWidgets.QLabel('变化速度')
        self.identify_freq_freq_label.setObjectName('identify_freq_freq_label')
        self.identify_freq_freq_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.identify_freq_freq_label, 2, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.identify_freq_freq_edit = QtWidgets.QLineEdit()
        self.identify_freq_freq_edit.setFixedSize(100, self.button_height)
        self.identify_freq_freq_edit.setPlaceholderText('0~20.0')
        double_validator2 = QtGui.QDoubleValidator()
        double_validator2.setRange(0, 20.0)
        double_validator2.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator2.setDecimals(2)
        self.identify_freq_freq_edit.setValidator(double_validator2)
        self.main_layout.addWidget(self.identify_freq_freq_edit, 2, 1, 1, 1, QtCore.Qt.AlignCenter)



        self.identify_freq_set_button = QtWidgets.QPushButton('设定参数')
        self.main_layout.addWidget(self.identify_freq_set_button, 3, 0, 1, 3, QtCore.Qt.AlignCenter)
        self.identify_freq_set_button.setObjectName("SET_IDENTIFY_CHANGING_FREQ")
        self.identify_freq_set_button.setFixedSize(180, self.button_height)












        self.identify_amp_fixed_label = QtWidgets.QLabel('幅度变化函数设置')
        self.identify_amp_fixed_label.setObjectName('identify_amp_fixed_label')
        self.main_layout.addWidget(self.identify_amp_fixed_label, 0, 3, 1, 3, QtCore.Qt.AlignCenter)



        self.identify_amp_amp_label = QtWidgets.QLabel('变化幅度')
        self.identify_amp_amp_label.setObjectName('identify_amp_amp_label')
        self.identify_amp_amp_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.identify_amp_amp_label, 1, 3, 1, 1, QtCore.Qt.AlignCenter)

        self.identify_amp_amp_edit = QtWidgets.QLineEdit()
        self.identify_amp_amp_edit.setFixedSize(100, self.button_height)
        self.identify_amp_amp_edit.setPlaceholderText('0~20')
        double_validator4 = QtGui.QDoubleValidator()
        double_validator4.setRange(0, 20)
        double_validator4.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator4.setDecimals(3)
        self.identify_amp_amp_edit.setValidator(double_validator4)
        self.main_layout.addWidget(self.identify_amp_amp_edit, 1, 4, 1, 1, QtCore.Qt.AlignCenter)



        self.identify_amp_freq_label = QtWidgets.QLabel('变化速度')
        self.identify_amp_freq_label.setObjectName('identify_amp_freq_label')
        self.identify_amp_freq_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.identify_amp_freq_label, 2, 3, 1, 1, QtCore.Qt.AlignCenter)

        self.identify_amp_freq_edit = QtWidgets.QLineEdit()
        self.identify_amp_freq_edit.setFixedSize(100, self.button_height)
        self.identify_amp_freq_edit.setPlaceholderText('0~20.0')
        double_validator5 = QtGui.QDoubleValidator()
        double_validator5.setRange(0, 20.0)
        double_validator5.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator5.setDecimals(2)
        self.identify_amp_freq_edit.setValidator(double_validator5)
        self.main_layout.addWidget(self.identify_amp_freq_edit, 2, 4, 1, 1, QtCore.Qt.AlignCenter)



        self.identify_amp_set_button = QtWidgets.QPushButton('设定参数')
        self.main_layout.addWidget(self.identify_amp_set_button, 3, 3, 1, 3, QtCore.Qt.AlignCenter)
        self.identify_amp_set_button.setObjectName("SET_IDENTIFY_CHANGING_AMP")
        self.identify_amp_set_button.setFixedSize(180, self.button_height)











        self.identify_offset_fixed_label = QtWidgets.QLabel('偏置变化函数设置')
        self.identify_offset_fixed_label.setObjectName('identify_offset_fixed_label')
        self.main_layout.addWidget(self.identify_offset_fixed_label, 0, 6, 1, 3, QtCore.Qt.AlignCenter)



        self.identify_offset_amp_label = QtWidgets.QLabel('变化幅度')
        self.identify_offset_amp_label.setObjectName('identify_offset_amp_label')
        self.identify_offset_amp_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.identify_offset_amp_label, 1, 6, 1, 1, QtCore.Qt.AlignCenter)

        self.identify_offset_amp_edit = QtWidgets.QLineEdit()
        self.identify_offset_amp_edit.setFixedSize(100, self.button_height)
        self.identify_offset_amp_edit.setPlaceholderText('0~10')
        double_validator4 = QtGui.QDoubleValidator()
        double_validator4.setRange(0, 10)
        double_validator4.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator4.setDecimals(3)
        self.identify_offset_amp_edit.setValidator(double_validator4)
        self.main_layout.addWidget(self.identify_offset_amp_edit, 1, 7, 1, 1, QtCore.Qt.AlignCenter)



        self.identify_offset_freq_label = QtWidgets.QLabel('变化速度')
        self.identify_offset_freq_label.setObjectName('identify_offset_freq_label')
        self.identify_offset_freq_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.identify_offset_freq_label, 2, 6, 1, 1, QtCore.Qt.AlignCenter)

        self.identify_offset_freq_edit = QtWidgets.QLineEdit()
        self.identify_offset_freq_edit.setFixedSize(100, self.button_height)
        self.identify_offset_freq_edit.setPlaceholderText('0~20.0')
        double_validator5 = QtGui.QDoubleValidator()
        double_validator5.setRange(0, 20.0)
        double_validator5.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator5.setDecimals(2)
        self.identify_offset_freq_edit.setValidator(double_validator5)
        self.main_layout.addWidget(self.identify_offset_freq_edit, 2, 7, 1, 1, QtCore.Qt.AlignCenter)



        self.identify_offset_set_button = QtWidgets.QPushButton('设定参数')
        self.main_layout.addWidget(self.identify_offset_set_button, 3, 6, 1, 3, QtCore.Qt.AlignCenter)
        self.identify_offset_set_button.setObjectName("SET_IDENTIFY_CHANGING_OFFSET")
        self.identify_offset_set_button.setFixedSize(180, self.button_height)





    def handle_click(self):
        if not self.isVisible():
            self.show()


    def handle_close(self):
        self.close()
