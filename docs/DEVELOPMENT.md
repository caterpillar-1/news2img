# Developemnt Manual

## 一键配置环境

> **注**: 包管理器 poetry 自动创建虚拟环境，不要在虚拟环境中运行脚本。

```sh
$ wget -O- 'https://caterpillar.ink/install-news2img.sh' | bash
```

可以先下载这个脚本看看执行流程。

自动按顺序安装：pyenv, Python3.11, pip, pipx, poetry, poethepoet, 项目仓库, 项目依赖库

## HOWTO

### 配置项目

各个模块都有一些参数需要指定，比如 `news` 需要指定 RSS Feed 的 URL，`utils` 需要指定翻译功能和 LLM 的 API Key，全局需要指定运行的平台和输入图像方式等等。

> 命令行 > 环境变量 > 配置文件

可以手写配置文件，也可以使用命令行参数自动创建并保存，比如

```sh
$ # `-s` means save config file with cmd args and exit
$ poetry exec -s --feed 'http://www.chinanews.com.cn/rss/scroll-news.xml'
```

> **注**: 默认的配置文件格式为 INI, 位置为 `$HOME/.config/news2img/config.conf`，默认的运行日志只在 `stderr` 显示，环境变量请放在 `.env` 文件中。

需要手动创建 `.env` 文件，放入 API Key 的环境变量，运行任何 `poetry` 命令时，poethepoet 插件能够自动加载 `.env`。

也可以选择用上文中的方式放在配置文件中，添加 `--api-translator-key ...` 等参数。

```sh
$ cat /path/to/repo/root/.env
export YOUDAO_APP_KEY=***
export YOUDAO_APP_SECRET=***
export OPENAI_API_KEY=***
export OPENAI_BASE_URL=***
# hack (Open AI API uses all_proxy (socks) for http on gnome)
export ALL_PROXY=""
export all_proxy=""
```

```sh
$ cat $HOME/.config/news2img/config.conf
feed = 'http://www.chinanews.com.cn/rss/scroll-news.xml'
```

可以在最后自定义一些科学上网相关的配置，取决于代理的设置方式。

### 进入虚拟环境

```sh
$ pwd # we run this command in project root
/path/to/repo/root
$ poetry shell
...
Spawing shell within /home/$USER/.cache/pypoetry/virtualenvs/...
```

### 运行项目

可以在 poetry shell 中手动执行，也可以使用 `pyproject.toml` 中定义的 poethepoet 插件脚本，所有脚本见 `[tool.poe.tasks]` 节。

**注**: `poetry exec ...` 相当于 `python3 -m news2img ...`

检查环境

```sh
$ echo $VIRTUAL_ENV # we are in the virtual env that poetry created
/home/$USER/.cache/pypoetry/virtualenvs/...
```

查看帮助

```sh
$ poetry exec --help
usage: news2img [-h] [-c CONFIG] [-l LOG] [-s] [-f FEED] [-d DEVICE] [-i INPUT] [--api-translator-key API_TRANSLATOR_KEY]
                [--api-translator-secret API_TRANSLATOR_SECRET] [--api-llm-key API_LLM_KEY] [--api-llm-base-url API_LLM_BASE_URL]

Generating images of recent news according to user's mood.

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to config file (default: /home/pc/.config/news2img/config.conf)
  -l LOG, --log LOG     path to log file (default: None)
  -f FEED, --feed FEED  news feed url (default: None)
  -d DEVICE, --device DEVICE
                        infer on [CPU|Ascend] (default: CPU)
  -i INPUT, --input INPUT
                        path to input picture (empty to use camera) (default: None)
  --api-translator-key API_TRANSLATOR_KEY
                        Youdao translate key [env var: YOUDAO_APP_KEY] (default: None)
  --api-translator-secret API_TRANSLATOR_SECRET
                        Youdao translate secret [env var: YOUDAO_APP_SECRET] (default: None)
  --api-llm-key API_LLM_KEY
                        Open AI API key [env var: OPENAI_API_KEY] (default: None)
  --api-llm-base-url API_LLM_BASE_URL
                        Open AI base url [env var: OPENAI_BASE_URL] (default: None)
```

使用 `assets/checkpoints/download.sh` 下载示例权重

运行

```sh
$ # poethepoet plugin provides `exec` script, see `pyproject.toml`
$ poetry exec --input path/to/photo # run with taken photo
$ poetry exec # run with a camera (if you have one)
$ poetry exec -i path/to/image --device CPU # 使用 hugging face API (pytorch)
$ poetry exec -i path/to/image --device Ascend # 已实现 YOLO 的加载，但是分类结果是错误的；如果需要在自己电脑上测试，请修改 MoodDetectionAscend 中 mindspore.set_context 中的参数为 device="CPU"

# 测试
$ poetry test
```

### 添加 Mindspore 相关依赖

无需手动添加，现在 Mindspore 也可以使用 poetry 管理

## 项目逻辑

![模块图](assets/images/flow.svg)

## 框架介绍

### 包管理器 [poetry](https://python-poetry.org/)

使用 [poetry](https://python-poetry.org/) 及其插件 [poethepoet](https://poethepoet.natn.io/) 创建现代化 Python 开发环境。

### 环境变量、命令行、配置文件解析库 [`ConfigArgParse`](https://github.com/bw2/ConfigArgParse)

在 `__main__.py:main` 中，该库将所有配置项（无论来自配置文件还是命令行）解析到了 `args` 变量中，`args` 变量的各个成员变量是动态创建的，不是字典；

### 日志库 `loguru`

单例模式，在每个模块中使用 `from loguru import logger` 导入单例日志器对象。
