import datetime
import os

import cv2
from app2 import config
from app2.config import *

"""
保存OK，NG图片，
创建OK文件夹，以OK图片为例，以年月日为子文件夹（OK/2020_10_10/），将每一秒检测的图片存入
"""



# 获取当前时间
def my_time():
    now = datetime.datetime.now()  # 获取当前时间信息（包括年、月、日、时、分、秒
    # print(f"{now.year}.{now.month}.{now.day}.{now.hour}.{now.minute}.{now.second}")
    time_day = f"{now.year}_{now.month}_{now.day}" # 年月日
    time_second = f"{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}"   # 年、月、日、时、分、秒
    return time_day, time_second



# 创建文件夹存放OK图像
def save_OK_img(img, cam_file):      # 保存图片， 文件夹名称（相机名称）
    root_path = save_images["root"] + "\\" + cam_file   # 保存图像的根路径 D:data/....  自定义修改

    day, img_name = my_time()    # NG/2023_10_10/2023_10_10_13_12_13.JPG
    # 压缩图片
    # img_sim = cv2.resize(img, (1500, 950))
    img_sim = img

    if not os.path.exists(os.path.join(root_path,"OK", day)):  # 判断OK文件夹  root_path/NG/2023_10_10  是否存在，
        # 如果文件夹不存在，创建它和中间目录
        os.makedirs(os.path.join(root_path,"OK", day))  # root_path/OK/2023_10_10
        # 当天文件夹完整路径
        day_file_path = os.path.join(root_path,"OK", day)
        # 保存图像的完整路径：  root_path/OK/2023_10_10/2023_10_10_13_12_13
        save_img_path = os.path.join(day_file_path,img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)   # root_path/OK/2023_10_10/2023_10_10_13_12_13.jpg


    else:  # 如果存在就直接保存
        day_file_path = os.path.join(root_path,"OK", day)
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)

    # print("OK图片保存成功")





# 创建文件夹存放NG图像
def save_NG_img(img, cam_file):
    root_path = save_images["root"] + "\\" + cam_file    # 保存图像的根路径 D:data/....

    day, img_name = my_time()  # NG/2023_10_10/2023_10_10_13_12_13.JPG
    # 压缩图片
    # img_sim = cv2.resize(img, (1500, 950))
    img_sim = img

    if not os.path.exists(os.path.join(root_path, "NG", day)):  # 判断NG文件夹  root_path/NG/2023_10_10  是否存在，
        # 如果文件夹不存在，创建它和中间目录
        os.makedirs(os.path.join(root_path, "NG", day))  # root_path/NG/2023_10_10
        # 当天文件夹完整路径
        day_file_path = os.path.join(root_path, "NG", day)
        # 保存图像的完整路径：  root_path/NG/2023_10_10/2023_10_10_13_12_13
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)  # root_path/NG/2023_10_10/2023_10_10_13_12_13.jpg


    else:  # 如果存在就直接保存
        day_file_path = os.path.join(root_path, "NG", day)
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)

    # print("NG图片保存成功")



# 创建文件夹存放OK图像
def save_OK_img2(img, cam_file):      # 保存图片， 文件夹名称（相机名称）
    root_path = save_images["root"] + "\\" + cam_file   # 保存图像的根路径 D:data/....  自定义修改

    day, img_name = my_time()    # NG/2023_10_10/2023_10_10_13_12_13.JPG
    # 压缩图片
    # img_sim = cv2.resize(img, (1500, 950))
    img_sim = img

    if not os.path.exists(os.path.join(root_path,"OK", day)):  # 判断OK文件夹  root_path/NG/2023_10_10  是否存在，
        # 如果文件夹不存在，创建它和中间目录
        os.makedirs(os.path.join(root_path,"OK", day))  # root_path/OK/2023_10_10
        # 当天文件夹完整路径
        day_file_path = os.path.join(root_path,"OK", day)
        # 保存图像的完整路径：  root_path/OK/2023_10_10/2023_10_10_13_12_13
        save_img_path = os.path.join(day_file_path,img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)   # root_path/OK/2023_10_10/2023_10_10_13_12_13.jpg


    else:  # 如果存在就直接保存
        day_file_path = os.path.join(root_path,"OK", day)
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)

    # print("OK图片保存成功")





# 创建文件夹存放NG图像
def save_NG_img2(img, cam_file):
    root_path = save_images["root"] + "\\" + cam_file    # 保存图像的根路径 D:data/....

    day, img_name = my_time()  # NG/2023_10_10/2023_10_10_13_12_13.JPG
    # 压缩图片
    # img_sim = cv2.resize(img, (1500, 950))
    img_sim = img

    if not os.path.exists(os.path.join(root_path, "NG", day)):  # 判断NG文件夹  root_path/NG/2023_10_10  是否存在，
        # 如果文件夹不存在，创建它和中间目录
        os.makedirs(os.path.join(root_path, "NG", day))  # root_path/NG/2023_10_10
        # 当天文件夹完整路径
        day_file_path = os.path.join(root_path, "NG", day)
        # 保存图像的完整路径：  root_path/NG/2023_10_10/2023_10_10_13_12_13
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)  # root_path/NG/2023_10_10/2023_10_10_13_12_13.jpg


    else:  # 如果存在就直接保存
        day_file_path = os.path.join(root_path, "NG", day)
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)

    # print("NG图片保存成功")


