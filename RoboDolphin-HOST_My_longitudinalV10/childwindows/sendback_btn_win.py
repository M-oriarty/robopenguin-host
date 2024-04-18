import os
import sys
import struct
import datetime
from PyQt5 import QtCore,QtGui,QtWidgets
import childwindows.analysis_btn_win # 解析数据窗口

class SendbackBtnWin(QtWidgets.QWidget):
    _signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(SendbackBtnWin, self).__init__(parent)
        self.filename = None # 数据文件的名字
        self.init_ui()

        self.ABW = childwindows.analysis_btn_win.AnalysisBtnWin()
        self.analysis_button.clicked.connect(self.ABW.handle_click)
        

    def init_ui(self):
        # 窗口设置
        self.setFixedSize(560, 110)  # 设置窗体大小
        self.setWindowTitle('回传数据——设置文件名')  # 设置窗口标题

        # 控件初始化
        self.filename_label = QtWidgets.QLabel('文件名：')
        self.filename_editor = QtWidgets.QLineEdit()
        self.save_button = QtWidgets.QPushButton('回传')
        self.analysis_button = QtWidgets.QPushButton('解析')

        # 布局
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.filename_label, 0, 0, 1, 2, QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.filename_editor, 1, 0, 1, 2)
        self.main_layout.addWidget(self.save_button, 1, 2, 1, 1)
        self.main_layout.addWidget(self.analysis_button, 1, 3, 1, 1)

        # 链接控件
        self.save_button.clicked.connect(self.sendback)

        # 给定预设
        #这里需要说明由于下位机软件中文件存储的操作时文件名只能是英文所以这里做如下假设
        #'0'--'a','1'--'b','2'--'c','3'--'d','4'--'e','5'--'f','6'--'g','7'--'h','8'--'i','9'--'j','_'--'k'
        #还有由于月份最大12，所以单个字母即可；小时只有24小时，所以单个字母即可
        #有两个地方需要修改，一个是点save建更新下推荐的时间，第二个是按照上面的编码把数字编码为英文字母

    def sendback(self):
        filename = self.filename_editor.text()
        if(len(filename)==0 or len(filename)>21):
            self.filename_editor.setText('字符串需大于0，小于21位英文字符，需以.txt结尾')
            return
        idx = filename.find('.txt')
        a = len(filename)
        if(idx == -1 or idx != len(filename)-4):
            self.filename_editor.setText('字符串需大于0，小于21位英文字符，需以.txt结尾')
            return
        self._signal.emit(filename)
        # self.filename_editor.setText('回传中，请耐心等待
    
    def set_lineeditor_text(self, str):
        self.filename_editor.setText(str)

    def handle_click(self):
        now_time = datetime.datetime.now()
        month_code = now_time.month
        month_code0 = chr(month_code+97)#月份单字母
        day_code = str(now_time.day).zfill(2)
        day_code0 = chr(ord(day_code[0])+49)
        day_code1 = chr(ord(day_code[1])+49)#日双字母
        hour_code = now_time.hour
        hour_code0 = chr(hour_code+97)#小时单字母
        time_code = str(now_time.minute).zfill(2)
        time_code0 = chr(ord(time_code[0])+49)
        time_code1 = chr(ord(time_code[1])+49)#分钟双字母
        second_code = str(now_time.second).zfill(2)
        second_code0 = chr(ord(second_code[0])+49)
        second_code1 = chr(ord(second_code[1])+49)#秒双字母
        filename = '/SijieLi/'+month_code0+day_code0+day_code1+hour_code0+time_code0+time_code1+second_code0+second_code1+'.txt'
        self.filename_editor.setText(filename)
        if not self.isVisible():
            self.show()


    def handle_close(self):
        self.close()
        self.ABW.handle_close