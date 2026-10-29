# coding:utf-8
"""
modbusTCP 通讯
包含两级管理员登录
参数修改子界面
URL
"""
import sys
import threading
from PyQt5.QtCore import  QUrl, pyqtSignal
from PyQt5.QtGui import QIcon, QDesktopServices, QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QTextEdit

from qfluentwidgets import (MessageBox, MSFluentWindow,
                            SubtitleLabel, setFont, ComboBox,
                            SwitchButton, PushButton,
                            )
from qfluentwidgets import FluentIcon as FIF

from VM_client.VM_tcp import *
# from util import yolo_result
from util.conf_write_read import *
from QT.QT_son_set_admin import *
from QT.QT_password import CustomMessageBox
from tool.cam_connect import *
from tool.yolo_dispose_2 import *
from ruamel.yaml import YAML





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

"""
modbusTcp通信，
连接服务端
"""
from pyModbusTCP.client import ModbusClient

host = my_yaml['modbusTcp_saver']['ip']  # ip
port = my_yaml['modbusTcp_saver']['port']  # 端口

on_off = True  # 循环连接开关

# 创建Modbus TCP客户端并连接服务端
client = ModbusClient(host, port=port)

# 循环链接
while on_off:
    if client.open():
        print("成功连接到Modbus服务器")
        on_off = False

    else:
        print("无法连接到Modbus服务器--正在重连")
        client = ModbusClient(host, port=port)





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
        self.comboBoxlogin.setGeometry(1200, 100, 100, 50)  # 按钮位置大小
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
        logo_img = cv2.imread("./logo_image/ccd.png")
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
        # 6个相机的label
        # 显示图像1---创建一个QLabel小部件用于
        self.image_label = QLabel(self)
        self.image_label.setGeometry(130, 300, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)

        # 显示图像2
        self.image_label2 = QLabel(self)
        self.image_label2.setGeometry(590, 300, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label2.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label2)

        # 显示图像3
        self.image_label2 = QLabel(self)
        self.image_label2.setGeometry(1060, 300, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label2.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label2)

        # 显示图像4
        self.image_label2 = QLabel(self)
        self.image_label2.setGeometry(130, 650, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label2.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label2)

        # 显示图像5
        self.image_label2 = QLabel(self)
        self.image_label2.setGeometry(590, 650, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label2.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label2)

        # 显示图像6
        self.image_label2 = QLabel(self)
        self.image_label2.setGeometry(1060, 650, 400, 300)  # 位置大小
        # 设置边框样式表
        border_style = "background-color: gray;border: 2px solid black;"  # 2px 宽度的蓝色实线边框
        self.image_label2.setStyleSheet(border_style)
        # 创建一个垂直布局管理器，并将image_label添加到其中
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label2)


        "初始化导航界面（假设该方法设置了窗口的导航元素）"
        self.initNavigation()
        # 初始化窗口设置（假设该方法设置了窗口的大小、图标和标题）
        self.initWindow()


        # "报警复位按钮"
        # 添软复位报警按钮
        self.button_fw = PushButton('报警复位', self)
        self.button_fw.setGeometry(800, 100, 100, 60)  # 位置大小
        self.button_fw.setFont(QFont('Arial', 12))  # 字体
        self.button_fw.setStyleSheet('background-color: #4CAF50; color: white;')  # 设置按钮的背景颜色和文字颜色
        self.button_fw.clicked.connect(self.baojinfuwei)

        # 添计数清零按钮
        self.button_fw = PushButton('计数清零', self)
        self.button_fw.setGeometry(1000, 100, 100, 60)  # 位置大小
        self.button_fw.setFont(QFont('Arial', 12))  # 字体
        self.button_fw.setStyleSheet('background-color: #4CAF50; color: white;')  # 设置按钮的背景颜色和文字颜色
        self.button_fw.clicked.connect(self.zero)

        # 登录按钮设置
        self.button_login = QPushButton('登录', self)
        self.button_login.setGeometry(1200, 150, 100, 30)  # 位置大小
        self.button_login.setFont(QFont('Arial', 12))  # 字体
        self.button_login.setStyleSheet('background-color: #4CAF50; color: white;')  # 设置按钮的背景颜色和文字颜色
        self.button_login.clicked.connect(self.show_login_dialog)


        # 打开url 按钮设置
        self.button_password = PushButton('打开 URL', self)
        self.button_password.setGeometry(1400, 100, 100, 60)  # 位置大小
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


        # --------------------------------------------
        # 创建统计数据区域
        # --------------------------------------------
        # 创建标签用于显示NG、OK、总数和准确率，并将它们添加到窗口中
        ng_label = QLabel('NG数:', self)
        self.ng_display = QLabel('0', self)
        ok_label = QLabel('OK数:', self)
        self.ok_display = QLabel('0', self)
        total_label = QLabel('总数:', self)
        self.total_display = QLabel('0', self)
        accuracy_label = QLabel('准确率:', self)
        self.accuracy_display = QLabel('0%', self)

        # 设置标签的位置
        ng_label.setGeometry(1700, 40, 80, 80)  # (1700, 30, 80, 80)
        self.ng_display.setGeometry(1750, 40, 80, 80)  # (1800, 30, 80, 80)
        ok_label.setGeometry(1700, 70, 80, 80)
        self.ok_display.setGeometry(1750, 70, 80, 80)
        total_label.setGeometry(1700, 100, 80, 80)
        self.total_display.setGeometry(1750, 100, 80, 80)
        accuracy_label.setGeometry(1700, 130, 80, 80)
        self.accuracy_display.setGeometry(1770, 130, 80, 80)

        # 设置标签样式
        ng_label.setStyleSheet('font-size: 18px;')
        self.ng_display.setStyleSheet('font-size: 18px; color: red;')
        ok_label.setStyleSheet('font-size: 18px;')
        self.ok_display.setStyleSheet('font-size: 18px; color: green;')
        total_label.setStyleSheet('font-size: 18px;')
        self.total_display.setStyleSheet('font-size: 18px; color: blue;')
        accuracy_label.setStyleSheet('font-size: 18px;')
        self.accuracy_display.setStyleSheet('font-size: 18px; color: purple;')


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


        """读取次数---打开检测函数"""
        with open("counter.txt", "a+") as count_file:
            count_file.seek(0)  # a+ 指针是在末尾，需要将指正移到开头
            r_data = count_file.readline()  # 读取txt
            print(len(r_data))
            count_file.write("1")  # 再次写入

        try:
            if len(r_data) < int(self.arges_yaml["counter_number"][0]):  # counter number
                self.th = threading.Thread(target=self.predict)
                self.th.start()
                print("-------------start predict-----------------")
            else:
                print("-------------stop predict------------------")

        except Exception as e:
            print(e)


        # 初始化添加文本框组件
        self.initUI()

        # 连接相机
        self.cam1, self.cam_name1, self.cam2, self.cam_name2, self.cam3, self.cam_name3, self.cam4, self.cam_name4,  self.cam5, self.cam_name5, self.cam6, self.cam_name6 = cam_connect()

        # 创建VM服务端
        self.vm_client_socket, self.vm_client_address, self.vm_server_socket = VM_socket()


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
            if w.urlLineEdit.text() == self.arges_yaml["password"][0]:
                # 打开文件并使用 'w' 模式，即写入模式，会清空文件内容
                with open("counter.txt", 'w') as file:
                    pass  # 使用 pass 来保持文件内容为空
                    # 初始化QT子线程线程做yolo检测
                    self.th = threading.Thread(target=self.predict)
                    self.th.start()
                    print("-------------start predict-----------")



    # 报警软复位；给PLC发送2
    def baojinfuwei(self):
        # ... 通信发送等其他部分 ...
        # data = '\x00'  # 点击复位按钮后给PLC 发00
        # client_socket.send(data.encode('UTF-8'))
        pass


    # 计数清零按钮
    def zero(self):
        global ng_count
        global ok_count
        global total_count
        ng_count = 0
        ok_count = 0
        total_count = 0
        pass

    # -------------------------
    # 更新OK，NG数据
    def update_counts(self, OKorNG):
        global ok_count
        global ng_count
        global total_count
        # 判断是ON 还是 NG
        if OKorNG == "OK":
            ok_count = ok_count + 1
        elif OKorNG == "NG":
            ng_count = ng_count + 1

        # 总数+1
        total_count = total_count + 1
        # 计算准确率
        accuracy = 0 if total_count == 0 else (ok_count / total_count) * 100

        # 更新显示的文本
        self.ng_display.setText(str(ng_count))
        self.ok_display.setText(str(ok_count))
        self.total_display.setText(str(total_count))
        self.accuracy_display.setText(f'{accuracy:.2f}%')


    # 关闭按钮的方法
    def closeEvent(self, event):
        # 关闭VM服务端
        self.vm_client_socket.close()
        # 关闭PLC 客户端
        if my_yaml["message"][0]:
            client.close()

        # 结束循环
        self.should_exit = True
        # 结束检测线程
        self.th.join()

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



    # """
    # YOLO检测方法及后处理
    # """
    # def yolo_predict1(self, cam):
    #     im = cam.getFrame()
    #     if im is None:
    #         print('get none')
    #         # im = np.zeros([100, 100, 3], dtype=np.uint8)
    #         im = cv2.imread(r"D:\wg\AI_project\24.ball\v8\yolo-xml_to_txt\dataset\VOCdevkit\image\Image_20240605152605063.jpg")
    #
    #     elif im.shape[2] != 3:
    #         im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    #     else:
    #         pass
    #
    #
    #     """
    #     ----检测算法调用
    #     """
    #     print("AI检测工位1启动")
    #     list_xywh = []  # WH通过阈值删选后的目标框
    #     list_cls_name = []  # WH通过阈值删选后的目标类型
    #     xywh, boxs, cls_name_list, conf, yolo_result_img = yolo_result.yolo_predict(im, self.conf_value)
    #
    #     "判断结果"
    #     # ******1.无缺陷  ---ok
    #     if cls_name_list is None:
    #         OKorNG = "OK"
    #         # 文本框显示信息
    #         self.addText(f"检测状态:OK(无缺陷)--检测时间:{time()}")
    #         cv2.putText(yolo_result_img, "OK", (20, 250), 1, 25, (0, 255, 0), 4)
    #         #--- 通讯发送 1：良品
    #         data_ok = 1
    #         client.write_multiple_registers(2, [data_ok])  # 从寄存器 15290 开始写, 写入的值是 1
    #
    #
    #     # *****2.有缺陷 ：缺陷大于阈值 NG， 缺陷小于阈值OK
    #     else:
    #         for idx, vlue in enumerate(xywh):
    #             x, y, w, h = vlue
    #
    #             if w > self.W_value and h > self.H_value:   # WH都大于阈值的留下来
    #                 list_xywh.append((x, y, w, h))
    #                 # xywh 与 cls_name 的索引是对应的，通过xywh索引去拿对应的目标类别
    #                 list_cls_name.append(cls_name_list[idx])
    #
    #
    #         # 再判断阈值 筛选后的list_xywh
    #         # *****无缺陷 OK
    #         if len(list_xywh) == 0:
    #             OKorNG = "OK"
    #             # 文本框显示信息
    #             self.addText(f"检测状态:OK(阈值)--检测时间:{time()}")
    #             cv2.putText(yolo_result_img, "OK", (20, 250), 1, 25, (0, 255, 0), 4)
    #             # 通讯发送 1：良品  ,最大缺陷面积
    #             array_xywh = np.array(xywh)
    #             w_ = array_xywh[:, 2]
    #             h_ = array_xywh[:, 3]
    #             max_w = np.max(w_)
    #             max_h = np.max(h_)
    #             "通讯发送部分"
    #             data_ok = "1"+"—"+str(max_w)+","+str(max_h)
    #             client.write_multiple_registers(3, [data_ok])  # 从寄存器 15290 开始写, 写入的值是 1
    #
    #
    #
    #         # *****有缺陷
    #         else:
    #
    #             # 判断筛选后的缺陷类型  ['1', '2', '3'] 1：凹坑，3：裂痕
    #             if "1" in list_cls_name:
    #                 OKorNG = "NG"
    #                 # 文本框显示信息
    #                 self.addText(f"检测状态:NG--检测时间:{time()}")
    #                 cv2.putText(yolo_result_img, "NG", (20, 250), 1, 25, (0, 0, 255), 4)
    #                 aokeng_idx = []
    #                 aokeng_xywh = []
    #                 aokeng_area = []
    #                 for idx, vlue in enumerate(list_cls_name):
    #                     if vlue == '1':
    #                         aokeng_idx.append(idx)
    #                 # print(aokeng_idx)
    #                 for xywh_idx in aokeng_idx:
    #                     aokeng_xywh.append(list_xywh[xywh_idx])
    #
    #                 # 凹坑面积放入列表
    #                 for aokeng in aokeng_xywh:
    #                     aokeng_area.append(int(aokeng[2])*int(aokeng[3]))  # 面积
    #                 array_aokeng_area = np.array(aokeng_area)  # 转numpy
    #                 max_aokeng_area = np.max(array_aokeng_area)  # 求最大面积
    #
    #                 array_aokeng_xywh = np.array(aokeng_xywh)
    #                 w_aokeng = array_aokeng_xywh[:, 2]
    #                 h_akkeng = array_aokeng_xywh[:, 3]
    #                 max_w = np.max(w_aokeng)
    #                 max_h = np.max(h_akkeng)
    #
    #                 "通讯发送部分"
    #                 # 通讯发送   2：凹坑  最大凹坑 W-H
    #                 # data_ng = "2" + "," + str(max_w) + "," + str(max_h)+"///"
    #                 data_ng = "2" + "-" + str(max_aokeng_area) + "///"
    #                 client.write_multiple_registers(4, [2])  # 从寄存器 15290 开始写, 写入的值是 1
    #
    #
    #
    #             if "2" in list_cls_name:  # 裂痕
    #                 OKorNG = "NG"
    #                 # 文本框显示信息
    #                 self.addText(f"检测状态:NG--检测时间:{time()}")
    #                 cv2.putText(yolo_result_img, "NG", (20, 250), 1, 25, (0, 0, 255), 4)
    #
    #                 liehen_idx = []
    #                 liehen_xywh = []
    #                 liehen_area = []
    #                 for idx, vlue in enumerate(list_cls_name):
    #                     if vlue == '2':
    #                         liehen_idx.append(idx)
    #                 for xywh_idx in liehen_idx:
    #                     liehen_xywh.append((list_xywh[xywh_idx]))
    #
    #                 # 裂痕面积放入列表
    #                 for liehen in liehen_xywh:
    #                     liehen_area.append(int(liehen[2])*int(liehen[3]))
    #
    #                 # 转numpy
    #                 array_liehen_area = np.array(liehen_area)
    #                 max_liehen_area = np.max(array_liehen_area)  # 最大面积
    #
    #                 array_lieheng_xywh = np.array(liehen_xywh)
    #                 w_liehen = array_lieheng_xywh[:, 2]
    #                 h_liehen = array_lieheng_xywh[:, 3]
    #                 max_w2 = np.max(w_liehen)
    #                 max_h2 = np.max(h_liehen)
    #                 "通讯发送部分"
    #                 # 通讯发送 3：裂痕  裂痕最大W-H
    #                 # data_ng2 = "3" + "," + str(max_w2) + "," + str(max_h2)+"///"
    #                 data_ng2 = "3" + "-" + str(max_liehen_area) + "///"
    #                 client.write_multiple_registers(5, [data_ng2])  # 从寄存器 15290 开始写, 写入的值是 1
    #
    #
    #     # 将图像从BGR格式转换为RGB格式
    #     img_rgb = cv2.cvtColor(yolo_result_img, cv2.COLOR_BGR2RGB)
    #     h, w, ch = im.shape
    #     bytes_per_line = ch * w
    #
    #     # 从图像数据创建QImage  用来显示在QT
    #     qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #
    #     # 使用新图像更新标签
    #     self.image_label.setPixmap(QPixmap(qimg))
    #     self.image_label.setScaledContents(True)  # 图像自适应大小
    #     # 使用完后删除数组引用
    #     del im



    # ---开始调用检测算法
    def predict(self):
        global client, data

        while not self.should_exit:

            # 下拉框判断选择哪个模型检测
            if self.fangan == "产品1" and self.on_off:

                # # ---通讯防呆 自动重连
                try:
                    data = client.read_holding_registers(1, 1)   # 从寄存器15288开始读，读1个寄存器
                    # 重连
                    if not data:
                        print("通讯断开连接--正在尝试重连")
                        client = ModbusClient(host, port=port)
                    else:
                        print("通讯已连接")
                except Exception as e:
                    print("1", e)
                    continue



                try:
                    # # 通讯触发
                    if self.arges_yaml["message"][0] and data[0] == self.arges_yaml["recv"][0]:

                        th1 = threading.Thread(target=yolo_predict1, args=(self.cam1, client, self.cam_name1, self.addText, self.conf_value, self.W_value, self.H_value, self.image_label, self.vm_client_socket, self.vm_client_address, self.vm_server_socket))
                        th2 = threading.Thread(target=yolo_predict1, args=(self.cam1, client, self.cam_name2, self.addText, self.conf_value, self.W_value, self.H_value, self.image_label, self.vm_client_socket, self.vm_client_address, self.vm_server_socket))
                        th3 = threading.Thread(target=yolo_predict1, args=(self.cam1, client, self.cam_name3, self.addText, self.conf_value, self.W_value, self.H_value, self.image_label, self.vm_client_socket, self.vm_client_address, self.vm_server_socket))
                        th4 = threading.Thread(target=yolo_predict1, args=(self.cam1, client, self.cam_name4, self.addText, self.conf_value, self.W_value, self.H_value, self.image_label, self.vm_client_socket, self.vm_client_address, self.vm_server_socket))
                        th5 = threading.Thread(target=yolo_predict1, args=(self.cam1, client, self.cam_name5, self.addText, self.conf_value, self.W_value, self.H_value, self.image_label, self.vm_client_socket, self.vm_client_address, self.vm_server_socket))
                        th6 = threading.Thread(target=yolo_predict1, args=(self.cam1, client, self.cam_name6, self.addText, self.conf_value, self.W_value, self.H_value, self.image_label, self.vm_client_socket, self.vm_client_address, self.vm_server_socket))

                        th1.start()
                        th2.start()
                        th3.start()
                        th4.start()
                        th5.start()
                        th6.start()

                        th1.join()
                        th2.join()
                        th3.join()
                        th4.join()
                        th5.join()
                        th6.join()

                        # # 1.开启写入VM信息线程
                        # th_VM_write = threading.Thread(target=VM.VM_write)
                        # # 开启VM线程
                        # th_VM_write.start()
                        # # 等待线程结束
                        # th_VM_write.join()

                        # 2.开启读取VM信息线程
                        th_VM_read = threading.Thread(target=VM_read, args=(client, self.vm_client_socket, self.vm_client_address, self.vm_server_socket))
                        # 开启VM线程
                        th_VM_read.start()
                        # 等待线程结束
                        th_VM_read.join()


                    # # 无触发
                    else:

                        print("无触发信号")
                        # self.yolo_predict1(cam)
                        # self.update_counts(OKorNG)


                except Exception as e:
                    print('2',e)

            else:
                print("请选择方案并打开检测")


        self.cam1.stop()
        self.cam2.stop()
        self.cam3.stop()
        self.cam4.stop()
        self.cam5.stop()
        self.cam6.stop()






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
#     app = QApplication(sys.argv)
#     window = Window(my_yaml)
#     window.show()
#     sys.exit(app.exec_())
