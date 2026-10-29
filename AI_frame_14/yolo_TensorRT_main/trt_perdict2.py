import time

from yolo_TensorRT_main.models import TRTModule
import cv2
import torch
from yolo_TensorRT_main.models.utils import blob, letterbox
from yolo_TensorRT_main.models.torch_utils import det_postprocess
import random


class TensorRTDetector2:
    def __init__(self, engine_path, class_names, device='cuda:0'):
        """
        初始化TensorRT检测器
        :param engine_path: TensorRT引擎文件路径
        :param class_names: 类别名称列表，例如['person', 'car']
        :param device: 计算设备，默认'cuda:0'
        """
        self.device = torch.device(device)
        self.engine = TRTModule(engine_path, self.device)
        self.H, self.W = self.engine.inp_info[0].shape[-2:]
        self.engine.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])
        self.class_names = class_names or []

        # 为每个类别生成随机但一致的颜色
        self.colors = {}
        for i in (self.class_names):
            random.seed(i)  # 确保每次运行颜色一致
            self.colors[i] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )

        print(f"Engine loaded: {engine_path}")
        print(f"Input shape: {self.engine.inp_info[0].shape}")



    def preprocess(self, image):
        """图像预处理并打印预处理信息"""
        self.image = image
        # 保存原始图像尺寸用于归一化和绘制
        self.orig_height, self.orig_width = self.image.shape[:2]

        # 执行预处理
        processed, self.ratio, self.dwdh = letterbox(self.image, (self.W, self.H))
        rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        tensor = blob(rgb, return_seg=False)
        self.dwdh_tensor = torch.asarray(self.dwdh * 2, dtype=torch.float32, device=self.device)

        print("\n=== Preprocessing Details ===")
        print(f"Original size: {self.orig_width}x{self.orig_height}")
        print(f"Resized to: {self.W}x{self.H}")
        print(f"Processed tensor shape: {tensor.shape}")

        return torch.asarray(tensor, device=self.device)



    def inference(self, tensor):
        """执行模型推理"""
        return self.engine(tensor)



    def postprocess(self, data, conf):
        """解析模型输出并返回结构化结果"""
        bboxes, scores, labels = det_postprocess(data)

        # 转换坐标到原始图像空间
        if bboxes.numel() > 0:
            bboxes -= self.dwdh_tensor
            bboxes /= self.ratio

        # 准备最终结果列表
        results = []
        # 颜色列表
        color_list = []

        # 处理每个检测对象
        for i, (bbox, score, label) in enumerate(zip(bboxes, scores, labels)):
            # 将边界框转换为[x1, y1, x2, y2]格式
            x1, y1, x2, y2 = bbox.cpu().numpy()

            # 确保坐标在图像范围内 (坐上，右下)
            x1 = max(0, min(x1, self.orig_width - 1))
            y1 = max(0, min(y1, self.orig_height - 1))
            x2 = max(0, min(x2, self.orig_width - 1))
            y2 = max(0, min(y2, self.orig_height - 1))


            # 转换为归一化的中心坐标和宽高
            width = (x2 - x1)
            height = (y2 - y1)
            x_center = x1 + width/2
            y_center = y1 + height/2



            """ 创建结果元组 (cls, conf, (x_center, y_center, width, height))"""
            # 获取类别名称和颜色
            cls_id = int(label.item())
            class_name = self.class_names[cls_id] if cls_id < len(self.class_names) else str(cls_id)

            result_tuple = (class_name,
                            float(score.item()),
                            (x_center, y_center, width, height))

            color_list.append(cls_id)

            # 置信度阈值
            if float(score.item()) > conf:
                # 添加输出结果
                results.append(result_tuple)



        """
       在原图上绘制检测框、类别和置信度
       :param image: 原始图像
       :param results: 检测结果列表
       :return: 绘制后的图像
        """
        # 创建图像的副本，避免修改原始图像
        img_with_detections = self.image

        # 绘制每个检测结果
        for idx, (cls_name, conf, (x_center, y_center, w, h)) in enumerate(results):
            # 绘制边界框
            cv2.rectangle(
                img_with_detections,
                (int(x_center - w/2), int(y_center - h/2)),
                (int(x_center + w/2), int(y_center + h/2)),
                self.colors[cls_name],
                5
            )

            # 准备标签文本
            label = f"{cls_name} {conf:.2f}"

            # 计算文本大小
            (label_width, label_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 2, 1
            )

            # 绘制标签背景
            # cv2.rectangle(
            #     img_with_detections,
            #     (int(x_center - w/2), int(y_center - h/2) - label_height - baseline - 5),
            #     (int(x_center - w/2) + label_width, int(y_center - h/2)),
            #     self.colors[cls_name],
            #     -1
            # )

            # 绘制标签文本
            cv2.putText(
                img_with_detections,
                label,
                (int(x_center - w/2), int(y_center - h/2) - baseline - 5 + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (0, 0, 255),
                2
            )


        return results, img_with_detections



    """
    模型推理
    """
    def process_image(self, image, conf=0.5):
        """
        端到端处理流水线并返回结构化结果和绘制后的图像
        :param image_path: 输入图像路径
        :param output_path: 输出图像保存路径（可选）
        :return: (检测结果列表, 绘制后的图像)
        """

        # 预处理
        a1 = time.time()
        tensor = self.preprocess(image)
        b1 = time.time()
        # print("-----预处理：", b1-a1)

        a = time.time()
        # 推理
        data = self.inference(tensor)
        b = time.time()
        # print("-----推理：", b-a)

        # 后处理
        # a2 = time.time()
        results, result_image = self.postprocess(data, conf)
        b2 = time.time()
        print("-----推理2：", b2 - a1)

        # ************************************
        # ------后处理
        G_li = []
        ng_li = []
        result_cls = []

        # 步骤1: 使用列表推导式筛选出所有 vlue[0] == 'G' 的元素
        g_elements = [value for value in results if value[0] == 'G']

        # 步骤2: 如果筛选结果非空，则取 vlue[1] 最大的元素；否则返回 None
        if g_elements:
            result = max(g_elements, key=lambda x: x[1])
            G_li.append(result[2])
            result_cls.append(result[0])
        else:
            result = None
        # print(G_li)

        # 步骤1: 使用列表推导式筛选出所有 vlue[0] == 'G' 的元素
        ng_li = [value[2] for value in results if value[0] == 'ng']
        # print(ng_li)

        # 判断 有无ng 目标
        if G_li and ng_li:
            G_x1 = int(G_li[0][0] - G_li[0][2] / 2)
            G_x2 = int(G_li[0][0] + G_li[0][2] / 2)
            G_y1 = int(G_li[0][1] - G_li[0][3] / 2)
            G_y2 = int(G_li[0][1] + G_li[0][3] / 2)

            for i, (center_x, center_y, w, h) in enumerate(ng_li):
                if G_x1 < center_x < G_x2 and G_y1 < center_y < G_y2:
                    result_cls.append("ng")

        # print(result_cls)

        # *******************************



        return result_cls, result_image




# ------预热------
# # 模型
engine_path =  r"D:\AI\AI_frame_12\yolo\ultralytics-main\runs\detect\train2\weights\best2.engine"

# 数据
img = cv2.imread(r"D:\AI\AI_frame_12\yolo_TensorRT_main\1.jpg")



# 类别名称（根据您的模型训练类别修改）
CLASS_NAMES =  ["G", "ng"]   # 替换为您的实际类别名称

# 初始化检测器
detector = TensorRTDetector2(engine_path, class_names=CLASS_NAMES)

# 推理单张图像
results, result_image = detector.process_image(img, 0.4)
print(results)





if __name__ == '__main__':
    pass

    # # ================= 配置参数 =================
    #
    # 模型
    # engine_path = r"D:\AI\AI_frame_12\yolo\ultralytics-main\train27\weights\best.engine"
    #
    # # 数据
    # img = cv2.imread(r"D:\img_data\1\2025_8_26\2025_8_26_18_26_47.jpg")
    #
    #
    # # 类别名称（根据您的模型训练类别修改）
    # CLASS_NAMES = ['ng_s', 'ok', 'ng', 'ok_ocr']  # 替换为您的实际类别名称
    #
    # # 初始化检测器
    # detector = TensorRTDetector2(engine_path, class_names=CLASS_NAMES)
    #
    # # 推理单张图像
    # results, result_image = detector.process_image(img, 0.3)
    # cv2.imwrite("1111.jpg", result_image)
    # print(results)


