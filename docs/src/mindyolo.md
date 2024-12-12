# Mindyolo 的使用

观察配置文件 `yolo*.yml`,

`network`: 由于 YOLO 各个版本的网络结构相似，其中有许多相同的部分，抽象出形成了类。这些类的构造函数的参数写在配置文件的 下。

`data`: 取 YOLO 模型输出中置信度最大的类型的下标，用来索引 `data.names` 数组，可以反向查找到类别名称。

## YOLO 原理

### YOLO 的工作模式

一个常见的需求是检测出图片中有什么物体。目标对象可能在图像的任意区域。

简单思路：先用一个检测模型找出所有物体所在的 Bounding Box，截图后传给分类模型，两步完成。

YOLO (You only look once) 如其名，能够一次正向推理，同时完成目标识别和分类两个任务。

YOLO 有 5 种工作模式，对于本项目的需求，应该使用 Detection 模式（而不是 Classification）。

### YOLO 的输入和输出

YOLO 的输入呈形 $([N,] C, H, W)$，就是 $N$ 张图片，每张图片 $C$ 个通道，宽 $W$ 高 $H$；

显然，$C = 3$；$H$, $W$ 对应了配置文件

YOLO 的输出呈形 $([N,] M, (x, y, w, h, c))$，就是对于输入的 $N$ 张图片，每一张图片识别出 $M$ 个 Bounding Box，这个 Box 位于 $(x, y)$ 处，尺寸为 $(w, h)$，类别为 $\mathsf{names}[\mathsf{int}(c)]$

> **注**: $c$ 的形式可能不只是一个数，可能是类似多分类的 One-hot Vector

### 输入输出的预处理

输入部分，因为模型输入尺寸是确定的，因此需要将图片缩放、居中、将背景涂成灰色。

输出部分，因为模型一定会预测 $M$ 个 Bounding Box，其中许多 Box 置信度很低，而且存在大量 Box 重叠、重复的问题。因此需要使用 Non-maximum Supression 算法进行去重、筛选。

## MindYOLO 框架实现

- MindYOLO 的输入预处理步骤、输出后期处理步骤、模型结构的配置项是通过 `eval(class_name: str)` 实现的，比如配置文件中是一个字符串 `Upsample`，在解析配置文件时，会在框架代码中 `eval` 这个 `str`，从而获得对应的 `nn.Cell` 子类；

## 训练和推理部分的接口

使用 MindYOLO 配置文件的格式，在其中添加一些新字段：

- `network.checkpoint` (相对路径字符串): `../checkpoints/yolov8s.ckpt`

- `data.names` (List\[str\]): 类别名称的列表，被模型输出类型下标索引