# 创建文件夹存放OK图像
def save_OK_img3(img, cam_file):      # 保存图片， 文件夹名称（相机名称）
    root_path = save_images["root"] + "\\" + cam_file   # 保存图像的根路径 D:data/....  自定义修改

    day, img_name = my_time()    # NG/2023_10_10/2023_10_10_13_12_13.JPG
    # 压缩图片
    # img_sim = cv2.resize(img, (1500, 950))
    img_sim = img

    if not os.path.exists(os.path.join(root_path,"OK", day)):  # 判断OK文件夹  root_path/NG/2023_10_10  是否存在，
        # 如果文件夹不存在，创建它和中间目录
        os.makedirs(os.path.join(root_path,"OK", day))  # root_path/OK/2023_10_10
        # 当天文件夹完整路径
        day_file_path = os.path.join(root_path,"OK", day)
        # 保存图像的完整路径：  root_path/OK/2023_10_10/2023_10_10_13_12_13
        save_img_path = os.path.join(day_file_path,img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)   # root_path/OK/2023_10_10/2023_10_10_13_12_13.jpg


    else:  # 如果存在就直接保存
        day_file_path = os.path.join(root_path,"OK", day)
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)

    # print("OK图片保存成功")





# 创建文件夹存放NG图像
def save_NG_img3(img, cam_file):
    root_path = save_images["root"] + "\\" + cam_file    # 保存图像的根路径 D:data/....

    day, img_name = my_time()  # NG/2023_10_10/2023_10_10_13_12_13.JPG
    # 压缩图片
    # img_sim = cv2.resize(img, (1500, 950))
    img_sim = img

    if not os.path.exists(os.path.join(root_path, "NG", day)):  # 判断NG文件夹  root_path/NG/2023_10_10  是否存在，
        # 如果文件夹不存在，创建它和中间目录
        os.makedirs(os.path.join(root_path, "NG", day))  # root_path/NG/2023_10_10
        # 当天文件夹完整路径
        day_file_path = os.path.join(root_path, "NG", day)
        # 保存图像的完整路径：  root_path/NG/2023_10_10/2023_10_10_13_12_13
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)  # root_path/NG/2023_10_10/2023_10_10_13_12_13.jpg


    else:  # 如果存在就直接保存
        day_file_path = os.path.join(root_path, "NG", day)
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)

    # print("NG图片保存成功")


# 创建文件夹存放OK图像
def save_OK_img4(img, cam_file):      # 保存图片， 文件夹名称（相机名称）
    root_path = save_images["root"] + "\\" + cam_file   # 保存图像的根路径 D:data/....  自定义修改

    day, img_name = my_time()    # NG/2023_10_10/2023_10_10_13_12_13.JPG
    # 压缩图片
    # img_sim = cv2.resize(img, (1500, 950))
    img_sim = img

    if not os.path.exists(os.path.join(root_path,"OK", day)):  # 判断OK文件夹  root_path/NG/2023_10_10  是否存在，
        # 如果文件夹不存在，创建它和中间目录
        os.makedirs(os.path.join(root_path,"OK", day))  # root_path/OK/2023_10_10
        # 当天文件夹完整路径
        day_file_path = os.path.join(root_path,"OK", day)
        # 保存图像的完整路径：  root_path/OK/2023_10_10/2023_10_10_13_12_13
        save_img_path = os.path.join(day_file_path,img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)   # root_path/OK/2023_10_10/2023_10_10_13_12_13.jpg


    else:  # 如果存在就直接保存
        day_file_path = os.path.join(root_path,"OK", day)
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)

    # print("OK图片保存成功")





# 创建文件夹存放NG图像
def save_NG_img4(img, cam_file):
    root_path = save_images["root"] + "\\" + cam_file    # 保存图像的根路径 D:data/....

    day, img_name = my_time()  # NG/2023_10_10/2023_10_10_13_12_13.JPG
    # 压缩图片
    # img_sim = cv2.resize(img, (1500, 950))
    img_sim = img

    if not os.path.exists(os.path.join(root_path, "NG", day)):  # 判断NG文件夹  root_path/NG/2023_10_10  是否存在，
        # 如果文件夹不存在，创建它和中间目录
        os.makedirs(os.path.join(root_path, "NG", day))  # root_path/NG/2023_10_10
        # 当天文件夹完整路径
        day_file_path = os.path.join(root_path, "NG", day)
        # 保存图像的完整路径：  root_path/NG/2023_10_10/2023_10_10_13_12_13
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)  # root_path/NG/2023_10_10/2023_10_10_13_12_13.jpg


    else:  # 如果存在就直接保存
        day_file_path = os.path.join(root_path, "NG", day)
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img_sim)

    # print("NG图片保存成功")


def save_img(img, cam_file):      # 保存图片， 文件夹名称（相机名称）
    root_path = r"D:/img_data/" + cam_file   # 保存图像的根路径 D:data/....  自定义修改

    day, img_name = my_time()    # NG/2023_10_10/2023_10_10_13_12_13.JPG

    if not os.path.exists(os.path.join(root_path, day)):  # 判断OK文件夹  root_path/NG/2023_10_10  是否存在，
        # 如果文件夹不存在，创建它和中间目录
        os.makedirs(os.path.join(root_path, day))  # root_path/OK/2023_10_10
        # 当天文件夹完整路径
        day_file_path = os.path.join(root_path, day)
        # 保存图像的完整路径：  root_path/OK/2023_10_10/2023_10_10_13_12_13
        save_img_path = os.path.join(day_file_path,img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img)   # root_path/OK/2023_10_10/2023_10_10_13_12_13.jpg

    else:  # 如果存在就直接保存
        day_file_path = os.path.join(root_path, day)
        save_img_path = os.path.join(day_file_path, img_name)
        cv2.imwrite(f"{save_img_path}.jpg", img)

    # print("原图图片保存成功")





if __name__ == '__main__':
    pass

    # img = cv2.imread(r"D:\wg\AI_project\8.AIkuangjia\logo_image\XDL.png")
    # im = save_NG_img(img, "cam1")

