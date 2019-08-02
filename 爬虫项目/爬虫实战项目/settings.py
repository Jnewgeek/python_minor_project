# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 11:31:57 2019

@author: Administrator

# 设置固定的函数,避免重复编写
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import os
os.chdir(".")
import sys
sys.path.append(r'./')
from myThread import MyThread     # 导入多线程

import warnings
warnings.filterwarnings('ignore')


class Clawer:
    
    def __init__(self):
        self.proxies=self.Abuyun_proxy()
        self.d_h,self.cookies=self.set_header_cookie()

    # 设置headers和cookie
    def set_header_cookie(self,d_h=None,cookies=None):
        if d_h is None:
            d_h = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        # 获取user-agent
        if cookies is not None:   # 不需要加cookies的网页爬取任务则不设置
            #cookies = 'bid=-Vb0mooHgwU; ll="108296"; _vwo_uuid_v2=D97DB4EC3A6DE4D04879B636254944105|03c959f87008dd845074a7dc37ce072f; douban-fav-remind=1; gr_user_id=3ecc0d09-a431-4b8c-9b2f-3a11c9c8534f; __yadk_uid=Pb1dulESnqmihil5iES7HQu618r13jBg; __gads=ID=c086f25de6162974:T=1547364458:S=ALNI_MaBRbdZtgiTQGzZGFTCRn3e11onbQ; _ga=GA1.2.1605809557.1531756417; __utmv=30149280.14670; viewed="25815707_33416858_1152126_1035848_27667378_33419041_30482656_5257905_2064814_25862578"; push_noty_num=0; push_doumail_num=0; __utma=30149280.1605809557.1531756417.1561789945.1561820352.110; __utmc=30149280; __utmz=30149280.1561820352.110.81.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1561820367%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.3ac3=*; __utma=81379588.2028513491.1535457105.1561789945.1561820367.43; __utmc=81379588; __utmz=81379588.1561820367.43.21.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=fb752381-b64e-43f8-9fe8-bfee8f24bf99; gr_cs1_fb752381-b64e-43f8-9fe8-bfee8f24bf99=user_id%3A0; ap_v=0,6.0; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_fb752381-b64e-43f8-9fe8-bfee8f24bf99=true; Hm_lvt_6e5dcf7c287704f738c7febc2283cf0c=1561820374; Hm_lpvt_6e5dcf7c287704f738c7febc2283cf0c=1561820374; _pk_id.100001.3ac3=dabd77c1e491d680.1535457105.43.1561821031.1561790041.; __utmt_douban=1; __utmb=30149280.8.10.1561820352; __utmt=1; __utmb=81379588.7.10.1561820367'
    	    d_c={}
    	    for i in cookies.split(";"):
    	        d_c[i.split("=")[0].strip("\n").strip()]=i.split("=")[1].strip("\n ")
        else:
            d_c=None
        return d_h,d_c
    
    # 获取网页内容
    def get_html(self,ui,d_h=None,d_c=None,proxies=None,response=False):
        d_h,d_c=self.set_header_cookie()
        try:
            try:
                html = requests.get(url = ui,headers=d_h,cookies=d_c)
            except:
                html = requests.get(url = ui,headers=d_h,cookies=d_c,proxies=proxies)
            # 访问网页
            content = BeautifulSoup(html.text, 'lxml')
        except Exception as e:
            print("Error:",e)
            content=None
        #print(response)
        if response:                # 是否返回HTML结果,默认不返回
            return html,content
        else:
            return content
        #return content
    
    # 保存图片
    def save_pic(self,imagefile,picdic):
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
            
    # 阿布云代理    
    def Abuyun_proxy(self):
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"
        proxyUser = "H524WR4337TA0M0D"         # 测试代理，会失效，需要使用请自行申请
        proxyPass = "11A93926CA1E01E1"
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }
        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        return proxies
    
    # 获取数据，需子类进行重写
    def get_data(self,content):
        pass
    
    # 解析页面
    def parse_data(self,ui,time1):  
        try:
            content=self.get_html(ui,d_c=self.cookies,proxies=self.proxies)
            # https://travel.qunar.com/p-cs299914-beijing-jingdian-1-38
            # content=get_html("https://travel.qunar.com/p-cs299914-beijing-jingdian-1-38",d_c=clawer.cookies,proxies=clawer.proxies)
            self.count+=self.get_data(content)
            time2=time.time()
            print(">> 数据采集成功，总共获取%i条数据,用时%.2fs"%(self.count,time2-time1))
        except:
            print(">> 数据采集失败, 数据网址为:",ui)
            #print("网页内容:\n",content)
            self.errorurl.append(ui)
            time.sleep(random.random()*10)
        time.sleep(random.random())
        
    # 多线程主函数
    def multi_main(self,url_i,time1):
         '''主函数.
         page_i: 评论所在页数
         p: 搜索结果所在页数
         j: 搜索结果的出现的次序
         content: 评论内容页
         '''
         threads=[]
         for i in range(len(url_i)):
             t=MyThread(self.parse_data,(url_i[i],time1))
             threads.append(t)
         
         for i in range(len(threads)):
             threads[i].start()
            
         for i in range(len(threads)):
             threads[i].join()

if __name__=="__main__":
    pass

