# coding: utf-8

'''
【项目04】  视频网站数据清洗整理和结论研究

作业要求：
1、数据清洗 - 去除空值
要求：创建函数
提示：fillna方法填充.缺失数据，注意inplace参数

2、数据清洗 - 时间标签转化
要求：
① 将时间字段改为时间标签
② 创建函数
提示：
需要将中文日期转化为非中文日期，例如 2016年5月24日 → 2016.5.24
'''

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#get_ipython().magic('matplotlib inline')
os.chdir(os.getcwd())


data=pd.read_csv("爱奇艺视频数据.csv",engine="python",encoding="utf-8")
data.head()


#1 去除缺失值
data.isnull().sum()
def clean(df):
    col=df.columns.tolist()
    for i in list(col):
        if df[i].dtype=="object":
            df[i].fillna("缺失数据",inplace=True)
        else:
            df[i].fillna(0,inplace=True)
    #return df
# 清洗数据
clean(data)
data.isnull().sum()


# 2.清洗时间
data.rename(columns={data.columns.tolist()[0]:"数据获取日期"},inplace=True)
def clean_time(df,*col):
    for i in col:
        df[i]=df[i].apply(lambda x:x.replace("年",".").replace("月",".").replace("日","").strip())
    return df
data=clean_time(data,"数据获取日期")


"""3、问题1 分析出不同导演电影的好评率，并筛选出TOP20
要求：
① 计算统计出不同导演的好评率，不要求创建函数
② 通过多系列柱状图，做图表可视化
提示：
① 好评率 = 好评数 / 评分人数
② 可自己设定图表风格"""
#data["好评率"]=data["好评数"]/data["评分人数"]
df=data[["导演","好评数","评分人数"]].groupby(by="导演").sum()
df["好评率"]=df["好评数"]/df["评分人数"]
df=df.sort_values(by="好评率",ascending=False)[:20]
df["好评率_n"]=df["好评率"]*100

# 绘图
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

ax=plt.subplot(111)
df["好评率_n"].plot(kind="bar",width=0.9,color="turquoise",alpha=0.7,figsize=(10,5),rot=45,ylim=[98,100.1])
# 设置平均线
plt.axhline(df["好评率_n"].mean(),linestyle="--")
# 添加标签
for i,j in enumerate(df["好评率_n"]):
    plt.text(i-0.5,j+0.02,"%.1f%%"%(j),color="k",fontsize="small")
plt.text(len(df["好评率"])-4,df["好评率_n"].mean()+0.04,"平均好评率：%.1f%%"%(df["好评率_n"].mean()))

#plt.yticks([i*100 for i in df["好评率"]])
ymajorFormatter = FormatStrFormatter('%.1f%%') # 设置y轴标签文本的格式
ax.yaxis.set_major_formatter(ymajorFormatter)  # 设置y轴标签文本格式

plt.title("不同导演电影的好评率")
plt.savefig("不同导演电影的好评率.png",dpi=400)


'''
4、问题2 统计分析2001-2016年每年评影人数总量
要求：
① 计算统计出2001-2016年每年评影人数总量，不要求创建函数
② 通过面积图，做图表可视化，分析每年人数总量变化规律
③ 验证是否有异常值（极度异常）
④ 创建函数分析出数据外限最大最小值）
⑤ 筛选查看异常值 → 是否异常值就是每年的热门电影？
提示：
① 通过箱型图验证异常值情况
② 通过quantile(q=0.5)方法，得到四分位数
③ IQR=Q3-Q1
④ 外限：最大值区间Q3+3IQR,最小值区间Q1-3IQR （IQR=Q3-Q1）
⑤ 可自己设定图表风格

'''
df2=data[[data["上映年份"][i] in range(2001,2017) for i in data.index]][["上映年份","评分人数"]].groupby(by="上映年份").sum().sort_index()
# 绘图
df2.plot(kind="area",color="green",figsize=(10,5),alpha=0.7,legend=False,grid=True)
plt.title("%d-%d年每年评影人数总量"%(df2.index.tolist()[0],df2.index.tolist()[-1]))
plt.savefig("%d-%d年每年评影人数总量.png"%(df2.index.tolist()[0],df2.index.tolist()[-1]),dpi=400)


# 箱型图
fig,axes = plt.subplots(4,4,figsize=(15,20))
for i,year in enumerate(range(2001,2017)):
    # 只取最后的评分记录
    data[data["上映年份"]==year][["上映年份","剧名","评分人数","好评数"]].groupby(by=["上映年份",
    "剧名"]).max().reset_index()[["评分人数","好评数"]].plot(kind="box",grid=True,ax=axes[i//4][i%4])
    axes[i//4][i%4].set_title(year)
    
    #设置y轴
#     cnt=int(int(max(data[data["上映年份"]==year][["评分人数","好评数"]].max().tolist()))/7)
#     cnt=int(str(cnt)[0])*10**(len(str(cnt))-1)
#     ymajorLocator = MultipleLocator(cnt) # 将y轴主刻度标签设置为cnt的倍数
#     axes[i//4][i%4].yaxis.set_major_locator(ymajorLocator)  # 设置y轴主刻度
    ymajorFormatter = FormatStrFormatter('%g') # 设置y轴标签文本的格式
    axes[i//4][i%4].yaxis.set_major_formatter(ymajorFormatter)  # 设置y轴标签文本格式
plt.savefig("2001-2016年每年评分人数&好评数箱型图.png",dpi=400)


# 根据异常值筛选出每年的热门电影
def get_hotmovie(df,year):
    '''
    根据原始的电影评分数据获取异常值，得到每年的热门电影
    '''
    df3=df[df["上映年份"]==year][["上映年份","剧名","评分人数","好评数"]].groupby(by=["上映年份","剧名"]).max().reset_index()
    # 四分之一分位数
    q1=df3[["评分人数","好评数"]].quantile(q=0.25).tolist()
    # 四分之三分位数
    q3=df3[["评分人数","好评数"]].quantile(q=0.75).tolist()
    # IQR=Q3-Q1
    iqr=[q3[i]-q1[i] for i in range(2)]
    # 外限上下界
    up_down=[(q3[i]+3*iqr[i],q1[i]-3*iqr[i]) for i in range(2)]
    #up_down
    hot_movie=df3[[df3["评分人数"][i]>=up_down[0][0] or df3["好评数"][i]>=up_down[1][0] for i in df3.index]]
    if len(hot_movie)!=0:
        return hot_movie.max()
    
# 生成每年的热门电影
hot_movie=pd.DataFrame(columns=["上映年份","剧名","评分人数","好评数"])
for i in range(2001,2017):
    hot_movie.loc[len(hot_movie)]=get_hotmovie(data,i)
print(hot_movie.head())


hot_movie.to_csv("2001-2016年每年热门电影.csv",index=False,encoding="utf-8")

