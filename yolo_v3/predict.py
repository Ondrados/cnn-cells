import os
import torch
import numpy as np
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader, random_split

from models import Darknet
from utils import non_max_suppression, xywh2xyxy

from dataset import MyTestDataset, get_test_transforms, my_collate

from conf.settings import BASE_DIR


models_path = os.path.join(BASE_DIR, "models")
images_path = os.path.join(BASE_DIR, "images")

if __name__ == "__main__":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Running on {device}...")

    model = Darknet(os.path.join(BASE_DIR, "yolo_v3/config/yolov3-custom.cfg")).to(device)
    model.load_state_dict(torch.load(os.path.join(models_path, "yolo_v3_2.pt"), map_location=device))

    dataset = MyTestDataset(split='stage1_test', transforms=get_test_transforms(rescale_size=(416, 416)))

    test_loader = DataLoader(dataset, batch_size=1, num_workers=0, shuffle=True)

    model.eval()
    for i, (image, targets) in enumerate(test_loader):
        image = image[0].to(device=device)
        name = targets["name"]

        outputs = model(image)
        outputs = non_max_suppression(outputs, conf_thres=0.5)

        boxes = outputs[0][:, 0:4]

        image_copy = Image.fromarray(image.cpu().numpy()[0, 0, :, :])
        if image_copy.mode != "RGB":
            image_copy = image_copy.convert("RGB")
        draw = ImageDraw.Draw(image_copy)
        for box in boxes:
            x0, y0, x1, y1 = box
            draw.rectangle([(x0, y0), (x1, y1)], outline=(255, 0, 255))
        image_copy.show()
        break