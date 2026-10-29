"""
# ------------------
# QT 子界面的设置。（参数设置）  不包含权限设置
# ------------------
"""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, \
    QDoubleSpinBox, QDialog, QLineEdit







"""
密码登录界面，设置
"""


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('输入密码')  # 提示
        self.resize(300, 150)  # 设置对话框的初始大小为宽度 300 像素，高度 150 像素。

        self.password_label = QLabel('密码:', self)  # 创建一个标签对象
        self.password_label.setFont(QFont('Arial', 11))  # 设置标签的字体为 Arial，大小为 11 磅
        self.password_label.setStyleSheet('color: blue')  # 设置标签的文本颜色为蓝色。

        self.password_input = QLineEdit(self)  # 创建一个单行文本输入框
        self.password_input.setEchoMode(QLineEdit.Password)  # 设置输入框的回显模式为密码模式，即输入的文本显示为掩码字符，通常是圆点或星号。

        self.ok_button = QPushButton('确定', self)  # 创建一个按钮对象
        self.ok_button.setStyleSheet(
            'background-color: #4CAF50; color: white; font-size: 16px;')  # 设置按钮的样式，包括背景颜色、文本颜色和字体大小。
        self.ok_button.clicked.connect(self.accept)  # 将按钮的 clicked 信号连接到 self.accept 槽函数，这表示当用户点击按钮时，对话框会被接受（关闭）。

        # 设置布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    # 方法用于获取用户在密码输入框中输入的文本内容
    def get_password(self):
        return self.password_input.text()  # 返回密码输入框的当前文本内容













"""
缺陷参数设置界面
"""


class DefectParameterDialog(QDialog):
    def __init__(self, conf_value,  W_value, H_value, parent=None):
        super().__init__(parent)
        self.conf_value = conf_value
        self.W_value = W_value
        self.H_value = H_value

        "子界面标题"
        self.setWindowTitle('视觉参数设置')
        self.resize(300, 400)

        """
        缺陷置信度设置
        """
        self.conf_label = QLabel('缺陷分数:', self)
        self.conf_label.setFont(QFont('Arial', 11))  # 设置字体大小
        self.conf_label.setStyleSheet('color: blue')  # 设置字体颜色

        self.conf_spinbox = QDoubleSpinBox(self)
        self.conf_spinbox.setRange(0.1, 1.0)  # 设置范围
        self.conf_spinbox.setSingleStep(0.1)  # 设置步长
        self.conf_spinbox.setValue(self.conf_value)  # 设置默认值

        # self.conf_button = QPushButton('确定', self)
        # self.conf_button.setStyleSheet('background-color: #4CAF50; color: white; font-size: 16px;')  # 设置按钮颜色、文字颜色、字体大小
        # self.conf_button.clicked.connect(self.accept)  # 将按钮的 clicked 信号连接到 self.accept 槽函数，这表示当用户点击按钮时，对话框会被接受（关闭）。

        """
        缺陷长
        """
        self.W_label = QLabel('缺陷长度:', self)
        self.W_label.setFont(QFont('Arial', 11))  # 设置字体大小
        self.W_label.setStyleSheet('color: blue')  # 设置字体颜色

        self.W_spinbox = QDoubleSpinBox(self)
        self.W_spinbox.setRange(0, 5000)  # 设置范围
        self.W_spinbox.setSingleStep(100)  # 设置步长
        self.W_spinbox.setValue(self.W_value)  # 设置默认值

        # self.W_ok_button = QPushButton('确定', self)
        # self.W_ok_button.setStyleSheet('background-color: #4CAF50; color: white; font-size: 16px;')  # 设置按钮颜色、文字颜色、字体大小
        # self.W_ok_button.clicked.connect(self.accept)  # 将按钮的 clicked 信号连接到 self.accept 槽函数，这表示当用户点击按钮时，对话框会被接受（关闭）。

        """
        缺陷宽
        """
        self.H_label = QLabel('缺陷宽度:', self)
        self.H_label.setFont(QFont('Arial', 11))  # 设置字体大小
        self.H_label.setStyleSheet('color: blue')  # 设置字体颜色

        self.H_spinbox = QDoubleSpinBox(self)
        self.H_spinbox.setRange(0, 5000)  # 设置范围
        self.H_spinbox.setSingleStep(100)  # 设置步长
        self.H_spinbox.setValue(self.H_value)  # 设置默认值

        self.H_ok_button = QPushButton('确定', self)
        self.H_ok_button.setStyleSheet('background-color: #4CAF50; color: white; font-size: 16px;')  # 设置按钮颜色、文字颜色、字体大小
        self.H_ok_button.clicked.connect(self.accept)  # 将按钮的 clicked 信号连接到 self.accept 槽函数，这表示当用户点击按钮时，对话框会被接受（关闭）。

        # 创建布局
        layout = QVBoxLayout(self)
        # 添加置信度
        layout.addWidget(self.conf_label)
        layout.addWidget(self.conf_spinbox)
        # layout.addWidget(self.conf_button)
        # 添加W
        layout.addWidget(self.W_label)
        layout.addWidget(self.W_spinbox)
        # layout.addWidget(self.W_ok_button)
        # 添加H
        layout.addWidget(self.H_label)
        layout.addWidget(self.H_spinbox)
        # layout.addWidget(self.H_ok_button)

        self.setLayout(layout)

    " 获取子界面缺陷参数值方法"
    def get_conf_WH_value(self):
        return self.conf_spinbox.value(), self.W_spinbox.value(), self.H_spinbox.value()  # 返回界面上设置的值
