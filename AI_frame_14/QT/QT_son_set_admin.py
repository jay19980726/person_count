import json
import os
from PyQt5.QtWidgets import QDialog, QLabel, QDoubleSpinBox, QPushButton, QMessageBox, QLineEdit
from PyQt5.QtGui import QFont

from app2.config import time_params_path, admin_password


# 放在 DefectParameterDialog_person 同一个文件里，上面或下面都行
class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('输入密码')
        self.resize(300, 150)
        self.setStyleSheet('background-color: white;')

        self.correct_password = admin_password["password"]

        self.password_label = QLabel('密码:', self)
        self.password_label.setFont(QFont('Arial', 11))
        self.password_label.setStyleSheet('color: blue')

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.ok_button = QPushButton('确定', self)
        self.ok_button.setStyleSheet(
            'background-color: #4CAF50; color: white; font-size: 16px;'
        )
        self.ok_button.clicked.connect(self.check_password)

        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def check_password(self):
        if self.password_input.text() == self.correct_password:
            self.accept()
        else:
            QMessageBox.warning(self, '错误', '密码错误，请重试！')
            self.password_input.clear()

    def get_password(self):
        return self.password_input.text()






class DefectParameterDialog_person(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)


        self.setWindowTitle('视觉参数设置')
        self.resize(420, 430)

        # ============ 配置文件路径 ============
        self.config_file = time_params_path["root"]

        # ============ 7个时间参数配置 ============
        # (标签文字, 默认最小值, 最大, y坐标)
        self.time_configs = [
            ("进钢化机 至 冲击线入口:",        5,  30),
            ("冲击线入口 至 进高温区:",       10,  80),
            ("进高温区 至 出高温区:",         15, 130),
            ("出高温区 至 冲击线网带出口:",    8, 180),
            ("冲击线网带出口 至 水槽出口:",    6, 230),
            ("水槽出口 至 进均温炉:",         4, 280),
            ("进均温炉 至 出均温炉:",        12, 330),
        ]

        # 从文件加载已保存的值
        saved_values = self._load_from_file()

        self.labels = []
        self.spinboxes = []

        for i, (text, default_val, y) in enumerate(self.time_configs):
            # 优先用文件里的值，没有才用默认值
            val = saved_values[i] if i < len(saved_values) else default_val

            # 标签
            label = QLabel(text, self)
            label.setGeometry(10, y, 280, 40)
            label.setFont(QFont('Arial', 11))
            label.setStyleSheet('color: blue')

            # 输入框
            spin = QDoubleSpinBox(self)
            spin.setGeometry(290, y + 5, 80, 30)
            spin.setRange(0, 5000)
            spin.setSingleStep(1)
            spin.setDecimals(0)
            spin.setValue(val)
            spin.setSuffix(" 分钟")

            self.labels.append(label)
            self.spinboxes.append(spin)

        # ============ 确定按钮 ============
        self.conf_button = QPushButton('确定', self)
        self.conf_button.setGeometry(160, 380, 100, 40)
        self.conf_button.setStyleSheet(
            'background-color: #4CAF50; color: white; font-size: 16px;'
        )
        self.conf_button.clicked.connect(self._on_confirm)


    # ============ 确定按钮回调 ============
    def _on_confirm(self):
        """保存并关闭"""
        values = self.get_time_values()
        self._save_to_file(values)
        QMessageBox.information(self, "提示", "参数已保存！")
        self.accept()

    # ============ 取值方法 ============
    def get_time_values(self):
        """返回7个时间参数的值（按顺序）"""
        return [spin.value() for spin in self.spinboxes]

    # ============ 文件读写 ============
    def _load_from_file(self):
        """从 JSON 文件读取保存的值，文件不存在返回空列表"""
        if not os.path.exists(self.config_file):
            return []
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("time_values", [])
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return []


    def _save_to_file(self, values):
        """把值写入 JSON 文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"time_values": values}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            QMessageBox.warning(self, "警告", f"保存失败：{e}")