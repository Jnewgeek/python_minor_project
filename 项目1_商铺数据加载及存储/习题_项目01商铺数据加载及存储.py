# coding: utf-8

'''
【项目01】  商铺数据加载及存储

作业要求：
1、成功读取“商铺数据.csv”文件
2、解析数据，存成列表字典格式：[{'var1':value1,'var2':value2,'var3':values,...},...,{}]
3、数据清洗：
① comment，price两个字段清洗成数字
② 清除字段缺失的数据
③ commentlist拆分成三个字段，并且清洗成数字
4、结果存为.pkl文件

'''

# 1. 读取数据
import os
import pandas as pd
os.chdir(os.getcwd())
data=pd.read_csv("商铺数据.csv",encoding="utf-8")
data.columns=['classify', 'name', 'comment', 'star', 'price', 'address',
       'commentlist']
print(data.head())


# 简单清洗，去除多余的空格
remove_blank=lambda x:str(x).replace(" ","")   # 简单删除空格
# 清洗评论人数
remove_blank_com=lambda x:int(str(x).replace(" ","").split("条")[0]) if "条" in str(x) else None     # 提取评论人数
# 清洗星级
star={"一":1,"二":2,"三":3,"四":4,"五":5}
def get_star(x):
    '''
    提取商户的星级
    '''
    for i in x:
        if i in star.keys():
            return star[i]
        else:
            continue
    # 无星级
    return None
remove_blank_star=lambda x:get_star(str(x))
# 清洗价格
remove_blank_pri=lambda x:round(float(str(x).replace(" ","").split("￥")[1]),2) if "￥" in str(x) else None   # 提取价钱
# 清洗点评详情
remove_blank_comlist=lambda x:str(x).replace("   ","").replace("  ",",").replace(",,",",")

# 清洗 'classify', 'name', 'address'
data[['classify', 'name', 'address']]=data[['classify', 'name', 'address']].applymap(remove_blank)
data["comment"]=data["comment"].apply(remove_blank_com)
data["star"]=data["star"].apply(remove_blank_star)
data["price"]=data["price"].apply(remove_blank_pri)
data["commentlist"]=data["commentlist"].apply(remove_blank_comlist)

# 清楚缺失值
data=data.dropna()
data.index=range(data.shape[0])

# 拆分点评数据
#(pd.Series(len(i.split(",")) for i in data["commentlist"])).value_counts() 检查是否3个属性都有
#new_comm=lambda x,i:float(str(x).split(",")[i][2:])       # 以逗号分割，取第i个，再截取3位之后的数字并转换数据类型
data["口味"]=pd.Series(map(lambda x:round(float(str(x).split(",")[0][2:]),1),data["commentlist"]))   # 常数不可迭代，因此不能将 0,1,2作为参数传入lambda
data["环境"]=pd.Series(map(lambda x:round(float(str(x).split(",")[1][2:]),1),data["commentlist"]))
data["服务"]=pd.Series(map(lambda x:round(float(str(x).split(",")[2][2:]),1),data["commentlist"]))
#data=data[['classify', 'name', 'comment', 'star', 'price', 'address',"口味","环境","服务"]]
print(data.head())

# 2.解析数据
store_data=[]
for i in data.index:
    store_data.append(dict(data.iloc[i,:]))
print(store_data)

# 保存数据
import pickle
with open("商铺数据.pkl","wb") as f:
    pickle.dump(store_data,f)

# 载入数据
with open("商铺数据.pkl","rb") as f:
    st=pickle.load(f)
print(st)

