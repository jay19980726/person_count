# coding:utf-8
import socket
import sys
import threading

import cv2
import numpy as np
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices,  QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout,  QLabel, QVBoxLayout
from qfluentwidgets import (NavigationItemPosition, MessageBox, MSFluentWindow,
                            SubtitleLabel, setFont, ComboBox,
                            SwitchButton,
                            )
from qfluentwidgets import FluentIcon as FIF
from MVSCam import MVSCam
from util import yolo_result, yolo_result2




server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8888))  # 绑定本地地址和端口
server_socket.listen(1)  # 开始监听，最多允许一个连接

print(f"等待客户端连接...")
client_socket, client_address = server_socket.accept()  # 是一个阻塞方法，它会一直等待，直到有客户端尝试连接到服务端
print(f"客户端已连接：{client_address}")




class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))




class Window(MSFluentWindow):

    def __init__(self):
        super().__init__()

        """
        # 开关按钮
        """
        self.on_off = None    # 当前开关组件的状态
        self.resize(160, 80)  # 开关大小
        self.switchButton = SwitchButton(parent=self)
        self.switchButton.move(400, 60)   # 开关位置
        self.switchButton.checkedChanged.connect(self.onCheckedChanged)



        """
        # 界面下拉框设置
        """
        self.comboBox = ComboBox(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.comboBox.setPlaceholderText("选择产品")
        items = ['OCR', '缺陷', 'logo',]
        self.comboBox.addItems(items)
        self.comboBox.setCurrentIndex(-1)
        # 获取下拉窗的选定方案文本
        self.comboBox.currentTextChanged.connect(self.onComboBoxTextChanged)
        # 下拉框的大小
        self.resize(500, 500)
        # 设置下拉框的位置
        self.comboBox.move(150, 60)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignCenter)
        self.setStyleSheet('Demo{background:white}')
        # 当前下拉菜单的方案
        self.fangan = ""



        """
        # 桌面控件设置
        """
        self.homeInterface = Widget('Home Interface', self)
        self.appInterface = Widget('Application Interface', self)
        self.videoInterface = Widget('Video Interface', self)
        self.libraryInterface = Widget('library Interface', self)

        self.image_label = QLabel(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)

        self.initNavigation()
        self.initWindow()


        # 初始化调用线程做yolo检测
        self.th = threading.Thread(target=self.predict)
        self.th.start()

        # 退出线程事件
        self.should_exit = False


    # 子线程关闭触发  (关闭界面同时关闭检测线程)
    def closeEvent(self, event):
        self.should_exit = True
        # 等待线程结束
        self.th.join()

        sys.exit()  # 关闭整个应用程序


    # 下拉框的文本
    def onComboBoxTextChanged(self, text):
        self.fangan = text
        print("Selected:", text)


    # 按钮状态
    def onCheckedChanged(self, isChecked: bool):
        text = 'On-检测状态' if isChecked else 'Off-关闭状态'
        self.on_off = isChecked   # 当前按钮的状态 True，False
        self.switchButton.setText(text)
        # 根据按钮状态启用或禁用下拉菜单
        self.comboBox.setEnabled(not isChecked)


    # yolo模型检测方法
    def predict(self):
        cam = MVSCam(devinfo="00K34756368")
        ret = cam.open(0)
        while not self.should_exit:
            if client_socket.recv(1024) == b"1":

                im = cam.getFrame()
                if im is None:
                    print('get none')
                    im = np.zeros([100, 100, 3], dtype=np.uint8)


                # 下拉框判断选择哪个模型检测
                if self.fangan == "缺陷" and self.on_off:
                    # YOLO
                    cls_name_list, conf, yolo_result_img = yolo_result.yolo_predict(im)
                    print("缺陷检测启动")

                elif self.fangan == "OCR" and self.on_off:
                    # YOLO
                    cls_name_list, conf, yolo_result_img = yolo_result2.yolo_predict(im)

                elif self.fangan == "logo" and self.on_off:
                    # YOLO
                    cls_name_list, conf, yolo_result_img = yolo_result3.yolo_predict(im)

                else:
                    print("请选择方案")
                    yolo_result_img = im


                # 将图像从BGR格式转换为RGB格式
                img_rgb = cv2.cvtColor(yolo_result_img, cv2.COLOR_BGR2RGB)
                h, w, ch = im.shape
                bytes_per_line = ch * w

                # 从图像数据创建QImage  用来显示在QT
                qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

                # 使用新图像更新标签
                self.image_label.setPixmap(QPixmap(qimg))
                self.image_label.setScaledContents(True)  # 图像自适应大小
                self.image_label.setGeometry(100, 100, 800, 650)

        # 关闭相机
        cam.stop()



    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.appInterface, FIF.APPLICATION, '应用')
        self.addSubInterface(self.videoInterface, FIF.VIDEO, '视频')

        self.addSubInterface(self.libraryInterface, FIF.BOOK_SHELF, '库', FIF.LIBRARY_FILL, NavigationItemPosition.BOTTOM)
        self.navigationInterface.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='帮助',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())



    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)


    def showMessageBox(self):
        w = MessageBox(
            '支持作者🥰',
            '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')

        if w.exec():
            QDesktopServices.openUrl(QUrl(""))



if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    w = Window()
    # w.showFullScreen()
    w.show()

    app.exec_()
