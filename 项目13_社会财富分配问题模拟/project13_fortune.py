# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 15:36:33 2019

@author: Administrator
项目13：财富分配模型
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import copy
sns.set(font='SimHei')
plt.rcParams['font.sans-serif'] = ['SimHei']  
# Matplotlib中设置字体-黑体，解决Matplotlib中文乱码问题
plt.rcParams['axes.unicode_minus'] = False    
# 解决Matplotlib坐标轴负号'-'显示为方块的问题
import warnings
warnings.filterwarnings("ignore")
import os
os.chdir(os.getcwd())
# 创建文件夹
for i in ["./data","./img"]:
    if not os.path.exists(i):
        os.mkdir(i)
# 创建图片文件夹
for i in ['财富分配模型_允许借贷','财富分配模型_允许借贷_负债玩家逆袭',
          '财富分配模型_初始模型_不排序绘制', '财富分配模型_初始模型_排序绘制',
          '财富分配模型_努力人生']:
    if not os.path.exists("./img/"+i):
        os.mkdir("./img/"+i)
########################################################################################
############################### 任务1 财富分配模型 ########################################
########################################################################################
print("             《项目13：社会财富分配问题模拟》\n")
print(">>>>>>>>>>>>>>     任务1 财富分配模型         <<<<<<<<<<<<<<\n")
# 初始化数据
class WealthDistribution:
    '''财富分配模型.'''
    def __init__(self,n=100,money=100,times=17000,hard_id=None,goods=0.01,loan=False,data=None):
        '''初始化财富数据.
        :param n:     人数,默认为100个
        :param money: 金额,默认为100元
        :param times: 游戏次数,默认为17000次
        :param hard_id: 努力的人员名单,默认为空
        :param goods: 竞争优势,默认为1%
        :param loan:  允许借贷,默认不允许
        :param data:  本地已经计算好的数据，默认为空
        '''
        # 创建初始数据
        self.n=n
        self.money=money
        self.times=times
        self.loan=loan
        # 设置初始概率
        p=1/n
        if isinstance(hard_id,list):
            hard_id=[int(i) for i in hard_id]
            # 为不努力的人设置概率
            if len(hard_id)==n:      # 如果全部很努力，则同一起跑线
                p_hard=p_normal=p
            else:
                p_hard=p*(1+goods)
                p_normal=(1-p_hard*len(hard_id))/(n-len(hard_id))
            self.pnt=[p_hard if i in hard_id else p_normal for i in range(1,n+1)]
        else:
            self.pnt=[p]*n
        if isinstance(data,pd.DataFrame):
            self.wealth=data
        else:
            self.wealth=pd.DataFrame(np.array([money]*n).reshape(n,1),index=list(range(1,n+1)))
    
    # 每轮游戏每个人应该给谁
    def give_receive(self):
        '''每一轮游戏中,每个人都需要给其他人一块钱,如果此时已经金额已经为0,则不需要给其他人.
        :return: 可以获的1块钱的人索引
        '''
        # 首先判断有只能拿出多少块钱
        if self.loan:
            N=self.n
            self.givewho=np.random.choice(range(1,self.n+1),size=N,p=self.pnt)  # 保证财富不会多出来
        else:
            N=sum(test.wealth.iloc[:,-1]!=0)
            self.givewho=np.random.choice(range(1,self.n+1),size=N)  # 保证财富不会多出来
    
    # 更新新一轮的财富值     
    def update_wealth(self,time):
        '''根据新一轮的收入支出人员索引,更新每个人的财富值.
        :param time: 游戏轮次
        '''
        self.wealth[time]=self.wealth.iloc[:,-1]   # 新的一轮数据初始化记为上一次的数据
        # for循环效率较低，修改为series操作提高计算速度
