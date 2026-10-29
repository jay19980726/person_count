import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
import datetime
from util import yolo_result
from pyModbusTCP.client import ModbusClient
from VM_client.VM_tcp import *

"""
modbusTCP 通讯
包含两级管理员登录
参数修改子界面
URL
"""



# 获取当前时间
def my_time():
    now = datetime.datetime.now()  # 获取当前时间信息（包括年、月、日、时、分、秒
    # print(f"{now.year}.{now.month}.{now.day}.{now.hour}.{now.minute}.{now.second}")
    time_day = f"{now.year}_{now.month}_{now.day}"  # 年月日
    time_second = f"{now.year}年{now.month}月{now.day}日{now.hour}时{now.minute}分{now.second}"  # 年、月、日、时、分、秒
    return time_second



# 给VM存图
def VM_save_img(cam_name, img):
    if cam_name == 1:
        cv2.imwrite(r"D:\VM_img\1.jpg", img)

    elif cam_name == 2:
        cv2.imwrite(r"D:\VM_img\2.jpg", img)

    elif cam_name == 3:
        cv2.imwrite(r"D:\VM_img\3.jpg", img)

    elif cam_name == 4:
        cv2.imwrite(r"D:\VM_img\4.jpg", img)

    elif cam_name == 5:
        cv2.imwrite(r"D:\VM_img\5.jpg", img)

    elif cam_name == 6:
        cv2.imwrite(r"D:\VM_img\6.jpg", img)



