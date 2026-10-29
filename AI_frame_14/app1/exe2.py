# coding:utf-8
"""
TCP/ip 通讯
包含两级管理员登录
参数修改子界面
URL
"""
import datetime
import queue
import sys
import threading
import socket
import time

import cv2
import numpy as np
from PyQt5.QtCore import  QUrl, pyqtSignal
from PyQt5.QtGui import QIcon, QDesktopServices, QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QTextEdit

from qfluentwidgets import (MessageBox, MSFluentWindow,
                            SubtitleLabel, setFont, ComboBox,
                            SwitchButton, PushButton, FluentWindow
                            )
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import QCoreApplication

from VM_client.VM_tcp import *
from util.auto_remove_Imgfile import *
from util.conf_write_read import *
from QT.QT_son_set_admin import *
from QT.QT_password import CustomMessageBox
from tool.yolo_dispose import yolo_predict1
from tool.cam_connect import cam_connect


# 初始化NG、OK、总数
ng_count = 0
ok_count = 0
total_count = 0

#  OK NG 开关
OKorNG = ""


"""
加载配置文件
"""

# 创建 YAML 实例
yaml = YAML()
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.load(file)
    return config


my_yaml = load_config("arges.yaml")


def my_time():
    now = datetime.datetime.now()  # 获取当前时间信息（包括年、月、日、时、分、秒
    # print(f"{now.year}.{now.month}.{now.day}.{now.hour}.{now.minute}.{now.second}")
    time_day = f"{now.year}_{now.month}_{now.day}"  # 年月日
    time_second = f"{now.second}"  #秒
    return time_second







# # tcp ip 通讯-----服务端
# if my_yaml["message"][0]:
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((my_yaml["tcpip"]["ip"], int(my_yaml["tcpip"]["port"])))  # 绑定本地地址和端口
#     server_socket.listen(1)  # 开始监听，最多允许一个连接
#
#     print(f"等待客户端连接...")
#     client_socket, client_address = server_socket.accept()  # 是一个阻塞方法，它会一直等待，直到有客户端尝试连接到服务端
#     print(f"客户端已连接：{client_address}")


# # tcp ip 通讯-----客户端

# def client_PLC(add_text):
connet = False
while connet:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((my_yaml["tcpip"]["ip"], int(my_yaml["tcpip"]["port"])))
        print("连接PLC客户端成功!")
        connet = False
    except Exception as e:
        print("链接PLC服务的出错：", e)

            # continue
            # return client

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect((my_yaml["tcpip"]["ip"], int(my_yaml["tcpip"]["port"])))
# print("连接PLC客户端成功!")


"""
自定义的小部件类 Widget
这个类继承自 QFrame，QFrame 是 Qt 框架中常用的容器类，可以用来创建具有边框、标题栏等的窗口部件。
"""
class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        # self.setStyleSheet("background-color: gray;")  # 颜色
        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', ' '))








