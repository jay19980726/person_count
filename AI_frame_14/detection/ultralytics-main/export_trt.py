from ultralytics import YOLO





#
# model = YOLO(r"D:\AI\AI_frame_12\yolo\ultralytics-main\yolo11n.pt",)  # load a pretrained model (recommended for training)
#
# if __name__ == '__main__':
#     result = model.export(format="engine")



from torch import nn

from ultralytics import YOLO

# Load the classification model
model = YOLO("yolo11n-cls.pt")

# Add average pooling layer
head = model.model.model[-1]
pool = nn.Sequential(nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten(start_dim=1))
pool.f, pool.i = head.f, head.i
model.model.model[-1] = pool

# Export to TensorRT
model.export(format="engine", half=True, dynamic=True, batch=32)