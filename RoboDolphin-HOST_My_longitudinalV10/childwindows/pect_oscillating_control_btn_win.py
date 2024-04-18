import os
import sys
from PyQt5 import QtCore,QtGui,QtWidgets

### 子界面类
class PectOscillatingControlBtnWin(QtWidgets.QWidget):
    _signal = QtCore.pyqtSignal(str)

    ## 初始化函数
    def __init__(self, parent=None):
        super(PectOscillatingControlBtnWin, self).__init__(parent)
        self.init_ui()

    ## 初始化串口UI界面
    def init_ui(self):

        # 窗口设置
        self.setFixedSize(780, 308)  # 设置窗体大小
        self.setWindowTitle('胸鳍拍动控制')  # 设置窗口标题

        # 布局
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.button_height = 30
        
        # 定义UI界面，这里由用户自己定义
        self.pect_fixed_label = QtWidgets.QLabel('胸鳍运动参数设置')
        self.pect_fixed_label.setObjectName('pect_fixed_label')
        self.main_layout.addWidget(self.pect_fixed_label, 0, 0, 1, 3, QtCore.Qt.AlignCenter)

        self.lpect_amp_label = QtWidgets.QLabel('左胸鳍幅度')
        self.lpect_amp_label.setObjectName('lpect_amp_label')
        self.lpect_amp_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.lpect_amp_label, 1, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_amp_edit = QtWidgets.QLineEdit()
        self.lpect_amp_edit.setFixedSize(100, self.button_height)
        self.lpect_amp_edit.setPlaceholderText('0~20')
        double_validator1 = QtGui.QDoubleValidator()
        double_validator1.setRange(0, 20)
        double_validator1.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator1.setDecimals(3)
        self.lpect_amp_edit.setValidator(double_validator1)
        self.main_layout.addWidget(self.lpect_amp_edit, 1, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_amp_button = QtWidgets.QPushButton('写入')
        self.main_layout.addWidget(self.lpect_amp_button, 1, 2, 1, 1, QtCore.Qt.AlignCenter)
        self.lpect_amp_button.setObjectName("SET_LPECT_AMP")
        self.lpect_amp_button.setFixedSize(60, self.button_height)



        self.lpect_freq_label = QtWidgets.QLabel('左胸鳍频率')
        self.lpect_freq_label.setObjectName('lpect_freq_label')
        self.lpect_freq_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.lpect_freq_label, 2, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_freq_edit = QtWidgets.QLineEdit()
        self.lpect_freq_edit.setFixedSize(100, self.button_height)
        self.lpect_freq_edit.setPlaceholderText('0~3.0')
        double_validator2 = QtGui.QDoubleValidator()
        double_validator2.setRange(0, 3.0)
        double_validator2.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator2.setDecimals(2)
        self.lpect_freq_edit.setValidator(double_validator2)
        self.main_layout.addWidget(self.lpect_freq_edit, 2, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_freq_button = QtWidgets.QPushButton('写入')
        self.main_layout.addWidget(self.lpect_freq_button, 2, 2, 1, 1, QtCore.Qt.AlignCenter)
        self.lpect_freq_button.setObjectName("SET_LPECT_FREQ")
        self.lpect_freq_button.setFixedSize(60, self.button_height)



        self.lpect_offset_label = QtWidgets.QLabel('左胸鳍偏移')
        self.lpect_offset_label.setObjectName('lpect_offset_label')
        self.lpect_offset_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.lpect_offset_label, 3, 0, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_offset_edit = QtWidgets.QLineEdit()
        self.lpect_offset_edit.setFixedSize(100, self.button_height)
        self.lpect_offset_edit.setPlaceholderText('-40~40')
        double_validator3 = QtGui.QDoubleValidator()
        double_validator3.setRange(-40, 40)
        double_validator3.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator3.setDecimals(2)
        self.lpect_offset_edit.setValidator(double_validator3)
        self.main_layout.addWidget(self.lpect_offset_edit, 3, 1, 1, 1, QtCore.Qt.AlignCenter)

        self.lpect_offset_button = QtWidgets.QPushButton('写入')
        self.main_layout.addWidget(self.lpect_offset_button, 3, 2, 1, 1, QtCore.Qt.AlignCenter)
        self.lpect_offset_button.setObjectName("SET_LPECT_OFFSET")
        self.lpect_offset_button.setFixedSize(60, self.button_height)








        self.rpect_amp_label = QtWidgets.QLabel('右胸鳍幅度')
        self.rpect_amp_label.setObjectName('rpect_amp_label')
        self.rpect_amp_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.rpect_amp_label, 1, 3, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_amp_edit = QtWidgets.QLineEdit()
        self.rpect_amp_edit.setFixedSize(100, self.button_height)
        self.rpect_amp_edit.setPlaceholderText('0~20')
        double_validator4 = QtGui.QDoubleValidator()
        double_validator4.setRange(0, 20)
        double_validator4.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator4.setDecimals(3)
        self.rpect_amp_edit.setValidator(double_validator4)
        self.main_layout.addWidget(self.rpect_amp_edit, 1, 4, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_amp_button = QtWidgets.QPushButton('写入')
        self.main_layout.addWidget(self.rpect_amp_button, 1, 5, 1, 1, QtCore.Qt.AlignCenter)
        self.rpect_amp_button.setObjectName("SET_RPECT_AMP")
        self.rpect_amp_button.setFixedSize(60, self.button_height)



        self.rpect_freq_label = QtWidgets.QLabel('右胸鳍频率')
        self.rpect_freq_label.setObjectName('rpect_freq_label')
        self.rpect_freq_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.rpect_freq_label, 2, 3, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_freq_edit = QtWidgets.QLineEdit()
        self.rpect_freq_edit.setFixedSize(100, self.button_height)
        self.rpect_freq_edit.setPlaceholderText('0~3.0')
        double_validator5 = QtGui.QDoubleValidator()
        double_validator5.setRange(0, 3.0)
        double_validator5.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator5.setDecimals(2)
        self.rpect_freq_edit.setValidator(double_validator5)
        self.main_layout.addWidget(self.rpect_freq_edit, 2, 4, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_freq_button = QtWidgets.QPushButton('写入')
        self.main_layout.addWidget(self.rpect_freq_button, 2, 5, 1, 1, QtCore.Qt.AlignCenter)
        self.rpect_freq_button.setObjectName("SET_RPECT_FREQ")
        self.rpect_freq_button.setFixedSize(60, self.button_height)



        self.rpect_offset_label = QtWidgets.QLabel('右胸鳍偏移')
        self.rpect_offset_label.setObjectName('rpect_offset_label')
        self.rpect_offset_label.setFixedSize(60, self.button_height)
        self.main_layout.addWidget(self.rpect_offset_label, 3, 3, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_offset_edit = QtWidgets.QLineEdit()
        self.rpect_offset_edit.setFixedSize(100, self.button_height)
        self.rpect_offset_edit.setPlaceholderText('-40~40')
        double_validator6 = QtGui.QDoubleValidator()
        double_validator6.setRange(-40, 40)
        double_validator6.setNotation(QtGui.QDoubleValidator.StandardNotation)
        double_validator6.setDecimals(2)
        self.rpect_offset_edit.setValidator(double_validator6)
        self.main_layout.addWidget(self.rpect_offset_edit, 3, 4, 1, 1, QtCore.Qt.AlignCenter)

        self.rpect_offset_button = QtWidgets.QPushButton('写入')
        self.main_layout.addWidget(self.rpect_offset_button, 3, 5, 1, 1, QtCore.Qt.AlignCenter)
        self.rpect_offset_button.setObjectName("SET_RPECT_OFFSET")
        self.rpect_offset_button.setFixedSize(60, self.button_height)

    def handle_click(self):
        if not self.isVisible():
            self.show()


    def handle_close(self):
        self.close()
