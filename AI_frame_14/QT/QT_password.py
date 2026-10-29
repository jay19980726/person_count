# coding:utf-8
import sys

from PyQt5.QtCore import Qt, QUrl


from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit

# # 加密部分
# with open("counter.txt", "a+") as count_file:
#     count_file.seek(0)   # a+ 指针是在末尾，需要将指正移到开头
#     r_data = count_file.readline()  # 读取txt
#     # print(r_data)
#     print(len(r_data))
#     count_file.write("1")  # 再次写入
#
# if len(r_data) < 10:
#     print("开启")
# else:
#     print("关闭")

"""
加密子界面
"""

class CustomMessageBox(MessageBoxBase):
    """ 自定义消息框 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建一个标题标签
        self.titleLabel = SubtitleLabel('打开 URL', self)
        # 创建一个输入框，用于输入URL
        self.urlLineEdit = LineEdit(self)

        # 设置输入框的占位文本
        self.urlLineEdit.setPlaceholderText('password')
        self.urlLineEdit.setClearButtonEnabled(True)  # 启用清除按钮
        self.urlLineEdit.setEchoMode(LineEdit.Password)  # 设置输入框的回显模式为密码模式，即输入的文本显示为掩码字符，通常是圆点或星号。
        # 将标题标签和输入框添加到视图布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        # 修改按钮的文本
        self.yesButton.setText('打开')
        self.cancelButton.setText('取消')

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)
        self.yesButton.setDisabled(True)  # 默认情况下禁用"打开"按钮
        self.urlLineEdit.textChanged.connect(self._validateUrl)  # 当文本改变时进行URL验证

        # self.hideYesButton()  # 如果需要，可以隐藏"打开"按钮

    def _validateUrl(self, text):
        # 验证输入的URL是否有效，如果有效则启用"打开"按钮
        self.yesButton.setEnabled(QUrl(text).isValid())