import pandas as pd
import os
filePath = 'D:/WORK_DATA/三期/推广使用/反诈中心数据结果/1'
allxls=os.listdir(filePath)
allxlss = []
for i in allxls:
    j = ('D:/WORK_DATA/三期/推广使用/反诈中心数据结果/1/'+i)
    allxlss.append(j)

li = []
for i in allxlss:
    print(i)
    li.append(pd.read_excel(i))
writer = pd.ExcelWriter('D:/WORK_DATA/三期/推广使用/反诈中心数据结果/陈前0319.xlsx',
                        engine='xlsxwriter',options={'strings_to_urls': False})
pd.concat(li).to_excel(writer, 'Sheet1', index=False)

writer.save()
