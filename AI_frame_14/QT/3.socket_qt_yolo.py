import sys
import socket
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread
from v8.yolo_result import yolo_predict
from MVSCam.MVSCam_class import *

"""
服务费发送服务，客户端连接后发送"1",服务端开始调用yolo检测。
"""

# 导入YOLO模型相关的库和函数
# 请根据您的YOLO模型库和配置进行相应的导入和设置

# 创建Qt应用程序
app = QApplication(sys.argv)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # 将self传递给super()构造函数

        self.initUI()

    def initUI(self):
        self.setWindowTitle('工业相机控制')
        self.setGeometry(100, 100, 800, 600)

        # 创建按钮
        self.btn_reset = QPushButton('计数清零', self)
        self.btn_reset.clicked.connect(self.reset_count)
        self.btn_reset.setGeometry(10, 10, 120, 40)

        self.btn_alert = QPushButton('关闭报警', self)
        self.btn_alert.clicked.connect(self.close_alert)
        self.btn_alert.setGeometry(10, 60, 120, 40)

        # 创建标签用于显示图像
        self.image_label = QLabel(self)
        self.image_label.setGeometry(150, 10, 640, 480)

        self.count = 0
        self.alert = False

        # 创建服务器Socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8888))   # 服务端建立服务
        self.server_socket.listen(1)

        # 等待客户端连接
        print("等待客户端连接...")
        self.client_socket, addr = self.server_socket.accept()
        print(f"连接来自 {addr}")

        # 启动图像捕获线程
        self.capture_thread = CaptureThread(self)
        self.capture_thread.start()

    def reset_count(self):
        self.count = 0

    def close_alert(self):
        self.alert = False



    # ---------------------------
    #  方法接受一个图像参数，并使用 Qt 的方法来在界面上显示图像。您需要根据您的 Qt 窗口的布局和需要，以及图像数据的格式来编写显示图像的逻辑。
    # ---------------------------
    def display_image(self, image):
        # 在界面上显示图像的逻辑
        # 这里需要使用 Qt 的方法来显示图像，例如使用 QLabel 等

        # 示例代码：
        pixmap = QPixmap.fromImage(QImage(image.data, image.shape[1], image.shape[0], image.shape[1] * 3, QImage.Format_RGB888))
        label = QLabel(self)
        label.setPixmap(pixmap)
        label.show()



# --------------------
# 创建了一个名为 CaptureThread 的线程类，该类用于与工业相机进行交互，处理图像捕获、YOLO物体检测和与客户端通信。以下是该类的主要功能：
#
# 在 __init__ 方法中，您初始化了 CaptureThread 类，接受一个 window 参数，该参数用于将窗口对象传递给线程，以便在线程中访问窗口中的属性和方法。
#
# 在 run 方法中，您创建了一个工业相机对象 cam，并尝试连接到指定的相机。然后，您进入一个无限循环，该循环主要处理以下任务：
#
# yolopredict 方法用于执行YOLO物体检测的逻辑。它接受图像作为输入，并返回YOLO检测的结果列表和结果图像。具体的YOLO检测逻辑需要在此方法中实现，可以使用YOLO库进行物体检测。如果检测成功，它将返回结果列表和图像；否则，它将返回 None。

class CaptureThread(QThread):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def run(self):
        # 初始化工业相机
        cam = MVSCam(devinfo='192.168.255.1')  # 连接相机
        ret = cam.open(0)   # 这一行代码尝试打开相机连接。cam.open(0) 方法通常返回一个表示连接状态的返回值，例如 0 表示成功

        while True:
            if self.window.alert:
                # 发送报警信息
                pass

            im = cam.getFrame()  # 这一行代码调用 cam 对象的 getFrame() 方法来获取相机的当前图像帧。im 变量将包含图像数据。通常，这个方法会从相机中捕获当前可用的图像帧。
            if im is None:       # 这个条件语句检查获取的图像是否为 None，如果图像为 None，则表示获取图像失败。
                print('get none')  # 图像获取失败
                # im = np.zeros([100, 100, 3], dtype=np.uint8)
                continue

            # 接收客户端数据
            data = self.window.client_socket.recv(1024)  # 是套接字对象的 recv 方法，它用于从套接字接收数据。1024 是指要接收的数据的最大字节数，这里表示一次最多接收 1024 字节的数据
            #if data == b'1':
            # 调用yolopredict方法
            result_list, result_image = self.yolopredict(im)   # yolo 返回结果 list和 image


            # 在界面上显示结果
            self.window.display_image(result_image)

            # 判断有无侦测到
            if result_list is not None:
                # 返回结果给客户端
                self.window.client_socket.send(b'OK')
            else:
                self.window.client_socket.send(b'NG')



    # yolo 检测
    def yolopredict(self, img):
        # 在此处实现YOLO预测逻辑
        # 使用YOLO模型进行物体检测，返回结果的图像
        result_list, result_image = yolo_predict(img)  # 这里需要根据YOLO库的具体用法进行设置
        if result_list is not None and result_image is not None:

            return result_list, result_image

        else:
            result_list = None
            return result_list, result_image



if __name__ == '__main__':
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
