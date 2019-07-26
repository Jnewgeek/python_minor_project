# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:12:30 2019

@author: Administrator

去哪网特定城市景点数据下载,添加pymongo模块
"""

''' pymongo 常用语句
# 连接数据库
myclient=pymongo.MongoClient("mongodb://localhost:27017/")
# 查询数据库名
myclient.list_database_names()
# 选择数据库
db1=myclient["table02"]
# 查询表名
db1.list_collection_names()
# 选择数据表
data1=db1["table05"]
# 插入数据
data1.insert_one(dic)
data1.insert_many(diclst)
# 查询数据
data1.find_one()   # 可设置条件 {key:value}
data1.find()
# Json 转 DataFrame
datadf=pd.DataFrame(list(data1.find()))
# DataFrame 转 Json
lst=datadf.to_dict(orient="records") 
# 删除数据
data1.delete_one({key:value})
data1.delete_many({key:value})
# 删除表
data1.drop()
'''

import time
import random
import pandas as pd
import pymongo
import os
os.chdir(".")
from settings import get_html

import warnings
warnings.filterwarnings('ignore')

# 获取城市代码
def get_citycode():
    if os.path.exists("./去哪儿网城市编码.xlsx"):
        citycode=pd.read_excel("./去哪儿网城市编码.xlsx")
    else:
        # 获取网页数据
        url="https://travel.qunar.com/place/"
        content=get_html(url,d_c=cookies)
        # 解析
        citycode=pd.DataFrame(get_citydata(content))
        # 保存文件
        citycode.to_excel("./去哪儿网城市编码.xlsx",index=False)
        print(">> 已将城市代码保存至本地.")
    return citycode

# 解析城市列表        
def get_citydata(content):
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
def get_urls(citycode,cityname="上海",n=20):
    # 从代码表中匹配城市名
    try:
        url=citycode[citycode["城市"]==cityname]["链接"].values[0]
    except:
        print("无[%s]的链接地址,请重新确认!"%cityname)
        return None
    beginurls=["{}-jingdian-1-{}".format(url,i) if i!=1 else "{}-jingdian".format(url) for i in range(1,n+1)]
    return beginurls

# 获取景点数据
def get_data(content,cityname=None,table=None):
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
        if cityname is not None:dic["城市"]=cityname
        try:
            table.insert_one(dic)
            n+=1
        except:
            pass
    return n


if __name__=="__main__":
    cityname="东莞"
    cookies="QN1=ezu0qF02oOtLLIGnE+84Ag==; QN205=organic; QN277=organic; _i=VInJOW3UnofqCZzxZx5MgIrJ_LJq; QN269=3D52BA51AD0E11E9B3C2FA163E72396C; Hm_lvt_c56a2b5278263aa647778d304009eafc=1563861232; fid=5d9fa9b8-8e57-4997-8bde-b56d832bbe8e; QN25=891ada9c-95c6-4e0e-9610-985e70868ba2-9f992f90; QN42=blyh4457; _q=U.pljqewu7871; _t=26173796; csrfToken=0kDhwxTekjtQp7cgwHUcODFphnnricSO; _s=s_YBKAEJ3QQXNZVIAO6EVPLXZHYQ; _v=AE723kHu7Q-xLQuOqnsHYRQIOX1Hsi2ROUduJTZkfwDbLMeRs-WN75Smkc_ExAXGZOXxHxGj7oUCuIuhswFtnPh-REznJt2Aw0HuKmSSk_IyRaiAYb9sCcnZlaRsA9frKIl3z0-oMPW5FiFhn8FpcTzY8-_3_NLfkM5QcQD4GfSo; QN44=pljqewu7871; QN48=tc_47403cdd02d5b2e6_16c1d66b463_48d5; QN99=1870; QN300=organic; QunarGlobal=10.86.213.150_47afbcc5_16c1d64a5f9_-41a7|1563861389127; QN601=828f3bfeea4088d0e6f16dafc7dd5202; QN163=0; QN667=B; quinn=529dec6368206af22e224d559f84eff115602568b4b4f17168530d3d23856ba418f7699858027462d408925c769fe5c1; activityClose=1; QN100=WyLkuIrmtbd8Il0%3D; QN243=12; QN57=15638615782980.36575468791369037; QN58=1563861578295%7C1563861578295%7C1; QN5=qunar_djmp_gnmdd_%E4%B8%8A%E6%B5%B7; viewdist=299878-8|299914-1|300195-3; uld=1-300195-3-1563862578|1-299914-1-1563862215|1-299878-8-1563862200; QN267=05269388050307847e; _vi=CAT-Ndpyg17SE1skcsEfF15jNZNIabnBugntln1LuvV-sfJK-XLGMRgN4RiehpxJaQdWd0RvVmVQUeFxm-xuFquqfg5QhMR3qxJh56P1Xn38ig3xG-5RawJm8tnsw-oQwptbAGQn7B3ASjzwIvMMf4_pstJ0Nj5Cq4yxSnHMyiBm; Hm_lpvt_c56a2b5278263aa647778d304009eafc=1563862582; QN271=e159d5b6-a2bb-479c-828b-d1e335604d08"
    # 获取城市列表
    citycode=get_citycode()
    # 构造需要爬取的数据链接：默认为上海市20页数据
    beginurls=get_urls(citycode,cityname=cityname,n=50)
    
    # 增加mongo数据库
    myclient=pymongo.MongoClient("mongodb://localhost:27017/")
    db=myclient["去哪儿网"]
    dbtable=db["jingdian"]
    
    # 采集分页网页信息
    count=0
    errorurl=[]           # 存放异常网页
    for page,ui in enumerate(beginurls):
        time1=time.time()
        try:
            content=get_html(ui,d_c=cookies)
            count+=get_data(content,cityname,dbtable)
            time2=time.time()
            print(">> 数据采集成功，总共获取%i条数据,用时%.2fs"%(count,time2-time1))
        except:
            print(">> 数据采集失败, 数据网址为:",ui)
            #print("网页内容:\n",content)
            errorurl.append(ui)
            time.sleep(random.random()*10)
        time.sleep(random.random())