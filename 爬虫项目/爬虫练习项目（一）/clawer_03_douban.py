# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 11:24:44 2019

@author: Administrator

豆瓣电影海报下载
"""

import time
import random
import os
os.chdir(".")
from settings import get_html,save_pic

import warnings
warnings.filterwarnings('ignore')

def get_urls(n=10):
    beginurls=["https://movie.douban.com/subject/26794435/photos?type=R&start={}&sortby=size&size=a&subtype=a".format(i*30) for i in range(n)]
    return beginurls

def get_data(title,page,content):
    poster=content.find("ul",class_="poster-col3 clearfix").find_all("li")
    lst=[]
    for i,li in enumerate(poster):
        picdic={}
        picdic["picname"]="%s%d-%d"%(title,page,i+1)
        picdic["picsrc"]=li.find("img")["src"]
        lst.append(picdic)
    return lst

if __name__=="__main__":
    beginurls=get_urls()

    # 采集分页网页信息
    infos=[]
    errorurl=[]           # 存放异常网页
    for page,ui in enumerate(beginurls):
        time1=time.time()
        try:
            content=get_html(ui)
            infos.extend(get_data("哪吒之魔童降世",page+1,content))
            time2=time.time()
            print(">> 数据采集成功，总共获取%i条数据,用时%.2fs"%(len(infos),time2-time1))
        except:
            print(">> 数据采集失败, 数据网址为:",ui)
            #print("网页内容:\n",content)
            errorurl.append(ui)
            time.sleep(random.random()*10)
        time.sleep(random.random())
        
    # 保存图片
    n=1
    for picdic in infos:
        time1=time.time()
        try:
            save_pic("哪吒之魔童降世",picdic)
            time2=time.time()
            print(">> 图片下载成功,已下载%i张图片,用时%.2fs"%(n,time2-time1))
            n+=1
        except:
            print(">> 图片下载失败, 图片名为:",picdic["picname"])
            time.sleep(random.random()*10)
        time.sleep(random.random())