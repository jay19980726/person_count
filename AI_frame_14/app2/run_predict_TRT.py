import queue
import threading
import time
from datetime import datetime
import cv2
import torch

from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from ModbusTcp1.mudbusTCP_client import *
from PyQt5.QtGui import QImage, QPixmap, QIcon


from util.save_OKorNG_img import *
from concurrent.futures import ThreadPoolExecutor,wait
from yolo_TensorRT_main.trt_perdict import TensorRTDetector
from yolo_TensorRT_main.trt_perdict2 import TensorRTDetector2
from yolo_TensorRT_main.trt_perdict3 import TensorRTDetector3
from yolo_TensorRT_main.trt_perdict4 import TensorRTDetector4

"""
    # modbustcp 是单向的-不支持同时进行读写操  这是因为它基于请求-响应机制。
    # 多个线程同时访问调用一个modbus客户端对象时（共享资源）需要加锁，避免资源竞争和数据不一致的问题引起的阻塞。

    send_msg = pyqtSignal(str)   # 定义一个信号 send_msg，当线程执行某些操作时，它将发射这个信号，并传递信息。
    self.worker1.send_msg.connect(self.handle_worker_msg)  # 连接 DetectWorker 的 send_msg 信号到 DetThread 的 handle_worker_msg 方法，
    self.send_msg.emit("摄像头打开失败")   # .emit() 是 PyQt 中信号的发射方法,(调用 handle_worker_msg()方法)

"""

"""
检测线程单个工位 -----如有多个工位可直接copy
"""


