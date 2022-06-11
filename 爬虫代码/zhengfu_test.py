import re
import requests
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
}
url = "http://www.gov.cn/2016public/bottom.htm"
response = requests.get(url, headers=header)
response.encoding = response.apparent_encoding
response = response.text
print(response)
# </a>
# <a rel="nofollow" target="_blank"  href="(.*?)">外交部</a>
pat_music_url = r'<a rel="nofollow" target="_blank" href="(.*?)">'
pat_music_name = r'<a rel="nofollow" target="_blank" href="(.*?)">[\s\s]*?(.*?)[\s\s]*?</a>'
music_url_list = re.findall(pat_music_url, response.strip())
music_name_list = re.findall(pat_music_name, response)
# 循环遍历
if len(music_url_list) == len(music_name_list):
    for i in range(0, len(music_url_list)):
        print(music_url_list[i], '  ', music_name_list[i][1], '政府类')
        #print(music_name_list[i][1])