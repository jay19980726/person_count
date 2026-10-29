from datetime import datetime
import queue
import threading
import time
import os
import cv2

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage

from ultralytics import YOLO
from concurrent.futures import ThreadPoolExecutor, wait
from http_pos.http_pos_data import *
from app2 import remove_th
from app2.config import *
from util import yolo_track, yolo_track5, yolo_track6, yolo_track7, yolo_track8, yolo_track1
from util.auto_remove_imgfile2 import delete_old_folders_until_space_enough
from util.save_OKorNG_img import save_img, save_OK_img
from util.write_excel_data import ExcelDataRecorder
from datetime import datetime
import time
from queue import Empty

"""
============================================================
摄像头拉流线程
============================================================
"""


class CameraReadThread(QThread):
    def __init__(self, cam, frame_queue):
        super().__init__()
        self.cam = cam
        self.frame_queue = frame_queue
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                ret, frame = self.cam.get_frame()
                if ret and frame is not None:
                    if self.frame_queue.full():
                        try:
                            self.frame_queue.get_nowait()
                        except:
                            pass
                    self.frame_queue.put(frame)
                else:
                    time.sleep(0.02)
            except:
                time.sleep(0.02)

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()


"""
============================================================
检测线程（核心）
============================================================
"""


class DetThread(QThread):
    # -------- 信号定义 --------
    update_conf = pyqtSignal(float)
    update_iou = pyqtSignal(float)
    update_auto_save_signal = pyqtSignal(bool)

    image_updated1 = pyqtSignal(QImage)
    image_updated2 = pyqtSignal(QImage)
    image_updated3 = pyqtSignal(QImage)
    image_updated4 = pyqtSignal(QImage)
    image_updated5 = pyqtSignal(QImage)
    image_updated6 = pyqtSignal(QImage)
    image_updated7 = pyqtSignal(QImage)
    image_updated8 = pyqtSignal(QImage)

    update_count_signal = pyqtSignal(int, int)

    def __init__(self, cams, conf_value, w_value, h_value, time_values):
        super().__init__()

        self.is_running = True
        self.cams = cams
        self.time_values = time_values

        # 每个相机一个帧队列
        self.frame_queues = [queue.Queue(maxsize=1) for _ in range(8)]

        # 每个相机一个拉流线程
        self.cam_threads = []
        for i, cam in enumerate(cams):
            t = CameraReadThread(cam, self.frame_queues[i])
            self.cam_threads.append(t)
            t.start()

        # 每一个相机结果存放队列
        self.cam_result_queues = [queue.Queue(maxsize=1) for _ in range(14)]

        # ---------- 检测参数 ----------
        self.conf = 0.6
        self.iou = 0.3
        self.auto_save = False

        self.update_conf.connect(self.set_conf)
        self.update_iou.connect(self.set_iou)
        self.update_auto_save_signal.connect(self.set_auto_save)

        # 推理锁（防止多线程同时调用 Tracker）
        self.lock = threading.Lock()

        # ========== 队列锁 ==========
        self.queue_lock = threading.Lock()  # ⭐ 用于保护队列操作

        # 线程池（8 路并行检测）
        self.executor = ThreadPoolExecutor(max_workers=8)

        # ============ 视频保存相关 ============
        self.video_root = save_images["root"]
        os.makedirs(self.video_root, exist_ok=True)
        self.video_states = [None] * 8

        # 线程列表，用来清零
        self.track_list = []




    # ---------- 参数回调 ----------
    def set_conf(self, value):
        self.conf = value

    def set_iou(self, value):
        self.iou = value

    def set_auto_save(self, on_off):
        self.auto_save = on_off


    # ---------- 停止线程 ----------
    def stop(self):
        self.is_running = False


        # 停止拉流线程
        for t in self.cam_threads:
            t.stop()

        # 关闭摄像头
        for cam in self.cams:
            cam.close()

        # 释放所有视频文件
        for state in self.video_states:
            if state is not None:
                state["writer"].release()

        self.executor.shutdown(wait=False)
        self.quit()
        self.wait()

    # ============ 初始化视频文件 ============
    def init_video_writer(self, index, w, h):
        today = datetime.now().strftime("%Y-%m-%d")
        day_dir = os.path.join(self.video_root, today)
        os.makedirs(day_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%H%M%S")
        filename = os.path.join(day_dir, f"cam{index + 1}_{timestamp}.mp4")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = 5

        writer = cv2.VideoWriter(filename, fourcc, fps, (w, h))
        return writer, today

    # =========== 重置相机计数器 ===========
    @pyqtSlot(int)
    def reset_camera_counter(self, cam_index):
        if cam_index < len(self.track_list):
            self.track_list[cam_index].reset()

    # ============ 单路相机检测逻辑 ============
    def start_predict(self, index, image_updated, direction):

        # Tracker 初始化
        if index == 4:
            track = yolo_track5.Track(direction=direction)
            self.track_list.append(track)
        elif index == 5:
            track = yolo_track6.Track(direction=direction)
            self.track_list.append(track)
        elif index == 6:
            track = yolo_track7.Track(direction=direction)
            self.track_list.append(track)
        elif index == 7:
            track = yolo_track8.Track(direction=direction)
            self.track_list.append(track)
        elif index == 0:
            track = yolo_track.Track(direction=direction)
            self.track_list.append(track)
        else:
            track = yolo_track1.Track(direction=direction)
            self.track_list.append(track)

        model = YOLO(models[f"path{index + 1}"])
        q = self.frame_queues[index]

        while self.is_running:
            time.sleep(0.01)

            try:
                img = q.get(timeout=1)
            except queue.Empty:
                continue

            if img is None:
                continue

            if len(img.shape) != 3 or img.shape[2] != 3:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            if self.auto_save:
                save_OK_img(img, f"cam{index + 1}")

            with self.lock:
                yolo_result_img, count = track.track_predict(model, img, self.conf, self.iou)

                # 放入结果队列（使用锁保护）
                if index == 4:
                    for i in [4, 5, 6]:
                        if self.cam_result_queues[i].full():
                            try:
                                self.cam_result_queues[i].get_nowait()
                            except:
                                pass
                    self.cam_result_queues[4].put(count[0])
                    self.cam_result_queues[5].put(count[1])
                    self.cam_result_queues[6].put(count[2])

                elif index == 5:
                    for i in [7, 8, 9]:
                        if self.cam_result_queues[i].full():
                            try:
                                self.cam_result_queues[i].get_nowait()
                            except:
                                pass
                    self.cam_result_queues[7].put(count[0])
                    self.cam_result_queues[8].put(count[1])
                    self.cam_result_queues[9].put(count[2])

                elif index == 6:
                    for i in [10, 11]:
                        if self.cam_result_queues[i].full():
                            try:
                                self.cam_result_queues[i].get_nowait()
                            except:
                                pass
                    self.cam_result_queues[10].put(count[0])
                    self.cam_result_queues[11].put(count[1])

                elif index == 7:
                    for i in [12, 13]:
                        if self.cam_result_queues[i].full():
                            try:
                                self.cam_result_queues[i].get_nowait()
                            except:
                                pass
                    self.cam_result_queues[12].put(count[0])
                    self.cam_result_queues[13].put(count[1])

                else:
                    if self.cam_result_queues[index].full():
                        try:
                            self.cam_result_queues[index].get_nowait()
                        except:
                            pass
                    self.cam_result_queues[index].put(count[0])

            # UI 显示
            img_rgb = cv2.cvtColor(yolo_result_img, cv2.COLOR_BGR2RGB)
            h, w, ch = img_rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
            image_updated.emit(qimg)

        print(f"相机 {index + 1} 检测线程退出")

    # ============ 主入口 ============
    def run(self):
        # excel 数据线程
        threading.Thread(target=self.excel_data, daemon=True).start()
        threading.Thread(target=self.periodic_upload, daemon=True).start()

        img_update = [
            self.image_updated1, self.image_updated2, self.image_updated3, self.image_updated4,
            self.image_updated5, self.image_updated6, self.image_updated7, self.image_updated8
        ]

        futures = [
            self.executor.submit(self.start_predict, 0, img_update[0], "down_up"),
            self.executor.submit(self.start_predict, 1, img_update[1], "up_down"),
            self.executor.submit(self.start_predict, 2, img_update[2], "down_up"),
            self.executor.submit(self.start_predict, 3, img_update[3], "down_up"),
            self.executor.submit(self.start_predict, 4, img_update[4], "up_down"),
            self.executor.submit(self.start_predict, 5, img_update[5], "down_up"),
            self.executor.submit(self.start_predict, 6, img_update[6], "down_up"),
            self.executor.submit(self.start_predict, 7, img_update[7], "up_down"),
        ]
        wait(futures)

    # ============ Excel 数据记录 ============
    def excel_data(self):
        """
        自动数据记录线程：
        - 按指定时间点触发写入 Excel
        - 每个时间点根据配置的延时分组读取各相机队列
        - 读取后立即清零对应 tracker
        - 每天自动新建 Excel 文件
        """

        # ========== 定时触发的时间点（时, 分）==========
        WRITE_TIMEPOINTS = [(7, 40), (15, 40), (23, 40)]

        # ========== 防御：展平 time_values ==========
        raw_values = self.time_values
        if not raw_values:
            print("❌ time_values 为空！")
            return

        time_values = []
        for v in raw_values:
            if isinstance(v, list):
                time_values.append(v[0] if v else 0)
            else:
                time_values.append(int(v))

        # ========== 每个结果队列对应的延时（分钟）==========
        queue_delays = [
            0, time_values[0], time_values[1], time_values[2],
            time_values[3], time_values[3], time_values[3],
            time_values[4], time_values[4], time_values[4],
            time_values[5], time_values[5],
            time_values[6], time_values[6],
        ]

        # ========== 队列索引 → tracker 索引的映射 ==========
        queue_to_track = [0, 1, 2, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7]

        # ========== 状态变量 ==========
        executed_marks = {}
        recorder = ExcelDataRecorder(write_interval_hour=1)
        last_date = None

        print("🚀 自动数据记录程序已启动")
        print(f"📌 time_values(展平后): {time_values}")
        print(f"📌 队列延时(分钟): {queue_delays}")
        print("=" * 80)

        # ========== 主循环 ==========
        while self.is_running:
            today = recorder.get_today_folder()
            now = datetime.now()
            current_h, current_m = now.hour, now.minute

            # ========== 跨天处理 ==========
            if today != last_date:
                print(f"\n📅 跨天检测：{last_date} → {today}")
                recorder = ExcelDataRecorder(write_interval_hour=1)
                last_date = today
                executed_marks.clear()

            # ========== 定时触发写入 ==========
            for tp_h, tp_m in WRITE_TIMEPOINTS:
                mark_key = f"{today}_{tp_h}_{tp_m}"

                if current_h == tp_h and current_m == tp_m and mark_key not in executed_marks:
                    executed_marks[mark_key] = True
                    print(f"\n🎯 触发时间点 {tp_h:02d}:{tp_m:02d}")

                    # 基准时间：今天的这个触发时刻
                    base_dt = datetime.now().replace(hour=tp_h, minute=tp_m, second=0, microsecond=0)
                    base_ts = base_dt.timestamp()

                    # ========== 按延时分组 ==========
                    delay_groups = {}
                    for i, d in enumerate(queue_delays):
                        delay_groups.setdefault(d, []).append(i)

                    counts = [0] * 14

                    # ========== 按延时顺序处理 ==========
                    for delay in sorted(delay_groups.keys()):
                        # 目标触发时间 = 基准时间 + 延时分钟数
                        target_ts = base_ts + delay * 60
                        wait_sec = max(0, target_ts - time.time())

                        # 如果需要等待，则休眠到目标时间
                        if wait_sec > 0:
                            print(f"⏳ 等待 {delay} 分钟...")
                            end_time = time.time() + wait_sec
                            while time.time() < end_time and self.is_running:
                                time.sleep(0.5)
                            if not self.is_running:
                                return

                        # ========== 使用锁读取该延时组的所有队列 ==========
                        with self.queue_lock:  # ⭐ 加锁保护
                            time.sleep(1)
                            to_reset = set()
                            for qidx in delay_groups[delay]:
                                try:
                                    counts[qidx] = self.cam_result_queues[qidx].get_nowait()
                                except Empty:
                                    counts[qidx] = 0

                                tid = queue_to_track[qidx]
                                to_reset.add(tid)
                                print(f"  队列[{qidx}]→{counts[qidx]}, 清零track[{tid}]")

                        # ========== 清零 tracker ==========
                        for tid in to_reset:
                            self.track_list[tid].reset()
                            print(f"  🔄 track[{tid}] 已清零")

                    # ========== 写入 Excel ==========
                    data = recorder.get_business_data(counts)
                    recorder.append_to_excel(data)
                    recorder.last_write_time_tag = recorder.get_current_time_tag()
                    print(f"✅ 写入完成: {counts}\n")

            # 每30秒检查一次时间
            time.sleep(30)


    # ============ 定时上传 ============
    def periodic_upload(self):
        """
        独立的定时上传线程：每5分钟触发一次上传
        """
        print("🔄 定时上传线程已启动（每5分钟上传一次）")

        while self.is_running:
            try:
                # 执行上传
                self.uploading_data()

                # 打印下次上传时间
                next_time = datetime.now().timestamp() + 5 * 60
                # print(f"⏰ 下次上传时间: {datetime.fromtimestamp(next_time).strftime('%Y-%m-%d %H:%M:%S')} (5分钟后)")
                # print("=" * 80)

                # 等待5分钟（支持优雅退出）
                end_time = time.time() + 5 * 60
                while time.time() < end_time and self.is_running:
                    time.sleep(0.5)

            except Exception as e:
                # print(f"❌ 定时上传异常: {e}")
                time.sleep(10)


    # ============ 上传数据 ============
    def uploading_data(self):
        """
        数据上传方法 - 从队列读取数据并上传到上位机
        """
        counts = [0] * 14

        try:
            # print(f"\n📤 开始数据上传... 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # ========== 展平 time_values ==========
            raw_values = self.time_values
            if not raw_values:
                print("❌ time_values 为空！")
                return

            time_values = []
            for v in raw_values:
                if isinstance(v, list):
                    time_values.append(v[0] if v else 0)
                else:
                    time_values.append(int(v))

            # ========== 计算队列延时 ==========
            queue_delays = [
                0, time_values[0], time_values[1], time_values[2],
                time_values[3], time_values[3], time_values[3],
                time_values[4], time_values[4], time_values[4],
                time_values[5], time_values[5],
                time_values[6], time_values[6],
            ]

            # ========== 按延时分组 ==========
            delay_groups = {}
            for i, d in enumerate(queue_delays):
                delay_groups.setdefault(d, []).append(i)

            # ========== 获取基准时间（当前时间的整分） ==========
            now = datetime.now()
            base_dt = now.replace(second=0, microsecond=0)
            base_ts = base_dt.timestamp()
            # print(f"📌 基准时间: {base_dt.strftime('%Y-%m-%d %H:%M:%S')}")

            # ========== 按延时顺序处理 ==========
            for delay in sorted(delay_groups.keys()):
                target_ts = base_ts + delay * 60
                wait_sec = max(0, target_ts - time.time())

                if wait_sec > 0:
                    # print(f"⏳ 等待 {delay} 分钟... (到 {datetime.fromtimestamp(target_ts).strftime('%H:%M:%S')})")
                    end_time = time.time() + wait_sec
                    while time.time() < end_time and self.is_running:
                        time.sleep(0.5)
                    if not self.is_running:
                        return

                # ========== 使用锁读取该延时组的所有队列 ==========
                with self.queue_lock:  # ⭐ 加锁保护
                    time.sleep(1)
                    for qidx in delay_groups[delay]:
                        try:
                            counts[qidx] = self.cam_result_queues[qidx].get_nowait()
                        except Empty:
                            counts[qidx] = 0
                        # print(f"  队列[{qidx}]→{counts[qidx]}")

            # print(f"📊 收集到的数据: {counts}")

        except Exception as e:
            print(f"❌ 数据上传过程获取数据失败：{e}")
            return

        # ========== 设备配置 ==========
        device_config = {
            "设备ID1": "进钢化机",
            "设备ID2": "冲击线入口",
            "设备ID3": "进高温区",
            "设备ID4": "出高温区",
            "设备ID5-1": "冲击线网带出口1",
            "设备ID5-2": "冲击线网带出口2",
            "设备ID5-3": "冲击线网带出口3",
            "设备ID6-1": "水槽出口1",
            "设备ID6-2": "水槽出口2",
            "设备ID6-3": "水槽出口3",
            "设备ID7-1": "进均温炉1",
            "设备ID7-2": "进均温炉2",
            "设备ID8-1": "出均温炉1",
            "设备ID8-2": "出均温炉2"
        }

        try:
            collector = DataCollector(
                device_config=device_config,
                gateway_id="192168222211",
                data_list=counts
            )

            sender = DataSender(
                url="http://192.168.222.8:8021/go/countingSystem/cj",
                timeout=5
            )

            uploader = DataUploader(collector, sender)
            success = uploader.upload(verbose=True)

            if success:
                # print(f"✅ 上传成功: {counts}")
                pass
            else:
                # print(f"❌ 上传失败: {counts}")
                pass
        except Exception as e:
            # print(f"❌ 数据上传异常: {e}")
            pass