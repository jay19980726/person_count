import socket
import time

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QFont
import sys

# 导入其他必要的库
import cv2
import numpy as np
from MVSCam.MVSCam_class import *
from v8.yolo_result import yolo_predict
import threading
from util import save_OKorNG_img, auto_remove_Imgfile
import threading



"""
1.MVS 调用相机
2.socket
3.多线程
"""



"""
socket 通信
"""
# -----------------
# 创建服务端套接字
# -----------------
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('localhost', 8888))  # 绑定本地地址和端口
# server_socket.listen(1)  # 开始监听，最多允许一个连接
#
# print(f"等待客户端连接...")
# client_socket, client_address = server_socket.accept()  # 是一个阻塞方法，它会一直等待，直到有客户端尝试连接到服务端
# print(f"客户端已连接：{client_address}")





"""
打开相机
"""
def testMVSCam(ip):    # 无触发
    cam = MVSCam(devinfo=ip)
    ret = cam.open(0)
    print(f"相机：{ip}---连接：{ret}")
    if ret is not None:
        return cam             # cam 是一个表示相机的对象，通过该对象可以进行相机的各种操作，比如打开、关闭、获取图像等。
    else:
        raise Exception("相机打开失败")



def Hard_test_MVSCam():
    imgqueue = queue.Queue()

    cam = MVSCam(triggermode='on', imgqueue=imgqueue)

    cam.open(0, 'hard',)

    return imgqueue




"""
#*******************************************
# 相机线程类 （包含调用yolo检测）  多线程
"""

