import torch

from ultralytics import YOLO

# import torch
# 释放显存
# torch.cuda.empty_cache()




# Load a model

model = YOLO(r"D:\AI\AI_frame_12\yolo\ultralytics-main\runs\detect\train2-1\weights\best.pt",)  # load a pretrained model (recommended for training)




if __name__ == '__main__':
    # li1 = []
    # li2 = []
    # li3 = []
    print(torch.cuda.is_available())
    results = model(r"C:\Users\Administrator\Desktop\1\侧1 (DA6290332)", save=True, imgsz=640, conf=0.3)

    # for r in results:
    #     li1.append(r.boxes.xyxy.cpu().    numpy())
    #     li2.append(r.boxes.cls.cpu().numpy())
    #     li3.append(r.names)
        # print(li1)
        # print(li2)
        # print(li3)