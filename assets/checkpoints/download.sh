#!/bin/bash

set -euo pipefail
IFS="\t\n"

wget -O yolov8s.ckpt 'https://download.mindspore.cn/toolkits/mindyolo/yolov8/yolov8-s_500e_mAP446-3086f0c9.ckpt'
