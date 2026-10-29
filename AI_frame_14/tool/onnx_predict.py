import copy
import os
import time

import onnxruntime as rt
import numpy as np
import cv2
import matplotlib.pyplot as plt
import yaml



# 前处理
def resize_image(image, size, letterbox_image):
    """
        对输入图像进行resize
    Args:
        size:目标尺寸
        letterbox_image: bool 是否进行letterbox变换
    Returns:指定尺寸的图像
    """
    ih, iw, _ = image.shape
    print(ih, iw)
    h, w = size
    # letterbox_image = False
    if letterbox_image:
        scale = min(w/iw, h/ih)
        nw = int(iw*scale)
        nh = int(ih*scale)
        image = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_LINEAR)
        # cv2.imshow("img", img)
        # cv2.waitKey()
        # print(image.shape)
        # 生成画布
        image_back = np.ones((h, w, 3), dtype=np.uint8) * 128
        # 将image放在画布中心区域-letterbox
        image_back[(h-nh)//2: (h-nh)//2 + nh, (w-nw)//2:(w-nw)//2+nw , :] = image
    else:
        image_back = image
        # cv2.imshow("img", image_back)
        # cv2.waitKey()
    return image_back


def img2input(img):
    img = np.transpose(img, (2, 0, 1))
    img = img/255
    return np.expand_dims(img, axis=0).astype(np.float32)

def std_output(pred):
    """
    将（1，84，8400）处理成（8400， 85）  85= box:4  conf:1 cls:80
    """
    pred = np.squeeze(pred)
    pred = np.transpose(pred, (1, 0))
    pred_class = pred[..., 4:]
    pred_conf = np.max(pred_class, axis=-1)
    pred = np.insert(pred, 4, pred_conf, axis=-1)
    return pred

def xywh2xyxy(*box):
    """
    将xywh转换为左上角点和左下角点
    Args:
        box:
    Returns: x1y1x2y2
    """
    ret = [box[0] - box[2] // 2, box[1] - box[3] // 2, \
          box[0] + box[2] // 2, box[1] + box[3] // 2]
    return ret

def get_inter(box1, box2):
    """
    计算相交部分面积
    Args:
        box1: 第一个框
        box2: 第二个狂
    Returns: 相交部分的面积
    """
    x1, y1, x2, y2 = xywh2xyxy(*box1)
    x3, y3, x4, y4 = xywh2xyxy(*box2)
    # 验证是否存在交集
    if x1 >= x4 or x2 <= x3:
        return 0
    if y1 >= y4 or y2 <= y3:
        return 0
    # 将x1,x2,x3,x4排序，因为已经验证了两个框相交，所以x3-x2就是交集的宽
    x_list = sorted([x1, x2, x3, x4])
    x_inter = x_list[2] - x_list[1]
    # 将y1,y2,y3,y4排序，因为已经验证了两个框相交，所以y3-y2就是交集的宽
    y_list = sorted([y1, y2, y3, y4])
    y_inter = y_list[2] - y_list[1]
    # 计算交集的面积
    inter = x_inter * y_inter
    return inter

def get_iou(box1, box2):
    """
    计算交并比： (A n B)/(A + B - A n B)
    Args:
        box1: 第一个框
        box2: 第二个框
    Returns:  # 返回交并比的值
    """
    box1_area = box1[2] * box1[3]  # 计算第一个框的面积
    box2_area = box2[2] * box2[3]  # 计算第二个框的面积
    inter_area = get_inter(box1, box2)
    union = box1_area + box2_area - inter_area   #(A n B)/(A + B - A n B)
    iou = inter_area / union
    return iou
def nms(pred, conf_thres, iou_thres):
    """
    非极大值抑制nms
    Args:
        pred: 模型输出特征图
        conf_thres: 置信度阈值
        iou_thres: iou阈值
    Returns: 输出后的结果
    """
    box = pred[pred[..., 4] > conf_thres]  # 置信度筛选
    cls_conf = box[..., 5:]
    cls = []
    for i in range(len(cls_conf)):
        cls.append(int(np.argmax(cls_conf[i])))
    total_cls = list(set(cls))  # 记录图像内共出现几种物体
    output_box = []
    # 每个预测类别分开考虑
    for i in range(len(total_cls)):
        clss = total_cls[i]
        cls_box = []
        temp = box[:, :6]
        for j in range(len(cls)):
            # 记录[x,y,w,h,conf(最大类别概率),class]值
            if cls[j] == clss:
                temp[j][5] = clss
                cls_box.append(temp[j][:6])
        #  cls_box 里面是[x,y,w,h,conf(最大类别概率),class]
        cls_box = np.array(cls_box)
        sort_cls_box = sorted(cls_box, key=lambda x: -x[4])  # 将cls_box按置信度从大到小排序
        # box_conf_sort = np.argsort(-box_conf)
        # 得到置信度最大的预测框
        max_conf_box = sort_cls_box[0]
        output_box.append(max_conf_box)
        sort_cls_box = np.delete(sort_cls_box, 0, 0)
        # 对除max_conf_box外其他的框进行非极大值抑制
        while len(sort_cls_box) > 0:
            # 得到当前最大的框
            max_conf_box = output_box[-1]
            del_index = []
            for j in range(len(sort_cls_box)):
                current_box = sort_cls_box[j]
                iou = get_iou(max_conf_box, current_box)
                if iou > iou_thres:
                    # 筛选出与当前最大框Iou大于阈值的框的索引
                    del_index.append(j)
            # 删除这些索引
            sort_cls_box = np.delete(sort_cls_box, del_index, 0)
            if len(sort_cls_box) > 0:
                # 我认为这里需要将clas_box先按置信度排序， 才能每次取第一个
                output_box.append(sort_cls_box[0])
                sort_cls_box = np.delete(sort_cls_box, 0, 0)
    return output_box

def cod_trf(result, pre, after):
    """
    因为预测框是在经过letterbox后的图像上做预测所以需要将预测框的坐标映射回原图像上
    Args:
        result:  [x,y,w,h,conf(最大类别概率),class]
        pre:    原尺寸图像
        after:  经过letterbox处理后的图像
    Returns: 坐标变换后的结果,
    """

    res = np.array(result)
    print(res.shape)

    # if res.size == 0:
    #     # print("预测结果为空，无法进行后续操作！")
    #     return None

    x, y, w, h, conf, cls = res.transpose((1, 0))
    x1, y1, x2, y2 = xywh2xyxy(x, y, w, h)  # 左上角点和右下角的点
    h_pre, w_pre, _ = pre.shape
    h_after, w_after, _ = after.shape
    scale = max(w_pre/w_after, h_pre/h_after)  # 缩放比例
    h_pre, w_pre = h_pre/scale, w_pre/scale  # 计算原图在等比例缩放后的尺寸
    x_move, y_move = abs(w_pre-w_after)//2, abs(h_pre-h_after)//2  # 计算平移的量
    ret_x1, ret_x2 = (x1 - x_move) * scale, (x2 - x_move) * scale
    ret_y1, ret_y2 = (y1 - y_move) * scale, (y2 - y_move) * scale
    ret = np.array([ret_x1, ret_y1, ret_x2, ret_y2, conf, cls]).transpose((1, 0))
    return ret


def draw(res, image, cls):
    """
    将预测框绘制在image上，并返回预测框及对应的类别
    Args:
        res: 预测框数据
        image: 原图
        cls: 类别列表
    Returns:
        results: 预测框信息列表，每个元素为 (x1, y1, x2, y2, class_name, confidence)
    """
    results = []
    for r in res:
        x1, y1, x2, y2, conf, cls_idx = list(map(int, r[:4])) + [r[4], r[5]]  # 修正转换问题
        class_name = cls[int(cls_idx)]
        results.append((x1, y1, x2, y2, class_name, round(float(conf), 2)))

        # 画框
        image = cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 5)
        # # 显示类别和置信度
        # text = f"{class_name}: {round(float(conf), 2)}"
        # cv2.putText(image, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        # 表明类别
        text = "{}:{}".format(cls[int(r[5])], round(float(r[4]), 2))
        h, w = int(r[3]) - int(r[1]), int(r[2]) - int(r[0])  # 计算预测框的长宽
        font_size = min(h / 640, w / 640) * 3  # 计算字体大小（随框大小调整）
        image = cv2.putText(image, text, (max(10, int(r[0])), max(20, int(r[1]) - 40)), cv2.FONT_HERSHEY_COMPLEX,
                            max(font_size, 3), (0, 0, 255), 6)  # max()为了确保字体不过界


    return results, image


# """
# 加载配置文件---yolo训练时的yaml
# """
# config_file = r"D:\wg\AI_project_BF\test\v8\yolo-xml_to_txt\data.yaml"
# with open(config_file, "r") as config:
#     config = yaml.safe_load(config)







"""
onnx 模型推理-----------------------------------------
"""

class Onnx_detection:

    def __init__(self, model_path):
        # 加载 ONNX 模型并创建推理会话
        self.sess = rt.InferenceSession(model_path)


    def inference(self, img, img_size, conf, iou):
        """
        进行 ONNX 模型推理，返回检测结果和绘制后的图像。

        Args:
            model_path (str): ONNX 模型文件路径。
            img (numpy.ndarray): 输入图像（BGR格式）。
            img_size (tuple): 目标输入尺寸 (height, width)。
            conf (float): 置信度阈值。
            iou (float): NMS 的 IOU 阈值。

        Returns:
            result (list): 预测框信息列表，每个元素为 (x1, y1, x2, y2, class_name, confidence)。
            result_image (numpy.ndarray): 绘制了预测框的图像。
        """

        # 获取标准输入尺寸
        std_h, std_w = img_size[0], img_size[1]

        # 类别名称，需与训练时的 YAML 文件保持一致
        class_list = ['a', 'b', 'ng', 'ng2', 'c', 'd']

        # 检查图像是否为空
        if img.size == 0:
            print("路径有误！")
            return None, None

        # 预处理：调整图像大小到标准尺寸（std_w, std_h），保持原始比例并进行填充
        img_after = resize_image(img, (std_w, std_h), True)  # 形状变为 (640, 640, 3)

        # 转换图像格式，使其符合模型输入要求
        data = img2input(img_after)



        # 获取模型输入和输出的名称
        input_name = self.sess.get_inputs()[0].name
        label_name = self.sess.get_outputs()[0].name

        # 进行推理，得到输出
        pred = self.sess.run([label_name], {input_name: data})[0]
        # 输出形状示例: (8400, 84)，其中：
        # - 8400：不同尺度的预测框总数
        # - 84：包含 80 个类别分数 + 4 个回归框参数 (x, y, w, h)

        # 处理模型输出，将格式转换为通用形式
        pred = std_output(pred)

        # 进行置信度过滤和非极大值抑制（NMS），获取最终的预测框
        result = nms(pred, conf, iou)  # 结果格式：[x, y, w, h, conf, class_id]


        # 检测到有目标
        if len(result) != 0:
            # 坐标变换：将 YOLOv8 预测的 (x, y, w, h) 转换为 (x1, y1, x2, y2)
            result = cod_trf(result, img, img_after)

            # 绘制预测框，并获取最终结果
            result, result_image = draw(result, img, class_list)

            return result, result_image  # 返回检测框信息和绘制后的图像

        # 无目标 []
        else:
            print("not target")
            return result, img







if __name__ == '__main__':
    img = cv2.imread(r"D:\wg\AI_project_BF\test\v8\yolo-xml_to_txt - 3\dataset\VOCdevkit\JPEGImages\000004.jpg")

    # 实例化对象
    onnx_predict = Onnx_detection(r"D:\wg\AI_project_BF\test\v8\ultralytics-main\runs\detect\train18\weights\best.onnx")

    a = time.time()
    result, img = onnx_predict.inference(img, (640, 640), 0.5, 0.7)
    b = time.time()
    print("predict time:", b-a)
    print(result)
    # img = cv2.resize(img, (1280, 950))
    # cv2.imshow("1", img)
    # cv2.waitKey(0)