class CameraThread(threading.Thread):
# class CameraThread():
    def __init__(self, cam1, camera_name, label, lock):
        threading.Thread.__init__(self)
        self.cam = cam1
        self.camera_name = camera_name
        self.label = label
        self.lock = lock
        self.num = camera_name

        # 创建线程事件
        self._stop_event = threading.Event()   # CameraThread 类中创建了一个线程事件对象 (threading.Event)，用于在多线程中控制线程的停止。



    def stop(self):   # 当调用 stop() 方法时，self._stop_event.set() 会将事件标志设置为已触发，表示线程应该停止
        self._stop_event.set()


    def stopped(self):  # 通过检查事件标志 (self._stop_event.is_set()) 来判断线程是否应该停止 True or False
        return self._stop_event.is_set()


    def im_predict(self, im, cam_name, label):
        if im is None:
            print('获取图像失败')
            # im = np.zeros([100, 100, 3], dtype=np.uint8)

        # --------------------------------------------------------------
        # 判断相机是否是黑白向， 黑白相机图片是单通道
        if im.shape[2] != 3:  # 判断图像是三通道还是单通道。HWC
            im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)  # 如果是单通道就转为3通道
            # im = cv2.resize(im, (100,100))
            print(im.shape)
            # print(im.shape)

        else:
            pass

        # ------------------------------------------------------------
        # 调用yolo检测。
        # ------------------------------------------------------------
        # 接收客户端数据

        result_list, result_img = yolo_predict(im)
        # time.sleep(2)
        # 保存 OK NG 图片
        # if result_list is not None:  # 没检测到缺陷，OK
        #     save_OKorNG_img.save_OK_img(result_img, cam_file=cam_name)  # 保存OK图片
        # else:
        #     save_OKorNG_img.save_NG_img(result_img, cam_file=cam_name)

        # 自动删除图片文件夹
        # auto_remove_Imgfile.auto_remove(3, self.camera_name)

        # ... 通信发送等其他部分 ...

        # print(cam_name, "检测完毕")
        img = cv2.resize(result_img, (1050, 850))  # 图像缩小显示
        # 将图像从BGR格式转换为RGB格式
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytes_per_line = ch * w

        # 从图像数据创建QImage  用来显示在QT
        qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # 使用新图像更新标签
        label.setPixmap(QPixmap(qimg))
        # cv2.waitKey(2000)     # 每隔多少毫秒检测一次


    def thre1(self):
        try:
            im1 = self.cam[0].getFrame()
            if im1 is not None:
                self.im_predict(im1, self.camera_name[0], self.label[0])
        except Exception as e:
            print("--------------------------------------------------------------线程1:", str(e))


    def thre2(self):
        try:
            im2 = self.cam[1].getFrame()
            self.im_predict(im2, self.camera_name[1], self.label[1])
        except Exception as e:
            print("--------------------------------------------------------------线程2:", str(e))

    def thre3(self):
        try:
            im3 = self.cam[2].getFrame()
            self.im_predict(im3, self.camera_name[2], self.label[2])
        except Exception as e:
            print("--------------------------------------------------------------线程3:", str(e))


    def thre4(self):
        try:
            im4 = self.cam[3].getFrame()
            self.im_predict(im4, self.camera_name[3], self.label[3])
        except Exception as e:
            print("--------------------------------------------------------------线程4:", str(e))


    def thre5(self):
        try:
            im5 = self.cam[4].getFrame()
            self.im_predict(im5, self.camera_name[4], self.label[4])
        except Exception as e:
            print("--------------------------------------------------------------线程5:", str(e))


    def run(self):
        # 在 run 方法中等待事件
        # self.start_event.wait()
        # 循环条件，当线程关闭结束循环。
        while not self.stopped():
            #data = client_socket.recv(1024)  # 是套接字对象的 recv 方法，它用于从套接字接收数据。1024 是指要接收的数据的最大字节数，这里表示一次最多接收 1024 字节的数据
            # if data == b'1':
            im1 = self.cam[0].getFrame()
            # im2 = self.cam[1].getFrame()
            # im3 = self.cam[2].getFrame()
            # im4 = self.cam[3].getFrame()
            # im5 = self.cam[4].getFrame()
            if im1 is not None:
                self.im_predict(im1, self.camera_name[0], self.label[0])
            # self.im_predict(im2, self.camera_name[1], self.label[1])
            # self.im_predict(im3, self.camera_name[2], self.label[2])
            # self.im_predict(im4, self.camera_name[3], self.label[3])
            # self.im_predict(im5, self.camera_name[4], self.label[4])


            # 开启多线程
            # self.threading1 = threading.Thread(target=self.thre1)
            # self.threading2 = threading.Thread(target=self.thre2)
            # self.threading3 = threading.Thread(target=self.thre3)
            # self.threading4 = threading.Thread(target=self.thre4)
            # self.threading5 = threading.Thread(target=self.thre5)

            # 开启线程
            # self.threading1.start()
            # self.threading2.start()
            # self.threading3.start()
            # self.threading4.start()
            # self.threading5.start()

            # 等待线程结束
            # self.threading1.join()
            # self.threading2.join()
            # self.threading3.join()
            # self.threading4.join()
            # self.threading5.join()



            # time.sleep(1)  # 三秒检测一次。
            # else:
            #     time.sleep(3)
            #     print("无触发型号")

            # self.thre1()