#        for i in self.wealth.index:
#            # 如果已经为0了，不再给出
#            if int(self.wealth.iat[i-1,-2])==0:
#                continue
#            else:
#                self.wealth.iat[i-1,-1]-=1               # 失去1块
#                self.wealth.iat[self.givewho[i-1],-1]+=1 # 获得1块
        # 首先判断是否给出1块钱
        # 允许借贷
        if self.loan:
            self.wealth[time]=self.wealth[time]-1
        else:
            self.wealth[time]=self.wealth[time].apply(lambda x:x-1 if x>0 else x)
        # 再将 self.who 转变为series
        add_money=pd.Series(self.givewho).value_counts().reindex(range(1,self.n+1)).fillna(0)
        self.wealth[time]=self.wealth[time]+add_money
        
    # 绘制柱状图            
    def plot_bar(self,time,bankrupt_id=None,ymin=0,ymax=None,yrange=None,imgname="graph1_round_",imgfile="./img/财富分配模型_初始模型_不排序绘制",sort=False):
        '''绘图.'''
        df=copy.deepcopy(self.wealth[[time]])
        if isinstance(bankrupt_id,list):
            # 设置颜色
            bankrupt_id=[int(i) for i in bankrupt_id]
            df["color"]=pd.Series(pd.Series(df.index,index=df.index).apply(lambda x:"red" if int(x) in bankrupt_id else "blue"),index=df.index)
        else:
            df["color"]="blue"
        if sort: # 排序
            df=df.sort_values(by=time)
        else:
            pass
        df.index=range(1,self.n+1)
        fig=plt.figure(figsize=(8,4))
        ax=fig.add_subplot(111)
        df[time].plot(kind="bar",color=df["color"],alpha=0.8,width=0.5,legend=False,ax=ax)
        # 设置纵坐标
        if yrange==None:
            yrange=int(self.money/2)
        if ymax==None:
            ymax=4*self.money+1
        plt.yticks([i for i in range(ymin,ymax,yrange)])
        #ax.set_yticklabels([i for i in range(0,4*self.money+1,int(self.money/2))])
        # 设置横坐标
        plt.xlim([-10,110])
        plt.xticks([i for i in range(0,101,20)],rotation=0)
        ax.set_xticklabels([i for i in range(0,101,20)])
        plt.title("Round %d"%time)   # 标题
        plt.savefig(imgfile+"//%s%d.png"%(imgname,time),dpi=100)
        
# 初始化类
filename="./data/wealth_no_loan.csv"
if os.path.exists(filename):
    wealth_no_loan=pd.read_csv(filename,engine="python",encoding="utf-8")
    print(">> 本地数据%s读取完成,共%d行"%(filename.replace("./data/","").strip(".csv"),wealth_no_loan.shape[0]))
    test=WealthDistribution(data=wealth_no_loan.T)   # 直接传入本地数据
else:
    time1=time.time()
    test=WealthDistribution()
    # 模拟17000次游戏
    for i in range(1,test.times+1):   # 进行17000游戏
        test.give_receive()    # 本轮每个人应该给谁1块钱
        test.update_wealth(i)  # 更新第i轮游戏的财富值
        if i<100 and i%10==0 or 100<=i<1000 and i%100==0 or i>=1000 and i%400==0 or i==test.times:
            # 财富情况
            # 最富有的
            max_money=test.wealth[i].max()
            min_money=test.wealth[i].min()
            # 前20%的人占据了百分之多少的财富？
            sort_wealth=sorted(test.wealth[i],reverse=True)
            percent=sum(sort_wealth[:int(test.n*0.2)])/sum(sort_wealth)
            # 多少人的财富缩水值100以下(即初始金额)
            low=sum(test.wealth[i]<test.money)
            print(">> 第%d轮模拟 -> 财富最多: %d,财富最少: %d,前20%%的人拥有: %.2f%%的财富(总值:%d),有%.2f%%的人资产缩水至%d以下."%(i,max_money,min_money,percent*100,sum(sort_wealth),100*low/test.n,test.money))
    # 最后的数据，需要转置
    wealth_no_loan=test.wealth.T
    time2=time.time()
    print(">> 模拟结束,总耗时: %.2fs.\n"%(time2-time1))
    # 保存数据
    wealth_no_loan.to_csv(filename,index=False,encoding="utf-8")
    
