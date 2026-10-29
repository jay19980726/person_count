from MVSCam_class import *
from queue import Queue


"""
无触发
"""
def testMVSCam():
    cam = MVSCam(devinfo="169.254.169.1")   # 这一行代码创建了一个名为 cam 的相机对象，并使用 MVSCam 类初始化它。devinfo 参数用于指定要连接的相机的设备信息，通常包括相机的 IP 地址或其他连接信息
    cam.open(0)                             # ret = cam.open(0)：这一行代码尝试打开相机连接。cam.open(0) 方法通常返回一个表示连接状态的返回值，例如 0 表示成功
    for i in range(1000000000000):
        im = cam.getFrame()
        if im is not None:
            im = cv2.resize(im, (640, 480))
            # cv2.imshow('im', im)
            print(im.shape)
            print(im.shape)
            cv2.imshow('ci', im)
            cv2.waitKey(1000)

    cam.stop()



if __name__ == "__main__":
    # testMVSCam()
    pass





"""
硬触发
"""
def test_MVSCam_tri():

    import queue
    q = queue.Queue(maxsize=1)    # 创建队列存放图片
    cam = MVSCam(devinfo="169.254.169.1", triggermode="on", imgqueue=q)

    cam.open(0, 'hard')

    for i in range(1000000000000000000000):
        try:
            im = q.get(False, 1)   # 第一个参数是 False，它表示不等待。如果设置为 True，则表示等待队列中有元素为止。如果队列为空，程序会阻塞在这一行，直到队列中有元素为止。1 表示最多等待 1 秒
            im = cv2.resize(im[0], dsize=(700, 800))
            cv2.imshow('im', im)
            cv2.waitKey(100)
        except queue.Empty:
            pass

        # print('time out')

    cam.stop()


if __name__ == '__main__':
    # test_MVSCam_tri()
    pass