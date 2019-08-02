# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:36:17 2019

@author: Allen

豆瓣关键词搜索结果与信息收集
"""
import time
import pandas as pd
import pymongo
from urllib import parse
from selenium import webdriver
import re
import sys
sys.path.append(r"../")
from settings import Clawer   # 继承基础类

import warnings
warnings.filterwarnings('ignore')

class DoubanSearch(Clawer):
    
    # 设置初始参数
    def __init__(self,keyword,cate,n,single=True,N=20,rootfile=r"../"):
        '''
        keyword: 搜索关键词
        cate: 分类
        n: 搜索结果页数
        single: 是否启用多线程,默认不启用
        N: 最大线程个数,由于Python自带GIL锁,因此不是N越大速度就越快,保持这里的默认设置即可,因为提供测试的阿布云代理效果一般，将N降低为5
        正常情况下可设置为20
        '''
        Clawer.__init__(self)       # 继承重写父类
        # 其他参数
        category={"电影":"movie","书籍":"book"}
        self.keyword=keyword
        self.cate=cate
        # mongodb 数据库配置
        myclient=pymongo.MongoClient("mongodb://localhost:27017/")
        db=myclient["豆瓣"]
        self.dbtable=db[category[cate]]  # 创建数据表
        self.cookies = 'bid=-Vb0mooHgwU; ll="108296"; _vwo_uuid_v2=D97DB4EC3A6DE4D04879B636254944105|03c959f87008dd845074a7dc37ce072f; douban-fav-remind=1; gr_user_id=3ecc0d09-a431-4b8c-9b2f-3a11c9c8534f; __yadk_uid=Pb1dulESnqmihil5iES7HQu618r13jBg; __gads=ID=c086f25de6162974:T=1547364458:S=ALNI_MaBRbdZtgiTQGzZGFTCRn3e11onbQ; _ga=GA1.2.1605809557.1531756417; __utmv=30149280.14670; viewed="25815707_33416858_1152126_1035848_27667378_33419041_30482656_5257905_2064814_25862578"; push_noty_num=0; push_doumail_num=0; __utma=30149280.1605809557.1531756417.1561789945.1561820352.110; __utmc=30149280; __utmz=30149280.1561820352.110.81.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1561820367%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.3ac3=*; __utma=81379588.2028513491.1535457105.1561789945.1561820367.43; __utmc=81379588; __utmz=81379588.1561820367.43.21.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=fb752381-b64e-43f8-9fe8-bfee8f24bf99; gr_cs1_fb752381-b64e-43f8-9fe8-bfee8f24bf99=user_id%3A0; ap_v=0,6.0; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_fb752381-b64e-43f8-9fe8-bfee8f24bf99=true; Hm_lvt_6e5dcf7c287704f738c7febc2283cf0c=1561820374; Hm_lpvt_6e5dcf7c287704f738c7febc2283cf0c=1561820374; _pk_id.100001.3ac3=dabd77c1e491d680.1535457105.43.1561821031.1561790041.; __utmt_douban=1; __utmb=30149280.8.10.1561820352; __utmt=1; __utmb=81379588.7.10.1561820367'
        # 关键词搜索结果链接
        self.start_url=parse.quote("https://{0}.douban.com/subject_search?search_text={1}".format(category[cate],keyword)).replace("%3F","?").replace("%3A",":").replace("%3D","=").replace("%26","&")
        # 搜索结果页数
        self.n=n
        self.single=single
        self.N=N
        # 计数器
        self.count=0
        self.errorurl=[]
        self.rootfile=rootfile

    # 获取N个搜索结果
    def get_urls(self):
        brower=webdriver.Chrome()
        
        # 数据链接
        url_lst=[]
        time1=time.time()
        for i in range(self.n):
            try:
                start_url=self.start_url if i==0 else self.start_url+"&start={}".format(i*15)
                brower.get(start_url)
                # 获取链接 sc-bZQynM bFpOIp sc-bxivhb hRIaFd //*[@id="root"]/div/div[2]/div[1]/div[1]/div[1]
                # //*[@id="root"]/div/div[2]/div[1]/div[1]/div[1]/div[1]/div/div[1]/a
                results=brower.find_elements_by_xpath(r'//*[@id="root"]/div/div[2]/div[1]/div[1]/div')
                urls=[i.find_element_by_tag_name("a").get_attribute("href") for i in results]
                url_lst.extend(list(set([i if "https:" in i else i.replace("//","https://") for i in urls if i is not None and "/subject/" in i])))
                time2=time.time()
                print("链接获取成功,总共收集%i条链接,用时%.2fs."%(len(url_lst),time2-time1))
            except:
                print("链接获取失败,数据网址为:",start_url)
        # 关闭浏览器
        brower.quit()
        return url_lst
    
    # 收集搜索结果里的详细信息
    def get_data(self,content):
        dic={}
        # 标题
        dic["名称"]=content.find("h1").text.strip("\n ")
        dic["关键词"]=self.keyword
        dic["分类"]=self.cate
        # info
        infos=re.sub(r' *','',re.sub(r':\n+\s*',":",content.find("div",id="info").text.strip("\n "))).split("\n")
        # 评分
        try:
            dic["评分"]=float(content.find("strong",class_="ll rating_num").text.strip("\n "))
            # 评论人数
            dic["评论人数"]=int(content.find("a",class_="rating_people").text.strip("\n ").replace("人评价",""))
        except:
            pass
        for i in infos:
            try:
                dic[i.split(":")[0].strip("\n ")]=i.split(":")[1].strip("\n ").replace("\xa0","")
            except:
                continue
        # 保存到数据库中
        self.dbtable.insert_one(dic)
        return 1
             
    # 调用主函数
    def main(self):
        # 构造搜索页面链接
        urls_lst=self.get_urls()
        # 开启多线程采集任务
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
                #time.sleep(1)
                
        print("数据爬取完成,导出数据库文件...")
        data=pd.DataFrame(list(self.dbtable.find({"关键词":self.keyword})))
        data.to_csv(self.rootfile+r"/data/【豆瓣-{}】 {}数据{}条.csv".format(self.keyword,self.cate,self.count),index=False,encoding="utf-8")
    
if __name__=="__main__":
    # 定义采集任务： 搜索科幻书籍10页数据,并采集其详细信息
    clawer=DoubanSearch(keyword="修仙",cate="书籍",n=10,single=False)
    #clawer.dbtable.remove({"关键词":clawer.keyword})
    clawer.main()