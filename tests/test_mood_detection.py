from news2img.mood import *
from PIL import Image
import tempfile
from pathlib import Path
from itertools import chain
from functools import reduce
from loguru import logger

IMAGE_BASE_DIR = "assets/images/"
IMAGE_PATTERNS = ["*.jpg", "*.png", "*.bmp"]

def test_mood_detection_ascend():
    CONFIG_FILE = "assets/configs/yolov8s.yaml"
    flatten = lambda f, xs: reduce(lambda a, b: list(a) + list(b), map(f, xs))
    images = flatten(Path(IMAGE_BASE_DIR).glob, IMAGE_PATTERNS)
    logger.info("Test images: {}", images)

    logger.info("Building model...")
    mood = MoodDetectionAscend(CONFIG_FILE)

    for image in images:
        logger.info("Image: {}", image)
        image = Image.open(image)
        try:
            result = mood(image)
        except NoFaceException:
            logger.info("Result: No face!")
            continue

        logger.info("Result: {}", result)
        
    
