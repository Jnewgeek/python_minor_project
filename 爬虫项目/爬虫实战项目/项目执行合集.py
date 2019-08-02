# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 16:50:35 2019

@author: Administrator
"""

import time
import os
rootfile=os.getcwd()   # 设置根目录
#os.chdir(".")
import sys
project={1:"bilibili弹幕",2:"豆瓣网",3:"拉勾网",4:"去哪儿网"}
sys.path.extend([rootfile+r'/%s'%i for i in project.values()])    # 添加模块路径，加载对应的脚本
from qunar_withmongo import Qunar      # 去哪儿网
from douban_search import DoubanSearch # 豆瓣网
from bilibili_danmu import Bilibili    # bilibili弹幕网
from lagou import Lagou                # 拉勾网

# bilibili 弹幕数据
def get_bilibili():
    keyword=input(">> 【BiliBili】 请输入视频关键词: ")
    judge=input("是否确定？y/n: ")
    while True:
        if judge=="y":
            break
        else:
            keyword=input(">> 【BiliBili】 请输入视频关键词: ")
            judge=input("是否确定？y/n: ")
    print("Sucessfully! 开始采集【bilibili %s】弹幕数据..."%keyword)
    clawer=Bilibili(keywords=keyword,single=False,rootfile=rootfile)
    #clawer.dbtable.remove({"关键词":clawer.keywords})
    clawer.main()
    
# 豆瓣网 数据 
def get_douban():
    keyword=input(">> 【豆瓣】 请输入搜索关键词: ")
    judge=input("是否确定？y/n: ")
    while True:
        if judge=="y":
            break
        else:
            keyword=input(">> 【豆瓣】 请输入搜索关键词: ")
            judge=input("是否确定？y/n: ")
    cate=input(">> 【豆瓣】 请选择分类(可选项:书籍/电影): ")
    if cate not in ["书籍","电影"]:
        print("输入分类有误,按照默认数据分类爬取数据.")
        cate="书籍"
    print("Sucessfully! 开始采集【豆瓣 %s-%s】 数据..."%(keyword,cate))
    clawer=DoubanSearch(keyword=keyword,cate=cate,n=10,single=False,rootfile=rootfile)
    clawer.dbtable.remove({"关键词":clawer.keyword})
    clawer.main()

# 拉勾网 数据挖掘职位信息
def get_lagou():
    keyword=input("【拉勾网】 请输入搜索关键词: ")
    judge=input("是否确定？y/n: ")
    while True:
        if judge=="y":
            break
        else:
            keyword=input(">> 【拉勾网】 请输入搜索关键词: ")
            judge=input("是否确定？y/n: ")
    city=input(">> 【拉勾网】 请输入城市: ")
    print("Sucessfully! 开始采集【拉勾网 %s-%s】 数据..."%(keyword,city))
    clawer=Lagou(username=None,password=None,city=city,keywords=keyword,n=None,rootfile=rootfile)
    #clawer.dbtable.remove({"城市":clawer.city,"关键词":clawer.keywords})
    clawer.main()
    
# 去哪儿网 景点数据
def get_qunar():
    cityname=input(">> 【去哪网】 请输入城市名(中文): ")
    judge=input("是否确定？y/n: ")
    while True:
        if judge=="y":
            break
        else:
            cityname=input(">> 【去哪网】 请输入城市名(中文): ")
            judge=input("是否确定？y/n: ")
    print("Sucessfully! 开始采集【去哪网 %s】 景点数据..."%(cityname))
    clawer=Qunar(cityname=cityname,n=50,single=False,rootfile=rootfile)
    #clawer.dbtable.remove({"城市":clawer.cityname})
    clawer.main()

if __name__=="__main__":
    print("----------------------《爬虫实战项目合集》----------------------")
    time.sleep(0.1)
    # 可执行的全部项目列表
    #project=["bilibili弹幕","豆瓣网","拉勾网","去哪儿网"]
    print("可选项目如下所示：")
    time.sleep(0.1)
    for i in project.keys():
        print("(%d) %s"%(i,project[i]))
    while True:
        num=input("请选择需要执行的项目(输入1-%d): "%len(project))
        while True:
            try:
                if int(num) in range(1,len(project)+1):
                    break
                else:
                    print("    ！！！请输入1-%d数字！！！"%len(project))
                    num=input("请选择需要执行的项目(输入1-%d): "%len(project))
            except:
                print("    ！！！请输入1-%d数字！！！"%len(project))
                num=input("请选择需要执行的项目(输入1-%d): "%len(project))
        # 开始选择执行对应的爬虫任务
        if int(num)==1:
            get_bilibili()         # bilibili 弹幕信息
        elif int(num)==2:
            get_douban()           # 豆瓣网数据
        elif int(num)==3:               
            get_lagou()            # 拉勾网数据
        elif int(num)==4:
            get_qunar()            # 去哪儿景点数据
        else:
            break
        
        # 是否退出
        q=input("是否退出?y/n: ")
        if q.lower() in ["y",'yes']:
            break
        else:
            print("\n可选项目如下所示：")
            time.sleep(0.1)
            for i in project.keys():
                print("(%d) %s"%(i,project[i]))
        