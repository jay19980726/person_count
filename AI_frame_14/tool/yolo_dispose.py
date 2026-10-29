"""
  YOLO检测方法及后处理
  TCP/ip  通讯

  """
import threading
import time

import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
import datetime

from VM_client.VM_tcp import VM_write
from util import yolo_result
from util.save_OKorNG_img import *
from util.auto_remove_Imgfile import *

"""
标定比例  ratio
"""
# ratio_w = 85/5472
# ratio_h = 62/3648
ratio_w = 72/5472
ratio_h = 68/3648
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



def yolo_predict1(cam, cam_name, client_socket, addText, conf_value, W_value, H_value, image_label_list, vm_client_socket, vm_client_address, vm_server_socket, result_queue):

    start_time = time.time()
    im = cam.getFrame()
    if im is None:
        print('get none')
        # im = np.zeros([100, 100, 3], dtype=np.uint8)
        im = cv2.imread("logo_image/exe_logo.ico")

    elif im.shape[2] != 3:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        # 给VM存图
        VM_save_img(cam_name, im)
    else:
        # 给VM存图
        VM_save_img(cam_name, im)
        pass

    # 发送存图完成
    if cam_name == 1:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name == 2:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name == 3:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name == 4:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name == 5:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    if cam_name == 6:
        VM_write(cam_name, vm_client_socket, vm_client_address, vm_server_socket)

    end_time = time.time()
    print(f"相机{cam_name}取图存图时间:", end_time-start_time)
    # print("触发VM时间：", my_time())


    """
    ----检测算法调用
    """
    print(f"AI检测工位{cam_name}启动")
    list_xywh = []  # WH通过阈值删选后的目标框
    list_cls_name = []  # WH通过阈值删选后的目标类型
    xywh, boxs, cls_name_list, conf, cv_img, yolo_result_img = yolo_result.yolo_predict(im, conf_value)

    # # 保存图片线程--
    # # save_img(cv_img, str(cam_name))
    # save_img_th = threading.Thread(target=save_img, args=(cv_img, str(cam_name)))
    # save_img_th.start()
    #
    # # 自动删图片线程--
    # # auto_remove(10, str(cam_name))
    # auto_remove_th = threading.Thread(target=auto_remove, args=(10, str(cam_name)))
    # auto_remove_th.start()

    # 结束检测时间
    end_predict_time = time.time()
    # print("cls", cls_name_list)



    # 什么都没有，空拍
    if cls_name_list is None:
        predict_time = str(format(end_predict_time - start_time, '.2f'))
        predict_time = predict_time.rjust(4, '0')
        data_ok1 = f'{cam_name}-1-0-4-0000-0000-0000-0000-0000-{predict_time[-4:]}'  # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
        # client_socket.sendall(data_ok1.encode("utf-8"))
        result_queue.put(data_ok1)
    #     return
    # else:
    #     pass



    # ******1.无产品--没有球只有吸盘-> NG
    elif "ball" not in cls_name_list and "tool" in cls_name_list:    #and "tool" in cls_name_list:
        # OKorNG = "NG"
        # 文本框显示信息
        addText(f"检测状态:{cam_name}号相机缺球--检测时间:{my_time()}")
        cv2.putText(yolo_result_img, "no target", (20, 270), 1, 25, (0, 0, 255), 10)
        # &&&&保存NG图片线程
        save_no_target_th = threading.Thread(target=save_NG_img, args=(yolo_result_img, str(cam_name)))
        save_no_target_th.start()

        # --- 通讯发送  检测结果(0:不良;1∶良品)
        # 固定四位字符--检测时间
        predict_time = str(format(end_predict_time - start_time, '.2f'))
        predict_time = predict_time.rjust(4, '0')
        data_ok1 = f'{cam_name}-1-0-4-0000-0000-0000-0000-0000-{predict_time[-4:]}'  # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
        # client_socket.sendall(data_ok1.encode("utf-8"))
        # 结果放入队列
        result_queue.put(data_ok1)

        # 等待存图线程结束
        save_no_target_th.join()


    # ******   大面积破损
    elif ("ball" not in cls_name_list and "tool" not in cls_name_list) or "damaged_big" in cls_name_list:
        # OKorNG = "NG"
        # 文本框显示信息
        addText(f"检测状态:{cam_name}号相机缺球--检测时间:{my_time()}")
        cv2.putText(yolo_result_img, "NG", (20, 270), 1, 25, (0, 0, 255), 10)
        # &&&&保存NG图片线程
        save_damaged_big_th = threading.Thread(target=save_NG_img, args=(yolo_result_img, str(cam_name)))
        save_damaged_big_th.start()

        # --- 通讯发送  检测结果(0:不良;1∶良品)
        # 固定四位字符--检测时间
        predict_time = str(format(end_predict_time - start_time, '.2f'))
        predict_time = predict_time.rjust(4, '0')
        data_ng = f'{cam_name}-1-0-2-9999-9999-9999-9999-9999-{predict_time[-4:]}'  # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
        # client_socket.sendall(data_ok1.encode("utf-8"))
        # 结果放入队列
        result_queue.put(data_ng)

        # 等待存图线程结束
        save_damaged_big_th.join()




    # 正常有球情况
    # *****2.有缺陷 ：缺陷大于阈值 NG， 缺陷小于阈值OK
    elif "ball" in cls_name_list:
        for idx, vlue in enumerate(xywh):
            x, y, w, h = vlue

            w = w*ratio_w
            h = h*ratio_h
            if w > W_value and h > H_value:  # WH都大于阈值的留下来
                list_xywh.append((x, y, w, h))
                # xywh 与 cls_name 的索引是对应的，通过xywh索引去拿对应的目标类别
                list_cls_name.append(cls_name_list[idx])

        # print(list_cls_name, "类别名---------------------")



        # 再判断阈值 筛选后的list_xywh
        """ *****1.---没有缺陷，只有球体-> OK"""
        # if len(list_xywh) == 1 and "ball" == list_cls_name[0]:
        if "ball" in list_cls_name and "damaged" not in list_cls_name and "crack" not in list_cls_name:
            # OKorNG = "OK"
            # 文本框显示信息
            addText(f"检测状态:{cam_name}号相机OK(阈值)--检测时间:{my_time()}")
            cv2.putText(yolo_result_img, "OK", (20, 250), 1, 25, (0, 255, 0), 10)
            # &&&&保存OK图片线程
            save_OK_th = threading.Thread(target=save_OK_img, args=(cv_img, str(cam_name)))
            save_OK_th.start()

            # 通讯发送 1：良品  ,最大缺陷面积
            # array_xywh = np.array(xywh)  # 转numpy
            # # 最大面积列表
            # max_area_list = []
            # for x_y_w_h in array_xywh:
            #     x, y, w, h, = x_y_w_h
            #     max_area_list.append(int(w)*int(h))
            # array_max_area = np.array(max_area_list)   # 转numpy
            # max_area = np.max(array_max_area)
            #
            # w_ = array_xywh[:, 2]
            # h_ = array_xywh[:, 3]
            # max_w = str(np.max(w_))
            # max_h = str(np.max(h_))

            # 固定四位字符--检测时间
            predict_time = str(format(end_predict_time - start_time, '.2f'))
            predict_time = predict_time.rjust(4, '0')
            # # 固定四位字符--凹坑长，宽
            # max_w = max_w.rjust(4, "0")
            # max_h = max_h.rjust(4, "0")

            "通讯发送部分"
            # data_ok2 = "1" + "-" + str(max_w) + "," + str(max_h)
            data_ok2 = f'{cam_name}-1-1-0-0000-0000-0000-0000-0000-{predict_time[-4:]}'  # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
            # client_socket.sendall(data_ok2.encode('utf-8'))
            # 结果放入队列
            result_queue.put(data_ok2)

            # 等待存图线程结束
            save_OK_th.join()


        # *****2.有缺陷----凹坑，裂痕
        else:
            # 判断筛选后的缺陷类型  ['ball', 'damaged', 'tool']
            # print(list_cls_name, "123456789")
            """-----只有凹坑"""
            if "damaged" in list_cls_name and "crack" not in list_cls_name:     # and "3" not in list_cls_name:
                # OKorNG = "NG"
                # 文本框显示信息
                addText(f"检测状态:{cam_name}号相机NG--检测时间:{my_time()}")
                cv2.putText(yolo_result_img, "NG", (20, 250), 1, 25, (0, 0, 255), 10)
                # &&&&保存NG图片线程
                save_NG_th = threading.Thread(target=save_NG_img, args=(yolo_result_img, str(cam_name)))
                save_NG_th.start()

                aokeng_idx = []
                aokeng_xywh = []
                aokeng_area = []
                for idx, vlue in enumerate(list_cls_name):
                    if vlue == 'damaged':
                        aokeng_idx.append(idx)
                # print(aokeng_idx)
                for xywh_idx in aokeng_idx:
                    aokeng_xywh.append(list_xywh[xywh_idx])

                # 凹坑面积放入列表
                # for aokeng in aokeng_xywh:
                #     aokeng_area.append(int(aokeng[2]) * int(aokeng[3]))  # 面积
                # array_aokeng_area = np.array(aokeng_area)  # 转numpy
                # max_aokeng_area = np.max(array_aokeng_area)  # 求最大面积

                array_aokeng_xywh = np.array(aokeng_xywh)
                w_aokeng = array_aokeng_xywh[:, 2]
                h_akkeng = array_aokeng_xywh[:, 3]
                max_w = np.max(w_aokeng)
                max_h = np.max(h_akkeng)

                # 固定四位字符--检测时间
                predict_time = str(format(end_predict_time - start_time, '.2f'))
                predict_time = predict_time.rjust(4, '0')
                # 固定四位字符--凹坑长，宽
                max_w = str(format(max_w * ratio_w, '.1f'))  # 保留一位小鼠
                max_h = str(format(max_h * ratio_h, '.1f'))  # 保留一位小鼠
                max_w = max_w.rjust(4, "0")
                max_h = max_h.rjust(4, "0")

                "通讯发送部分"
                # 通讯发送   2：凹坑  最大凹坑 W-H
                # data_ng1 = "2" + "," + str(max_w) + "," + str(max_h)+"///"
                # data_ng1 = "2" + "-" + str(max_aokeng_area) + "///"
                data_ng1 = f'{cam_name}-1-0-2-0000-{max_w}-{max_h}-0000-0000-{predict_time[-4:]}'  # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
                # client_socket.sendall(data_ng1.encode('utf-8'))
                result_queue.put(data_ng1)

                # 等待存图线程结束
                save_NG_th.join()



            ## 只有裂痕
            elif "crack" in list_cls_name and "damaged" not in list_cls_name:   # 裂痕
                OKorNG = "NG"
                # 文本框显示信息
                addText(f"检测状态:NG--检测时间:{my_time()}")
                cv2.putText(yolo_result_img, "NG", (20, 250), 1, 25, (0, 0, 255), 10)

                liehen_idx = []
                liehen_xywh = []
                liehen_area = []
                for idx, vlue in enumerate(list_cls_name):
                    if vlue == 'crack':
                        liehen_idx.append(idx)
                for xywh_idx in liehen_idx:
                    liehen_xywh.append((list_xywh[xywh_idx]))

                # 裂痕面积放入列表
                # for liehen in liehen_xywh:
                #     liehen_area.append(int(liehen[2]) * int(liehen[3]))

                # 转numpy
                # array_liehen_area = np.array(liehen_area)
                # max_liehen_area = np.max(array_liehen_area)  # 最大面积

                array_lieheng_xywh = np.array(liehen_xywh)
                w_liehen = array_lieheng_xywh[:, 2]
                h_liehen = array_lieheng_xywh[:, 3]
                max_w2 = np.max(w_liehen)
                max_h2 = np.max(h_liehen)

                # 固定四位字符--检测时间
                predict_time = str(format(end_predict_time - start_time, '.2f'))
                predict_time = predict_time.rjust(4, '0')
                # 固定四位字符--裂痕长，宽
                max_w2 = str(format(max_w2 * ratio_w, '.1f'))  # 保留一位小鼠
                max_h2 = str(format(max_h2 * ratio_h, '.1f'))  # 保留一位小鼠
                max_w2 = max_w2.rjust(4, "0")
                max_h2 = max_h2.rjust(4, "0")

                "通讯发送部分"
                # 通讯发送 3：裂痕  裂痕最大W-H
                # data_ng2 = "3" + "," + str(max_w2) + "," + str(max_h2)+"///"
                # data_ng2 = "3" + "-" + str(max_liehen_area) + "///"
                data_ng2 = f'{cam_name}-0-0-3-0000-0000-0000-{max_w2}-{max_h2}-{predict_time[-4:]}'   # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
                # client_socket.sendall(data_ng2.encode('utf-8'))
                result_queue.put(data_ng2)



            #""" ----凹坑和裂痕都有(只发凹坑)"""
            else:
                OKorNG = "NG"
                # 文本框显示信息
                addText(f"检测状态:NG--检测时间:{my_time()}")
                cv2.putText(yolo_result_img, "NG", (20, 250), 1, 25, (0, 0, 255), 10)

                liehen_aokeng_idx = []
                liehen_aokeng_xywh = []
                liehen_aokeng_area = []
                for idx, vlue in enumerate(list_cls_name):
                    if vlue == 'damaged' or vlue == "crack":
                        liehen_aokeng_idx.append(idx)
                for xywh_idx in liehen_aokeng_idx:
                    liehen_aokeng_xywh.append((list_xywh[xywh_idx]))

                # 裂痕面积放入列表
                # for liehen_aokeng in liehen_aokeng_xywh:
                #     liehen_aokeng_area.append(int(liehen_aokeng[2]) * int(liehen_aokeng[3]))

                # 转numpy
                # array_liehen_aokeng_area = np.array(liehen_aokeng_area)
                # max_liehen_aokeng_area = np.max(array_liehen_aokeng_area)  # 最大面积

                array_lieheng_aokeng_xywh = np.array(liehen_aokeng_xywh)
                # print('*********',array_lieheng_aokeng_xywh)
                w_liehen_aokeng = array_lieheng_aokeng_xywh[:, 2]
                h_liehen_aokeng = array_lieheng_aokeng_xywh[:, 3]
                max_w3 = np.max(w_liehen_aokeng)
                max_h3 = np.max(h_liehen_aokeng)

                # 固定四位字符--检测时间
                predict_time = str(format(end_predict_time - start_time, '.2f'))
                predict_time = predict_time.rjust(4, '0')
                # 固定四位字符--裂痕长，宽
                max_w3 = str(format(max_w3 * ratio_w, '.1f'))  # 保留一位小鼠
                max_h3 = str(format(max_h3 * ratio_h, '.1f'))  # 保留一位小鼠
                max_w3 = max_w3.rjust(4, "0")
                max_h3 = max_h3.rjust(4, "0")

                "通讯发送部分"
                # 通讯发送 2：凹坑  裂痕最大W-H
                # data_ng2 = "3" + "," + str(max_w2) + "," + str(max_h2)+"///"
                # data_ng2 = "3" + "-" + str(max_liehen_area) + "///"
                data_ng2 = f'{cam_name}-0-0-2-0000-0000-0000-{max_w3}-{max_h3}-{predict_time[-4:]}'   # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
                # client_socket.sendall(data_ng2.encode('utf-8'))
                result_queue.put(data_ng2)



    else:
        print("********逻辑判断错误1")
        pass



    # 将图像从BGR格式转换为RGB格式
    img_rgb = cv2.cvtColor(yolo_result_img, cv2.COLOR_BGR2RGB)
    h, w, ch = im.shape
    bytes_per_line = ch * w

    # 从图像数据创建QImage  用来显示在QT
    qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

    # 判断显示的画面是几号相机
    if cam_name == 1:
        # 使用新图像更新标签
        image_label_list[0].setPixmap(QPixmap(qimg))
        image_label_list[0].setScaledContents(True)  # 图像自适应大小

    if cam_name == 2:
        # 使用新图像更新标签
        image_label_list[1].setPixmap(QPixmap(qimg))
        image_label_list[1].setScaledContents(True)  # 图像自适应大小

    if cam_name == 3:
        # 使用新图像更新标签
        image_label_list[2].setPixmap(QPixmap(qimg))
        image_label_list[2].setScaledContents(True)  # 图像自适应大小

    if cam_name == 4:
        # 使用新图像更新标签
        image_label_list[3].setPixmap(QPixmap(qimg))
        image_label_list[3].setScaledContents(True)  # 图像自适应大小

    if cam_name == 5:
        # 使用新图像更新标签
        image_label_list[4].setPixmap(QPixmap(qimg))
        image_label_list[4].setScaledContents(True)  # 图像自适应大小

    if cam_name == 6:
        # 使用新图像更新标签
        image_label_list[5].setPixmap(QPixmap(qimg))
        image_label_list[5].setScaledContents(True)  # 图像自适应大小


    # 等待线程结束
    # save_img_th.join()
    # auto_remove_th.join()

    # 使用完后删除数组引用
    del im

