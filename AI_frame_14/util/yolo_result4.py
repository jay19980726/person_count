import os
import threading

import cv2
import numpy as np
import torch.cuda
import yaml
from ultralytics import YOLO
from app2.config import *

from MVSCam import MVSCam




# # 加载YOLOv8模型
model = YOLO(models["path2"])
print("*****************************************")
print("loader model4")
print("*****************************************\n")

"""
yolo 推理及后处理
"""


# 在模块级别创建一个锁 防止多线程同时调用情
yolo_predict_lock = threading.Lock()


def yolo_predict4(cv_img, conf, iou):

    # 使用锁
    with yolo_predict_lock:  # 在多线程或多进程环境中，为了避免多个线程或进程同时访问共享资源而导致的问题，可以使用锁（Lock）

        # 定义容器存放抠出的目标区域
        imglist = []

        # yolo模型做侦测
        result = model(source=cv_img, save=False, conf=conf, iou=iou, imgsz=640)
        # print(type(result))
        # print(len(result))   #  YOLO有没有检测到目标 ，输出长度都1

        # img = result[0].orig_img   # 从检测结果中拿出原图片

        # 判断当前有没有侦测到目标，没有就返回None, 有目标就继续往下执行
        if len(result[0].boxes) != 0:     # 侦测到结果的坐标 （侦测到目标result[0].boxes的长度就是目标个数， ，没有侦测到目标result[0].boxes的长度就是0）
            # print(result[0].boxes)
            # print(len(result[0].boxes))
            yolo_result_img = result[0].plot()

            for r in result:  # r=result[0]
                # print(r.boxes)  # 打印包含检测边界框的Boxes对象
                # num = r.boxes
                # print(len(num))

                # ------总类别
                target = r.names
                # ------当前目标类别
                cls = r.boxes.cls.cpu().numpy()
                # print("类别：", cls)
                # ------当前目标置信度
                conf = r.boxes.conf.cpu().numpy()
                # print("置信度：", conf)
                # 目标的框xyxy
                boxs = r.boxes.xyxy.cpu().numpy()

                cls_name_list = []   # 存放类别名称的列表
                for idx in cls:
                    cls_name = target[idx]
                    cls_name_list.append(cls_name)

                # print(cls_name_list)


                # print(target,"-----------------------------------")

                # for box in num:
                #     box=box.xyxy[0]  # tensor([1122.2811, 1944.4788, 1265.3495, 2043.8615], device='cuda:0')
                #     # print(box)
                #     box_numpy = box.cpu().numpy()   # tensor 转numpy
                #     # print(box_numpy)
                #
                #     # 抠出目标区域
                #     img_obj = img[int(box_numpy[1]):int(box_numpy[3]), int(box_numpy[0]):int(box_numpy[2])]
                #
                #     imglist.append(img_obj)
                #
                #     # cv2.imshow("1", img_obj)
                #     # cv2.waitKey(0)
                #     # cv2.destroyAllWindows()

            return boxs, cls_name_list, conf, yolo_result_img  # 目标框的列表，  yolo预测结果


        # 没有目标就返回None
        else:
            print("model未识别到目标")
            return None, None, None, cv_img

print("模型4预热")
img = np.zeros((640,640,3))
yolo_predict4(img, 0.5, 0.7)

"""
设置单类别置信度
cls:类别列表
conf:类别对应的置信度
"""
def cls_conf(cls, conf):
    # 设置每个类别的阈值
    thresholds = {'person': 0.9, 'dog': 0.85, 'cat': 0.6, 'handbag': 0.75}
    # 筛选类别
    filtered_categories = [category for category, confidence in zip(cls, conf) if
                           confidence >= thresholds.get(category, 0.5)]
    print("筛选后的类别:", filtered_categories)

    return filtered_categories


