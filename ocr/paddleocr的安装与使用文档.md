# paddleocr的安装与使用文档

## 一、介绍

[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 是一个基于百度飞桨的OCR工具库，包含总模型仅8.6M的超轻量级中文OCR，单模型支持中英文数字组合识别、竖排文本识别、长文本识别。同时支持多种文本检测、文本识别的训练算法。

本教程将介绍PaddleOCR的基本使用方法以及如何使用它开发一个自动搜题的小工具。

项目地址：

https://gitee.com/puzhiweizuishuai/OCR-CopyText-And-Search

OR

https://github.com/PuZhiweizuishuai/OCR-CopyText-And-Search

## 二、安装

虽然PaddleOCR支持服务端部署并提供识别API，但根据我们的需求，搭建一个本地离线的OCR识别环境，所以此次我们只介绍如何在本地安装并使用的做法。

### 1、安装PaddlePaddle飞桨框架

#### 环境准备

目前飞桨支持的环境

Windows 7/8/10 专业版/企业版 (64bit)

GPU版本支持CUDA 10.1/10.2/11.0/11.2，且仅支持单卡

Python 版本 3.6+/3.7+/3.8+/3.9+ (64 bit)

pip 版本 20.2.2或更高版本 (64 bit)

**官方安装文档：https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/pip/linux-pip.html**

#### 1.1  CPU版本安装

```python
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
```

(注意此版本为CPU版本，如需GPU版本请查看[PaddlePaddle文档](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/pip/windows-pip.html))

#### 1.2  GPU版本安装（外星人服务器举例）

- **CUDA 工具包10.1/10.2配合cuDNN 7 (cuDNN版本>=7.6.5, 如需多卡支持，需配合NCCL2.7及更高)**

- 执行以下命令安装：

```python
python -m pip install paddlepaddle-gpu==2.2.1.post101 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

​      安装完成后您可以使用 `python` 进入python解释器，输入`import paddle` ，再输入 `paddle.utils.run_check()`

如果出现`PaddlePaddle is installed successfully!`，说明您已成功安装。

### 2、安装PaddleOCR

```bash
pip install "paddleocr>=2.0.1" # 推荐使用2.0.1+版本
```

（注意：切换到同一python环境下，可以用python -m pip install ***，注意后边是否需要加 --user）

## 三、测试使用

**参数use_gpu默认为False，若使用gpu环境，则改为True：**

```
ocr = PaddleOCR(use_angle_cls=True, use_gpu=True, lang="ch")
```

**参考代码：**

```python
# import sys
# sys.path.append("/wfd_batch_cloud/")
# sys.path.append("/wfd_batch_cloud/core/utils")
import os
import csv
import time
from paddleocr import PaddleOCR, draw_ocr

# Paddleocr目前支持中英文、英文、法语、德语、韩语、日语，可以通过修改lang参数进行切换
# 参数依次为`ch`, `en`, `french`, `german`, `korean`, `japan`。
ocr = PaddleOCR(use_angle_cls=True, use_gpu=True, lang="ch")  # need to run only once to download and load model into memory
# 选择你要识别的图片路径
def test_ocr(img_path):
    result = ocr.ocr(img_path, cls=True)
    OCR_result = []
    for line in result:
        OCR_result.append(line[1][0])
    res = ' '.join(OCR_result)
    print(res)
    return res


if __name__ == '__main__':
    """
    读取filepath下的所有jpg文件，图片识别之后存入save_file中，加上识别每张图片的时间
    """
    save_file = 'result_1223.csv'
    filePath = 'pics/'
    paths = os.listdir(filePath)
    with open(save_file, 'w', encoding='utf-8',newline='') as save_f:
        writer = csv.writer(save_f)
        # 先写入columns_name
        writer.writerow(["url", "paddle_ocr", "ocr_time"])
        for i in paths:
            a = time.time()
            img_path = f'{filePath}{i}'
            baidu_res = test_ocr(img_path)
            b1 = time.time() - a
            line = [i, baidu_res, b1]
            # 写入多行用writerows
            writer.writerow(line)
```

## 四、结果对比

使用GPU环境和CPU环境分别识别240张异常网站图片，时间对比如下：

|           | GPU    | CPU     |
| --------- | ------ | ------- |
| time_sum  | 24.49s | 341.79s |
| time_mean | 0.102s | 1.42s   |
| time_     | 0.05s  | 2.0s    |