"""
#********************************************
# 主窗口类
"""
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # 设置窗口大小
        self.setFixedSize(2560, 1440)  # 设置窗口的宽度和高度
        # 设置窗口标题
        self.setWindowTitle("欣动力视觉检测系统")  # 设置窗口标题


        self.central_widget = QWidget()    # 创建一个名为 central_widget 的 QWidget 对象。在 PyQt 中，QWidget 是构建用户界面的基本元素之一。
        self.setCentralWidget(self.central_widget)  # 创建一个名为 central_widget 的 QWidget 对象。在 PyQt 或 PySide 中，QWidget 是构建用户界面的基本元素之一。

        self.layout = QVBoxLayout(self.central_widget)  # 创建一个垂直布局管理器（QVBoxLayout），并将它关联到 central_widget 上。布局管理器用于管理部件的摆放方式。在这里，垂直布局会将添加到其中的部件按垂直方向排列


        # --------------------------------
        # LOGO显示
        # --------------------------------
        self.label_logo = QLabel(self)    # 创建logo图像标签
        self.label_logo.setGeometry(10, 10, 150, 150)  # 位置大小 x, y, width, height

        logo_img = cv2.imread(r"D:\wg\AI_project\16.feisite\logo_image\XDL.png")
        logo_img = cv2.resize(logo_img, (150, 150))  # 图像缩小显示
        # 将图像从BGR格式转换为RGB格式
        logo_img_rgb = cv2.cvtColor(logo_img, cv2.COLOR_BGR2RGB)
        h, w, ch = logo_img_rgb.shape
        bytes_per_line = ch * w

        # 从图像数据创建QImage  用来显示在QT
        qimg = QImage(logo_img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # 使用新图像更新标签
        self.label_logo.setPixmap(QPixmap(qimg))



        # --------------------------------------------
        # 创建显示图片的标签
        #--------------------------------------------
        # 标签1
        self.label1 = QLabel(self)
        self.label1.setGeometry(600, 150, 1550, 1250)   # 位置大小 x, y, width, height
        # 标签2
        self.label2 = QLabel(self)
        self.label2.setGeometry(1100, 150, 550, 450)

        # 标签3
        self.label3 = QLabel(self)
        self.label3.setGeometry(200, 550, 550, 450)   # 位置大小 x, y, width, height
        # 标签4
        self.label4 = QLabel(self)
        self.label4.setGeometry(750, 550, 550, 450)

        # 标签5
        self.label5 = QLabel(self)
        self.label5.setGeometry(1350, 550, 550, 450)   # 位置大小 x, y, width, height


        # 线程安全锁
        self.lock = threading.Lock()   # 创建一个简单的二进制锁，它有两个状态：锁定（locked）和未锁定（unlocked）。一旦一个线程获得了锁，其他线程就无法获得锁，直到持有锁的线程释放它


        """
           # 创建相机对象，
        """
        self.cam1 = testMVSCam("00K88301994")
        # self.cam2 = testMVSCam("DA1356792")
        # self.cam3 = testMVSCam("DA1294978")
        # self.cam4 = testMVSCam("DA1295030")
        # self.cam5 = testMVSCam("DA1356802")

        camlist = [self.cam1]  # self.cam2,self.cam3,self.cam4,self.cam5
        lebellist = [self.label1]  #  self.label2, self.label3, self.label4, self.label5
        cam_name = ["cam1"]  # , "cam2", "cam3", "cam4", "cam5"

        # 为QT界面显示相机创建线程：  run()方法中的 while True ：会阻止主线程往下执行，所以要创建
        self.thread1 = CameraThread(camlist, cam_name, lebellist, self.lock)

        # 放入线程列表
        self.threads = [self.thread1]   #, self.thread2, self.thread3, self.thread4, self.thread5]

        # 启动线程之前设置事件
        # CameraThread.start_event.set()


        # 启动QT显示界面线程
        for thread in self.threads:
            thread.start()



        # 添加关闭按钮
        self.close_button = QPushButton("关闭检测", self)  # 构造函数的第一个参数是按钮上显示的文本，第二个参数是按钮的父级部件。在这里，按钮的父级部件是 self，即 MainWindow
        self.close_button.setGeometry(900, 30, 130, 100)  # 设置按钮的位置和大小
        self.close_button.setStyleSheet("background-color: red; color: white; font-size: 28px;")  # 设置按钮的背景颜色，和文本颜色，字体大小
        self.close_button.clicked.connect(self.close_application)  # 这一行代码是将按钮的点击事件（clicked 信号）连接到 self.close_application 方法。当按钮被点击时，与此信号连接的方法将被调用


    # -------------------------
    # 关闭程序方法
    def close_application(self):
        # 在这里添加释放资源等需要在程序关闭时执行的操作
        print("程序即将关闭...")
        # # 停止线程
        for thread in self.threads:
            thread.stop()  # 关闭线程

        # 关闭相机
        for cam in [self.cam1]:  # self.cam2, self.cam3, self.cam4, self.cam5
            cam.close()

        # 等待所有线程完成
        for thread in self.threads:
            thread.join()

        sys.exit()  # 关闭整个应用程序




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