################################ 可视化 ########################################
# 不排序
# 绘制初始状态
print(">> 输出游戏结果：\n")
test.plot_bar(0)
test.plot_bar(0,imgname="graph2_round_",imgfile="./img/财富分配模型_初始模型_排序绘制",sort=True)
# 绘制后续轮次
for i in range(1,test.times+1):   # 进行17000游戏
    if i<100 and i%10==0 or 100<=i<1000 and i%100==0 or i>=1000 and i%400==0 or i==test.times:
        print(">> 第%d轮结果."%i)
        test.plot_bar(i)       # 绘制第 i 轮 游戏结果
        test.plot_bar(i,imgname="graph2_round_",imgfile="./img/财富分配模型_初始模型_排序绘制",sort=True)
    else:
        continue
print(">> 柱状图导出完成.")

########################################################################################
############################### 任务2 允许借贷模型 ########################################
########################################################################################
print("\n>>>>>>>>>>>>>>     任务2 允许借贷模型         <<<<<<<<<<<<<<\n")
filename="./data/wealth_with_loan.csv"
if os.path.exists(filename):
    wealth_with_loan=pd.read_csv(filename,engine="python",encoding="utf-8")
    print(">> 本地数据%s读取完成,共%d行"%(filename.replace("./data/","").strip(".csv"),wealth_with_loan.shape[0]))
    test=WealthDistribution(loan=True,data=wealth_with_loan.T)   # 直接传入本地数据
else:
    time1=time.time()
    test=WealthDistribution(loan=True)
    # 模拟17000次游戏
    for i in range(1,test.times+1):   # 进行17000游戏
        test.give_receive()    # 本轮每个人应该给谁1块钱
        test.update_wealth(i)  # 更新第i轮游戏的财富值
        if i<100 and i%10==0 or 100<=i<1000 and i%100==0 or i>=1000 and i%400==0 or i==test.times:
            # 财富情况
            # 最富有的
            max_money=test.wealth[i].max()
            min_money=test.wealth[i].min()
            # 前20%的人占据了百分之多少的财富？
            sort_wealth=sorted(test.wealth[i],reverse=True)
            percent=sum(sort_wealth[:int(test.n*0.2)])/sum(sort_wealth)
            # 多少人的财富缩水值100以下(即初始金额)
            low=sum(test.wealth[i]<test.money)
            print(">> 第%d轮模拟 -> 财富最多: %d,财富最少: %d,前20%%的人拥有: %.2f%%的财富(总值:%d),有%.2f%%的人资产缩水至%d以下."%(i,max_money,min_money,percent*100,sum(sort_wealth),100*low/test.n,test.money))
    # 最后的数据，需要转置
    wealth_with_loan=test.wealth.T
    time2=time.time()
    print(">> 模拟结束,总耗时: %.2fs.\n"%(time2-time1))
    # 保存数据
    wealth_with_loan.to_csv(filename,index=False,encoding="utf-8")
    
################################ 可视化 ########################################
# 不排序
# 绘制初始状态
print(">> 输出游戏结果：\n")
test.plot_bar(0,ymin=-200,yrange=100,imgname="graph3_round_",imgfile="./img/财富分配模型_允许借贷",sort=True)
# 绘制后续轮次
for i in range(1,test.times+1):   # 进行17000游戏
    if i<100 and i%10==0 or 100<=i<1000 and i%100==0 or i>=1000 and i%400==0 or i==test.times:
        print(">> 第%d轮结果."%i)
        test.plot_bar(i,ymin=-200,yrange=100,imgname="graph3_round_",imgfile="./img/财富分配模型_允许借贷",sort=True)
    else:
        continue
print(">> 柱状图导出完成.")

# 绘制标准差折线图
print(">> 模拟游戏财富标准差折线图：\n")
std=wealth_with_loan.std(axis=1)
std.plot(kind="line",figsize=(8,4),title="财富模拟标准差变化情况",color="red",alpha=0.8)
plt.savefig("./img/财富模拟标准差变化情况.png",dpi=100)

# 负债玩家逆袭
# 6200轮游戏结束时的破产的玩家Id是：
bankrupt_id=list(wealth_with_loan.columns[wealth_with_loan.loc[6200]<0])
print(">> 第6200轮模拟结束时,总计有%d名玩家破产."%len(bankrupt_id))
# 设置柱状图的颜色
for i in range(6200,test.times+1):   # 进行17000游戏
    if i==6200 or i%500==0 or i==test.times:
        print(">> 第%d轮结果."%i)
        test.plot_bar(i,bankrupt_id,ymin=-200,yrange=100,imgname="graph4_round_",imgfile="./img/财富分配模型_允许借贷_负债玩家逆袭",sort=True)
    else:
        continue
