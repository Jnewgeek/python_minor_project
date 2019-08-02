# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:12:30 2019

@author: Administrator

去哪网特定城市景点数据下载,添加pymongo模块
"""
import time
import pandas as pd
import pymongo
import os
import sys
sys.path.append('../')           # 导入父级模块
from settings import Clawer   # 继承基础类

import warnings
warnings.filterwarnings('ignore')

class Qunar(Clawer):
    
    def __init__(self,cityname,n,single=True,N=20,rootfile=r'../'):
        Clawer.__init__(self)       # 继承重写父类
        self.cityname=cityname
        self.n=n
        self.single=single
        self.N=N
        self.cookies="QN1=ezu0qF02oOtLLIGnE+84Ag==; QN205=organic; QN277=organic; _i=VInJOW3UnofqCZzxZx5MgIrJ_LJq; QN269=3D52BA51AD0E11E9B3C2FA163E72396C; Hm_lvt_c56a2b5278263aa647778d304009eafc=1563861232; fid=5d9fa9b8-8e57-4997-8bde-b56d832bbe8e; QN25=891ada9c-95c6-4e0e-9610-985e70868ba2-9f992f90; QN42=blyh4457; _q=U.pljqewu7871; _t=26173796; csrfToken=0kDhwxTekjtQp7cgwHUcODFphnnricSO; _s=s_YBKAEJ3QQXNZVIAO6EVPLXZHYQ; _v=AE723kHu7Q-xLQuOqnsHYRQIOX1Hsi2ROUduJTZkfwDbLMeRs-WN75Smkc_ExAXGZOXxHxGj7oUCuIuhswFtnPh-REznJt2Aw0HuKmSSk_IyRaiAYb9sCcnZlaRsA9frKIl3z0-oMPW5FiFhn8FpcTzY8-_3_NLfkM5QcQD4GfSo; QN44=pljqewu7871; QN48=tc_47403cdd02d5b2e6_16c1d66b463_48d5; QN99=1870; QN300=organic; QunarGlobal=10.86.213.150_47afbcc5_16c1d64a5f9_-41a7|1563861389127; QN601=828f3bfeea4088d0e6f16dafc7dd5202; QN163=0; QN667=B; quinn=529dec6368206af22e224d559f84eff115602568b4b4f17168530d3d23856ba418f7699858027462d408925c769fe5c1; activityClose=1; QN100=WyLkuIrmtbd8Il0%3D; QN243=12; QN57=15638615782980.36575468791369037; QN58=1563861578295%7C1563861578295%7C1; QN5=qunar_djmp_gnmdd_%E4%B8%8A%E6%B5%B7; viewdist=299878-8|299914-1|300195-3; uld=1-300195-3-1563862578|1-299914-1-1563862215|1-299878-8-1563862200; QN267=05269388050307847e; _vi=CAT-Ndpyg17SE1skcsEfF15jNZNIabnBugntln1LuvV-sfJK-XLGMRgN4RiehpxJaQdWd0RvVmVQUeFxm-xuFquqfg5QhMR3qxJh56P1Xn38ig3xG-5RawJm8tnsw-oQwptbAGQn7B3ASjzwIvMMf4_pstJ0Nj5Cq4yxSnHMyiBm; Hm_lpvt_c56a2b5278263aa647778d304009eafc=1563862582; QN271=e159d5b6-a2bb-479c-828b-d1e335604d08"
        # 增加mongo数据库
        myclient=pymongo.MongoClient("mongodb://localhost:27017/")
        db=myclient["去哪儿网"]
        self.dbtable=db["jingdian"]
        self.count=0
        self.errorurl=[]           # 存放异常网页
        self.rootfile=rootfile
        
    # 获取城市代码
    def get_citycode(self):
        if os.path.exists("./去哪儿网城市编码.xlsx"):
            citycode=pd.read_excel("./去哪儿网城市编码.xlsx")
        else:
            # 获取网页数据
            url="https://travel.qunar.com/place/"
            content=self.get_html(url,d_c=self.cookies)
            # 解析
            citycode=pd.DataFrame(self.get_citydata(content))
            # 保存文件
            citycode.to_excel("./去哪儿网城市编码.xlsx",index=False)
            print(">> 已将城市代码保存至本地.")
        return citycode
    
    # 解析城市列表        
    def get_citydata(self,content):
        lst=[]
        city=content.find("div",class_="contbox current").find_all("dl")   # 默认选国内
        for i in city:
            # 地区
            region=i.dt.text.strip("\n ")   # 直辖市等
            for j in i.find_all("div",class_="sub_list"):
                # 省份
                try:
                    province=j.find("span",class_="tit").text.strip("\n :：").replace("&nbsp;","").replace("\xa0","").replace(" ","")
                except:
                    province=None    
                # 精确到城市
                for k in j.find_all("li"):
                    citycode={}
                    c_=k.a.text.strip("\n ")
                    href=k.find("a")["href"]
                    citycode["区域"]=region
                    citycode["省份"]=province if province is not None else c_
                    citycode["城市"]=c_
                    citycode["链接"]=href
                    lst.append(citycode)
        return lst
    
    # 数据链接
    def get_urls(self,citycode):
        # 从代码表中匹配城市名
        try:
            url=citycode[citycode["城市"]==self.cityname]["链接"].values[0]
        except:
            print("无[%s]的链接地址,请重新确认!"%self.cityname)
            return None
        beginurls=["{}-jingdian-1-{}".format(url,i) if i!=1 else "{}-jingdian".format(url) for i in range(1,self.n+1)]
        return beginurls
    
    # 获取景点数据
    def get_data(self,content):
        # 景点名称、评分、排名、简介、攻略提到数量、点评数量、多少比例驴友来过、经纬度
        # name
        n=0
        for i in content.find("ul",class_="list_item clrfix").find_all("li"):
            dic={}
            try:
                dic["英文名"]=i.find("span",class_="en_tit").text.replace("&nbsp;","").replace("\xa0","").replace(" ","")
            except:
                dic["英文名"]=""
            dic["景点名称"]=i.find("span",class_="cn_tit").text.replace("&nbsp;","").replace("\xa0","").replace(" ","").replace(dic["英文名"],"")
            dic["评分"]=int(i.find("span",class_="cur_star")["style"].strip("width:%").strip("\n "))
            try:
                dic["排名"]=int(i.find("span",class_="ranking_sum").span.text.strip("\n "))
            except:
                pass
            try:
                dic["简介"]=i.find("div",class_="desbox").text.replace("&nbsp;","").replace("\xa0","").replace(" ","")
            except:
                pass
            dic["攻略提到数量"]=int(i.find("div",class_="titbox clrfix").find("div",class_="strategy_sum").text.strip("\n "))
            dic["点评数量"]=int(i.find("div",class_="titbox clrfix").find("div",class_="comment_sum").text.strip("\n "))
            dic["驴友到达比例"]=float(i.find("div",class_="txtbox clrfix").find("span",class_="sum").text.strip("\n %"))/100.0
            dic["纬度"]=float(i["data-lat"])
            dic["经度"]=float(i["data-lng"])
            if self.cityname is not None:dic["城市"]=self.cityname
            try:
                self.dbtable.insert_one(dic)
                n+=1
            except:
                pass
        return n
        
    def main(self):
        # 获取城市列表
        citycode=self.get_citycode()
        # 构造需要爬取的数据链接：默认为上海市20页数据
        urls_lst=self.get_urls(citycode)
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
                
        # 导出数据
        print("数据爬取完成,导出数据库文件...")
        data=pd.DataFrame(list(self.dbtable.find({"城市":self.cityname})))
        data.to_csv(self.rootfile+r"/data/【去哪儿网-%s】景点数据%d条.csv"%(self.cityname,len(data)),index=False,encoding="utf-8")

if __name__=="__main__":
    clawer=Qunar(cityname="南京",n=50,single=False)
    #clawer.dbtable.remove({"城市":clawer.cityname})
    clawer.main()
