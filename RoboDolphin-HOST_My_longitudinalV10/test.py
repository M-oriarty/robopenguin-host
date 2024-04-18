import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5 import QtGui

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.slider = QSlider(Qt.Horizontal)  # 创建水平滑动条
        self.slider.setMinimum(3)  # 设置滑动条的最小值
        self.slider.setMaximum(11)  # 设置滑动条的最大值
        self.slider.setValue(7)  # 设置滑动条的初始位置

        self.line_edit = QLineEdit()
        self.line_edit.setValidator(QtGui.QIntValidator(3, 11))  # 设置输入框只能输入3-11的整数
        self.line_edit.setText(str(self.slider.value()))  # 设置输入框的初始值为滑动条的初始位置

        self.button = QPushButton("Update")  # 创建按钮

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)  # 将按钮添加到布局中

        self.setLayout(layout)

        # 连接按钮的点击事件到槽函数
        self.button.clicked.connect(self.updateSlider)

        # 连接滑动条的值改变事件到槽函数
        self.slider.valueChanged.connect(self.updateLineEdit)

        # 连接输入框的编辑完成事件到槽函数
        self.line_edit.editingFinished.connect(self.updateSlider)

    def updateSlider(self):
        text = self.line_edit.text()
        value = int(text) if text.isdigit() else self.slider.value()
        self.slider.setValue(value)
        self.line_edit.setText(str(self.slider.value()))

    def updateLineEdit(self, value):
        self.line_edit.setText(str(value))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec_())
