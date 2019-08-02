# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 17:49:46 2019

@author: Administrator

拉勾网数据采集,与另外3个不使用同一模块,完全靠
"""

from selenium import webdriver
from urllib import parse
import pandas as pd
import pymongo
import re
import time
import random
# 不发出警告
import warnings
warnings.filterwarnings('ignore')
import datetime
    
class Lagou:
    
    def __init__(self,username=None,password=None,city="上海",keywords="数据分析",n=None,rootfile=r'../'):
        '''
        username: 用户名
        password: 密码
        keywords: 关键词
        '''
        self.username=username
        self.password=password
        self.keywords=keywords
        self.n=n
        self.lagou_zy='https://www.lagou.com/'
        self.searchurl=parse.quote("https://www.lagou.com/jobs/list_%s?px=default&city=%s#filterBox"%(keywords,city)).replace("%3F","?").replace("%3A",":").replace("%3D","=").replace("%26","&").replace("%23","#")
        self.city=city
        
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = myclient['拉勾网']
        self.dbtable = db['work']
        # 设置数据库集合   
        self.errorurl = []
        self.count = 0
        
        self.rootfile=rootfile
        
    def open_brower(self):
        self.brower = webdriver.Chrome()
        
    def close_brower(self):
        self.brower.quit()
        
    def login(self):
        '''
        【登陆】函数
        u：起始网址
        username：用户名
        password：密码
        '''
        self.brower.get(self.lagou_zy)
            # 访问网页
        self.brower.find_element_by_xpath('//*[@id="changeCityBox"]/p[1]/a').click()
            # 选择全国站（第一次弹出需要设置）
        self.brower.find_element_by_xpath('//*[@id="lg_tbar"]/div/div[2]/div/a[1]').click()
            # 点击登录
        username = self.brower.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[1]/input')
        password = self.brower.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[2]/input')
            # 找到input标签
        username.clear()
        password.clear()
        username.send_keys(self.username)
        password.send_keys(self.password)
            # 输入相关信息
        self.brower.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[2]/div[2]/div[2]').click()
        print('登陆成功，返回目前网址：',self.brower.current_url)
            # 点击“登陆”，注意超时问题
    
    # 获取当前页数据，然后点击下一页
    def get_and_click(self):
        self.brower.get(self.searchurl)
        time1=time.time()
        if self.n is None:    # 不限制页数，能采集多少采集多少
            cnt=1
            while True and cnt<=100:       # 加上限制条件防止出现异常情况导致陷入死循环
                # 采集信息
                try:
                    self.count+=self.get_data(cnt)
                    time2=time.time()
                    print('成功采集%i条数据,用时%.2fs' % (self.count,time2-time1))
                    # 点击到下一页
                    self.brower.find_element_by_xpath(r'//*[@id="s_position_list"]/div[3]/div/span[@class="pager_is_current"]/following-sibling::span[1]').click()  # 定位到当前活动页面的下一个页面
                except:
                    self.errorurl.append(self.brower.current_url)
                    print('数据采集失败，数据网址为：{},页数为: {}'.format(self.brower.current_url,cnt))
                try:  # 如果跳转到了其他页面，则结束采集任务
                    if self.brower.find_element_by_xpath(r'//*[@id="s_position_list"]/div[3]/div/span[6]').get_attribute("class")=="pager_next pager_next_disabled": #已到达最后一页
                        break
                except:
                    break
                time.sleep(random.random()*2)
                cnt+=1
        else:
            cnt=1
            while True and cnt<=self.n:
                # 采集信息
                try:
                    self.count+=self.get_data(cnt)
                    time2=time.time()
                    print('成功采集%i条数据,用时%.2fs' % (self.count,time2-time1))
                    # 点击到下一页
                    self.brower.find_element_by_xpath(r'//*[@id="s_position_list"]/div[3]/div/span[@class="pager_is_current"]/following-sibling::span[1]').click()
                except:
                    self.errorurl.append(self.brower.current_url)
                    print('数据采集失败，数据网址为：{},页数为: {}'.format(self.brower.current_url,cnt))
                try:
                    if self.brower.find_element_by_xpath(r'//*[@id="s_position_list"]/div[3]/div/span[6]').get_attribute("class")=="pager_next pager_next_disabled": #已到达最后一页
                        break
                except:
                    break
                time.sleep(random.random()*2)
                cnt+=1
    
    def get_data(self,cnt):
        '''
        【访问页面 + 采集岗位信息】函数
        ui：数据页面网址
        table：mongo集合对象
        '''  
        # 定位到第一个页面
        # 访问网页
        ul = self.brower.find_element_by_xpath('//*[@id="s_position_list"]/ul')
        lis = ul.find_elements_by_tag_name('li')
            # 获取所有li标签
        n = 0
        for li in lis:
            dic = {}
            dic['岗位名称'] = li.find_element_by_tag_name('h3').text.strip("\n ")
            dic['发布时间'] = li.find_element_by_class_name('format-time').text.strip("\n ")
            # 统一发布时间
            if "天前发布" in dic['发布时间']:
                dic['发布时间']=datetime.datetime.strftime(datetime.datetime.now()-
                   datetime.timedelta(int(dic['发布时间'].replace("天前发布",""))),"%Y-%m-%d")
            elif "发布" in dic["发布时间"]:              # 如果是小时，则是当前日期发布的
                dic["发布时间"]=datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d")+dic["发布时间"].replace("发布","")+":00"
            else:
                pass
            info1 = li.find_element_by_class_name('li_b_l').text.strip("\n ")
            info1 = re.split(r'[ /]+',info1)
            dic['薪资'] = info1[0].strip("\n ")
            dic['经验要求'] = info1[1].strip("\n ")
            dic['学历要求'] = info1[2].strip("\n ")
            dic['企业'] = li.find_element_by_class_name('company_name').text.strip("\n ")
            info2 = li.find_element_by_class_name('industry').text.split(' / ')
            dic['行业'] = info2[0].strip("\n ")
            dic['融资情况'] = info2[1].strip("\n ")
            dic['企业规模'] = info2[2].strip("\n ")
            dic["城市"]=self.city
            dic["关键词"]=self.keywords
            dic["页数"]=cnt
            dic["福利"]=li.find_element_by_class_name("list_item_bot").find_element_by_class_name("li_b_r").text.strip("\n ").replace("“","").replace("”","")
            self.dbtable.insert_one(dic)  # 数据入库
            n += 1
        return n
        
    def main(self):
        # 打开浏览器
        self.open_brower()
        # 登录
        if self.username is None:       # 如果没有用户名则不登录
            pass
        else:
            self.login()
        # 搜索职位采集数据
        self.get_and_click()
        # 关闭浏览器
        self.close_brower()
                
        # 保存数据
        data=pd.DataFrame(list(self.dbtable.find({"城市":self.city,"关键词":self.keywords})))
        data.to_csv(self.rootfile+r"/data/【拉勾网-%s-%s】 数据%d条.csv"%(self.keywords,self.city,len(data)),index=False,encoding="utf-8")

if __name__ == "__main__":  
    clawer=Lagou(username=None,password=None,city="深圳",keywords="数据分析",n=None)
    clawer.dbtable.remove({"城市":clawer.city,"关键词":clawer.keywords})
    clawer.main()