def yolo_predict1(cam, cam_name, client_socket, addText, conf_value, W_value, H_value, image_label, vm_client_socket, vm_client_address, vm_server_socket):
    im = cam.getFrame()
    if im is None:
        print('get none')
        # im = np.zeros([100, 100, 3], dtype=np.uint8)
        im = cv2.imread(r"D:\wg\AI_project\24.ball\v8\yolo-xml_to_txt\dataset\VOCdevkit\image\Image_20240605152605063.jpg")

    elif im.shape[2] != 3:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        # 给VM存图
        VM_save_img(cam_name, im)
    else:
        # 给VM存图
        VM_save_img(cam_name, im)
        pass

    # 发送寸土完成
    if cam_name ==1:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name ==2:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name ==3:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name ==4:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name ==5:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name ==6:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)



    """
    ----检测算法调用
    """
    print("AI检测工位1启动")
    list_xywh = []  # WH通过阈值删选后的目标框
    list_cls_name = []  # WH通过阈值删选后的目标类型
    xywh, boxs, cls_name_list, conf, yolo_result_img = yolo_result.yolo_predict(im, conf_value)

    "判断结果"
    # ******1.无缺陷  ---ok
    if cls_name_list is None:
        OKorNG = "OK"
        # 文本框显示信息
        addText(f"检测状态:OK(无缺陷)--检测时间:{my_time()}")
        cv2.putText(yolo_result_img, "OK", (20, 250), 1, 25, (0, 255, 0), 4)
        #--- 通讯发送 1：良品
        data_ok = 1
        client_socket.write_multiple_registers(2, [data_ok])  # 从寄存器 2 开始写, 写入的值是 1


    # *****2.有缺陷 ：缺陷大于阈值 NG， 缺陷小于阈值OK
    else:
        for idx, vlue in enumerate(xywh):
            x, y, w, h = vlue

            if w > W_value and h > H_value:   # WH都大于阈值的留下来
                list_xywh.append((x, y, w, h))
                # xywh 与 cls_name 的索引是对应的，通过xywh索引去拿对应的目标类别
                list_cls_name.append(cls_name_list[idx])


        # 再判断阈值 筛选后的list_xywh
        # *****无缺陷 OK
        if len(list_xywh) == 0:
            OKorNG = "OK"
            # 文本框显示信息
            addText(f"检测状态:OK(阈值)--检测时间:{my_time()}")
            cv2.putText(yolo_result_img, "OK", (20, 250), 1, 25, (0, 255, 0), 4)
            # 通讯发送 1：良品  ,最大缺陷面积
            array_xywh = np.array(xywh)
            w_ = array_xywh[:, 2]
            h_ = array_xywh[:, 3]
            max_w = np.max(w_)
            max_h = np.max(h_)
            "通讯发送部分"
            data_ok = "1"+"—"+str(max_w)+","+str(max_h)
            client_socket.write_multiple_registers(3, [data_ok])  # 从寄存器 3 开始写, 写入的值是 1



        # *****有缺陷
        else:

            # 判断筛选后的缺陷类型  ['1', '2', '3'] 1：凹坑，3：裂痕
            if "1" in list_cls_name:
                OKorNG = "NG"
                # 文本框显示信息
                addText(f"检测状态:NG--检测时间:{my_time()}")
                cv2.putText(yolo_result_img, "NG", (20, 250), 1, 25, (0, 0, 255), 4)
                aokeng_idx = []
                aokeng_xywh = []
                aokeng_area = []
                for idx, vlue in enumerate(list_cls_name):
                    if vlue == '1':
                        aokeng_idx.append(idx)
                # print(aokeng_idx)
                for xywh_idx in aokeng_idx:
                    aokeng_xywh.append(list_xywh[xywh_idx])

                # 凹坑面积放入列表
                for aokeng in aokeng_xywh:
                    aokeng_area.append(int(aokeng[2])*int(aokeng[3]))  # 面积
                array_aokeng_area = np.array(aokeng_area)  # 转numpy
                max_aokeng_area = np.max(array_aokeng_area)  # 求最大面积

                array_aokeng_xywh = np.array(aokeng_xywh)
                w_aokeng = array_aokeng_xywh[:, 2]
                h_akkeng = array_aokeng_xywh[:, 3]
                max_w = np.max(w_aokeng)
                max_h = np.max(h_akkeng)

                "通讯发送部分"
                # 通讯发送   2：凹坑  最大凹坑 W-H
                # data_ng = "2" + "," + str(max_w) + "," + str(max_h)+"///"
                data_ng = "2" + "-" + str(max_aokeng_area) + "///"
                client_socket.write_multiple_registers(4, [2])  # 从寄存器 4 开始写, 写入的值是 1



            if "2" in list_cls_name:  # 裂痕
                OKorNG = "NG"
                # 文本框显示信息
                addText(f"检测状态:NG--检测时间:{my_time()}")
                cv2.putText(yolo_result_img, "NG", (20, 250), 1, 25, (0, 0, 255), 4)

                liehen_idx = []
                liehen_xywh = []
                liehen_area = []
                for idx, vlue in enumerate(list_cls_name):
                    if vlue == '2':
                        liehen_idx.append(idx)
                for xywh_idx in liehen_idx:
                    liehen_xywh.append((list_xywh[xywh_idx]))

                # 裂痕面积放入列表
                for liehen in liehen_xywh:
                    liehen_area.append(int(liehen[2])*int(liehen[3]))

                # 转numpy
                array_liehen_area = np.array(liehen_area)
                max_liehen_area = np.max(array_liehen_area)  # 最大面积

                array_lieheng_xywh = np.array(liehen_xywh)
                w_liehen = array_lieheng_xywh[:, 2]
                h_liehen = array_lieheng_xywh[:, 3]
                max_w2 = np.max(w_liehen)
                max_h2 = np.max(h_liehen)
                "通讯发送部分"
                # 通讯发送 3：裂痕  裂痕最大W-H
                # data_ng2 = "3" + "," + str(max_w2) + "," + str(max_h2)+"///"
                data_ng2 = "3" + "-" + str(max_liehen_area) + "///"
                client_socket.write_multiple_registers(5, [data_ng2])  # 从寄存器 5 开始写, 写入的值是 1


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
    del im



#
# def asv(cam_name):
#     if cam_name == 1:
#
#         VM_write(cam_name)
#
#     if cam_name == 2:
#
#         VM_write(cam_name)
#
#     if cam_name == 3:
#
#         VM_write(cam_name)
#
#     if cam_name == 4:
#
#         VM_write(cam_name)
#
#     if cam_name == 5:
#
#         VM_write(cam_name)
#
#     if cam_name == 6:
#
#         VM_write(cam_name)
#
# if __name__ == '__main__':
#     VM_socket()
#     # asv(1)
#     VM_read()