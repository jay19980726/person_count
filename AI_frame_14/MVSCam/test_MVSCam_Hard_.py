import queue
import cv2
from MVSCam import MVSCam




# 创建队列
# imgqueue = queue.Queue()

def Hard_test_MVSCam(ip, imgqueue):

    cam = MVSCam(devinfo=ip, triggermode='on', imgqueue=imgqueue)

    cam.open(0, 'hard',)

    return cam



    # for i in range(1000000):
    # while True:
    #     try:
    #         im = imgqueue.get(False, 1)
    #         print(im)
    #         im = im[0]
    #         img = cv2.resize(im, (800, 700))
    #         # print("取图后队列长度", imgqueue.qsize())
    #         cv2.imshow('im', img)
    #         cv2.waitKey(1)
    #         print('time out')
    #
    #     except queue.Empty:
    #         # print("队列为空，没有可用的图像数据。")
    #         pass


    # cam.stop()





# 创建队列
imgqueue1 = queue.Queue()

def Hard_test_MVSCam1(imgqueue):

    cam = MVSCam(devinfo="DA3313364", triggermode='on', imgqueue=imgqueue)

    cam.open(0, 'hard')


    for i in range(100000000):

        try:
            im = imgqueue.get(False, 1)
            # print(im)
            img = im[0]
            print(img.shape)
            img = cv2.resize(img, (800, 700))
            # print("取图后队列长度", imgqueue.qsize())
            cv2.imshow('im', img)
            cv2.waitKey(1)
            print('time out')

        except queue.Empty:
            # print("队列为空，没有可用的图像数据。")
            # pass
            pass


    cam.stop()





if __name__ == '__main__':
    # Hard_test_MVSCam1(imgqueue1)
    pass