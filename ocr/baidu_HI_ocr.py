# -*- coding: utf-8 -*-
# @Author: bgods.cn
# @Create Date: 2020-07-22 17:08
# @File Name: api.py
# @Description: 图片转文字API

import base64
import requests
import time
import os
import csv

HI_URL='http://10.1.126.186:9001/HI_CV/OCR'
HI_URL2 = 'http://10.1.126.186:8970/HI_CV/OCR'
API_KEY = 'L5CD7euIrOw65I4uiGPEcq6w' # 自行获取
SECRET_KEY = 'p3TN283yBGBsezWHdKMahRRfgumequpj'  # 自行获取
OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"  # OCR接口
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'  # TOKEN获取接口

def fetch_token():
    # 获取token
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    try:
        f = requests.post(TOKEN_URL, params, timeout=5)
        if f.status_code == 200:
            result = f.json()
            if 'access_token' in result.keys() and 'scope' in result.keys():
                if not 'brain_all_scope' in result['scope'].split(' '):
                    return None, 'please ensure has check the  ability'
                return result['access_token'], ''
            else:
                return None, '请输入正确的 API_KEY 和 SECRET_KEY'
        else:
            return None, '请求token失败: code {}'.format(f.status_code)
    except BaseException as err:
        return None, '请求token失败: {}'.format(err)

def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')  # 二进制读取图片信息
        return f.read(), ''
    except BaseException as e:
        return None, '文件({0})读取失败: {1}'.format(image_path, e)
    finally:
        if f:
            f.close()

def pic2text(img_path):
    def request_orc(img_base, token):
        """
        调用百度OCR接口，图片识别文字
        :param img_base: 图片的base64转码后的字符
        :param token: fetch_token返回的token
        :return: 返回一个识别后的文本字典
        """
        try:
            req = requests.post(
                OCR_URL + "?access_token=" + token,
                data={'image': img_base},
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            if req.status_code == 200:
                result = req.json()
                if 'words_result' in result.keys():
                    return req.json()["words_result"], ''
                elif 'error_msg' in result.keys():
                    return None, '图片识别失败: {}'.format(req.json()["error_msg"])
            else:
                return None, '图片识别失败: code {}'.format(req.status_code)
        except BaseException as err:
            return None, '图片识别失败: {}'.format(err)

    file_content, file_error = read_file(img_path)
    OCR_result = []
    if file_content:
        token, token_err = fetch_token()
        if token:
            results, result_err = request_orc(base64.b64encode(file_content), token)
            if result_err: # 打印失败信息
                print(result_err)
                return result_err
            for result in results: # 打印处理结果
                OCR_result.append(result['words'])
            res = ','.join(OCR_result)
            print(res)
            return res

# 对比HI的ocr效果
def HI_ocr(img_path):
    img_bytes = open(img_path, 'rb').read()
    img_64 = base64.b64encode(img_bytes)
    respose = requests.post(HI_URL2, data={'imageBase64':img_64})
    if respose:
        result = respose.json()
        res = ' '.join(eval(result['results']))
        print(res)
        return res
    else:
        print(respose.status_code)
        return respose.status_code

if __name__ == '__main__':
    # save_file = 'D:/work_data/四期/百度调用OCR/result_1214.csv'
    # filePath = 'D:/work_data/四期/百度调用OCR/图片/'
    # paths = os.listdir(filePath)
    # with open(save_file, 'w', encoding='utf-8',newline='') as save_f:
    #     writer = csv.writer(save_f)
    #     # 先写入columns_name
    #     writer.writerow(["url", "baidu_ocr", "HI", "baidu_time","HI_time"])
    #     for i in paths:
    #         a = time.time()
    #         img_path = f'{filePath}{i}'
    #         baidu_res = pic2text(img_path)
    #         b1 = time.time() - a
    #         # hi_res = HI_ocr(img_path)
    #         b2 = time.time() - a
    #         line = [i, baidu_res, b1]
    #         # 写入多行用writerows
    #         writer.writerow(line)
    img_path = 'D:/work_data/四期/百度调用OCR/图片/3ede144dae9b3866f6d564ec0638b29.jpg.jpg'
    baidu_res = pic2text(img_path)
    print(baidu_res)







