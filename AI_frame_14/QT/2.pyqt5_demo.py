import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class AlarmApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口大小为屏幕大小
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        self.setGeometry(0, 0, screen_rect.width(), screen_rect.height())

        # 创建水平布局来容纳所有按钮
        button_layout = QHBoxLayout()

        # 创建开始检测按钮
        self.start_button = QPushButton('开始检测', self)
        self.start_button.setFixedSize(100, 50)
        self.start_button.clicked.connect(self.start_detection)
        button_layout.addWidget(self.start_button)

        # 创建报警按钮，与其他按钮大小一样
        self.alarm_button = QPushButton('关闭报警', self)
        self.alarm_button.setFixedSize(100, 50)
        self.alarm_button.clicked.connect(self.toggle_alarm)
        self.alarm_button.setStyleSheet("background-color: green")
        button_layout.addWidget(self.alarm_button)

        # 创建计数清零按钮
        self.reset_button = QPushButton('计数清零', self)
        self.reset_button.setFixedSize(100, 50)
        self.reset_button.clicked.connect(self.reset_count)
        button_layout.addWidget(self.reset_button)


        "报价复位按钮"
        self.zero_button = QPushButton("报警复位",self)  # 构造函数的第一个参数是按钮上显示的文本，第二个参数是按钮的父级部件。在这里，按钮的父级部件是 self，即 MainWindow
        self.zero_button.setGeometry(1500, 30, 130, 100)  # 设置按钮的位置和大小
        self.zero_button.setStyleSheet("background-color: red; color: white; font-size: 28px;")  # 设置按钮的背景颜色，和文本颜色，字体大小
        self.zero_button.clicked.connect(self.baojinfuwei)  # 这一行代码是将按钮的点击事件（clicked 信号）连接到 self.close_application 方法。当按钮被点击时，与此信号连接的方法将被调用


        # 将按钮布局添加到主垂直布局中
        layout = QVBoxLayout()
        layout.addLayout(button_layout)

        # 创建显示图片的区域
        self.image_label = QLabel()
        pixmap = QPixmap('your_image_path.jpg')
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label, 1, Qt.AlignHCenter)

        self.setLayout(layout)
        self.setWindowTitle('报警界面')
        self.show()



    # 报警软复位；给PLC发送2
    def baojinfuwei(self):
        # ... 通信发送等其他部分 ...
        # data = '\x00'  # 点击复位按钮后给PLC 发00
        # client_socket.send(data.encode('UTF-8'))
        pass



    def toggle_alarm(self):
        if self.alarm_button.text() == '关闭报警':
            self.alarm_button.setText('打开报警')
            self.alarm_button.setStyleSheet("background-color: red")
        else:
            self.alarm_button.setText('关闭报警')
            self.alarm_button.setStyleSheet("background-color: green")


    def start_detection(self):
        # 添加开始检测按钮的处理逻辑
        pass

    def reset_count(self):
        # 添加计数清零按钮的处理逻辑
        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AlarmApp()
    sys.exit(app.exec_())
