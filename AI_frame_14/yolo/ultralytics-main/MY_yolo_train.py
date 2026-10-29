from ultralytics import YOLO

import torch
# 释放显存
torch.cuda.empty_cache()
# print(torch.cuda.is_available())




# model = YOLO(r"D:\AI\AI_frame_12\yolo\ultralytics-main\yolo11n.pt")  # load a pretrained model (recommended for training)
model = YOLO(r"D:\AI_predict\AI_frame_14\yolo\ultralytics-main\runs\detect\train\weights\last.pt")  # load a pretrained model (recommended for training)



if __name__ == '__main__':
    # Train the model
    results = model.train(data=r'D:\AI_predict\AI_frame_14\yolo\yolo-xml_to_txt\data.yaml',
                          epochs=300, imgsz=640, patience=30, batch=4, workers=4, resume=True)  # scale=0, mosaic=0, close_mosaic=0


