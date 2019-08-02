# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:10:20 2019

@author: Administrator
"""
import time
import random
import pymongo
import requests
from urllib import parse
import pandas as pd
import re
import sys
sys.path.append(r"../")
from settings import Clawer   # 继承基础类

import warnings
warnings.filterwarnings('ignore')

class Bilibili(Clawer):
    
    def __init__(self,keywords="丞相",single=True,N=20,rootfile="../"):
        Clawer.__init__(self)       # 继承重写父类
        self.keywords=keywords
        self.single=single
        self.N=N
        self.cookies="_uuid=4BC56DA1-44D3-C8B0-BE31-56CB1E2AB53387580infoc; buvid3=FDD8C7C3-C7B2-4D75-9EB1-913521C37FA9155819infoc; CURRENT_FNVAL=16; sid=75f77aqu; stardustvideo=1; DedeUserID=111939890; DedeUserID__ckMd5=d7bbf0e1ebc01c82; SESSDATA=9296aaf6%2C1566729232%2C867c7971; bili_jct=fefa84340874e816ab57f9bb090c42e9; LIVE_BUVID=AUTO6815641372358045; rpdid=|(umRYl)R)l)0J'ulYRuJ~k)~"
        
        # mongo 数据库信息
        myclient=pymongo.MongoClient("mongodb://localhost:27017/")
        db=myclient["bilibili"]
        self.dbtable=db["danmu"]
        
        # 获取弹幕信息
        self.count=0
        self.errorurl=[]
        self.rootfile=rootfile
        
    def get_urls(self,content):
        '''视频地址'''
        lst=[]
        urls=content.find("ul",class_="video-contain clearfix").find_all("li")
        for i in urls:
            try:
                lst.append("https:"+i.find("a")["href"])
            except:
                print(i)
        return lst
        
    # 重写数据获取函数
    def get_data(self,content,html):
        '''获取弹幕信息.'''
        name = content.h1['title']
        date = re.search(r'(20.*\d)',content.find('div',class_ = 'video-data').text).group(1)
        cid = re.search(r'"cid":(\d*),',html.text).group(1)
        u2 = 'https://comment.bilibili.com/%s.xml' % cid
            # 采集视频基本信息及cid
        r2= requests.get(url = u2)
        r2.encoding = r2.apparent_encoding
        dmlst = re.findall('<d p=.*?</d>',r2.text)
            # 获取弹幕列表
        n = 0
        for dm in dmlst:
            dic = {}
            dic['标题'] = name
            dic['发布时间'] = date
            dic['cid'] = cid
            dic['弹幕'] = re.search(r'>(.*)</d',dm).group(1)
            dic['其他信息'] = re.search(r'<d p="(.*)"',dm).group(1)
            dic['关键词']=self.keywords
            try:
                self.dbtable.insert_one(dic)  # 数据入库
                n += 1
            except:
                pass
        return n
    
    # 重写单条解析函数
    def parse_data(self,ui,time1):  
        try:
            html,content=self.get_html(ui,d_c=self.cookies,proxies=self.proxies,response=True)
            # https://travel.qunar.com/p-cs299914-beijing-jingdian-1-38
            # content=get_html("https://travel.qunar.com/p-cs299914-beijing-jingdian-1-38",d_c=clawer.cookies,proxies=clawer.proxies)
            self.count+=self.get_data(content,html)
            time2=time.time()
            print(">> 数据采集成功，总共获取%i条数据,用时%.2fs"%(self.count,time2-time1))
        except:
            print(">> 数据采集失败, 数据网址为:",ui)
            #print("网页内容:\n",content)
            self.errorurl.append(ui)
            time.sleep(random.random()*10)
        time.sleep(random.random())
    
    def main(self):
        # 链接
        url0=parse.quote("https://search.bilibili.com/all?keyword=%s"%self.keywords).replace("%3F","?").replace("%3A",":").replace("%3D","=").replace("%26","&")
        # 获取网页内容    
        content=self.get_html(url0,d_c=self.cookies,proxies=self.proxies)
        urls_lst=self.get_urls(content)    # 获取视频地址
    
        time1=time.time()
        if self.single==True:
            for i in range(len(urls_lst)):
                self.parse_data(urls_lst[i],time1)
        else:
            # 判断线程数不能大于整体数量
            start=0
            for i in range(0,len(urls_lst),self.N):
                # 设置最多N个线程
                url_i=[urls_lst[i+start] for i in range(self.N) if i+start<len(urls_lst)]
                start+=self.N
                self.multi_main(url_i,time1)
            
        # 导出文件
        print("数据采集完成,导出数据库文件...")
        data=pd.DataFrame(list(self.dbtable.find({"关键词":self.keywords})))
        data.to_csv(self.rootfile+r"/data/【bilibili-%s】弹幕%d条.csv"%(self.keywords,len(data)),index=False,encoding="utf-8")

if __name__=="__main__":
    clawer=Bilibili(keywords="元首",single=False)
    #clawer.dbtable.remove({"关键词":clawer.keywords})
    clawer.main()
    