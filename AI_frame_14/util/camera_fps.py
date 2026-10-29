import cv2
import time

def camera_fps():
    cap = cv2.VideoCapture(0)  # 打开默认摄像头，你也可以指定摄像头索引来打开其他摄像头

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    frame_count = 0
    start_time = time.time()  # 记录开始时间

    while True:
        ret, frame = cap.read()  # 从摄像头读取一帧图像

        if ret:
            frame_count += 1  # 记录帧数

            # 计算FPS（帧每秒）
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time

            # 在图像上显示FPS
            cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("摄像头", frame)  # 显示摄像头画面

            input_key = cv2.waitKey(1)
            if input_key == ord('q'):
                break  # 如果用户按下'q'键，退出循环
        else:
            break

    cap.release()  # 释放摄像头资源
    cv2.destroyAllWindows()  # 关闭所有打开的窗口

if __name__ == "__main__":
    camera_fps()  # 调用主函数
