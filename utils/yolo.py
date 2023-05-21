from ultralytics.yolo.utils import ops
from ultralytics.nn.tasks import  attempt_load_weights
import cv2
import time
import torch
import numpy as np

INPUT_W=640
INPUT_H=640

def preprocess_image(image_raw):
    h, w, c = image_raw.shape
    image = cv2.cvtColor(image_raw, cv2.COLOR_BGR2RGB)

    r_w = INPUT_W / w
    r_h = INPUT_H / h
    if r_h > r_w:
        tw = INPUT_W
        th = int(r_w * h)
        tx1 = tx2 = 0
        ty1 = int((INPUT_H - th) / 2)
        ty2 = INPUT_H - th - ty1
    else:
        tw = int(r_h * w)
        th = INPUT_H
        tx1 = int((INPUT_W - tw) / 2)
        tx2 = INPUT_W - tw - tx1
        ty1 = ty2 = 0

    image = cv2.resize(image, (tw, th),interpolation=cv2.INTER_LINEAR)
  
    image = cv2.copyMakeBorder(
        image, ty1, ty2, tx1, tx2, cv2.BORDER_CONSTANT, (114, 114, 114)
    )
    image = image.astype(np.float32)
    image /= 255.0

    image = np.transpose(image, [2, 0, 1])
    image = np.expand_dims(image, axis=0)
    image = np.ascontiguousarray(image)
    return image, image_raw, h, w

def postprocess(preds, img, orig_img):
    preds = ops.non_max_suppression(preds,
                                    conf_thres=0.25,
                                    iou_thres=0.45,
                                    agnostic=False,
                                    max_det=300)
    return preds

def predict(model, image_raw, name):
    """
    说明:
        预测
    参数:
        :param model: 模型
        :param image_raw: 图片
        :param name: 标签
    返回:
        预设数据
    """
    data = []

    image,image_raw,h,w = preprocess_image(image_raw)
    input_ = torch.tensor(image)

    preds = model(input_)

    preds = postprocess(preds, image, image_raw)

    for i, det in enumerate(preds):
        if det is not None and len(det):
            det[:, :4] = ops.scale_boxes(image.shape[2:], det[:, :4], image_raw.shape).round()
            for i in det:
                if int(i[5]) != 12:
                    data.append({"name": name[int(i[5])],"credibility": int(i[4] * 100) / 100,"pos": (int(i[0]), int(i[1]), int(i[2]), int(i[3]))})
                    
    return data
