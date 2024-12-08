"""Providing mood detection ability.

Todo:
    * Implement ``MoodDectionAscend``.
"""

import cv2
import PIL
from typing import List, Dict

class MoodDetection:
    def __init__(self, **kwargs):
        pass

    def __call__(self, image: str | PIL.Image) -> List[Dict]:
        """Get the mood of given image.

        Args:
            image: path to the image file or an existing PIL Image

        Returns:
            ``list`` in form ``[{ 'label': 'happy', 'score': 0.9 }, 
            { 'label': 'sad, score: 0.3 }]`` sorted by score from high to low.

        """
        raise NotImplementedError()

class MoodDetectionAscend(MoodDetection):
    pass


class MoodDetectionCpu(MoodDetection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from transformers import pipeline
        self._mood_detection = pipeline("image-classification", model="dima806/facial_emotions_image_detection")

    def __call__(self, image: str | cv2.UMat):
        return self._mood_detection(image)

__all__ = [MoodDetection, MoodDetectionCpu, MoodDetectionAscend]
