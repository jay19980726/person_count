import time

# from app2.config import *
from MVSCam.MVSCam_class import MVSCam







def cam_connect():

    cam1 = MVSCam(devinfo=MVS_cam["ip_number1"])
    ret1 = cam1.open(0)
    cam_name1 = 1

    cam2 = MVSCam(devinfo=MVS_cam["ip_number2"])
    ret2 = cam2.open(0)
    cam_name2 = 2
    #
    cam3 = MVSCam(devinfo=MVS_cam["ip_number3"])
    ret3 = cam3.open(0)
    cam_name3 = 3
    #
    cam4 = MVSCam(devinfo=MVS_cam["ip_number4"])
    ret4 = cam4.open(0)
    cam_name4 = 4


    # return cam1, cam2, cam3, cam4, cam5, cam6
    return cam1, cam2,  cam3,  cam4