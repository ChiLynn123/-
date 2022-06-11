import re
import requests
# 音乐导航网址：http://www.hao123.com/music/wangzhi
# 请求头
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
}
# 请求的URL
url = "http://www.hao123.com/music/wangzhi"
# 发送请求，获取响应
response = requests.get(url, headers=header).text
print(response)
"""
<a href="http://music.taihe.com?fr=hao123" title="" target="_blank" class="text-con">
千千音乐
</a>
<a rel="nofollow" target="_blank" href="http://www.fmprc.gov.cn/web/">外交部</a>
"""
# 正则表达式：获取音乐导航链接URL
pat_music_url = r'<a href="(.*?)" title="" target="_blank" class="text-con">'
# 正则表达式：获取音乐导航名字
pat_music_name = r'<a href=".*?" title="" target="_blank" class="text-con">[\s\s]*?(.*?)[\s\s]*?</a>'
# 音乐导航URL列表
music_url_list = re.findall(pat_music_url, response.strip())
# 音乐导航名字列表
music_name_list = re.findall(pat_music_name, response)
# 循环遍历
if len(music_url_list) == len(music_name_list):
    for i in range(0, len(music_url_list)):
        print(music_name_list[i], ":", music_url_list[i])


# import urllib.request
# import urllib
# import re
# #获取网站首页全部内容
# url = "http://www.hao123.com"
# user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
# req = urllib.request.Request(url, headers={'User-Agent': user_agent})
# response = urllib.request.urlopen(req)
# content = response.read().decode('utf-8')
# #print(content)
# #初级筛选
# pattern = re.compile('<a.*?href="http://.*?".*?>.*?</a>')
# items = re.findall(pattern, content)
# for item in items:
#     pattern_one = re.compile('href=".*?"')
#     pattern_two = re.compile('.*?</a>')
#     http = re.findall(pattern_one, item)
#     name = re.findall(pattern_two, item)
#     name = name.__str__().replace('</a>', '')
#     #print(name)
#     aa = name.rindex('">')
#     print(name[aa+1:len(name)].replace('\']','').replace('</span>','').replace('>','') + ':' + http.__str__().replace('href=','').replace('"','').replace('\'','').replace('[','').replace(']',''))

