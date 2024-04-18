import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLineEdit

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_recording = False
        self.file_path = ""

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle('Record and Save Data')

        self.textbox = QLineEdit(self)
        self.textbox.setGeometry(50, 50, 200, 30)

        self.start_button = QPushButton('Start', self)
        self.start_button.setGeometry(50, 100, 100, 30)
        self.start_button.clicked.connect(self.start_recording)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setGeometry(160, 100, 100, 30)
        self.stop_button.clicked.connect(self.stop_recording)

        self.save_button = QPushButton('Save Data', self)
        self.save_button.setGeometry(270, 50, 100, 80)
        self.save_button.clicked.connect(self.save_data)

    def start_recording(self):
        self.is_recording = True

    def stop_recording(self):
        self.is_recording = False

    def save_data(self):
        if self.is_recording:
            if self.file_path:
                data_to_save = "Your data to be saved.\n"
                with open(self.file_path, "a") as file:
                    file.write(data_to_save)
            else:
                file_name = self.textbox.text() + ".txt"
                self.file_path = os.path.join(os.getcwd(), file_name)

                data_to_save = "Your data to be saved.\n"
                with open(self.file_path, "w") as file:
                    file.write(data_to_save)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