print(">> 柱状图导出完成.")
bankrupt_id2=list(wealth_with_loan.columns[wealth_with_loan.loc[17000]<0])
print(">> 最后一轮模拟结束时,共计有%d名玩家完成了逆袭."%len(set(bankrupt_id).difference(set(bankrupt_id2))))

########################################################################################
############################### 任务3 努力的人生会更好吗 ###################################
########################################################################################
# 设置努力的人员id
hard_id=[1,11,21,31,41,51,61,71,81,91]
print("\n>>>>>>>>>>>>     任务3 努力的人生会更好吗    <<<<<<<<<<<<<<<<\n")
filename="./data/wealth_workhard.csv"
if os.path.exists(filename):
    wealth_workhard=pd.read_csv(filename,engine="python",encoding="utf-8")
    print(">> 本地数据%s读取完成,共%d行"%(filename.replace("./data/","").strip(".csv"),wealth_workhard.shape[0]))
    test=WealthDistribution(loan=True,data=wealth_workhard.T)   # 直接传入本地数据
else:
    time1=time.time()
    test=WealthDistribution(hard_id=hard_id,loan=True)   # 加入努力的人员名单
    # 模拟17000次游戏
    for i in range(1,test.times+1):   # 进行17000游戏
        test.give_receive()    # 本轮每个人应该给谁1块钱
        test.update_wealth(i)  # 更新第i轮游戏的财富值
        if i<100 and i%10==0 or 100<=i<1000 and i%100==0 or i>=1000 and i%400==0 or i==test.times:
            # 财富情况
            # 最富有的
            max_money=test.wealth[i].max()
            min_money=test.wealth[i].min()
            # 前20%的人占据了百分之多少的财富？
            sort_wealth=sorted(test.wealth[i],reverse=True)
            percent=sum(sort_wealth[:int(test.n*0.2)])/sum(sort_wealth)
            # 多少人的财富缩水值100以下(即初始金额)
            low=sum(test.wealth[i]<test.money)
            print(">> 第%d轮模拟 -> 财富最多: %d,财富最少: %d,前20%%的人拥有: %.2f%%的财富(总值:%d),有%.2f%%的人资产缩水至%d以下."%(i,max_money,min_money,percent*100,sum(sort_wealth),100*low/test.n,test.money))
    # 最后的数据，需要转置
    wealth_workhard=test.wealth.T
    time2=time.time()
    print(">> 模拟结束,总耗时: %.2fs.\n"%(time2-time1))
    # 保存数据
    wealth_workhard.to_csv(filename,index=False,encoding="utf-8")
    
################################ 可视化 ########################################
# 不排序
# 绘制初始状态
print(">> 输出游戏结果：\n")
test.plot_bar(0,ymin=-200,ymax=601,yrange=100,imgname="graph5_round_",imgfile="./img/财富分配模型_努力人生",sort=True)
# 绘制后续轮次
for i in range(1,test.times+1):   # 进行17000游戏
    if i<100 and i%10==0 or 100<=i<1000 and i%100==0 or i>=1000 and i%400==0 or i==test.times:
        print(">> 第%d轮结果."%i)
        test.plot_bar(i,ymin=-200,ymax=601,yrange=100,imgname="graph5_round_",imgfile="./img/财富分配模型_努力人生",sort=True)
    else:
        continue
print(">> 柱状图导出完成.")

# 最努力的10名玩家多少进入了富人前20
fortune_rank=wealth_workhard.iloc[-1,].sort_values(ascending=False)
top_20=fortune_rank.index[:20]
hard_in_top20=set(hard_id)&set(int(i) for i in top_20)
print(">> 模拟实验结束时,更努力的%d人当中有%.1f%%进入了富人前20."%(len(hard_id),len(hard_in_top20)*100/len(hard_id)))

print(">> 全部财富分配模拟实验结束.")