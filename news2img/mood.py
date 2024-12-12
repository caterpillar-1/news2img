"""Providing mood detection ability.

Todo:
    * Implement ``MoodDectionAscend``.
"""

import copy
import cv2
import os
from PIL import Image
from typing import List, Dict, Tuple
from loguru import logger
from collections import defaultdict
from pathlib import Path

class NoFaceException(Exception):
    def __init__(self):
        super().__init__(self)

    def __str__(self):
        return "No face is found in the photo."
        

class MoodDetection:
    def __init__(self, **kwargs):
        pass

    def __call__(self, image: str | Image.Image) -> List[Dict]:
        """Get the mood of given image.

        Args:
            image: path to the image file or an existing PIL Image

        Returns:
            ``list`` in form ``[{ 'label': 'happy', 'score': 0.9 }, 
            { 'label': 'sad, score: 0.3 }]`` sorted by score from high to low.

        Raises:
            NoFaceException: if no face is found after NMS.
        """
        raise NotImplementedError()

class MoodDetectionAscend(MoodDetection):

    def __init__(self, config_file: os.PathLike):
        """Initialize model from CONFIG_FILE

        Args:
            config_file: path to config file in MindYOLO-like format
        """

        import mindspore as ms
        from mindyolo.models.model_factory import create_model
        from mindyolo.utils.config import load_config, Config 

        ms.set_context(device_id=0, device_target="CPU", mode=1)

        cfg, _, _ = load_config(config_file)
        cfg = Config(cfg)
        self._cfg = copy.deepcopy(cfg)

        ckpt = Path(cfg.network.checkpoint)
        if not ckpt.is_absolute():
            ckpt = Path(config_file).parent / ckpt
        ckpt = str(ckpt)

        self._network = create_model(
            model_name=cfg.network.model_name,
            model_cfg=cfg.network,
            num_classes=cfg.data.nc,
            sync_bn=False,
            checkpoint_path=ckpt,
        )
        
    @staticmethod
    def _scale_and_pad(input_image: Image.Image, output_shape: Tuple[int, int]) -> Image.Image:
        iw, ih = input_image.size
        ow, oh = output_shape
        scale = min(ow/iw, oh/ih)
        nw, nh = int(iw*scale), int(ih*scale)
        dx, dy = (ow-nw) // 2, (oh-nh) // 2

        input_image = input_image.resize((nw, nh))
        output_image = Image.new("RGB", (ow, oh), (128, 128, 128))
        output_image.paste(input_image, (dx, dy))

        return output_image

    def __call__(self, image: str | Image.Image) -> List[Dict]:
        import mindspore as ms
        from mindspore import Tensor
        from mindyolo.utils.metrics import non_max_suppression
        import numpy as np
        import sys

        # 1. Preprocess: transfrom input image
        if isinstance(image, str):
            image = PIL.Image.open(image)
        elif isinstance(image, Image.Image):
            pass
        else:
            raise TypeError()

        # now image: PIL.Image.Image, scale and pad with gray
        img_size = self._cfg.img_size
        image = self._scale_and_pad(image, (img_size, img_size))
        image.show()
        image = np.array(image)
        logger.warning("Check image's shape 1: {}", image.shape)

        # (H, W, C) -> (C, H, W), [0, 255] -> [0, 1]
        image = image.transpose(2, 0, 1) / 255.0
        image = np.expand_dims(image, 0)
        logger.warning("Check image's shape 2: {}", image.shape)

        image = Tensor(image, ms.float32)

        # 2. Model predict
        out, _ = self._network(image)
        # now out:
        # (x, y, w, h, c) or
        # (idx, (x, y, w, h, c))
        out = out.asnumpy()
        logger.warning("Check out's shape 1: {}", out.shape)

        # print(out)
        # 3. Non-maximun supression (reduce duplicate bboxs)
        out = non_max_suppression(
            out, 
            conf_thres=0.001,
            iou_thres=0.65,
            conf_free=False,
            multi_label=True,
            time_limit=20.0
        )

        
        # 4. Get mood label
        #    taking all the faces in the picture into account
        out = out[0]
        if len(out) == 0:
            raise NoFaceException()
        result = defaultdict(float)

        class_names = self._cfg.data.names
        logger.info("{} faces in total", len(out))
        for face in out:
            # logger.info("Face: {}", face)
            class_idx = int(face[5])
            score = face[4]
            result[class_idx] += score

        result = {class_names[k]: v for k, v in result.items()}
        return result


class MoodDetectionCpu(MoodDetection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from transformers import pipeline
        self._mood_detection = pipeline("image-classification", model="dima806/facial_emotions_image_detection")

    def __call__(self, image: str | Image.Image) -> List[Dict]:
        return self._mood_detection(image)

__all__ = ['MoodDetection', 'MoodDetectionCpu', 'MoodDetectionAscend', 'NoFaceException']
