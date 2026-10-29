# -- coding: utf-8 --

import queue
import sys
import threading
import msvcrt
import numpy as np
from ctypes import *

import math
import cv2
import time
import inspect
#sys.path.append("../MvImport")
from MvCameraControl_class import *
# from get_config import *


# 创建队列
imgqueue = queue.Queue(maxsize=1)



winfun_ctype = WINFUNCTYPE
stFrameInfo = POINTER(MV_FRAME_OUT_INFO_EX)
pData = POINTER(c_ubyte)
FrameInfoCallBack = winfun_ctype(None, pData, stFrameInfo, c_void_p)

# 输出帧的信息    \~english Output Frame Information
class _USER_DATA_INFO_EX_(Structure):
    pass

_USER_DATA_INFO_EX_._fields_ = [                                  # < \~chinese 图像宽             \~english Image Width
    ('pData', c_void_p),                                   # < \~chinese 图像高             \~english Image Height
]
USER_DATA_INFO_EX = _USER_DATA_INFO_EX_



def image_control(data, stFrameInfo):
    if stFrameInfo.enPixelType == 17301505:
        image = data.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth))
        # image = cv2.cvtColor(data, cv2.COLOR_GRAY2RGB)
        # print("image", image.shape)


    elif stFrameInfo.enPixelType == 17301514:
        data = data.reshape(stFrameInfo.nHeight, stFrameInfo.nWidth, -1)
        image = cv2.cvtColor(data, cv2.COLOR_BAYER_GB2RGB)

    elif stFrameInfo.enPixelType == 35127316:
        data = data.reshape(stFrameInfo.nHeight, stFrameInfo.nWidth, -1)
        image = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

    elif stFrameInfo.enPixelType == 34603039:
        data = data.reshape(stFrameInfo.nHeight, stFrameInfo.nWidth, -1)
        image = cv2.cvtColor(data, cv2.COLOR_YUV2BGR_Y422)

    im_ = image
    return im_



