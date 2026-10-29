from MVSCam_class import *


def test_MVSCam():
    cam = MVSCam(devinfo="0")
    ret = cam.open(0)
    while True:
        im = cam.getFrame()
        if im is None:
            print('get none')
            im = np.zeros([100, 100, 3], dtype=np.uint8)
        im = cv2.resize(im, (640, 480))
        # result=yolo(im)
        cv2.imshow('im', im)
        print(i)
        cv2.waitKey(100)

    cam.stop()



if __name__ == '__main__':
    test_MVSCam()




#
#

#
# from MVSCam_class import *
# import cv2
# import numpy as np
# from v8.yolo_result import yolo_predict
#
# def open_camera(devinfo):
#     cam = MVSCam(devinfo)
#     ret = cam.open(0)
#     return cam if ret else None
#
# def get_frame(cam):
#     im = cam.getFrame()
#     return im if im is not None else np.zeros([100, 100, 3], dtype=np.uint8)
#
# def stop_camera(cam):
#     cam.stop()
#
# def test_MVSCam(ip):
#     cam = open_camera(ip)
#
#     try:
#         if cam is None:
#             print("打开相机失败。")
#             return
#
#         # while True:
#         im = get_frame(cam)
#         # im = cv2.resize(im, (640, 480))
#         # result = yolo_predict(im)
#         cv2.imshow('im', im)
#         # print(i)
#         # cv2.waitKey(0)
#         return im
#     finally:
#         stop_camera(cam)
#
# if __name__ == "__main__":
#     test_MVSCam("192.168.255.1")
#
