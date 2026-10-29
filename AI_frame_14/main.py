import sys
import os
import datetime

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QCheckBox, QPushButton, QSpinBox, QApplication,
    QComboBox, QFrame, QGroupBox, QFormLayout, QMessageBox, QGridLayout
)
from PyQt5.QtGui import QImage, QPixmap, QIcon

# from app2.config import admin_password, tcp, save_images, Hikv_cam
from app2.run_predict import DetThread

from QT.QT_son_set_admin import *
from util.conf_write_read import *
# from ModbusTcp1.mudbusTCP_client import mod_bus_tcp
from Hikvision_camera.ivms_4200_sdk import Hikv_link
from PyQt5.QtCore import pyqtSignal



class MainWindow(QMainWindow):
    # 相机清零信号：参数为相机索引 0~7
    camera_reset_signal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI视觉检测系统")
        self.setGeometry(50, 30, 1400, 850)

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f7fa; }
            * { font-family: 'Microsoft YaHei', 'Segoe UI'; }
        """)

        if os.path.exists("icon.png"):
            self.setWindowIcon(QIcon("icon.png"))

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        self.view_panel = self.create_view_panel()
        content_layout.addWidget(self.view_panel, 8)

        settings_panel = self.create_settings_panel()
        settings_panel.setMinimumWidth(340)
        content_layout.addWidget(settings_panel, 2)

        main_layout.addLayout(content_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # ===== 8 个相机 =====
        #
        self.cams = [
            Hikv_link(Hikv_cam["ip_1"]),
            Hikv_link(Hikv_cam["ip_2"]),
            Hikv_link(Hikv_cam["ip_3"]),
            Hikv_link(Hikv_cam["ip_4"]),
            Hikv_link(Hikv_cam["ip_5"]),
            Hikv_link(Hikv_cam["ip_6"]),
            Hikv_link(Hikv_cam["ip_7"]),
            Hikv_link(Hikv_cam["ip_8"]),
        ]

        self.conf_value = float(read_conf())
        self.W_value, self.H_value = map(int, map(float, read_WH()))

        self.time_values = load_from_file()


        # ===== 创建 8 个画面 =====
        self.image_labels = []
        self.image_frames = []
        self.cam_counters = []

        for i in range(8):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setLineWidth(1)
            frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #d0d7de;
                    border-radius: 6px;
                }
            """)
            frame.setMinimumSize(240, 180)
            frame.setMaximumSize(400, 300)

            layout = QVBoxLayout()
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(2)

            name = ["进钢化机", "冲击线入口", "进高温区", "出高温区", "冲击线网带出口", "水槽出口", "进均温炉",
                    "出均温炉"]
            cam_label = QLabel(f"{name[i]}")
            cam_label.setAlignment(Qt.AlignCenter)
            cam_label.setFixedHeight(25)
            cam_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 12px;
                    font-weight: bold;
                    background-color: #f8f9fa;
                    border-radius: 3px;
                }
            """)
            layout.addWidget(cam_label)

            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("background:#f0f0f0;")
            layout.addWidget(image_label, 1)

            count_label = QLabel("")  # ===
            count_label.setAlignment(Qt.AlignCenter)
            count_label.setFixedHeight(22)
            count_label.setStyleSheet("""
                QLabel {
                    color: #4a90e2;
                    font-size: 12px;
                    font-weight: bold;
                    background-color: #f1f5fb;
                    border-radius: 3px;
                }
            """)
            layout.addWidget(count_label)

            frame.setLayout(layout)

            self.image_labels.append(image_label)
            self.image_frames.append(frame)
            self.cam_counters.append(count_label)

            setattr(self, f'image_label{i + 1}', image_label)
            setattr(self, f'frame{i + 1}', frame)

        # ===== 2×4 布局 =====
        main_grid = QVBoxLayout()
        main_grid.setSpacing(70)
        main_grid.setContentsMargins(10, 10, 10, 10)

        row1 = QHBoxLayout()
        row1.addWidget(self.frame1, 1)
        row1.addWidget(self.frame2, 1)
        row1.addWidget(self.frame3, 1)
        row1.addWidget(self.frame4, 1)

        row2 = QHBoxLayout()
        row2.addWidget(self.frame5, 1)
        row2.addWidget(self.frame6, 1)
        row2.addWidget(self.frame7, 1)
        row2.addWidget(self.frame8, 1)

        main_grid.addLayout(row1, 1)
        main_grid.addLayout(row2, 1)

        self.view_panel.layout().addLayout(main_grid)


        # ===== 检测线程 =====
        self.det_thread = DetThread(
            self.cams,
            self.conf_value, self.W_value, self.H_value,self.time_values
        )

        # 绑定更新图像信号
        for i in range(8):
            getattr(self.det_thread, f'image_updated{i + 1}').connect(
                lambda img, idx=i: self.update_image(img, idx)
            )

        # 绑定更新计数信号
        self.det_thread.update_count_signal.connect(self.update_counts)
        # ✅ 连接相机清零信号
        self.camera_reset_signal.connect(self.det_thread.reset_camera_counter)

        self.det_thread.start()


    # ===== 图像更新 =====
    @pyqtSlot(QImage)
    def update_image(self, qimg, index):
        if qimg.isNull():
            return

        label = self.image_labels[index]
        pixmap = QPixmap.fromImage(qimg)

        scaled = pixmap.scaled(
            label.width(), label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        label.setPixmap(scaled)


    # ===== 相机计数 =====
    def update_counts(self, cam_index, result):
        # if result not in ("OK", "NG"):
        #     return

        label = self.cam_counters[cam_index]
        # count = int(label.text().split("：")[1]) + 1
        label.setText(f"检测数：{result}")

        # if result == "NG":
        #     self._show_message(f"相机 {cam_index + 1} 检测到 NG", "warning")



    # ===== 顶部栏 =====
    def create_top_bar(self):
        top_bar = QFrame()
        top_bar.setFixedHeight(150)
        top_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #4a90e2, stop:1 #63b3ed);
                border-radius: 8px;
            }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 0, 15, 0)

        title = QLabel("AI视觉检测系统\n智能视觉分析与检测平台 - 3线")
        title.setStyleSheet("color:white;font-size:19px;")
        title.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(title)
        layout.addStretch()

        top_bar.setLayout(layout)
        return top_bar


    # ===== 左侧画面区（无标题）=====
    def create_view_panel(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #d0d7de;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        frame.setLayout(layout)
        return frame


    # ===== 右侧设置面板（已修复不均匀问题）=====
    def create_settings_panel(self):
        group = QGroupBox("系统设置")
        group.setMinimumWidth(320)
        group.setMaximumWidth(380)

        group.setStyleSheet("""
            QGroupBox {
                font-size:16px;font-weight:bold;color:#4a90e2;
                border:1px solid #d0d7de;border-radius:8px;
                background:white;
                margin-top:10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # ===== 模型设置 =====
        model_box = QGroupBox("模型设置")
        model_layout = QVBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.addItems(["模型V1.0", "模型V2.0", "模型V3.0"])
        model_layout.addWidget(self.model_combo)
        model_box.setLayout(model_layout)
        layout.addWidget(model_box)

        # ===== 系统控制 =====
        ctrl_box = QGroupBox("系统控制")
        ctrl_layout = QVBoxLayout()
        self.camera_btn = QPushButton("⚙ 参数设置")
        self.reset_btn = QPushButton("🔄 系统复位")
        self.folder_btn = QPushButton("📁 打开目录")

        for btn in (self.camera_btn, self.reset_btn, self.folder_btn):
            btn.setMinimumHeight(36)
            ctrl_layout.addWidget(btn)

        self.camera_btn.clicked.connect(self.show_login_dialog)
        self.reset_btn.clicked.connect(self.reset)
        self.folder_btn.clicked.connect(self._open_specified_folder)

        ctrl_box.setLayout(ctrl_layout)
        layout.addWidget(ctrl_box)

        # ===== 检测参数 =====
        param_box = QGroupBox("检测参数")
        form = QFormLayout()
        self.iou_slider = QSlider(Qt.Horizontal)
        self.iou_slider.setValue(70)
        form.addRow("IoU阈值:", self.iou_slider)
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setValue(50)
        form.addRow("置信度:", self.conf_slider)
        self.save_checkbox = QCheckBox("⚡ 自动保存异常图像")
        form.addRow(self.save_checkbox)
        self.save_checkbox.stateChanged.connect(
            lambda: self.det_thread.update_auto_save_signal.emit(self.save_checkbox.isChecked()))
        param_box.setLayout(form)
        layout.addWidget(param_box)

        # ===== 系统日志 =====
        log_box = QGroupBox("系统日志")
        log_box.setMinimumHeight(120)
        log_box.setMaximumHeight(200)
        log_layout = QVBoxLayout()
        self.message_area = QLabel("系统已启动...")
        self.message_area.setWordWrap(True)
        self.message_area.setStyleSheet("""
            QLabel {
                background:#f8f9fa;
                border:1px solid #e1e4e8;
                border-radius:4px;
                padding:6px;
            }
        """)
        log_layout.addWidget(self.message_area)
        log_box.setLayout(log_layout)
        layout.addWidget(log_box)


        # ===============================
        # ✅ 从这里开始插入相机复位
        # ===============================
        cam_btn_box = QGroupBox("检测复位")
        cam_btn_box.setMinimumHeight(140)
        cam_btn_layout = QGridLayout()
        cam_btn_layout.setSpacing(6)

        cam_names = [
            "进钢化机", "冲击线入口", "进高温区", "出高温区",
            "冲击线网带出口", "水槽出口", "进均温炉", "出均温炉"
        ]

        self.cam_buttons = []
        for i, name in enumerate(cam_names):
            btn = QPushButton(name)
            btn.setMinimumHeight(28)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f1f5fb;
                    color: #4a90e2;
                    border: 1px solid #c0d4f0;
                    border-radius: 4px;
                    font-size: 11px;
                    padding: 4px 6px;
                }
                QPushButton:hover {
                    background-color: #e1ebf7;
                }
                QPushButton:pressed {
                    background-color: #4a90e2;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.camera_reset_signal.emit(idx))
            cam_btn_layout.addWidget(btn, i // 4, i % 4)
            self.cam_buttons.append(btn)

        cam_btn_box.setLayout(cam_btn_layout)
        layout.addWidget(cam_btn_box)
        # ===============================
        # ✅ 插入结束
        # ===============================

        layout.addStretch()
        group.setLayout(layout)
        return group






    # ===== 辅助函数 =====
    def _show_message(self, msg, level="info"):
        color = {"info": "#4a90e2", "warning": "#ff9500"}.get(level, "#000")
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.message_area.setText(
            f"[{ts}] <span style='color:{color}'>{msg}</span><br>" +
            self.message_area.text()
        )

    def show_login_dialog(self):
        dlg = PasswordDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return

        # ✅ 不用再检查密码了，能到这里一定是密码对的
        p = DefectParameterDialog_person(self)
        if p.exec_() == QDialog.Accepted:
            self.det_thread.time_values = p.get_time_values()



    def reset(self):
        try:
            # mod_bus_tcp().write_multiple_registers(tcp["write_result_addr"], [2])
            self._show_message("系统复位成功", "info")
        except Exception as e:
            self._show_message(str(e), "warning")


    def _open_specified_folder(self):
        if os.path.exists(save_images["root"]):
            os.startfile(save_images["root"])


    def closeEvent(self, e):
        self.det_thread.stop()
        e.accept()