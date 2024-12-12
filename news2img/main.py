"""Main routine of the APP.

This module instantiates components in submodules and perform data processing
pipeline, which mainly consists of four steps:

#. init: load config, parse arguments and enable logging
#. get news and mood
#. generate prompt from text and mood
    
    #. translate
    #. extract keywords

#. draw a picture with given news and mood

Example:
    To run the app, you can use poetry_ ::

        $ pwd
        /path/to/repo/root
        $ # run with taken picture
        $ poetry exec -i <path/to/photo>
        $ # run with a camera to take picture
        $ poetry exec
    
    You should read `README.md` for more infomation.

Todo:
    * turn to ``MoodDectionAscend`` and ``DrawAscend``

.. _poetry:
    https://python-poetry.org/

"""


APP = "news2img"

import os
import re
import platformdirs
import configargparse
import cv2
import random
import pprint
from loguru import logger
from PIL import Image

from .news import News
from .mood import MoodDetectionCpu, MoodDetectionAscend
from .device import Camera
from .utils import Translator, SummarizerLLM
from .draw import DrawCpu, DrawAscend

def main():
    # 1. init: load config, parse arguments and enable logging

    config_file = str(platformdirs.user_config_path(APP, ensure_exists=True) / "config.conf")

    configargparse.init_argument_parser(
        prog=APP,
        description='''
            Generating images of recent news according to user's mood.
        ''',
        default_config_files=[config_file],
    )

    parser = configargparse.get_argument_parser()
    parser.add("-c", "--config", is_config_file=True, help="path to config file", default=config_file)
    parser.add("-l", "--log", help="path to log file")
    parser.add("-s", help="save command line parameters to config file", action="store_true")

    parser.add("-f", "--feed", help="news feed url")
    parser.add("-d", "--device", help="infer on [CPU|Ascend]", default="CPU")
    parser.add("-i", "--input", help="path to input picture (empty to use camera)")

    parser.add("--api-translator-key", help="Youdao translate key", env_var='YOUDAO_APP_KEY')
    parser.add("--api-translator-secret", help="Youdao translate secret", env_var='YOUDAO_APP_SECRET')

    parser.add("--api-llm-key", help="Open AI API key", env_var="OPENAI_API_KEY")
    parser.add("--api-llm-base-url", help="Open AI base url", env_var="OPENAI_BASE_URL")

    args = parser.parse_args()

    if args.s:
        parser.write_config_file(args, [args.config], exit_after=True)

    if args.log:
        logger.add(args.log, rotation="1 MB")

    config_error = lambda c: (logger.error(f"set '{c}' in config file or pass in cmd."), exit(1))

    # 2. get news and mood
    news = News(args.feed or config_error("feed"))
    args.device in ["CPU", "Ascend"] or config_error("device")
    mood = MoodDetectionCpu() if args.device == "CPU" else MoodDetectionAscend("assets/configs/yolov8s.yaml") # TODO: change

    if args.input:
        photo = Image.open(args.input)
    else:
        camera = Camera(0)
        photo = camera()[0]

    news = [e['summary'] for e in news]

    logger.info("news: {}", pprint.pformat(news))
    photo.show()
    mood = mood(photo)
    logger.info("mood: {}", mood)

    text = random.choice(news)
    logger.info("text: {}", text)

    # 3. generate prompt from text and mood

    ## 3.1 translate
    if bool(re.search(r'[\u4e00-\u9fff]', text)): # detect chinese news
        translator = Translator(
        # ConfigArgParse library has a bug, we hack it
            os.environ.get('YOUDAO_APP_KEY') or args.api_translator_key or config_error('translator_key'), 
            os.environ.get('YOUDAO_APP_SECRET') or args.api_translator_secret or config_error('translator_secret')
        )
        # translate into english
        english_text = translator(text, src='auto', dst='en')
    else:
        english_text = text

    logger.info("translated_text: {}", english_text)

    ## 3.2 extract keywords

    #if len(english_text) < 500:
        ### 3.2.1 short news - LLMs might perform better
    summarizer = SummarizerLLM(
        api_key = os.environ.get('OPENAI_API_KEY') or args.api_llm_key or config_error('OPENAI_API_KEY'),
        base_url = os.environ.get('OPENAI_BASE_URL') or args.api_llm_base_url or config_error('OPENAI_BASE_URL')
    )
    #else:
    #    ### 3.2.2 long news - traditional methods perform faster
    #    raise NotImplementedError()

    summary = summarizer(english_text)
    logger.info("summary = {}", summary)

    keywords = list(map(str.strip, summary.splitlines()))
    logger.info("keywords = {}", keywords)

    # 4. draw a picture with given news and mood

    draw = DrawCpu() if args.device == "CPU" else DrawAscend()
    prompt = '((' + mood[0]['label'] + ')), ' + ", ".join(keywords)
    logger.info("prompt = {}", prompt)
    images = draw(prompt)

    logger.info("images = {}", images)
