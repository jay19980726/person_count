"""
  YOLO检测方法及后处理
  """
import time

import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
import datetime
from util import yolo_result
from PyQt5.QtGui import QPixmap, QTransform




# 获取当前时间
def my_time():
    now = datetime.datetime.now()  # 获取当前时间信息（包括年、月、日、时、分、秒
    # print(f"{now.year}.{now.month}.{now.day}.{now.hour}.{now.minute}.{now.second}")
    time_day = f"{now.year}_{now.month}_{now.day}"  # 年月日
    time_second = f"{now.year}年{now.month}月{now.day}日{now.hour}时{now.minute}分{now.second}"  # 年、月、日、时、分、秒
    return time_second




def yolo_predict1(cam, image_label):
    start_time = time.time()
    im = cam.getFrame()
    if im is None:
        print('get none')
        # im = np.zeros([100, 100, 3], dtype=np.uint8)
        im = cv2.imread(
            r"D:\wg\AI_project\24.ball\v8\yolo-xml_to_txt\dataset\VOCdevkit\image\Image_20240605165617453.jpg")

    elif im.shape[2] != 3:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    else:
        pass



    """
    ----检测算法调用
    1.整体检测数个数（切片，检测4次）
    """
    print("AI检测工位1启动")


    "******1.算法检测--完整"
    xywh, a, cls_name_list, conf, cv_img, yolo_result_img = yolo_result.yolo_predict(im, 0.5)
    end_time = time.time()
    # addText(f"检测时间:{end_time-start_time}")

    "判断结果"
    # ******
    if xywh is None:    # 无产品
        OKorNG = ""
        # 文本框显示信息
        # addText(f"检测状态:OK(无缺陷)--检测时间:{my_time()}")
        cv2.putText(yolo_result_img, "not target", (20, 250), 1, 10, (0, 255, 0), 10)



    # *****  数个数
    else:

        cv2.putText(yolo_result_img, "NG", (20, 250), 1, 10, (0, 0, 255), 10)


    # 将图像从BGR格式转换为RGB格式
    img_rgb = cv2.cvtColor(yolo_result_img, cv2.COLOR_BGR2RGB)

    h, w, ch = im.shape
    bytes_per_line = ch * w

    # 从图像数据创建QImage  用来显示在QT
    qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

    # 使用新图像更新标签
    image_label.setPixmap(QPixmap(qimg))
    image_label.setScaledContents(True)  # 图像自适应大小

    # 使用完后删除数组引用
    del im, yolo_result_img,





