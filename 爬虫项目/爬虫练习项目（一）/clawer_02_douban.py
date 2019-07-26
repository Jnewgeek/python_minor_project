# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 09:50:55 2019

@author: Administrator

豆瓣特定分类图书分页数据1000条
"""
import time
import random
import pandas as pd
import re
import os
os.chdir(".")
from settings import get_html

import warnings
warnings.filterwarnings('ignore')

def get_urls(n=10):
    beginurls=["https://book.douban.com/tag/%E7%94%B5%E5%BD%B1?start={}&type=T".format(i*20) for i in range(n)]
    return beginurls

def get_data(content):
    # 采集信息
    #subject_list > ul > li:nth-child(1)
    lis=content.find("ul",class_="subject-list").find_all("li")
    lst=[]
    for i in lis:
        dic={}
        # 书名
        try:
            dic["标题"]=i.h2.text.replace("\n","").replace(" ","")
        except:
            pass
        # 详细信息
        try:
            dic["其他信息"]=i.find("div",class_="pub").text.replace("\n","").replace(" ","")
        except:
            pass
        # 评分和评论人数
        try:
            dic["评价"]=i.find("div",class_="star clearfix").find("span",class_="rating_nums").text.replace("\n","").replace(" ","")
        except:
            pass
        try:
            review=i.find("div",class_="star clearfix").find("span",class_="pl").text.replace("\n","").replace(" ","")
        except:
            pass
        try:
            dic["评论人数"]=0 if review=="(目前无人评价)" else re.compile("\d+").findall(review)[0]
        except:
            pass
        try:
            dic["简介"]=i.p.text.replace("\n","").replace(" ","")
        except:
            pass
        lst.append(dic)
    return lst

if __name__=="__main__":
    # 构建地址
    beginurls=get_urls(n=50)

    # 采集分页网页信息
    infos=[]
    errorurl=[]           # 存放异常网页
    for ui in beginurls:
        time1=time.time()
        try:
            content=get_html(ui)
            infos.extend(get_data(content))
            time2=time.time()
            print(">> 数据采集成功，总共获取%i条数据,用时%.2fs"%(len(infos),time2-time1))
        except:
            print(">> 数据采集失败, 数据网址为:",ui)
            #print("网页内容:\n",content)
            errorurl.append(ui)
            time.sleep(random.random()*10)
        time.sleep(random.random())
        
    # 整理数据
    data=pd.DataFrame(infos)
    data["价格"]=data["其他信息"].str.split("/").str[-1].str.strip()
    
    data.to_excel("案例2_豆瓣数据%d条.xlsx"%len(data),index=False)