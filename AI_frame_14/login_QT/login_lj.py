from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from login_QT.login import Ui_Dialog


class Login(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(Login, self).__init__()
        self.setupUi(self)

        # 加载保存的用户名和密码
        self.load_credentials()

        # 将登录方法与登录按钮关联
        self.pushButton.clicked.connect(self.login)
        self.accept()

        # 关闭按钮
        self.pushButton_close.clicked.connect(self.on_close)


    def login(self):
        # 获取输入框中的用户名和密码
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()

        # 判断用户名和密码是否正确
        if (username == "admin" and password == "123456") or \
                (username == "1" and password == "2") or \
                (username == "user2" and password == "password2"):
            # 登录成功，弹出提示框
            QMessageBox.information(self, "提示", "登录成功！")
            self.save_credentials()  # 保存用户名和密码
            self.accept()  # 关闭登录界面
        else:
            # 登录失败，弹出提示框
            QMessageBox.warning(self, "警告", "用户名或密码错误！")


    def on_close(self):
        # 添加自定义逻辑（例如弹确认框）
        reply = QMessageBox.question(
            self, "确认关闭", "确定要退出登录吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reject()  # 或 self.close()
        # sys.exit(app.exec_())
            return


    def save_credentials(self):
        settings = QtCore.QSettings()
        if self.checkBox.isChecked():
            settings.setValue("username", self.lineEdit.text())
            settings.setValue("password", self.lineEdit_2.text())
        else:
            settings.setValue("username", "")
            settings.setValue("password", "")

    def load_credentials(self):
        settings = QtCore.QSettings()
        username = settings.value("username", "")
        password = settings.value("password", "")
        self.lineEdit.setText(username)
        self.lineEdit_2.setText(password)
        self.checkBox.setChecked(bool(username and password))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = Login()
    if Dialog.exec_() == QtWidgets.QDialog.Accepted:
        print("登录成功！")
        # 下一步操作


