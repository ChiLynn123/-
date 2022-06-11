# socket请求ip遇到的问题

请求ip及归属地代码：

```Python
import socket
q = QQwry()
q.load_file('qqwry.dat')
ip = socket.gethostbyname(url)  #ip
address = list(q.lookup(ip))    #归属地及服务商
```

## 问题汇总：

### 1、出现第三方包已安装但是import出错的解决方法：

```Python
#注意python版本2和3的区别
import sys
sys.path.append(r'/usr/local/lib/python3.6/site-packages')
```

### 2、.gethostbyname（）的参数必须是域名，不能带有http和https:

```python 
from urllib.parse import urlparse
if url.startswith("http"):
    url = urlparse(url).netloc
```

### 3、请求超时问题：如果不加时间限制，如果网速慢可能会请求到30s也请求不到，必须设置时间限制，超时跳出。尝试解决的方法：

#### （1）eventlet方式：

```Python
import eventlet
eventlet.monkey_patch()
with eventlet.Timeout(1, False):
      ip = socket.gethostbyname(url)
      address = list(q.lookup(ip))
```

问题：单独运行脚本可以，但是与项目集成失败，与gunicorn部署的flask不兼容。

#### （2）socket.setdefaulttimeout(1)方式：

问题：这个setdefaulttimeout对socket模块方法没有用处，只是针对socket.socket对象设置超时。

socket模块介绍：https://blog.51cto.com/unixman/1656641

socket实例时间设置：https://blog.csdn.net/whatday/article/details/104059531

#### （3）修改/etc/resolv.conf配置文件：

域名解析优化方案;https://www.jianshu.com/p/2c1c081cc521

问题：可以限制住时间，因为要更改配置文件，但是不确定是否会影响其他的socket模块如爬虫

#### （4）用装饰器 func_timeout 解决函数超时问题（已使用此方法）

参考: https://zhuanlan.zhihu.com/p/39743129

```Python
#安装：pip install func_timeout

#使用：在你的函数前加上装饰器，如下：
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from func_timeout import func_set_timeout

@func_set_timeout(1)
def task():
    while True:
        print('hello world')
        time.sleep(1)
if __name__ == '__main__':
     try:
        task()
    except func_timeout.exceptions.FunctionTimedOut:
        print('task func_timeout')
```

# 中国地图展示：

```python
from pyecharts import Map
province_distribution = {'四川': 239.0, '浙江': 231.0, '福建': 203.0, '江苏': 185.0, '湖南': 152.0, '山东': 131.0, '安徽': 100.0, '广东': 89.0, '河北': 87.0, '湖北': 84.0, '吉林': 75.0}
province = list(province_distribution1.keys()) 
num = list(province_distribution1.values()) 
chinaMap = Map(width=1200, height=600) 
chinaMap.add(name="分布数量", 
             attr=province, 
             value=num, 
             visual_range=[0, 239], 
             maptype='china', 
             is_visualmap=True) 
chinaMap.render(path="中国地图.html")
"""
其中参数name指的是显示在地图正上方的标题，
attr就是一个包含了各省份名称的列表，
value就是包含了各省份对应数值的列表，
visual_range指的是整个数据中的数值范围，
maptype就是指的地图类型，
is_visualmap代表是否显示颜色
"""
```

1、第一步：安装pyecharts

```Python
pip install pyecharts==0.1.9.4 
```

2、显示地市名称：添加1923行:

```Python
"label":{"normal":{"show":true}},
```

3、只显示province_distribution中的名称：

在133行中删除其他地市的名称即可









