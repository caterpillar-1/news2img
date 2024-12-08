"""Over-simplified abstraction layer over sensors."""

import cv2
from PIL import Image
from typing import List
from loguru import logger

class Camera:
    def __init__(self, id: int):
        self._capture = cv2.VideoCapture(id)

    def __call__(self, frame_count: int=1) -> List[PIL.Image]:
        """
            Example:
                ::

                    cam = Camera(0)
                    photo = cam(frame_count=1)[0]
        """
        frame_list = []
        while len(frame_list) < frame_count:
            while True:
                rc, frame = self._capture.read()
                if rc:
                    frame_list.append(Image.fromarray(cv2.cvtColor(frame ,cv2.COLOR_BGR2RGB)))
                else:
                    logger.error("failed to capture")
