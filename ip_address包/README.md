1、所需python包：

```python
from qqwry import QQwry   #pip install qqwry-py3
from IPy import IP
import socket
import threading
import csv
import time
import eventlet
from urllib.parse import urlparse
```

2、多线程处理函数：

threads_ip(参数1，参数2)：

输入：线程数，要处理的csv文件（只有一列netloc）

输出：有ip结果的csv(netloc，ip， address)