if __name__ == '__main__':
    # result = model(r"C:\Users\Owen\Desktop\111\MV-CE200-11UC (00K88301994)\Video_20240227161632307.avi")

    # cls, conf, resultimg = yolo_predict(r"C:\Users\Owen\Desktop\111\MV-CE200-11UC (00K88301994)\Video_20240227161632307.avi")
    # cls = list(cls)
    # conf = list(conf)
    # print("原来的类别:", cls)
    #
    # cls_ = cls_conf(cls, conf)

    pass





    # path = r"C:\Users\Owen\Desktop\MV-CE200-11UC (00K88301994)\Video_20231229174225966.avi"
    # image_name = os.listdir(path)
    # for img in image_name:
    #     image_path = os.path.join(path, img)
    #     yolo_predict(image_path)



    # cam = MVSCam(devinfo="00K88301994")   # 这一行代码创建了一个名为 cam 的相机对象，并使用 MVSCam 类初始化它。devinfo 参数用于指定要连接的相机的设备信息，通常包括相机的 IP 地址或其他连接信息
    # cam.open(0)                             # ret = cam.open(0)：这一行代码尝试打开相机连接。cam.open(0) 方法通常返回一个表示连接状态的返回值，例如 0 表示成功
    # for i in range(1000000000000):
    #     im = cam.getFrame()
    #     if im is not None:
    #         # im = cv2.resize(im, (640, 480))
    #         # cv2.imshow('im', im)
    #
    #         target, img = yolo_predict(im)
    #         # print(im.shape)
    #         # print(im.shape)
    #         img = cv2.resize(img, (1100, 850))
    #         cv2.imshow('ci', img)
    #         cv2.waitKey(100)
    #
    # cam.stop()
    #
    # pass







"""
YOLO对象生成器
"""
# def yolo_stream_True(img):
#     results = model(source=img, save=False, stream=True, conf=0.65)
#
#     yolo_img_list= []
#     for result in results:
#         boxes = result.boxes  # 用于存储边界框（bounding box）输出的 Boxes 对象
#         masks = result.masks  # 用于存储分割遮罩（segmentation masks）输出的 Masks 对象
#         keypoints = result.keypoints  # 用于存储姿势（pose）输出的 Keypoints 对象
#         probs = result.probs  # 用于存储分类（classification）输出的概率（probability）对象
#
#         # 预测狂的坐标
#         boxes_xyxy = boxes.xyxy.cpu().numpy()   # 从GPU解绑并转为numpy
#
#         # 判断yolo有没有预测结果
#         if len(boxes_xyxy ) != None:
#             yolo_plot_img = img
#             # 遍历预测框
#             for one_boxe in boxes_xyxy:
#                 # 将预测结果从原图上切下来
#                 img_obj = img[int(one_boxe[1]):int(one_boxe[3]), int(one_boxe[0]):int(one_boxe[2])]
#                 yolo_img_list.append(img_obj)
#                 # 绘制结果
#                 cv2.rectangle(yolo_plot_img, (int(one_boxe[0]), int(one_boxe[1])), (int(one_boxe[2]), int(one_boxe[3])), (255,0,0), 2)
#
#             return yolo_img_list,yolo_plot_img   # 预测框的集合和绘制的结果
#
#
#
#         else:
#             return None, None





"""
计算YOLO检测耗时
"""
# def camera_fps():
#     cap = cv2.VideoCapture(r"C:\Users\DELL\Desktop\gq.mp4")  # 打开默认摄像头，你也可以指定摄像头索引来打开其他摄像头
#
#     if not cap.isOpened():
#         print("无法打开摄像头")
#         return
#
#
#     while True:
#         ret, frame = cap.read()  # 从摄像头读取一帧图像
#
#         # YOLO 做检测
#         start_time = time.time()   # 开始时间
#         img_list, img= yolo_stream_True(frame)
#         end_time = time.time()
#         print(f"yolo所用时间{end_time-start_time}")
#
#
#         cv2.imshow("摄像头", img)  # 显示摄像头画面
#
#
#         input_key = cv2.waitKey(1)
#         if input_key == ord('q'):
#             break  # 如果用户按下'q'键，退出循环
#
#
#     cap.release()  # 释放摄像头资源
#     cv2.destroyAllWindows()  # 关闭所有打开的窗口
#
# if __name__ == "__main__":
#     pass
#     camera_fps()  # 调用主函数
#
#



