import socket
import threading
import time

from PyQt5.QtCore import QThread, pyqtSignal


from util.save_OKorNG_img import *




"""
  modbus通讯心跳线程
    # modbustcp 是单向的-不支持同时进行读写操  这是因为它基于请求-响应机制。
    # 多个线程同时访问调用一个modbus客户端对象时（共享资源）需要加锁，避免资源竞争和数据不一致的问题引起的阻塞。
"""

class heartbeat_Thread(QThread):

    client_updated = pyqtSignal(object)  # 发送新 client 实例

    def __init__(self, client):
        super(heartbeat_Thread, self).__init__()

        self.is_running = True
        self.client = client  # modbustcp 客户端

        # 线程锁
        self.lock = threading.Lock()



    def stop(self):
        self.is_running = False
        print("心跳线程结束")




    def run(self):
        print("心跳线程启动")

        # 延时4秒启动心跳
        time.sleep(3)
        data = 1
        while self.is_running:
            # 心跳延时---2s 交替
            time.sleep(2)
            with self.lock:
                try:
                    if data == "？":
                        data = "!"
                    else:
                        data = "？"

                    self.client.sendall(data.encode())



                except Exception as e:
                    # self.send_msg.emit(f"心跳异常: {e}")
                    print(f"心跳异常: {e}")

                    host = tcp['ip']  # ip
                    port = int(tcp['port'])  # 端口
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client.connect(host, port)

                    print("modbus---重连成功")
                    """ 
                    发送信号，让检测线程 更新 client
                    """
                    self.client_updated.emit(self.client)





