class DetThread(QThread):
    # 定义一个信号 send_msg，当线程执行某些操作时，它将发射这个信号，并传递信息。
    send_msg = pyqtSignal(str)  # 给QT主线程发送检测状态信息的信号
    """
    置信度，iou 信号槽
    """
    update_conf = pyqtSignal(float)  # 信号用于接收主线程更新的置信度值
    update_iou = pyqtSignal(float)  # 信号用于接收主线程更新的 IOU 值
    update_auto_save_signal = pyqtSignal(bool)   # 信号用于接收主线程更新的自动保存设置

    # 添加一个信号用于传递图像
    image_updated1 = pyqtSignal(QImage)
    image_updated2 = pyqtSignal(QImage)
    image_updated3 = pyqtSignal(QImage)
    image_updated4 = pyqtSignal(QImage)

    def __init__(self, cam1, cam2, cam3, cam4, image_label, image_label2, image_label3, image_label4,
                 imgqueue1, imgqueue2, imgqueue3, imgqueue4,
                 client, conf_value, w_value, h_value, update_counts1):
        super(DetThread, self).__init__()

        self.is_running = True
        self.cam1 = cam1
        self.cam2 = cam2
        self.cam3 = cam3
        self.cam4 = cam4

        # 触发计数
        self.cam1_count = 0
        self.cam2_count = 0
        self.cam3_count = 0
        self.cam4_count = 0

        self.image_label1 = image_label
        self.image_label2 = image_label2
        self.image_label3 = image_label3
        self.image_label4 = image_label4

        self.imgqueue1 = imgqueue1
        self.imgqueue2 = imgqueue2
        self.imgqueue3 = imgqueue3
        self.imgqueue4 = imgqueue4

        self.client = client  # 客户端实例
        self.number1 = "cam1"  # 相机编号表示
        self.number2 = "cam2"
        self.number3 = "cam3"
        self.number4 = "cam4"


        # 连接信号到槽
        self.update_conf.connect(self.set_conf)
        self.update_iou.connect(self.set_iou)
        self.update_auto_save_signal.connect(self.set_auto_save)


        # 主界面更新计数统计方法
        self.update_counts1 = update_counts1  # 相机1的

        # conf 参数
        self.conf_value = conf_value

        # W,H 参数
        self.w_value, self.h_value = w_value, h_value

        # 线程锁
        self.lock = threading.Lock()

        # -----------TRT---------------
        CLASS_NAMES = ["G", "ng"]  # 替换为您的实际类别名称、
        engine_path = r"D:\AI\AI_frame_12\yolo\ultralytics-main\runs\detect\train3\weights\best1.engine"
        self.trt_predict = TensorRTDetector(engine_path, class_names=CLASS_NAMES)

        CLASS_NAMES2 = ["G", "ng"]  # 替换为您的实际类别名称、
        engine_path2 = r"D:\AI\AI_frame_12\yolo\ultralytics-main\runs\detect\train3\weights\best2.engine"
        self.trt_predict2 = TensorRTDetector2(engine_path2, class_names=CLASS_NAMES2)


        CLASS_NAMES3 = ["G", "ng"]  # 替换为您的实际类别名称、
        engine_path3 = r"D:\AI\AI_frame_12\yolo\ultralytics-main\runs\detect\train3\weights\best3.engine"
        self.trt_predict3 = TensorRTDetector3(engine_path3, class_names=CLASS_NAMES3)

        CLASS_NAMES4 = ["G", "ng"]  # 替换为您的实际类别名称、
        engine_path4 = r"D:\AI\AI_frame_12\yolo\ultralytics-main\runs\detect\train3\weights\best4.engine"
        self.trt_predict4 = TensorRTDetector4(engine_path4, class_names=CLASS_NAMES4)



        # """  创建定时器
        #     # 每 100 毫秒，定时器会触发 timeout 信号，并调用 self.process_images 方法。
        #     # 这是为了定期检查相机数据和图像处理任务，确保后台处理不会阻塞界面更新。
        #     # 定时器的作用是避免使用阻塞式的 `time.sleep()`，从而确保实时性并保持 UI 响应。
        # """
        # self.timer = QTimer(self)  # 定时器对象，self 表示定时器归当前线程管理
        # self.timer.timeout.connect(self.process_images)  # 将定时器的 timeout 信号连接到 process_images 方法
        # self.timer.start(10)  # 启动定时器，设置时间间隔为 100 毫秒（即每 100 毫秒调用一次 process_images）
        self.executor = ThreadPoolExecutor(max_workers=4)

        self.auto_save = False  # 默认状态


    def set_conf(self, value):
        self.conf = value  # 更新置信度值

    def set_iou(self, value):
        self.iou = value  # 更新 IOU 值

    def handle_worker_msg(self, msg):
        # self.send_msg.emit(msg) # 可以传递给另一个线程，可以不需要
        print(msg)
        if msg == "摄像头打开失败":
            self.stop()
            print("相机打开失败")

    def set_auto_save(self, state):
        # 更新自动保存的状态
        self.auto_save = state  # true 或者 false
        print("自动保存状态：", state)



    # 定义检测线程的 stop 方法
    def stop(self):
        self.is_running = False
        print("检测线程结束")
        # 关闭相机
        self.cam1.close()
        self.cam2.close()
        self.cam3.close()
        self.cam4.close()

        print("相机关闭完成")
        self.quit()  # 发送退出信号
        # self.wait()  # 等待线程完全退出并释放资源
        print("检测线程退出")



    def update_client(self, new_client):
        """接收 心跳线程 发送的新 client 并更新"""
        print(" 收到新的 ModbusTCP 客户端")

        # 关闭旧 client（如果已连接）
        if self.client and self.client.connected:
            self.client.close()
            print(" 关闭旧客户端")

        # 更新为新的 client
        self.client = new_client



    @torch.no_grad()  # 上下文管理器来禁止梯度计算
    def predict1(self):
        OK_or_NG = ""

        a = time.time()

        try:
            im1 = self.imgqueue1.get(True, 0.02)
            # print(im)
            img1 = im1[0]
            self.imgqueue1.queue.clear()

            if img1 is None:
                print('get none')
                img1 = cv2.imread(config.logo_img_path)

            elif img1.shape[2] != 3:
                img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)

            else:
                pass


            if self.auto_save:
                save_img(img1, "1")
                b = time.time()
                print("相机1取图时间：", b - a)
                yolo_result_img = img1


            else:
                list_xywh = []  # WH通过阈值删选后的目标框
                """调用检测算法"""
                results, yolo_result_img = self.trt_predict.process_image(img1, self.conf_value)
                # cls_name_list = [item[0] for item in results]
                cls_name_list = results
                print("cam1:", cls_name_list, "\n")


                """后处理部分"""
                # [('ok', 0.984375, (1351.4202270507812, 483.38433837890625, 1122.1593, 966.7686767578125))]


                # 判断结果
                if results is None:
                    cv2.putText(yolo_result_img, "OK", (20, 250), 1, 10, (0, 255, 0), 10)
                    # 通讯发送结果
                    # self.send_msg.emit(f"工位{self.number}检测OK")
                    save_NG_img(img1, self.number1)
                    OK_or_NG = "OK"


                # *****2.有缺陷 ：缺陷大于阈值 NG， 缺陷小于阈值OK
                elif "ng" in cls_name_list:
                    cv2.putText(yolo_result_img, "NG", (20, 250), 1, 10, (0, 0, 255), 10)
                    OK_or_NG = "NG"
                    save_NG_img(img1, self.number1)

                else:
                    cv2.putText(yolo_result_img, "OK", (20, 250), 1, 10, (0, 255, 0), 10)
                    OK_or_NG = "OK"
                    #save_OK_img(img1, self.number1)

            # 将图像从BGR格式转换为RGB格式
            img_rgb = cv2.cvtColor(yolo_result_img, cv2.COLOR_BGR2RGB)
            h, w, ch = img1.shape
            bytes_per_line = ch * w
            # 从图像数据创建QImage  用来显示在QT
            qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()

            # 发射信号而不是直接更新UI
            self.image_updated1.emit(qimg)


            # --------------------------------------
            # 从图像数据创建QImage  用来显示在QT
            # qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            #
            # # 使用新图像更新标签
            # self.image_label1.setPixmap(QPixmap(qimg))
            # # -------------------------------------

            # # 计数
            self.cam1_count = self.cam1_count + 1
            print("相机1计数：",self.cam1_count, "\n")
            return OK_or_NG


        except queue.Empty:
            # print("相机1 erro :", e)
            # time.sleep(0.005)
            # print("相机1队列为空，没有可用的图像数据。")
            return "none"



    @torch.no_grad() # 上下文管理器来禁止梯度计算
    def predict2(self):
        OK_or_NG = ""

        a = time.time()

        try:
            im2 = self.imgqueue2.get(True, 0.02)
            # print(im)
            img2 = im2[0]
            self.imgqueue2.queue.clear()

            if img2 is None:
                print('get none')
                img2 = cv2.imread(config.logo_img_path)

            elif img2.shape[2] != 3:
                img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)

            else:
                pass


            if self.auto_save:
                save_img(img2, "2")
                b = time.time()
                print("相机2取图时间：", b - a)
                yolo_result_img = img2

            else:

                list_xywh = []  # WH通过阈值删选后的目标框
                """调用检测算法"""
                results, yolo_result_img = self.trt_predict2.process_image(img2, self.conf_value)
                # cls_name_list = [item[0] for item in results]
                cls_name_list = results
                print("cam1:", cls_name_list, "\n")

                """后处理部分"""
                # [('ok', 0.984375, (1351.4202270507812, 483.38433837890625, 1122.1593, 966.7686767578125))]

                # 判断结果
                if results is None:
                    cv2.putText(yolo_result_img, "OK", (20, 250), 1, 10, (0, 255, 0), 10)
                    # 通讯发送结果
                    # self.send_msg.emit(f"工位{self.number}检测OK")
                    save_NG_img(img2, self.number2)
                    OK_or_NG = "OK"


                # *****2.有缺陷 ：缺陷大于阈值 NG， 缺陷小于阈值OK
                elif "ng" in cls_name_list:
                    cv2.putText(yolo_result_img, "NG", (20, 250), 1, 10, (0, 0, 255), 10)
                    OK_or_NG = "NG"
                    save_NG_img(img2, self.number2)

                else:
                    cv2.putText(yolo_result_img, "OK", (20, 250), 1, 10, (0, 255, 0), 10)
                    OK_or_NG = "OK"
                    # save_OK_img(img2, self.number2)

            # 将图像从BGR格式转换为RGB格式
            img_rgb = cv2.cvtColor(yolo_result_img, cv2.COLOR_BGR2RGB)
            h, w, ch = img2.shape
            bytes_per_line = ch * w
            # 从图像数据创建QImage  用来显示在QT
            qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()

            # 发射信号而不是直接更新UI
            self.image_updated2.emit(qimg)

            # # --------------------------------------
            # # 从图像数据创建QImage  用来显示在QT
            # qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            #
            # # 使用新图像更新标签
            # self.image_label2.setPixmap(QPixmap(qimg))
            # # -------------------------------------


            # 计数
            self.cam2_count = self.cam2_count + 1
            print("相机2计数：",self.cam2_count, "\n")
            return OK_or_NG


        except queue.Empty:
            # print("相机1 erro :", e)
            # time.sleep(0.005)
            # print("相机1队列为空，没有可用的图像数据。")
            return "none"



    @torch.no_grad()  # 上下文管理器来禁止梯度计算
    def predict3(self):
        OK_or_NG = ""
        a = time.time()

        try:
            im3 = self.imgqueue3.get(True, 0.02)
            # print(im)
            img3 = im3[0]
            self.imgqueue3.queue.clear()

            if img3 is None:
                print('get none')
                img3 = cv2.imread(config.logo_img_path)

            elif img3.shape[2] != 3:
                img3 = cv2.cvtColor(img3, cv2.COLOR_GRAY2BGR)

            else:
                pass

            if self.auto_save:
                save_img(img3, "3")
                b = time.time()
                print("相机3取图时间：", b - a)
                yolo_result_img = img3

            else:
                list_xywh = []  # WH通过阈值删选后的目标框
                """调用检测算法"""
                results, yolo_result_img = self.trt_predict3.process_image(img3, self.conf_value)
                # cls_name_list = [item[0] for item in results]
                cls_name_list = results
                print("cam3:", cls_name_list, "\n")

                """后处理部分"""
                # names: ['ok_w', 'ng_w_s', 'ng', 'ok_b', 'ng_b_s', 'ok_y', 'ng_y_s', 'ng_r_s', 'ok_r']
                # 判断结果
                if results is None:
                    cv2.putText(yolo_result_img, "OK", (20, 250), 1, 10, (0, 255, 0), 10)
                    # 通讯发送结果
                    # self.send_msg.emit(f"工位{self.number}检测OK")
                    save_NG_img(img3, self.number3)
                    OK_or_NG = "OK"


                # *****2.有缺陷 ：缺陷大于阈值 NG， 缺陷小于阈值OK
                elif "ng" in cls_name_list:
                    cv2.putText(yolo_result_img, "NG", (20, 250), 1, 10, (0, 0, 255), 10)
                    OK_or_NG = "NG"
                    save_NG_img(img3, self.number3)

                else:
                    cv2.putText(yolo_result_img, "OK", (20, 250), 1, 10, (0, 255, 0), 10)
                    OK_or_NG = "OK"
                    #save_OK_img(img3, self.number3)

            # 将图像从BGR格式转换为RGB格式
            img_rgb = cv2.cvtColor(yolo_result_img, cv2.COLOR_BGR2RGB)
            h, w, ch = img3.shape
            bytes_per_line = ch * w
            # # 从图像数据创建QImage  用来显示在QT
            qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
            # # 发射信号而不是直接更新UI
            self.image_updated3.emit(qimg)

            # 计数
            self.cam3_count = self.cam3_count + 1
            print("相机3计数：",self.cam3_count, "\n")
            return OK_or_NG


        except queue.Empty:
            # print("相机3 erro :", e)
            # time.sleep(0.005)
            return "none"


    @torch.no_grad()  # 上下文管理器来禁止梯度计算
    def predict4(self):
        OK_or_NG = ""
        a = time.time()

        try:
            im4 = self.imgqueue4.get(True, 0.02)
            # print(im)
            img4 = im4[0]
            self.imgqueue4.queue.clear()

            if img4 is None:
                print('get none')
                img4 = cv2.imread(config.logo_img_path)

            elif img4.shape[2] != 3:
                img4 = cv2.cvtColor(img4, cv2.COLOR_GRAY2BGR)

            else:
                pass

            if self.auto_save:
                save_img(img4, "4")
                b = time.time()
                print("相机4取图时间：", b - a)
                yolo_result_img = img4

            else:
                list_xywh = []  # WH通过阈值删选后的目标框
                """调用检测算法"""
                results, yolo_result_img = self.trt_predict4.process_image(img4, self.conf_value)
                # cls_name_list = [item[0] for item in results]
                cls_name_list = results
                print("cam4:", cls_name_list, "\n")

                """后处理部分"""
                # names: ['ok', 'ng_s', 'ng', 'ok_yuan', 'ng_yuan_s', 'ng_yuan']
                # 判断结果
                if results is None:
                    cv2.putText(yolo_result_img, "OK", (20, 250), 1, 10, (0, 255, 0), 10)
                    # 通讯发送结果
                    # self.send_msg.emit(f"工位{self.number}检测OK")
                    save_NG_img(img4, self.number4)
                    OK_or_NG = "OK"


                # *****2.有缺陷 ：缺陷大于阈值 NG， 缺陷小于阈值OK
                elif "ng" in cls_name_list:
                    cv2.putText(yolo_result_img, "NG", (20, 250), 1, 10, (0, 0, 255), 10)
                    OK_or_NG = "NG"
                    save_NG_img(img4, self.number4)

                else:
                    cv2.putText(yolo_result_img, "OK", (20, 250), 1, 10, (0, 255, 0), 10)
                    OK_or_NG = "OK"
                    # save_OK_img(img4, self.number4)

            # 将图像从BGR格式转换为RGB格式
            img_rgb = cv2.cvtColor(yolo_result_img, cv2.COLOR_BGR2RGB)
            h, w, ch = img4.shape
            bytes_per_line = ch * w
            # 从图像数据创建QImage  用来显示在QT
            qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
            # 发射信号而不是直接更新UI
            self.image_updated4.emit(qimg)

            # # --------------------------------------
            # # 从图像数据创建QImage  用来显示在QT
            # qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            #
            # # 使用新图像更新标签
            # self.image_label4.setPixmap(QPixmap(qimg))
            # # -------------------------------------

            # 计数
            self.cam4_count = self.cam4_count + 1
            print("相机4计数：",self.cam4_count,"\n")
            return OK_or_NG


        except queue.Empty:

            # print("相机4 erro :")
            # time.sleep(0.005)
            return "none"




    def run(self):

        while self.is_running:
            time.sleep(0.01)

            # 判断相机队列是否为空-不为空再执行检测线程
            if not self.imgqueue1.empty() and not self.imgqueue2.empty() and not self.imgqueue3.empty() and not self.imgqueue4.empty():

                # -------创建线程池
                start_time = time.time()

                # 一次性提交所有任务
                futures = [
                    self.executor.submit(self.predict1),
                    self.executor.submit(self.predict2),
                    self.executor.submit(self.predict3),
                    self.executor.submit(self.predict4)
                ]

                # 等待所有任务完成
                # wait() 会阻塞直到所有Future对象完成
                done, not_done = wait(futures)

                # 所有任务完成后，获取结果
                results_ = [future.result() for future in futures]

                end_time = time.time()
                if end_time - start_time > 0.05:
                    print("$$$$$$$ 检测时间：", end_time - start_time, "-" * 40, "\n")
                    print("---", results_, "\n")

                # -----汇总结果
                if "NG" not in results_ and results_.count(None) != 4:
                    self.update_counts1("OK")  # 更新计数统计
                    # self.client.sendall("OK".encode('utf-8'))
                    pass

                # NG
                elif "NG" in results_:
                    # self.client.sendall("NG".encode('utf-8'))
                    # 结果发送
                    try:
                        self.client.write_multiple_registers(0, [2])
                    except Exception as e:
                        print("通讯数据发送数据异常", "\n")

                    self.update_counts1("NG")  # 更新计数统计

                    # timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    # print("**************发送时间：", timestamp_str, "\n")

            else:
                # print("*********两个相机未同时触发***********")
                pass


        # else:
        #     # time.sleep(0.02)
        #     pass


