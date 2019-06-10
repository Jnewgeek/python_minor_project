# coding: utf-8

'''
【项目05】  多场景下的算法构建

数据：
某公司A,B产品在2018年1,2,3月的销量数据，数据格式为xlsx

作业要求：
1、批量读取数据，并输出以下信息
（1）数据量
（2）数据字段columns
（3）输出每个文件分别有多少缺失值

2、批量读取数据，用均值填充缺失值数据，并完成以下计算及图表制作
（1）读取数据并用均值填充缺失值；对“日期”字段进行时间序列处理，转换成日period ，最后输出三个Dataframe文件data1,data2,data3
（2）分别计算data1，data2，data3中A,B产品的月总销量，并绘制多系列柱状图，存储在对应的图片文件夹路径
（3）分别计算A产品在每个月中哪一天超过了月度80%的销量，输出日期

3、读取数据并合并，做散点图观察A,B产品销量，并做回归，预测当A销量为1200时，B产品销量值
（1）读取数据删除缺失值；对“日期”字段进行时间序列处理，转换成日period ，合并三个月数据，输出data；
（2）针对A产品销量和B产品销量数据做回归分析，制作散点图并存储，并预测当A销量为1200时，B产品销量值
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#from sklearn.linear_model import LinearRegression
import os
#get_ipython().magic('matplotlib inline')

import os
import pprint
address=os.getcwd()

# 自动创建图片文件夹
if not os.path.exists(address+"\\img"):
    os.mkdir(address+"\\img")

file=dict((i,address+"\\"+i) for i in os.listdir(address) if ".xlsx" in i)
print("可用数据表文件地址:")
pprint.pprint(file)

#### 任务1.读取数据
# 读取文件函数    
def read_data(file,datafile,i,clean=False,drop=False):
    '''
    读取xlsx文件，并输出以下内容：
    （1）数据量
    （2）数据字段columns
    （3）输出每个文件分别有多少缺失值
    
    参数
    -------
    ：param : file，文件路径字典
    : param : datafile, 文件名
    : param : i,循环读取时的计数器
    ：param : clean, 是否清洗缺失值，默认不清洗（因为任务1要求输出缺失记录）
    : param : drop,是否删除缺失值
    '''
    data=pd.read_excel(file[datafile],encoding="utf-8",index_col=0)
    # 是否删除缺失值
    if drop: 
        data.dropna(inplace=True)
    # 是否清洗
    if clean and drop==False:
        data=clean_data(data,data.columns)       # 清洗数据
    # 输出内容
    data_lens=data.shape[0]         # 数据量
    data_columns=data.columns       # 字段
    data_null=data[data.isnull().values == True].shape[0]   # 缺失值数量
    print('''(%d) 数据表：%s
    数据量:     %d
    字段名：    %s
    缺失值数量: %d'''%(i,datafile,data_lens,",".join(data_columns.tolist()),data_null))
    return data

# 清洗数据
def clean_data(data,*col):
    '''
    1、批量处理data中的缺失值
    2、对“日期”字段进行时间序列处理，转换成日period ，
    '''
    # 处理日期字段
    data.index=pd.period_range(data.index[0],data.index[-1],freq="D")    # to_period 方法不存在
    # 处理缺失值
    for i in col:
        data[i]=data[i].fillna(data[i].mean())
    return data


# In[52]:

# 循环读取3张数据表
for i,filename in enumerate(sorted(file.keys())):
    exec("{0}=read_data(file,filename,{1})".format(filename.split(".")[0],i+1))
print("\n>>> 任务1批量读取输出信息过程完成。")


# In[53]:

##### 任务2.销售情况
for i,filename in enumerate(sorted(file.keys())):
    exec("{0}=read_data(file,filename,{1},clean=True)".format(filename.split(".")[0],i+1))
print("\n>>> 任务2清洗过程完成。")


# In[56]:

# 多系列柱状图
sale={}
for i in sorted(file.keys()):
    key=i.split(".")[0].replace("data","")
    if key[0]=="0":   # 去除多余的零
        key=key[1]
    exec("sale[key+'月']=%s.sum()"%(i.split('.')[0]))#{"1月":data01.sum(),"2月":data2.sum(),"3月":data3.sum()}).T)
sale=pd.DataFrame(sale).T
print(sale)
print("-"*20)
sale.plot(kind="bar",rot=0,title="A,B产品的月总销量")
plt.savefig(address+"\\img\\A,B产品的月总销量.png",dpi=100)


# 分别计算A产品在哪一天完成了月度80%的销售目标
for i in range(len(file)):
    exec('{0}["A产品月度销售达成率"]=({0}["productA"]/{0}["productA"].sum()).cumsum();    targetdate=str({0}[{0}["A产品月度销售达成率"]>=0.8]["A产品月度销售达成率"].index[0])'.format("data%d"%(i+1)))
    print("({0}) {0}月 A产品在 {1} 完成月度总销量的80%.".format(i+1,targetdate))


## 任务3.回归分析
# 删除缺失值，合并数据表
def connect_data(file,columns):
    '''
    合并数据表
    '''
    data0=pd.DataFrame(columns=columns)    # 创建初始空表，用来连接
    for i,filename in enumerate(sorted(file.keys())):
        data=read_data(file,filename,i+1,drop=True)
        data0=pd.concat([data0,data],axis=0)
    print("多表连接完成,记录数为: %d"%data0.shape[0])
    return data0

# 回归分析
from sklearn.linear_model import LinearRegression

# 回归分析绘图函数
def Linear_anlysis(data,x_col,y_col,img_name):
    '''
    回归分析主函数
    
    参数
    ------
    :param: data，数据表
    :param：x_col, 自变量
    :param: y_col，因变量
    :param: img_name,图片名字
    '''
    rng = np.random.RandomState(1) 
    xtrain = np.array(data[x_col])
    ytrain = np.array(data[y_col])

    fig = plt.figure(figsize =(12,3))
    ax1 = fig.add_subplot(1,2,1)
    plt.scatter(xtrain,ytrain,marker = '.',color = 'k')
    plt.grid()
    plt.title('AB产品散点图')

    model = LinearRegression()
    model.fit(xtrain[:,np.newaxis],ytrain)
    # LinearRegression → 线性回归评估器，用于拟合数据得到拟合直线
    # model.fit(x,y) → 拟合直线，参数分别为x与y
    # x[:,np.newaxis] → 将数组变成(n,1)形状

    xtest = np.linspace(int(data[x_col].min()),int(data[x_col].max()),1000)
    ytest = model.predict(xtest[:,np.newaxis])
    # 创建测试数据xtest，并根据拟合曲线求出ytest
    # model.predict → 预测

    ax2 = fig.add_subplot(1,2,2)
    plt.scatter(xtrain,ytrain,marker = '.',color = 'k')
    plt.plot(xtest,ytest,color = 'r')
    plt.grid()
    plt.title('线性回归拟合')
    plt.savefig(address+"\\img\\%s.png"%img_name,dpi=100)

    # 预测值
    print("当%s为%d时，%s预计为%d"%(x_col,1200,y_col,model.predict(1200)[0]))


# 读取数据
data=connect_data(file,columns=["productA","productB"])


# 回归分析
Linear_anlysis(data,"productA","productB","AB 回归分析")