# @
def ImageCallBack(pData, pFrameInfo, pUserData,):
    # 将C指针转换为缓冲区对象
    data = cast(pUserData, c_void_p)
    pUser = cast(data,py_object).value
    # print('HKCamera CallBack camid=',pUser.camid)
    if not pUser.isAcquisition:
        return
    global img_buff
    img_buff = None
    im = None
    stFrameInfo = cast(pFrameInfo, POINTER(MV_FRAME_OUT_INFO_EX)).contents



    """
    图像空间转化；自己写的
    """
    # if stFrameInfo:
    #     print("get one frame: Width[%d], Height[%d], nFrameNum[%d]" % (
    #         stFrameInfo.nWidth, stFrameInfo.nHeight, stFrameInfo.nFrameNum))
    # if img_buff is None and stFrameInfo.enPixelType == 17301505:
    #     img_buff = (c_ubyte * stFrameInfo.nWidth * stFrameInfo.nHeight)()
    #     cdll.msvcrt.memcpy(byref(img_buff), pData, stFrameInfo.nWidth * stFrameInfo.nHeight)
    #     data = np.frombuffer(img_buff, count=int(stFrameInfo.nWidth * stFrameInfo.nHeight), dtype=np.uint8)
    #     im = image_control(data=data, stFrameInfo=stFrameInfo)
    #     del img_buff
    # elif img_buff is None and stFrameInfo.enPixelType == 17301514:
    #     img_buff = (c_ubyte * stFrameInfo.nWidth * stFrameInfo.nHeight)()
    #     cdll.msvcrt.memcpy(byref(img_buff), pData, stFrameInfo.nWidth * stFrameInfo.nHeight)
    #     data = np.frombuffer(img_buff, count=int(stFrameInfo.nWidth * stFrameInfo.nHeight), dtype=np.uint8)
    #     im = image_control(data=data, stFrameInfo=stFrameInfo)
    #     del img_buff
    # elif img_buff is None and stFrameInfo.enPixelType == 35127316:
    #     img_buff = (c_ubyte * stFrameInfo.nWidth * stFrameInfo.nHeight * 3)()
    #     cdll.msvcrt.memcpy(byref(img_buff), pData, stFrameInfo.nWidth * stFrameInfo.nHeight * 3)
    #     data = np.frombuffer(img_buff, count=int(stFrameInfo.nWidth * stFrameInfo.nHeight * 3), dtype=np.uint8)
    #     im = image_control(data=data, stFrameInfo=stFrameInfo)
    #     del img_buff
    # elif img_buff is None and stFrameInfo.enPixelType == 34603039:
    #     img_buff = (c_ubyte * stFrameInfo.nWidth * stFrameInfo.nHeight * 2)()
    #     cdll.msvcrt.memcpy(byref(img_buff), pData, stFrameInfo.nWidth * stFrameInfo.nHeight * 2)
    #     data = np.frombuffer(img_buff, count=int(stFrameInfo.nWidth * stFrameInfo.nHeight * 2), dtype=np.uint8)
    #     im = image_control(data=data, stFrameInfo=stFrameInfo)
    #     del img_buff
    #
    # else:
    #     print("图像格式不正确，请用MVS调整相机图像格式")

    # if img_buff is None:





    """
    图像空间转化；原来
    """
    if stFrameInfo:
        pass
        print("Cam[%d] frame: Width[%d], Height[%d], nFrameNum[%d],pixelType=[%d]" % (
        pUser.camid, stFrameInfo.nWidth, stFrameInfo.nHeight, stFrameInfo.nFrameNum, stFrameInfo.enPixelType))

    cn = stFrameInfo.nFrameLen/(stFrameInfo.nHeight*stFrameInfo.nWidth)
    cn = int(math.ceil(cn))
    npArray = np.zeros(
        (stFrameInfo.nHeight, stFrameInfo.nWidth, cn), dtype=np.uint8)
    npArrayPtr = npArray.ctypes.data_as(POINTER(c_ubyte))
    cdll.msvcrt.memcpy(npArrayPtr, pData, stFrameInfo.nFrameLen)
    # print("tuxiang:", stFrameInfo.enPixelType)
    if img_buff is None and stFrameInfo.enPixelType == PixelType_Gvsp_Mono8:
        im = cv2.cvtColor(npArray, cv2.COLOR_GRAY2RGB)
        # del img_buff
    elif img_buff is None and stFrameInfo.enPixelType == PixelType_Gvsp_BayerRG8:
        im = cv2.cvtColor(npArray, cv2.COLOR_BayerRG2RGB)
        # del img_buff
    elif img_buff is None and stFrameInfo.enPixelType == PixelType_Gvsp_BayerGB8:
        im = cv2.cvtColor(npArray, cv2.COLOR_BayerGB2RGB)
        del img_buff
    elif img_buff is None and stFrameInfo.enPixelType == PixelType_Gvsp_RGB8_Packed:
        im = cv2.cvtColor(npArray, cv2.COLOR_BGR2RGB)
        # del img_buff
    elif img_buff is None and stFrameInfo.enPixelType == PixelType_Gvsp_YUV422_Packed:
        im = cv2.cvtColor(npArray, cv2.COLOR_YUV2BGR_YUYV)
        # del img_buff
    elif img_buff is None and stFrameInfo.enPixelType == PixelType_Gvsp_YUV422_YUYV_Packed:
        im = cv2.cvtColor(npArray, cv2.COLOR_YUV2BGR_YUYV)
        # del img_buff

    # 黑白相机 Mono8
    elif stFrameInfo.enPixelType == 17301505:
        # 假设 17301505 代表灰度图像格式
        im = cv2.cvtColor(npArray, cv2.COLOR_GRAY2RGB)
        # del img_buff


    # 以上图像格式都不是
    else:
        # print('stFrameInfo.enPixelType:',stFrameInfo.enPixelType)
        print('相机传输的图像格式为:', type(stFrameInfo.enPixelType))

    # del img_buff


    index = pUser.camid
    print(index)
    print(f'cam{index}>>>>>>>>>>>>>>>>>>>>>>>>img success!>>>>>>>>>>>>>>>>>>')

    t0 = time.time()

    # 图像im 放入队列 imgqueue中
    pUser.imgqueue.put([im])


CALL_BACK_FUN = FrameInfoCallBack(ImageCallBack)   # 这段代码似乎定义了一个回调函数 CALL_BACK_FUN，并将其设置为 FrameInfoCallBack 的参数，参数是 ImageCallBack 函数。



def Async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def Stop_thread(thread):
    Async_raise(thread.ident, SystemExit)


