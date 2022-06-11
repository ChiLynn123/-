
from html.parser import HTMLParser
import urllib.request
import os
#点击链接测试网址
url="https://github.com/wrf-model/WRF/compare/v4.0.1...master"


import sys
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Lack of parameters")
        exit(-1)
EXCEL_RESULT_DIR=sys.argv[1]
os.mkdir(EXCEL_RESULT_DIR)

#函数名解析函数
def rudefunname(name):
    print("函数名解析前："+name)
    name_f=name.split('(')[0]
    return name_f.split(' ')[-1]
#解析github网页的下所有commit支线的类
class getallCommit(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.div=False
        self.a_href_content_column=[]
    def handle_starttag(self, tag, attrs):
        if tag == 'div' and len(attrs) == 1:
            for (variable, value) in attrs:
                if variable == "class" and value=="commit-message pr-1":
                    self.div=True
        elif tag=="a" and self.div==True:
            for (variable,value) in attrs:
                if variable=="href":
                    self.a_href_content_column.append("https://github.com"+value)#添加链接
                    self.div=False
#解析github网页的下所有缺陷描述和标题
class defectParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.div=False
        self.defect_des=""
        self.pre=False
        self.p=False
        self.title=""
    def handle_starttag(self, tag, attrs):
        if tag == 'div' and len(attrs) == 1:
            for (variable, value) in attrs:
                if variable == "class" and value=="commit-desc":
                    self.div=True
        elif tag=="pre" and self.div==True:
            self.pre=True
        elif tag=="p":
            for (variable, value) in attrs:
                if variable == "class" and value=="commit-title":
                    self.p=True
    def handle_data(self, data):
        if self.pre==True:
            self.defect_des+=str(data)
        if self.p==True:
            self.title=data
    def handle_endtag(self, tag):
        if tag=='pre':
            self.div=False
            self.pre=False
        if tag=='p':
            self.p=False
    #problem
    def get_title_and_desc(self):
        res=str(self.title+self.defect_des).replace("\n","")
        return res
#获取网页下所有的.c/cpp文件名以及描述
class getc_descParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        #位置自变量
        self.div=False#一个框的开始，遇到tbody则结束
        self.on=True#是否接受第一个的开关,在tbody后设为True
        self.first=False#是否可以接受第一个,在tbody一通结束
        self.content=False#接受内容开关
        #内容自变量
        self.fun_name=""#获取第一行的函数名
        self.file_name=""#文件名
        self.code_content=""#存放函数code
        self.res=[]
        self.is_receive_function_content=False#是否接受函数内容开关，与函数名判断挂钩，若函数名提取为@@直接pass
    def handle_starttag(self, tag, attrs):
        if tag == 'div':#只有检测为c/cpp文件才可以开始
            temp_bool=False
            for (variable, value) in attrs:
                if variable=="class" and value=="file-header file-header--expandable js-file-header ":
                    temp_bool=True
            for (variable, value) in attrs:
                if variable=="data-path" and temp_bool==True:
                    length=value.split('/')[-1]
                    if len(length.split('.'))==2:
                        temp_str=length.split('.')[1]
                        if temp_str=="cpp" or temp_str=="c" or temp_str=="C" or temp_str=="CPP":
                            self.div=True#当检成功时候就设为开始
                            self.file_name=length.split('.')[0]#设置文件名
        elif tag=='td' and self.div==True:
            for (variable,value) in attrs:
                if variable=="class" and value=="blob-code blob-code-inner blob-code-hunk" and self.first==False and self.on==True:
                    self.first=True#开始接受函数名
                elif variable=="class" and value=="blob-code blob-code-context" and self.is_receive_function_content==True:
                    self.content=True#开始接受内容
                elif variable == "class" and value == "blob-code blob-code-inner blob-code-hunk" and self.first == True and self.is_receive_function_content==True:
                    self.content=True#开始接受内容
    def handle_data(self, data):
        if self.content==True:
            #print(data)
            self.code_content+=data
        elif self.first==True and self.on==True:
            temp_name=rudefunname(data)#接受函数名
            if temp_name=='@@':
                self.fun_name=""
                self.is_receive_function_content=False
                self.first=False
            else:
                self.fun_name=temp_name
                self.is_receive_function_content=True
            self.on=False
    def handle_endtag(self, tag):
        if tag=='table':#还原并添加内容
            self.div=False
            self.on=True
            self.first=False
            self.content=False
            self.is_receive_function_content = False
            temp=[]
            if len(self.file_name)!=0 and len(self.fun_name)!=0:
                temp.append(self.file_name+'_'+self.fun_name)
                #替换转义字符
                self.code_content=self.code_content.replace("\\n","")
                self.code_content = self.code_content.replace("\\t", "")
                temp.append(self.code_content)
                self.res.append(temp)
            self.fun_name=""
            self.file_name=""
            self.code_content=""
        elif tag=='td':
            self.content=False
#通过url获取网页内容的函数
def getHtml(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    return str(html)
#获取所有commit链接的函数 一个列表
def getcommitcontent(url):
    MyParser=getallCommit()
    MyParser.feed(getHtml(url))
    commit_a=MyParser.a_href_content_column
    MyParser.close()
    return commit_a
#获取一个链接下的dec
def get_defect_desc(url):
    tempParser=defectParser()
    tempParser.feed(getHtml(url))
    desc=tempParser.get_title_and_desc()
    tempParser.close()
    return desc
#获取一个链接下的.c/cpp文件的名字和代码
def get_detail(url):
    tempParser=getc_descParser()
    tempParser.feed(getHtml(url))
    desc=tempParser.res
    tempParser.close()
    return desc
#整体架构
def gen_result(url):
    hrefs=getcommitcontent(url)#获取所有的href然后一个个进去
    result=[]
    count=1#进度计数器
    sum=len(hrefs)
    for href in hrefs:
        print("进度："+str(count)+"/"+str(sum))
        count+=1
        #先通过列表是否为空，判断是否有.c/cpp文件
        details=get_detail(href)#二维列表
        if len(details)!=0:#列表为空则直接pass
            defect_describle=get_defect_desc(href)
            defect_describle=defect_describle.replace("\\n",'')
            for (index,value) in enumerate(details):
                for (index2,value2) in enumerate(value):
                    details[index][index2]=value2.replace("\n",'')
            temp_res=[]
            temp_res.append(defect_describle)
            temp_res.append(details)
            result.append(temp_res)
    return result
import xlwt
import xlrd
FAILURE_DATA=gen_result(url)


failureColumnName=["软件名称","编程语言","版本","缺陷类型","缺陷所在的模块","缺陷严重等级","缺陷来源阶段","发现阶段","缺陷描述","缺陷修改描述","选取标准"]

temp_name='result.xls'
temp_failure_name="Failure.xls"


EXCEL_FAILURE_NAME=os.path.join(EXCEL_RESULT_DIR,temp_failure_name)
failure_column_length=len(failureColumnName)
failure_workbook = xlwt.Workbook()
failure_sheet = failure_workbook.add_sheet(u'sheet1', cell_overwrite_ok=True)

for num in range(failure_column_length):

        failure_sheet.write(0, num, failureColumnName[num])



rowNum=0
for i in range(len(FAILURE_DATA)):
    for j in range(len(FAILURE_DATA[i][1])):
        rowNum+=1
        for k in range(len(FAILURE_DATA[i][1][j])):
            failure_sheet.write(rowNum, 8, FAILURE_DATA[i][0])
            failure_sheet.write(rowNum, 10,"IEEE Std 1044-1993" )
            if k==0:
                failure_sheet.write(rowNum, 4, FAILURE_DATA[i][1][j][k])
            if k==1:
                failure_sheet.write(rowNum, 9, FAILURE_DATA[i][1][j][k])
failure_workbook.save(EXCEL_FAILURE_NAME)