"""
主窗口
"""
class Window(MSFluentWindow):
    # 定义一个信号，不带参数
    updateTextSignal = pyqtSignal(str)

    def __init__(self, arges_yaml):
        super().__init__()
        self.arges_yaml = arges_yaml  # 参数配置文件
        " 1.初始化读取置信度参数,读取上一次修改的参数配置"
        self.conf_value = read_value()
        # 字符型转浮点型
        self.conf_value = float(self.conf_value)

        " 2.初始化读取W,H参数,读取上一次修改的参数配置"
        self.W_value, self.H_value = read_WH()
        # 字符型转整型
        self.W_value, self.H_value = int(float(self.W_value)), int(float(self.H_value))


        """
        # 开关按钮
        """
        self.on_off = None  # 当前开关组件的状态
        self.resize(250, 80)  # 开关大小
        self.switchButton = SwitchButton(parent=self)
        self.switchButton.move(600, 100)  # 开关位置
        self.switchButton.checkedChanged.connect(self.onCheckedChanged)
        self.should_exit_event = threading.Event()  # threading.Event() 返回一个新的 Event 对象，这个对象可以用来在多个线程之间进行事件通信。
        # 开关按钮文字说明
        label_on_off = QLabel(self)
        label_on_off.setText("检测开关")
        label_on_off.setAlignment(Qt.AlignCenter)  # 文本居中对齐
        font = QFont("Arial", 14)  # 字体 Arial，大小 20
        label_on_off.setFont(font)
        label_on_off.setStyleSheet('color: black;')  # 设置文本颜色
        label_on_off.setGeometry(480, 120, 300, 70)  # 设置位置和大小

        """
        # 界面下拉框设置
        """
        self.comboBox = ComboBox(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.comboBox.setPlaceholderText("选择产品")
        self.comboBox.setGeometry(400, 100, 100, 60)  # 按钮位置大小
        self.comboBox.setStyleSheet('background-color: #4CAF50; color: white; font-size: 16px;')  # 设置按钮颜色、文字颜色、字体大小
        items = ['产品1']
        self.comboBox.addItems(items)
        self.comboBox.setCurrentIndex(-1)  # 将下拉框的当前索引设置为 -1，即没有选中任何项。
        self.comboBox.currentTextChanged.connect(self.onComboBoxTextChanged)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignCenter)
        self.setStyleSheet('Demo{background:white}')
        self.fangan = ""

        """
        权限选择 操作员，管理员
        """
        self.comboBoxlogin = ComboBox(self)
        self.hBoxLayoutlogin = QHBoxLayout(self)
        self.comboBoxlogin.setPlaceholderText("权限")
        self.comboBoxlogin.setGeometry(1400, 100, 100, 50)  # 按钮位置大小
        self.comboBoxlogin.setStyleSheet('background-color: #4CAF50; color: white; font-size: 12px;')  # 设置按钮颜色、文字颜色、字体大小
        qx_items = ['操作员', '管理员']
        self.comboBoxlogin.addItems(qx_items)
        self.comboBoxlogin.setCurrentIndex(-1)  # 将下拉框的当前索引设置为 -1，即没有选中任何项。
        self.comboBoxlogin.currentTextChanged.connect(self.onComboBoxTextChanged_qx)
        self.hBoxLayoutlogin.addWidget(self.comboBoxlogin, 0, Qt.AlignCenter)
        self.setStyleSheet('Demo{background:white}')
        self.qx = ""


        # 线程退出事件
        self.should_exit = False

        """
        LOGO显示
        """
        self.label_logo = QLabel(self)  # 创建logo图像标签
        self.label_logo.setGeometry(70, 50, 200, 170)  # 位置大小 x, y, width, height
        logo_img = cv2.imread(my_yaml["logoimg"][0])
        logo_img = cv2.resize(logo_img, (200, 170))  # 图像缩小显示
        # 将图像从BGR格式转换为RGB格式
        logo_img_rgb = cv2.cvtColor(logo_img, cv2.COLOR_BGR2RGB)
        h, w, ch = logo_img_rgb.shape
        bytes_per_line = ch * w
        # 从图像数据创建QImage  用来显示在QT
        qimg = QImage(logo_img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # 使用新图像更新标签
        self.label_logo.setPixmap(QPixmap(qimg))

        """
        # 桌面控件设置
        """
        self.homeInterface = Widget(' ', self)
        # self.appInterface = Widget('image_data', self)
        # self.videoInterface = Widget(' ', self)
        # self.libraryInterface = Widget(' ', self)

        "图像显示"
        self.image_label_list = []
        # 6个相机的label
        # 显示图像1---创建一个QLabel小部件用于
        self.image_label = QLabel(self)
        self.image_label.setGeometry(130, 330, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        # 图像组件添加到组件列表
        self.image_label_list.append(self.image_label)

        # 显示图像2
        self.image_label2 = QLabel(self)
        self.image_label2.setGeometry(590, 330, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label2.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label2)
        # 图像组件添加到组件列表
        self.image_label_list.append(self.image_label2)

        # 显示图像3
        self.image_label3 = QLabel(self)
        self.image_label3.setGeometry(1060, 330, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label3.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label3)
        # 图像组件添加到组件列表
        self.image_label_list.append(self.image_label3)

        # 显示图像4
        self.image_label4 = QLabel(self)
        self.image_label4.setGeometry(130, 680, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label4.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label4)
        # 图像组件添加到组件列表
        self.image_label_list.append(self.image_label4)


        # 显示图像5
        self.image_label5 = QLabel(self)
        self.image_label5.setGeometry(590, 680, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label5.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label5)
        # 图像组件添加到组件列表
        self.image_label_list.append(self.image_label5)


        # 显示图像6
        self.image_label6 = QLabel(self)
        self.image_label6.setGeometry(1060, 680, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label6.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label6)
        # 图像组件添加到组件列表
        self.image_label_list.append(self.image_label6)



        # "初始化导航界面（假设该方法设置了窗口的导航元素）"
        # self.initNavigation()
        # # 初始化窗口设置（假设该方法设置了窗口的大小、图标和标题）
        # self.initWindow()


        # "报警复位按钮"
        # 添软复位报警按钮
        self.button_fw = PushButton('', self)
        self.button_fw.setGeometry(800, 100, 100, 60)  # 位置大小
        self.button_fw.setFont(QFont('Arial', 12))  # 字体
        self.button_fw.setStyleSheet('background-color: #4CAF50; color: white;')  # 设置按钮的背景颜色和文字颜色
        self.button_fw.clicked.connect(self.baojinfuwei)

        # 添计数清零按钮
        self.button_fw = PushButton('', self)
        self.button_fw.setGeometry(1000, 100, 100, 60)  # 位置大小
        self.button_fw.setFont(QFont('Arial', 12))  # 字体
        self.button_fw.setStyleSheet('background-color: #4CAF50; color: white;')  # 设置按钮的背景颜色和文字颜色
        self.button_fw.clicked.connect(self.zero)

        # 登录按钮设置
        self.button_login = QPushButton('登录', self)
        self.button_login.setGeometry(1400, 150, 100, 30)  # 位置大小  (1200, 150, 100, 30)
        self.button_login.setFont(QFont('Arial', 12))  # 字体
        self.button_login.setStyleSheet('background-color: #4CAF50; color: white;')  # 设置按钮的背景颜色和文字颜色
        self.button_login.clicked.connect(self.show_login_dialog)


        # 打开url 按钮设置
        self.button_password = PushButton('', self)
        self.button_password.setGeometry(1200, 100, 100, 60)  # 位置大小  (1400, 100, 100, 60)
        self.button_password.setFont(QFont('Arial', 12))  # 字体
        self.button_password.setStyleSheet('background-color: #4CAF50; color: white;')  # 设置按钮的背景颜色和文字颜色
        self.button_password.clicked.connect(self.show_password_son)


        "1.创建 QLabel 组件，图像区域"
        label_img = QLabel(self)
        label_img.setText("图像区域:")
        label_img.setAlignment(Qt.AlignCenter)  # 文本居中对齐
        font = QFont("Arial", 16)  # 字体 Arial，大小 20
        label_img.setFont(font)
        label_img.setStyleSheet('color: blue;')  # 设置文本颜色
        label_img.setGeometry(90, 240, 100, 50)  # 设置位置和大小
        "2.创建 QLabel 组件，消息区域"
        label_data = QLabel(self)
        label_data.setText("消息区域:")
        label_data.setAlignment(Qt.AlignCenter)  # 文本居中对齐
        font = QFont("Arial", 16)  # 字体 Arial，大小 20
        label_data.setFont(font)
        label_data.setStyleSheet('color: blue;')  # 设置文本颜色
        label_data.setGeometry(1550, 240, 100, 50)  # 设置位置和大小
        "3.创建 QLabel 组件，功能区域"
        label_function = QLabel(self)
        label_function.setText("功  能  区:")
        label_function.setAlignment(Qt.AlignCenter)  # 文本居中对齐
        font = QFont("Arial", 16)  # 字体 Arial，大小 20
        label_function.setFont(font)
        label_function.setStyleSheet('color: blue;')  # 设置文本颜色
        label_function.setGeometry(170, 50, 300, 70)  # 设置位置和大小


        arges_label = QLabel('参数设置', self)
        arges_label.setGeometry(1400, 60, 120, 30)  # (1700, 30, 80, 80)
        arges_label.setStyleSheet('font-size: 20px; color: green;')
        # --------------------------------------------
        # 创建统计数据区域
        # --------------------------------------------
        # # 创建标签用于显示NG、OK、总数和准确率，并将它们添加到窗口中
        # ng_label = QLabel('NG数:', self)
        # self.ng_display = QLabel('0', self)
        # ok_label = QLabel('OK数:', self)
        # self.ok_display = QLabel('0', self)
        # total_label = QLabel('总数:', self)
        # self.total_display = QLabel('0', self)
        # accuracy_label = QLabel('准确率:', self)
        # self.accuracy_display = QLabel('0%', self)
        #
        # # 设置标签的位置
        # ng_label.setGeometry(1700, 40, 80, 80)  # (1700, 30, 80, 80)
        # self.ng_display.setGeometry(1750, 40, 80, 80)  # (1800, 30, 80, 80)
        # ok_label.setGeometry(1700, 70, 80, 80)
        # self.ok_display.setGeometry(1750, 70, 80, 80)
        # total_label.setGeometry(1700, 100, 80, 80)
        # self.total_display.setGeometry(1750, 100, 80, 80)
        # accuracy_label.setGeometry(1700, 130, 80, 80)
        # self.accuracy_display.setGeometry(1770, 130, 80, 80)
        #
        # # 设置标签样式
        # ng_label.setStyleSheet('font-size: 18px;')
        # self.ng_display.setStyleSheet('font-size: 18px; color: red;')
        # ok_label.setStyleSheet('font-size: 18px;')
        # self.ok_display.setStyleSheet('font-size: 18px; color: green;')
        # total_label.setStyleSheet('font-size: 18px;')
        # self.total_display.setStyleSheet('font-size: 18px; color: blue;')
        # accuracy_label.setStyleSheet('font-size: 18px;')
        # self.accuracy_display.setStyleSheet('font-size: 18px; color: purple;')

        # "相机编号显示"
        cam1_label = QLabel('相机1', self)
        cam1_label.setGeometry(130, 280, 160, 60)
        cam1_label.setStyleSheet('font-size: 18px;')
        cam2_label = QLabel('相机2', self)
        cam2_label.setGeometry(590, 280, 160, 60)
        cam2_label.setStyleSheet('font-size: 18px;')
        cam3_label = QLabel('相机3', self)
        cam3_label.setGeometry(1060, 280, 160, 60)
        cam3_label.setStyleSheet('font-size: 18px;')
        cam4_label = QLabel('相机4', self)
        cam4_label.setGeometry(130, 630, 160, 60)
        cam4_label.setStyleSheet('font-size: 18px;')
        cam5_label = QLabel('相机5', self)
        cam5_label.setGeometry(590, 630, 160, 60)
        cam5_label.setStyleSheet('font-size: 18px;')
        cam6_label = QLabel('相机6', self)
        cam6_label.setGeometry(1060, 630, 160, 60)
        cam6_label.setStyleSheet('font-size: 18px;')


        "画线"
        self.button1 = PushButton('', self)
        self.button1.setGeometry(75, 230, 1820, 5)  # 位置大小
        self.button1.setFont(QFont('Arial', 12))  # 字体
        self.button1.setStyleSheet('background-color: green; color: green;')  # 设置按钮的背景颜色和文字颜色

        "画线2"
        self.button2 = PushButton('', self)
        self.button2.setGeometry(1500, 230, 5, 850)  # 位置大小
        self.button2.setFont(QFont('Arial', 12))  # 字体
        self.button2.setStyleSheet('background-color: green; color: green;')  # 设置按钮的背景颜色和文字颜色


        # 初始化添加文本框组件
        self.initUI()

        "初始化导航界面（假设该方法设置了窗口的导航元素）"
        self.initNavigation()
        # 初始化窗口设置（假设该方法设置了窗口的大小、图标和标题）
        self.initWindow()



        # 连接相机
        self.cam1, self.cam_name1, self.cam2, self.cam_name2, self.cam3, self.cam_name3, self.cam4, self.cam_name4,  self.cam5, self.cam_name5, self.cam6, self.cam_name6 = cam_connect()

        cam_name_list = [self.cam_name1, self.cam_name2, self.cam_name3, self.cam_name4, self.cam_name5, self.cam_name6]

        """ 第一次运行判断文件夹是否需要删除"""
        for cam_name in cam_name_list:
            # 删除OK文件夹
            auto_remove_OK_th = threading.Thread(target=auto_remove_OK, args=(5, str(cam_name)))
            auto_remove_OK_th.start()
            auto_remove_OK_th.join()
            # 删除NG文件夹
            auto_remove_NG_th = threading.Thread(target=auto_remove_NG, args=(5, str(cam_name)))
            auto_remove_NG_th.start()
            auto_remove_NG_th.join()



        # 创建VM服务端
        self.vm_client_socket, self.vm_client_address, self.vm_server_socket = VM_socket()

        # VM循环链接条件
        self.start_counte_VM = True



        # """读取次数---打开主线程，检测函数"""
        # with open("counter.txt", "a+") as count_file:
        #     count_file.seek(0)  # a+ 指针是在末尾，需要将指正移到开头
        #     r_data = count_file.readline()  # 读取txt
        #     print(len(r_data))
        #     count_file.write("1")  # 再次写入

        # try:
        #     # if len(r_data) < int(self.arges_yaml["counter_number"][0]):  # counter number
        #         self.th = threading.Thread(target=self.predict)
        #         self.th.start()
        #         print("-------------start predict-----------------")
        #     else:
        #         print("-------------stop predict------------------")
        #
        # except Exception as e:
        #     print(e)


        try:
            self.th = threading.Thread(target=self.predict)
            self.th.start()
            print("-------------start predict-----------------")

        except Exception as e:
            print("检测主线th程异常", e)



        # PLC客户端
        # client = client_PLC()




    "消息文本框显示"
    def initUI(self):
        # 创建文本框，使用QTextEdit来显示多行文本
        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(1550, 300, 330, 730)  # 设置文本框位置和大小
        # 设置样式表，添加边框
        self.textEdit.setStyleSheet("background-color: white;border: 2px solid black;")
        # # 设置初始内容
        self.textEdit.append("DATA:\n")
        # 连接信号 updateTextSignal 到槽函数 updateTextSlot
        self.updateTextSignal.connect(self.updateTextSlot)



    " 该方法用于向信号发射新的文本内容，每次调用 addText 方法时，会发射 updateTextSignal 信号，并将 new_text 作为参数传递给连接的槽函数 updateTextSlot。"

    def addText(self, new_text):
        # 发射 updateTextSignal 信号，传递新文本 new_text
        self.updateTextSignal.emit(new_text)



    "  槽函数"

    def updateTextSlot(self, new_text):
        # 在文本框中追加新文本
        self.textEdit.append(new_text)

    # 1111111111111111111



    """
    权限登录按钮 设置参数
    """
    def show_login_dialog(self):

        if self.qx == "操作员":
            # 创建密码输入对话框
            password_dialog = PasswordDialog(self)  # 登录子界面

            # 如果用户点击了对话框中的确定按钮
            if password_dialog.exec():
                # 获取用户输入的密码
                password = password_dialog.get_password()
                # 检查输入的密码是否与配置文件中的密码匹配
                if password == self.arges_yaml["conf-password"][0]:
                    # 显示缺陷参数设置子界面
                    dialog = DefectParameterDialog_person(self.conf_value, self.W_value, self.H_value)  # 参数设置子界面
                    if dialog.exec():
                        # 获取并更新新的缺陷参数值 conf , W, H
                        self.conf_value, self.W_value, self.H_value = dialog.get_conf_WH_value()
                        # 将更新后的conf参数值写入到文件中
                        write_value(self.conf_value)
                        print(f"缺陷置信度设置成功：{self.conf_value}")
                        # 将更新后的 W,H 阈值参数值写入到文件中
                        write_WH(f"{int(self.W_value)},{int(self.H_value)}")
                        print(f"缺陷 W 设置成功：{self.W_value}, 缺陷 H 设置成功：{self.H_value}")

                else:
                    # 如果密码不匹配，打印密码错误提示
                    print("密码错误")


        if self.qx == "管理员":
            # 创建密码输入对话框
            password_dialog = PasswordDialog(self)  # 登录子界面

            # 如果用户点击了对话框中的确定按钮
            if password_dialog.exec():
                # 获取用户输入的密码
                password = password_dialog.get_password()
                # 检查输入的密码是否与配置文件中的密码匹配
                if password == self.arges_yaml["conf-password"][1]:
                    # 显示缺陷参数设置子界面
                    dialog = DefectParameterDialog_super_person(self.conf_value, self.W_value, self.H_value)  # 参数设置子界面
                    if dialog.exec():
                        # 获取并更新新的缺陷参数值 conf , W, H
                        self.conf_value, self.W_value, self.H_value = dialog.get_conf_WH_value()
                        # 将更新后的conf参数值写入到文件中
                        write_value(self.conf_value)
                        print(f"缺陷置信度设置成功：{self.conf_value}")
                        # 将更新后的 W,H 阈值参数值写入到文件中
                        write_WH(f"{int(self.W_value)},{int(self.H_value)}")
                        print(f"缺陷 W 设置成功：{self.W_value}, 缺陷 H 设置成功：{self.H_value}")

                else:
                    # 如果密码不匹配，打印密码错误提示
                    print("密码错误")




    """
    password ++方法
    """
    def show_password_son(self):
        # 显示自定义消息框
        w = CustomMessageBox(self)
        if w.exec():
            # 如果消息框返回接受状态，打印输入的URL
            print(w.urlLineEdit.text())
            # if w.urlLineEdit.text() == self.arges_yaml["password"][0]:
            #     # 打开文件并使用 'w' 模式，即写入模式，会清空文件内容
            #     with open("counter.txt", 'w') as file:
            #         pass  # 使用 pass 来保持文件内容为空
            #         # 初始化QT子线程线程做yolo检测
            #         self.th = threading.Thread(target=self.predict)
            #         self.th.start()
            #         print("-------------start predict-----------")



    # 报警软复位；给PLC发送2
    def baojinfuwei(self):
        # ... 通信发送等其他部分 ...
        # data = '\x00'  # 点击复位按钮后给PLC 发00
        # client_socket.send(data.encode('UTF-8'))
        pass


    # 计数清零按钮
    def zero(self):
        # global ng_count
        # global ok_count
        # global total_count
        # ng_count = 0
        # ok_count = 0
        # total_count = 0
        pass

    # -------------------------
    # 更新OK，NG数据
    def update_counts(self, OKorNG):
        # global ok_count
        # global ng_count
        # global total_count
        # # 判断是ON 还是 NG
        # if OKorNG == "OK":
        #     ok_count = ok_count + 1
        # elif OKorNG == "NG":
        #     ng_count = ng_count + 1
        #
        # # 总数+1
        # total_count = total_count + 1
        # # 计算准确率
        # accuracy = 0 if total_count == 0 else (ok_count / total_count) * 100
        #
        # # 更新显示的文本
        # self.ng_display.setText(str(ng_count))
        # self.ok_display.setText(str(ok_count))
        # self.total_display.setText(str(total_count))
        # self.accuracy_display.setText(f'{accuracy:.2f}%')
        pass

    # 关闭按钮的方法
    def closeEvent(self, event):

        try:

            # 结束循环
            self.should_exit = True

            # 关闭循环链接VM
            self.start_counte_VM = False  # 停止循环读取

            # 等待所有检测线程结束
            if self.th1_on_off:
                self.th1.join()
                print("1111111")
            if self.th2_on_off:
                self.th2.join()
                print("222222")
            if self.th3_on_off:
                self.th3.join()
                print("333333")
            if self.th4_on_off:
                self.th4.join()
                print("444444")
            if self.th5_on_off:
                self.th5.join()
                print("555555")
            if self.th6_on_off:
                self.th6.join()
                print("666666")


            if self.vm_read_on_off:
                self.th_VM_read.join()
                print("VMVMVMVMVMVM")

            # 等待VM心跳线程结束
            self.vm_heartbeat_th.join()

            # 关闭VM服务端
            self.vm_client_socket.close()
            self.vm_server_socket.close()
            print("VM--socket-close")

            # 等待PLC心跳线程结束
            self.heartbeat_th.join()
            print("心跳线程关闭完成")


            """判断PLC有无发送触发-如没有发送触发则线程会阻塞在接受PLC消息哪里，所以就需要先断开PLC连接
            """
            if self.PLC_trigger:   # PLC 有触发，按顺序等待线程结束再断开PLC

                # 等待主线程结束
                self.th.join()
                print("所有线程关闭已完成")

                # 关闭PLC 客户端
                if my_yaml["message"][0]:
                    client.close()

            else:                    # PLC 没有发送触发，直接断开PLC链接，
                # 关闭PLC 客户端
                if my_yaml["message"][0]:
                    client.close()

                # 等待主线程结束
                self.th.join()
                print("所有线程关闭已完成")


            # 关闭相机
            self.cam1.close()
            self.cam1.close()
            self.cam2.close()
            self.cam3.close()
            self.cam4.close()
            self.cam5.close()
            self.cam6.close()
            print("相机关闭成功")

            sys.exit()

        except Exception as e:
            print("关闭异常：", e)
            # 关闭相机
            self.cam1.close()
            self.cam2.close()
            self.cam3.close()
            self.cam4.close()
            self.cam5.close()
            self.cam6.close()
            print("相机关闭成功")
            # raise SystemExit(0)  # 退出程序，返回状态码0
            sys.exit()


    """
    # 下拉框的文本
    """
    def onComboBoxTextChanged(self, text):
        try:
            self.fangan = text
            print("Selected:", text)
        except Exception as e:
            print(e)

    def onComboBoxTextChanged_qx(self, text):
        try:
            self.qx = text
            print("Selected:", text)
        except Exception as e:
            print(e)

    """
    # 开始按钮状态
    """

    def onCheckedChanged(self, isChecked: bool):
        try:
            text = 'On-检测状态' if isChecked else 'Off-关闭状态'
            self.on_off = isChecked  # 当前按钮的状态 True，False
            self.switchButton.setText(text)
            # 根据按钮状态启用或禁用下拉菜单
            self.comboBox.setEnabled(not isChecked)
        except Exception as e:
            print(e)



    # 给PLC发送心跳 方法--- 1秒切换一次
    def heartbeat(self, client):

        while not self.should_exit:
            try:
                # 心跳，监听有无断开链接
                second = my_time()
                if float(second) % 2 == 0:
                    heartbeat = "A"
                else:
                    heartbeat = "B"
                client.sendall(heartbeat.encode("utf-8"))
                # print("发送PLC心跳正常:", heartbeat)
                time.sleep(1)
            except Exception as e:
                print("发送PLC心跳异常--重连")
                # self.addText(f"发送PLC心跳异常--重连---{e}")
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((my_yaml["tcpip"]["ip"], int(my_yaml["tcpip"]["port"])))
                print("重连PLC成功")
                # self.addText("重连PLC成功")
                continue
            # finally:
            #     if self.should_exit:
            #         return


    # 给vm客户端发送心跳--断开重连
    def vm_heartbeat(self):
        self.vm_server_socket.settimeout(1)  # 设置超时为1秒

        while not self.should_exit:
            try:
                ## VM心跳
                self.vm_client_socket.send("VM".encode("utf-8"))
                time.sleep(1)
            except Exception as e:
                # 重连异常
                try:
                    print("与VM客户端链接出错-----正在重连：", e)
                    # self.addText(f"与VM客户端链接出错-----正在重连：{e}")
                    self.vm_client_socket, self.vm_client_address = self.vm_server_socket.accept()
                    print("与VM客户端重连成功---", self.vm_client_address)
                    # self.addText(f"与VM客户端重连成功--- {self.vm_client_address}")
                except socket.timeout:
                    # 如果重新连接时也超时
                    print("重连时 accept() 超时，继续重试...")
                    continue
                continue



    # ---开始调用检测算法
    def predict(self):
        global client, data
        # 创建一个队列用于在线程之间共享数据
        result_queue_AI_1 = queue.Queue()
        result_queue_AI_2 = queue.Queue()
        result_queue_AI_3 = queue.Queue()
        result_queue_AI_4 = queue.Queue()
        result_queue_AI_5 = queue.Queue()
        result_queue_AI_6 = queue.Queue()
        result_queue_VM = queue.Queue()

        # 开启PLC心跳线程
        self.heartbeat_th = threading.Thread(target=self.heartbeat, args=(client, ))
        self.heartbeat_th.start()

        # 开启VM线程
        self.vm_heartbeat_th = threading.Thread(target=self.vm_heartbeat)
        self.vm_heartbeat_th.start()

        while not self.should_exit:
            # 开启创建标志
            self.vm_read_on_off = False
            self.th1_on_off = False
            self.th2_on_off = False
            self.th3_on_off = False
            self.th4_on_off = False
            self.th5_on_off = False
            self.th6_on_off = False
            # PLC 有无触发（阻塞读取触发-如果PLC一直没触发在关闭软件时就需要要先断开连接再等待线程结束）
            self.PLC_trigger = False


            # # 下拉框判断选择哪个模型检测
            # if self.fangan == "产品1" and self.on_off:

            try:
                # 读取拍照信号
                data = client.recv(6)   # 6个字节   b'\x01\x01\x01\x01\x01\x00'
                print("接收到PLC的触发指令", data)
                self.PLC_trigger = True
            except Exception as e:
                client.close()
                print("与PLC链接出错", e)
                print("尝试重连----")
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((my_yaml["tcpip"]["ip"], int(my_yaml["tcpip"]["port"])))
                print("重连PLC成功")
                continue



            try:

                self.th1 = threading.Thread(target=yolo_predict1, args=(
                self.cam1, self.cam_name1, client, self.addText, self.conf_value, self.W_value, self.H_value,
                self.image_label_list, self.vm_client_socket, self.vm_client_address, self.vm_server_socket,
                result_queue_AI_1))

                self.th2 = threading.Thread(target=yolo_predict1, args=(
                self.cam2, self.cam_name2, client, self.addText, self.conf_value, self.W_value, self.H_value,
                self.image_label_list, self.vm_client_socket, self.vm_client_address, self.vm_server_socket,
                result_queue_AI_2))

                self.th3 = threading.Thread(target=yolo_predict1, args=(
                self.cam3, self.cam_name3, client, self.addText, self.conf_value, self.W_value, self.H_value,
                self.image_label_list, self.vm_client_socket, self.vm_client_address, self.vm_server_socket,
                result_queue_AI_3))

                self.th4 = threading.Thread(target=yolo_predict1, args=(
                self.cam4, self.cam_name4, client, self.addText, self.conf_value, self.W_value, self.H_value,
                self.image_label_list, self.vm_client_socket, self.vm_client_address, self.vm_server_socket,
                result_queue_AI_4))

                self.th5 = threading.Thread(target=yolo_predict1, args=(
                self.cam5, self.cam_name5, client, self.addText, self.conf_value, self.W_value, self.H_value,
                self.image_label_list, self.vm_client_socket, self.vm_client_address, self.vm_server_socket,
                result_queue_AI_5))

                self.th6 = threading.Thread(target=yolo_predict1, args=(
                self.cam6, self.cam_name6, client, self.addText, self.conf_value, self.W_value, self.H_value,
                self.image_label_list, self.vm_client_socket, self.vm_client_address, self.vm_server_socket,
                result_queue_AI_6))

                # # 通讯触发
                if data[0] == int(self.arges_yaml["recv"][0]):
                    self.th1.start()
                    self.th1_on_off=True
                if data[0] == int(self.arges_yaml["recv"][0]):
                    self.th2.start()
                    self.th2_on_off = True
                if data[0] == int(self.arges_yaml["recv"][0]):
                    self.th3.start()
                    self.th3_on_off = True
                if data[0] == int(self.arges_yaml["recv"][0]):
                    self.th4.start()
                    self.th4_on_off = True
                if data[0] == int(self.arges_yaml["recv"][0]):
                    self.th5.start()
                    self.th5_on_off = True
                if data[0] == int(self.arges_yaml["recv"][0]):
                    self.th6.start()
                    self.th6_on_off = True


                if self.th1_on_off:
                    self.th1.join()
                if self.th2_on_off:
                    self.th2.join()
                if self.th3_on_off:
                    self.th3.join()
                if self.th4_on_off:
                    self.th4.join()
                if self.th5_on_off:
                    self.th5.join()
                if self.th6_on_off:
                    self.th6.join()

                # # 1.开启写入VM信息线程
                # th_VM_write = threading.Thread(target=VM.VM_write)
                # # 开启VM线程
                # th_VM_write.start()
                # # 等待线程结束
                # th_VM_write.join()


                # 判断有没有关闭循环
                if not self.should_exit and data[0] == 1:
                    # 2.开启读取VM信息线程
                    self.th_VM_read = threading.Thread(target=VM_read, args=(self.vm_client_socket, self.vm_client_address, self.vm_server_socket, result_queue_VM))
                    # 开启VM线程
                    self.th_VM_read.start()
                    self.vm_read_on_off = True
                    # 等待线程结束
                    self.th_VM_read.join()
                    #
                    # print(result_queue_AI_1.get(), "-----队列1")
                    # print(result_queue_AI_2.get(), "-----队列2")
                    # print(result_queue_AI_3.get(), "-----队列3")
                    # print(result_queue_AI_4.get(), "-----队列4")
                    # print(result_queue_AI_5.get(), "-----队列5")
                    # print(result_queue_AI_6.get(), "-----队列6")

                    """
                    # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
                    # 从队列中获取AI缺陷结果
                    # 调用将AI检测结果与VM结果整合后发送给PLC的方法
                    """
                    data_plc = sum_data_VM_AI(result_queue_VM, result_queue_AI_1, result_queue_AI_2, result_queue_AI_3,
                                              result_queue_AI_4, result_queue_AI_5, result_queue_AI_6)
                    print("合并后的数据：", data_plc)
                    # self.addText(f"合并后的数据：, {data_plc}")

                    run = True
                    while run:
                        # 发送给PLC检测结果
                        try:
                            client.sendall(data_plc.encode('utf-8'))
                            print("数据发送给PLC成功")
                            # self.addText("数据发送给PLC成功")
                            run = False
                        except Exception as e:
                            print("数据发送PLC异常---")
                            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            client.connect((my_yaml["tcpip"]["ip"], int(my_yaml["tcpip"]["port"])))
                            continue
            #
            except Exception as e:
                print('6个检测线程异常', e)
                # self.addText(f"6个检测线程异常' {e} ")


            # else:
            #     print("请选择方案并打开检测")
            #     # continue
            #     pass

        # self.cam1.stop()
        # 关闭心跳线程
        # self.heartbeat_th.join()





    def initNavigation(self):
        # 将主页界面添加为子界面
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        # 设置当前导航项为主页界面
        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())


    # 用于初始化窗口的外观和属性
    def initWindow(self):
        self.resize(2000, 1040)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('视觉检测系统')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


    def showMessageBox(self):
        w = MessageBox(
            ' ',
            ' ',
            self
        )
        w.yesButton.setText('')
        w.cancelButton.setText('')

        if w.exec():
            QDesktopServices.openUrl(QUrl(""))




# if __name__ == '__main__':
#     second = my_time()
#     print(float(second) % 2)
#     print(second)