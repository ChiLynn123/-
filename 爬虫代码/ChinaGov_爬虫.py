from lxml import etree
import requests
U_list=[]
def get_data():
    global U_list
    basurl = 'http://www.gov.cn/2016public/bottom.htm'
    response = requests.get(basurl)
    print(response)
    html = response.content.decode('utf-8')
    #print(html)
    data = etree.HTML(html)
    #/html/body/div/div/div[3]/div[2]/ul
    son_url=data.xpath('/html/body/div/div/div[3]/div[2]/ul//@href')
    #print("共有url：",len(son_url))
    for i in son_url:
        if i!='javascript:void();':
            U_list.append(i)
            print(i)
    print(len(U_list))
get_data()