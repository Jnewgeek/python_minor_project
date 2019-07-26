# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 11:31:57 2019

@author: Administrator

# 设置固定的函数,避免重复编写
"""
import requests
from bs4 import BeautifulSoup
import os
os.chdir(".")

import warnings
warnings.filterwarnings('ignore') 

# 豆瓣cookie
def set_header_cookie(d_h=None,cookies=None):
    if d_h is None:
        d_h = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    # 获取user-agent
    if cookies is None:
        cookies = 'bid=-Vb0mooHgwU; ll="108296"; _vwo_uuid_v2=D97DB4EC3A6DE4D04879B636254944105|03c959f87008dd845074a7dc37ce072f; douban-fav-remind=1; gr_user_id=3ecc0d09-a431-4b8c-9b2f-3a11c9c8534f; __yadk_uid=Pb1dulESnqmihil5iES7HQu618r13jBg; __gads=ID=c086f25de6162974:T=1547364458:S=ALNI_MaBRbdZtgiTQGzZGFTCRn3e11onbQ; _ga=GA1.2.1605809557.1531756417; __utmv=30149280.14670; viewed="25815707_33416858_1152126_1035848_27667378_33419041_30482656_5257905_2064814_25862578"; push_noty_num=0; push_doumail_num=0; __utma=30149280.1605809557.1531756417.1561789945.1561820352.110; __utmc=30149280; __utmz=30149280.1561820352.110.81.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1561820367%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.3ac3=*; __utma=81379588.2028513491.1535457105.1561789945.1561820367.43; __utmc=81379588; __utmz=81379588.1561820367.43.21.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=fb752381-b64e-43f8-9fe8-bfee8f24bf99; gr_cs1_fb752381-b64e-43f8-9fe8-bfee8f24bf99=user_id%3A0; ap_v=0,6.0; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_fb752381-b64e-43f8-9fe8-bfee8f24bf99=true; Hm_lvt_6e5dcf7c287704f738c7febc2283cf0c=1561820374; Hm_lpvt_6e5dcf7c287704f738c7febc2283cf0c=1561820374; _pk_id.100001.3ac3=dabd77c1e491d680.1535457105.43.1561821031.1561790041.; __utmt_douban=1; __utmb=30149280.8.10.1561820352; __utmt=1; __utmb=81379588.7.10.1561820367'
    d_c={}
    for i in cookies.split(";"):
        d_c[i.split("=")[0].strip("\n").strip()]=i.split("=")[1].strip("\n ")
    return d_h,d_c

def get_html(ui,d_h=None,d_c=None):
    d_h,d_c=set_header_cookie()
    try:
        html = requests.get(url = ui,headers=d_h,cookies=d_c)
        # 访问网页
        content = BeautifulSoup(html.text, 'lxml')
    except Exception as e:
        print("Error:",e)
        content=None
    return content

def save_pic(imagefile,picdic):
    '''
    【数据采集】函数
    picdic：图片存储的字典，包括图片id和图片src
    '''
    if not os.path.exists("./img/%s"%imagefile):
        os.makedirs("./img/%s"%imagefile)
    img = requests.get(url = picdic['picsrc'])
        # 访问网页
    with open(os.path.join(".","img",imagefile,picdic['picname'] + '.jpg'), 'ab') as f:
        f.write(img.content)
        f.close()    
        # 写入文件

if __name__=="__main__":
    pass