def Color_numpy(data, nWidth, nHeight):
    data_ = np.frombuffer(data, count=int(
        nWidth*nHeight*3), dtype=np.uint8, offset=0)
    data_r = data_[0:nWidth*nHeight*3:3]
    data_g = data_[1:nWidth*nHeight*3:3]
    data_b = data_[2:nWidth*nHeight*3:3]

    data_r_arr = data_r.reshape(nHeight, nWidth)
    data_g_arr = data_g.reshape(nHeight, nWidth)
    data_b_arr = data_b.reshape(nHeight, nWidth)
    numArray = np.zeros([nHeight, nWidth, 3], "uint8")

    numArray[:, :, 0] = data_r_arr
    numArray[:, :, 1] = data_g_arr
    numArray[:, :, 2] = data_b_arr
    return numArray


def Work_thread(self):
    stOutFrame = MV_FRAME_OUT()
    img_buff = None
    buf_cache = None
    numArray = None
    self.b_save_jpg = False
    self.b_save_bmp = False
    while True:
        ret = self.cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
        #print('MV_CC_GetImageBuffer', ret)
        if 0 == ret:
            if None == buf_cache:
                buf_cache = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
            # 获取到图像的时间开始节点获取到图像的时间开始节点
            self.st_frame_info = stOutFrame.stFrameInfo
            cdll.msvcrt.memcpy(
                byref(buf_cache), stOutFrame.pBufAddr, self.st_frame_info.nFrameLen)
            print("get one frame: Width[%d], Height[%d], nFrameNum[%d]" % (
                self.st_frame_info.nWidth, self.st_frame_info.nHeight, self.st_frame_info.nFrameNum))
            self.n_save_image_size = self.st_frame_info.nWidth * \
                self.st_frame_info.nHeight * 3 + 2048
            if img_buff is None:
                img_buff = (c_ubyte * self.n_save_image_size)()

            if True == self.b_save_jpg:
                self.Save_jpg(buf_cache)  # ch:保存Jpg图片 | en:Save Jpg
            if True == self.b_save_bmp:
                self.Save_Bmp(buf_cache)  # ch:保存Bmp图片 | en:Save Bmp
        else:
            #print("no data, nret = ", (ret))
            continue

        # 转换像素结构体赋值
        stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
        memset(byref(stConvertParam), 0, sizeof(stConvertParam))
        stConvertParam.nWidth = self.st_frame_info.nWidth
        stConvertParam.nHeight = self.st_frame_info.nHeight
        stConvertParam.pSrcData = cast(buf_cache, POINTER(c_ubyte))
        stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
        stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType

        # RGB直接显示
        if PixelType_Gvsp_RGB8_Packed == self.st_frame_info.enPixelType:
            numArray = Color_numpy(
                buf_cache, self.st_frame_info.nWidth, self.st_frame_info.nHeight)

        # 如果是彩色且非RGB则转为RGB后显示
        else:
            nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
            stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed
            stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
            stConvertParam.nDstBufferSize = nConvertSize
            time_start = time.time()
            ret = self.cam.MV_CC_ConvertPixelType(stConvertParam)
            time_end = time.time()
            print('MV_CC_ConvertPixelType:', time_end - time_start)
            if ret != 0:
                print('convert pixel fail! ret = ', (ret))
                continue
            cdll.msvcrt.memcpy(
                byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
            numArray = Color_numpy(
                img_buff, self.st_frame_info.nWidth, self.st_frame_info.nHeight)

        # 合并OpenCV到Tkinter界面中
        if self.frame_callback is not None:
            self.frame_callback(numArray)

        nRet = self.cam.MV_CC_FreeImageBuffer(stOutFrame)
        if self.b_exit == True:
            if img_buff is not None:
                del img_buff
            if buf_cache is not None:
                del buf_cache
            break


deviceList = MV_CC_DEVICE_INFO_LIST()
tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE

# ch:枚举设备 | en:Enum device
ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
if ret != 0:
    print("enum devices fail! ret[0x%x]" % ret)
    #sys.exit()

if deviceList.nDeviceNum == 0:
    print("find no device!")
    #sys.exit()

print("Find %d devices!" % deviceList.nDeviceNum)

for i in range(0, deviceList.nDeviceNum):
    mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(
        MV_CC_DEVICE_INFO)).contents
    if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
        print("\ngige device: [%d]" % i)
        strModeName = ""
        for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
            strModeName = strModeName + chr(per)
        print("device model name: %s" % strModeName)

        nip1 = (
            (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
        nip2 = (
            (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
        nip3 = (
            (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
        nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
        print("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
    elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
        print("\nu3v device: [%d]" % i)
        strModeName = ""
        for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
            if per == 0:
                break
            strModeName = strModeName + chr(per)
        print("device model name: %s" % strModeName)

        strSerialNumber = ""
        for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
            if per == 0:
                break
            strSerialNumber = strSerialNumber + chr(per)
        print("user serial number: %s" % strSerialNumber)

def GetCamNum():
    return deviceList.nDeviceNum

img_buff = []


class MVSCam:

    def __init__(self, id=-1, devinfo='', triggermode='off', imgqueue=None):
        self.b_thread_closed = False
        self.b_start_grabbing = False
        self.devinfo = devinfo
        self.camid = id
        self.triggermode = triggermode
        self.imgqueue = imgqueue
        self.cam = None
        self.data_buf = None
        self.isAcquisition = True
        self.frame_callback = CALL_BACK_FUN
        # if id>=0:
        #     self.open(self.camid)

    def open(self, camindex, triggermode='off', frame_callback=None):
        # camindex = input("please input the number of the device to connect:")
        self.index = camindex
        # self.triggermode = triggermode
        # self.frame_callback = frame_callback
        if self.b_start_grabbing:
            return None

        if int(camindex) >= deviceList.nDeviceNum:
            print("intput error!")
            # sys.exit()
            return None

        # ch:创建相机实例 | en:Creat Camera Object
        cam = MvCamera()
        self.cam = cam

        DevWillBeOpen = None
        if self.devinfo != '':
            # ch:选择设备并创建句柄 | en:Select device and create handle
            for i in range(0, deviceList.nDeviceNum):
                mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(
                    MV_CC_DEVICE_INFO)).contents
                if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:

                    strModeName = ""
                    strIpaddress = ""
                    strSerialNumber = ""
                    for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                        strModeName = strModeName + chr(per)

                    nip1 = (
                            (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                    nip2 = (
                            (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                    nip3 = (
                            (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                    nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)

                    strIpaddress = '%d.%d.%d.%d' % (nip1, nip2, nip3, nip4)

                    for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chSerialNumber:
                        if per == 0:
                            break
                        strSerialNumber = strSerialNumber + chr(per)

                    # print("\ngige device: [%d]" % i)
                    # print("device model name: %s" % strModeName)
                    # print("current ip: %d.%d.%d.%d" % (nip1, nip2, nip3, nip4))
                    # print('serial number:%s' % strSerialNumber)

                    if self.devinfo.upper() in strIpaddress.upper():
                        DevWillBeOpen = mvcc_dev_info
                        print('connect dev:', self.devinfo)
                        break
                    elif self.devinfo.upper() in strSerialNumber.upper():
                        DevWillBeOpen = mvcc_dev_info
                        print('connect dev:', self.devinfo)
                        break


                elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:

                    strModeName = ""
                    strSerialNumber = ""
                    for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                        if per == 0:
                            break
                        strModeName = strModeName + chr(per)

                    for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                        if per == 0:
                            break
                        strSerialNumber = strSerialNumber + chr(per)

                    # print("\nu3v device: [%d]" % i)
                    # print("device model name: %s" % strModeName)
                    # print("user serial number: %s" % strSerialNumber)

                    if self.devinfo.upper() in strSerialNumber.upper():
                        DevWillBeOpen = mvcc_dev_info
                        print('connect dev:', self.devinfo)
                        break
        else:
            DevWillBeOpen = cast(deviceList.pDeviceInfo[int(
                camindex)], POINTER(MV_CC_DEVICE_INFO)).contents

        if DevWillBeOpen is None:
            print("can't match the device info")
            # stDeviceList = cast(deviceList.pDeviceInfo[int(
            #     camindex)], POINTER(MV_CC_DEVICE_INFO)).contents
            # sys.exit()
            return None
        else:
            stDeviceList = DevWillBeOpen
        ret = cam.MV_CC_CreateHandle(stDeviceList)
        if ret != 0:
            print("create handle fail! ret[0x%x]" % ret)
            sys.exit()

        # ch:打开设备 | en:Open device
        ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            print("open device fail! ret[0x%x]" % ret)
            return None
            # sys.exit()

        # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
        if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = cam.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                if ret != 0:
                    print("Warning: Set Packet Size fail! ret[0x%x]" % ret)
            else:
                print("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)

        if self.triggermode == 'off':
            # ch:设置触发模式为off | en:Set trigger mode as off
            ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print("set trigger mode fail! ret[0x%x]" % ret)
                sys.exit()
        else:
            # ch:设置触发模式为off | en:Set trigger mode as off
            ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_ON)
            if ret != 0:
                print("set trigger mode fail! ret[0x%x]" % ret)
                sys.exit()

            if self.triggermode == 'soft':
                ret = self.cam.MV_CC_SetEnumValue(
                    "TriggerSource", MV_TRIGGER_SOURCE_SOFTWARE)
                if ret != 0:
                    print('set triggersource fail! ret = ', (ret))
            else:
                ret = cam.MV_CC_SetEnumValue(
                    "TriggerSource", MV_TRIGGER_SOURCE_LINE0)
                if ret != 0:
                    print('set triggersource fail! ret = ', (ret))

                # ch:注册抓图回调 | en:Register image callback


                ret = cam.MV_CC_RegisterImageCallBackEx(CALL_BACK_FUN, py_object(self))
                if ret != 0:
                    print("register image callback fail! ret[0x%x]" % ret)
                    sys.exit()

                    # ch:获取数据包大小 | en:Get payload size
        stParam = MVCC_INTVALUE()
        memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))

        ret = cam.MV_CC_GetIntValue("PayloadSize", stParam)
        if ret != 0:
            print("get payload size fail! ret[0x%x]" % ret)
            sys.exit()
        nPayloadSize = stParam.nCurValue

        ret = cam.MV_CC_StartGrabbing()
        if ret != 0:
            print('show error', 'start grabbing fail! ret = ', (ret))
            return None
        self.b_exit = False
        self.b_start_grabbing = True
        print("start grabbing successfully!")
        # if not self.triggermode == 'off':
        #     try:
        #         #self.n_win_gui_id = random.randint(1,10000)
        #         self.h_thread_handle = threading.Thread(
        #             target=Work_thread, args=(self,))
        #         self.h_thread_handle.start()
        #         self.b_thread_closed = True
        #     except:
        #         print('show error', 'error: unable to start thread')
        #         False == self.b_start_grabbing

        data_buf = (c_ubyte * nPayloadSize)()

        self.pData = byref(data_buf)
        self.nDataSize = nPayloadSize
        stFrameInfo = MV_FRAME_OUT_INFO_EX()
        memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))
        self.cam = cam
        self.stFrameInfo = stFrameInfo
        self.data_buf = data_buf

        return self.cam


    def getFrame(self):
        if not self.isAcquisition:
            return None
        im = self.getFrame1()
        cam = self.cam
        if im is None:
            #self.close()
            #self.open(self.index)
            im = self.getFrame1()
        
        return im

    def getFrame1(self):
        cam = self.cam
        if cam is None:
            return
        pData = self.pData
        nDataSize = self.nDataSize
        stFrameInfo = self.stFrameInfo
        # ret = cam.MV_CC_StopGrabbing()
        # ret = cam.MV_CC_StartGrabbing()
        ret = cam.MV_CC_GetOneFrameTimeout(pData, nDataSize, stFrameInfo, 1000)

        if ret == 0:
            #print ("get one frame: Width[%d], Height[%d], nFrameNum[%d]"  % (stFrameInfo.nWidth, stFrameInfo.nHeight, stFrameInfo.nFrameNum))
            pass
        else:
            print("cam%d getFram no data[0x%x]" % (self.camid,ret))
            return None

        cn = nDataSize/(stFrameInfo.nHeight*stFrameInfo.nWidth)
        cn = int(math.ceil(cn))
        npArray = np.zeros(
            (stFrameInfo.nHeight, stFrameInfo.nWidth, cn), dtype=np.uint8)
        npArrayPtr = npArray.ctypes.data_as(POINTER(c_ubyte))
        memmove(npArrayPtr, pData, nDataSize)
        # print("无触发；", stFrameInfo.enPixelType)

        if PixelType_Gvsp_YUV422_YUYV_Packed == stFrameInfo.enPixelType:   # stFrameInfo.enPixelType：这表示相机传输的图像格式
            # print(cv2.COLOR_YUV2BGR_YUYV)
            # print(cv2.COLOR_YUV2BGR_Y422)
            npArray = cv2.cvtColor(npArray, cv2.COLOR_YUV2BGR_YUYV)

        elif PixelType_Gvsp_BayerRG8 == stFrameInfo.enPixelType:
            npArray = cv2.cvtColor(npArray, cv2.COLOR_BAYER_RG2RGB)
        elif PixelType_Gvsp_BayerGB8== stFrameInfo.enPixelType:
            npArray = cv2.cvtColor(npArray, cv2.COLOR_BAYER_GB2RGB)

        # 相机传输的图像格式为 RGB8 = 35127316
        elif PixelType_Gvsp_RGB8_Packed == stFrameInfo.enPixelType:
            npArray = cv2.cvtColor(npArray, cv2.COLOR_BGR2RGB)

        # 相机图像为黑白 Mono8
        elif PixelType_Gvsp_Mono8 == PixelType_Gvsp_Mono8:
            npArray = cv2.cvtColor(npArray, cv2.COLOR_GRAY2RGB)
        # 以上格式都不是就打印出传输格式
        else:
            # print('stFrameInfo.enPixelType:',stFrameInfo.enPixelType)
            print('相机传输的图像格式为:', stFrameInfo.enPixelType)
        return npArray



    def stop(self):
     
        cam = self.cam
        if cam is None:
            return          
        data_buf = self.data_buf
        if True == self.b_thread_closed:
            Stop_thread(self.h_thread_handle)
            self.b_thread_closed = False
        # msvcrt.getch()
        # ch:停止取流 | en:Stop grab image
        ret = cam.MV_CC_StopGrabbing()
        if ret != 0:
            print("stop grabbing fail! ret[0x%x]" % ret)
            del data_buf
            sys.exit()

        # ch:关闭设备 | Close device
        ret = cam.MV_CC_CloseDevice()
        if ret != 0:
            print("close deivce fail! ret[0x%x]" % ret)
            del data_buf
            sys.exit()

        # ch:销毁句柄 | Destroy handle
        ret = cam.MV_CC_DestroyHandle()
        if ret != 0:
            print("destroy handle fail! ret[0x%x]" % ret)
            del data_buf
            sys.exit()

        del data_buf
        self.b_thread_closed = False
        self.b_start_grabbing = False

    def close(self):
        self.stop()
        print('close')
        self.cam = None
    
    def CloseDevice(self):
        self.stop()
        self.cam = None
        
    def isopen(self):
        return self.cam is not None


def test_MVSCam():
    cam = MVSCam(devinfo='169.254.169.1')
    ret = cam.open(0)
    for i in range(10000000):
        im = cam.getFrame()
        if im is None:
            print('get none')
            im = np.zeros([100, 100, 3], dtype=np.uint8)
        im = cv2.resize(im, (640, 480))
        cv2.imshow('im', im)
        print(i)
        cv2.waitKey(100)

    cam.stop()


import queue
def test_MVSCam_tri():

    cam = MVSCam(triggermode='on', imgqueue=imgqueue)

    cam.open(0, 'hard',)

    # for i in range(1000000):
    while True:
        try:
            im = imgqueue.get(False, 1)
            print(im)
            img = cv2.resize(im[0], dsize=(800, 700))
            print("取图后队列长度", imgqueue.qsize())
            cv2.imshow('im', img)
            cv2.waitKey(1000)
            print('time out')

        except queue.Empty:
            # print("队列为空，没有可用的图像数据。")
            pass


    cam.stop()



def test_MVSCams():
    ncam = cap_num()
    cams = [MVSCam() for i in range(ncam)]
    [cams[i].open(i) for i in range(ncam)]
    for ii in range(100):
        ims = [cams[i].getFrame() for i in range(ncam)]
        ims = [cv2.resize(ims[i], (640, 480)) for i in range(ncam)]
        [cv2.imshow(f'im{i}', ims[i]) for i in range(ncam)]
        print(ii)
        cv2.waitKey(100)

    [cams[i].stop() for i in range(ncam)]
    print('end')




if __name__ == "__main__":
    pass

    # test_MVSCam()

    # test_MVSCam_tri()    # 硬触发，回调函数。
