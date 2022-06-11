#!/usr/bin/python3
# -*- coding:utf-8 -*-

# import json
# import tablib
# # json.text文件的格式： [{"a":1},{"a":2},{"a":3},{"a":4},{"a":5}]
# # 获取json数据
# with open('custom_out.txt', 'r', encoding='utf-8', errors='ignore') as f:
#     lines = f.readlines()
#     rrr=list()
#     for line3 in lines:
#         rrr.append(line3)
#     print(type(rrr))
#     rows = json.loads(json.dumps(rrr))
# # 将json中的key作为header, 也可以自定义header（列名）
# header = tuple([i for i in rows[0].keys()])
# data = []
# # 循环里面的字典，将value作为数据写入进去
# for row in rows:
#     body = []
#     for v in row.values():
#         body.append(v)
#     data.append(tuple(body))
# # 将含标题和内容的数据放到data里
# data = tablib.Dataset(*data,headers=header)
# # 写到桌面
# open('data_.xls', 'wb').write(data.xls)

import pandas as pd
import json

# 读取单行的json（1）
d_one = []
file_one = open(r"custom_out.txt", 'r', encoding='utf-8')
# 对txt进行遍历
for line in file_one:
    try:
        d_one.append(json.loads(line))
    except Exception as e:
        continue

# 创造一个dataframe，并讲空list中的内容赋入dataframe
df_one=pd.DataFrame(d_one)


df_one.to_excel("data_0318.xlsx", index=None)