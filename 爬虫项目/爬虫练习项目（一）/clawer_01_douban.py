# -*- coding: utf-8 -*-
"""
Created on Mon July 22 10:00:00 2019

@author: Allen.Jiang

豆瓣特定分类图书数据1000条
"""
import requests
import time
import random
from lxml import etree
import pandas as pd
import re
import os
os.chdir(".")

# import threading
# from time import ctime


# class MyThread(threading.Thread):

# 	def __init__(self,func,args,name='',prints=False):
# 		threading.Thread.__init__(self)
# 		self.name=name
# 		self.func=func
# 		self.args=args
# 		self.prints=prints

# 	def getResult(self):
# 		return self.res

# 	def run(self): 
# 		if self.prints:print('Starting < %s > at: %s\n'%(self.name,ctime()))
# 		self.res=self.func(*self.args)
# 		if self.prints:print('< %s > finished at: %s\n'%(self.name,ctime()))


def get_html(url,d_h,d_c):
    html=requests.get(url,headers=d_h,cookies=d_c)
    html.encoding=html.encoding
    content = etree.HTML(html.text, parser=etree.HTMLParser(encoding='utf-8'))
    #print(html.text)
    return content

# 获取网页链接
def get_url(content):
    url=content.xpath('//h2/a/@href')  # 20个
    return url

# 解析详细数据
def get_info(html):
    pattern=re.compile('<span class="pl">.*<br>')
    tt=pattern.findall(html)[0].split("<br>")[:-1]
    info={}
    # 字段名
    for i in range(len(tt)):
        try:
            label=re.compile(r'<span class="pl">(.*)</span>').findall(tt[i])[0].strip()
            # 值
            value=re.sub('<.*?>', '', tt[i], flags=re.M | re.S).replace(label,"")
            label=re.sub('<.*?>', '', label, flags=re.M | re.S)
            label=re.sub(':.*', '', label, flags=re.M | re.S)
            value = re.sub(r'(\s*\n)+', '\n', value, flags=re.M | re.S)
            info[label.strip(":")]=value.replace(" ","").replace(label,"").lstrip(":")
        except:
            pass#print(tt[i])
    # 清洗数据
    for i in ["评分","评论人数","页数"]:   # 因为货币问题，价格不能直接进行提取数字
        try:
            a=info[i]   # 有该键则进行替换,否则跳过
            info[i]=re.compile(r"[0-9.]+").findall(info[i])[0]
        except:
            continue
    return info

# 获取每一本书的数据
def get_data(content):
    title=content.xpath('//*[@id="wrapper"]/h1/span/text()')
    title=title[0].strip() if title else None
    # 获取详细信息
    infos=content.xpath('//*[@id="info"]')[0]
    result = etree.tostring(infos, encoding = "utf-8", pretty_print = True, method = "html").decode("utf-8")
    info=get_info(result.replace("\n","").replace("&nbsp;","").replace("<br/>","<br>").replace("\xa0",""))
    # 获取评分和评论人数
    star=content.xpath('//strong[@property="v:average"]/text()')
    star=star[0].strip() if star else None
    review=content.xpath('//span[@property="v:votes"]/text()')
    review=review[0].strip() if review else None
    info["标题"]=title
    info["评分"]=star
    info["评论人数"]=review
    return info

# def multithread(begin,urls,func,extend,d_h,d_c):
#      '''主函数.'''
#      threads=[]
#      for u in begin:
#          t=MyThread(func,(u,d_h,d_c))
#          threads.append(t)
     
#      for i in range(len(threads)):
#          threads[i].start()
        
#      for i in range(len(threads)):
#          threads[i].join()
#          if extend:
#          	urls.extend(threads[i].getResult())  # 添加数据网页
#          else:
#          	urls.append(threads[i].getResult())  # 添加数据采集结果

# def f1(u,d_h,d_c):
# 	return get_url(get_html(u,d_h,d_c))

# def f2(u,d_h,d_c):
# 	return get_data(get_html(u,d_h,d_c))



if __name__=="__main__":
    n=50
    d_h = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        # 获取user-agent
    cookies = 'bid=RxS3WIq8C58; __yadk_uid=2ycrqyTuNUIe2MehR6P0EWrjBg7t5Qvc; push_noty_num=0; push_doumail_num=0; __utmv=30149280.20002; ll="118297"; ct=y; _vwo_uuid_v2=D484D2738615D9BEFA97638DA02D94089|fea446a814145cfef4432570b86ca313; gr_user_id=16d5b6bf-8f35-4a36-b64b-5df4fb21af49; __utmc=30149280; douban-fav-remind=1; ap_v=0,6.0; ck=VoeZ; ps=y; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1563791610%2C%22https%3A%2F%2Faccounts.douban.com%2Fsafety%2Funlock_sms%2Fresetpassword%3Fconfirmation%3D867a54dda3d92e84%26alias%3D%22%5D; _pk_id.100001.8cb4=4ae57e6c9aaf0683.1563526901.4.1563791610.1563785818.; _pk_ses.100001.8cb4=*; __utma=30149280.427303014.1563526825.1563785810.1563791612.7; __utmz=30149280.1563791612.7.4.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/safety/unlock_sms/resetpassword; __utmt=1; __utmb=30149280.1.10.1563791612; dbcl2="200021295:gIJ1qzpuxp8"'
    d_c={}
    for i in cookies.split(";"):
        d_c[i.split("=")[0].strip("\n").strip()]=i.split("=")[1].strip().strip("\n")
    beginurls=["https://book.douban.com/tag/%E7%94%B5%E5%BD%B1?start={}&type=T".format(i*20) for i in range(n)]

    # # 多线程
    # urls=[]   # 详情页链接
    # print(">> 开始获取数据信息网页...")
    # time1=time.time()
    # multithread(beginurls,urls,f1,True,d_h,d_c)
    # time2=time.time()
    # print(">> 数据信息网页获取结束,总共获取%d条网页,用时%.2fs"%(len(urls),time2-time1))

    # # 数据采集
    # infos=[]
    # print(">> 开始采集数据...")
    # time1=time.time()
    # multithread(urls,infos,f2,False,d_h,d_c)
    # time2=time.time()
    # print(">> 数据采集完成,总共采集%d条数据,用时%.2fs"%(len(urls),time2-time1))

    
    #单线程执行
    urls=[]   # 详情页链接
    limit=0
    for u in beginurls:
        try:
            urls.extend(get_url(get_html(u,d_h,d_c)))
            #print(urls)
            print('>> 数据信息网页获取成功, 总共获取%i条网页' % len(urls))
        except: 
            print('>> 数据信息网页获取失败, 分页网址为:',u)
            time.sleep(random.random()*10)
        time.sleep(random.random())
        
    # 获取详情页信息
    infos=[]
    for url in urls:
        try:
            infos.append(get_data(get_html(url,d_h,d_c)))
            print(">> 数据采集成功，总共获取%i条网页"%len(infos))
        except:
            print(">> 数据采集失败, 数据网址为:",url)
            time.sleep(random.random()*10)
        time.sleep(random.random())

    # 保存信息
    data=pd.DataFrame(infos)
    data.to_excel("案例1_豆瓣数据%d条.xlsx"%len(data),index=False)