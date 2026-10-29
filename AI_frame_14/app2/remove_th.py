import queue
import time

from PyQt5.QtCore import QThread, pyqtSignal

from app2.config import tcp


class DetThread_remove(QThread):
    # 定义一个信号 send_msg，当线程执行某些操作时，它将发射这个信号，并传递信息。
    send_msg = pyqtSignal(str)  # 给QT主线程发送检测状态信息的信号


    def __init__(self, client, remove_queue, remove_sleep_time):
        super(DetThread_remove, self).__init__()

        self.is_running = True

        self.client = client   # 客户端实例

        # 剔除延时队列
        self.remove_queue = remove_queue
        self.remove_sleep_time = remove_sleep_time



    def run(self):
        while self.is_running:

            try:
                result_list = self.remove_queue.get(False, 1)
                result = result_list[0]
                print(result, "123456789")
                if result == 1:
                    w_regs_addr = tcp["write_result_addr"]
                    w_NG_regs_value = tcp["write_result_NG"]
                    # ----剔除延时
                    times = self.remove_sleep_time / 1000
                    time.sleep(times)
                    self.client.write_multiple_registers(w_regs_addr, w_NG_regs_value)
                    print("剔除")

            except queue.Empty:
                # print("相机2队列为空，没有可用的图像数据。")
                continue
                # pass