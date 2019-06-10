
# coding: utf-8

# In[ ]:

'''
【项目06】  多场景下的图表可视化表达
'''


# In[125]:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#get_ipython().magic('matplotlib inline')
import os
os.chdir(os.getcwd())

import warnings
warnings.filterwarnings('ignore') 

sns.set_style("white")
sns.set_context("notebook")

plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体设置-黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
sns.set(font='SimHei')  # 解决Seaborn中文显示问题


# 1. 运动员身高密度曲线
data1=pd.read_excel("奥运运动员数据.xlsx",sheet_name="运动员信息")
print(data1.head())
print("-"*30)
print(data1.isnull().sum())


# 绘制密度图
h_male=data1[data1["gender"]=="男"]["height"]
h_female=data1[data1["gender"]=="女"]["height"]

fig=plt.figure(figsize=(8,5))

sns.kdeplot(h_male, label="male_height",
            linestyle = '--',linewidth = 2,color='orange')    # 男性
sns.kdeplot(h_female, label="female_height",
            linestyle = '--',linewidth = 2,color='g')    # 女性
# 数据频率分布图
sns.rugplot(h_male,height = 0.1,color = 'orange')
sns.rugplot(h_female,height = 0.05,color = 'g')

# 绘制辅助线 
male_height_mean=h_male.mean()                           # 男性平均身高
female_height_mean=h_female.mean()                       # 女性平均身高
plt.axvline(x=male_height_mean,linestyle="--",linewidth = 1.2,color="orange",alpha=0.5)
plt.axvline(x=female_height_mean,linestyle="--",linewidth = 1.2,color="g",alpha=0.5)

# 添加注释
plt.text(male_height_mean,0.005,"male_height_mean: %.1fcm"%male_height_mean,color="orange")
plt.text(female_height_mean,0.01,"female_height_mean: %.1fcm"%female_height_mean,color="g")

# 标题
plt.title("Athlete's height")
plt.grid(linestyle="--")
plt.savefig("Athlete's height.png",dpi=200)


# 运动员指标评分
cols_need=["name","age","height","weight","arm","leg"]      # 姓名，年龄，身高，体重，臂长，腿长
data2=data1[cols_need].dropna().drop_duplicates()                             # 去除缺失值
print(data2.shape)
print(data2.isnull().sum())

# 计算四个指标
"""
a. BMI 指数（BMI =体重kg ÷ 身高m**2，详细信息可百度查询）→ 越接近22分数越高
   b. 腿长/身高 指数 → 数据筛选，只选取小于0.7的数据，越大分数越高
   c. 臂展/身高 指数 → 数据筛选，只选取大于0.7的数据，比值越接近1分数越高
   d. 年龄 指数 → 年龄越小分数越高
   对上述abcd指标分别标准化得到n1,n2,n3,n4（划分到0-1的分值）
   最后评分： finalscore = (n1 + n2 + n3 + n4)/4
"""
data2["BMI_c"]=data2["weight"]/(data2["height"]/100)**2         # BMI
data2["leg_c"]=data2["leg"]/data2["height"]                     # 腿长/身高
data2["arm_c"]=data2["arm"]/data2["height"]                     # 臂展/身高
data2=data2[[data2["leg_c"][i]<0.7 and data2["arm_c"][i]>0.7 for i in data2.index]]      # 筛选数据
# 标准化
x=np.array(data2[["BMI_c","leg_c","arm_c","age"]])              # 转换为矩阵方便计算
for i in ["BMI_nor","leg_nor","arm_nor","age_nor"]:
    data2[i]=None        # 新创建列
data2[["BMI_nor","leg_nor","arm_nor","age_nor"]]=(x-x.min(0))/x.ptp(0)   # ptp 为极差
data2["finalscore"]=np.array(data2[["BMI_nor","leg_nor","arm_nor","age_nor"]]).mean(1)
data2=data2.sort_values(by="finalscore",ascending=False).reset_index(drop=True)
print(data2.head())


# 堆叠图
# sns.color_palette("hls")
fig=plt.figure(figsize=(8,5))
ax=fig.add_subplot(111)

data2[["age_nor","BMI_nor","leg_nor","arm_nor"]].plot.area(stacked=True ,colormap ="Oranges",alpha=0.8,ax=ax)
plt.grid(linestyle="--")

sns.despine()
ax.spines['bottom'].set_position(('data', 0))     # 解决坐标轴偏移问题
ax.spines['left'].set_position(('data', 0))

plt.title("Athlete's Score Distribution Plot")
plt.savefig("Athlete's Score Distribution Plot.png",dpi=200)

# 绘制雷达图
athlete_info=data2[["name","BMI_nor","leg_nor","arm_nor","age_nor","finalscore"]][:8]
print(athlete_info)

# 雷达图
fig=plt.figure(figsize=(16,4))
# fig.subplots_adjust(wspace=0.1,hspace=0.4) #设置子图间的间距，为子图宽度的40%
for i in range(8):
    ax=fig.add_subplot(2,4,i+1,projection='polar') #设置第一个坐标轴为极坐标体系
    
    info=np.array(athlete_info[["leg_nor","arm_nor","age_nor","BMI_nor"]].iloc[i,:]) #提取运动员的信息
    label=np.array(["腿长/身高","臂展/身高","年龄","BMI"])                        #提取标签
    
    angle = np.linspace(0, 2*np.pi, len(info), endpoint=False) #info里有几个数据，就把整圆360°分成几份
    angles = np.concatenate((angle, [angle[0]])) #增加第一个angle到所有angle里，以实现闭合
    info = np.concatenate((info, [info[0]])) #增加第一个人的第一个info到第一个人所有的data里，以实现闭合
    
    ax.set_theta_direction(1)
    ax.set_thetagrids(angles*180/np.pi, label) #设置网格标签
    ax.plot(angles,info,"o-")
#     ax.set_theta_zero_location('NW') #设置极坐标0°位置
    ax.set_theta_offset(np.pi/8*4)
    ax.set_rlim(0,1) #设置显示的极径范围
    ax.set_rmax(1.2)
#     ax.set_rticks(np.arange(0, 1.0,0.2),)
    ax.set_yticks(ticks=np.arange(0, 1.0,0.2))
    ax.set_yticklabels("")                     # 隐藏实际数值
    ax.fill(angles,info,facecolor='purple', alpha=0.6*(8-i)/8+0.1) #填充颜色
    ax.set_rlabel_position('255') #设置极径标签位置
    ax.set_title("Top%d %s: %.3f"%(i+1,athlete_info["name"][i],athlete_info["finalscore"][i]),fontproperties="SimHei",fontsize=16) #设置标题
plt.tight_layout()
plt.savefig("运动员指标雷达图.png",dpi=200)


# 3 CP 关系指标计算
"""
奥运运动员数据.xlsx，sheet → 运动员CP热度
① 三个指标评判运动员CP综合热度，并加权平均
   a. cp微博数量 → 数量越多分数越高
   b. cp微博话题阅读量 → 阅读量越多分数越高
   c. B站cp视频播放量 → 播放量越大分数越高
   对上述abcd指标分别标准化得到n1,n2,n3,n4（划分到0-1的分值）
   最后评分： finalscore = n1*0.5 + n2*0.3 + n3*0.2
"""
data3=pd.read_excel("奥运运动员数据.xlsx",sheet_name="运动员CP热度")
print(data3.head())
print("-"*30)
print(data3.isnull().sum())
# 缺失值处理 
data3.fillna(0,inplace=True)
data3[["cp微博数量","cp微博话题阅读量","B站cp视频播放量"]]=data3[["cp微博数量","cp微博话题阅读量","B站cp视频播放量"]].replace("无数据",0)        
print("-"*30,)
print("缺失值处理完毕。")
print(data3.isnull().sum())

# 计算指标,标准化
for i in ["cp_weibo_1","cp_weibo_2","cp_B"]:
    data3[i]=None
x1=np.array(data3[["cp微博数量","cp微博话题阅读量","B站cp视频播放量"]])   # 转化为ndarray
data3[["cp_weibo_1","cp_weibo_2","cp_B"]]=(x1-x1.min(0))/x1.ptp(0)        # 0-1 区间       因为数据中包含一些无数据，这里未做删除而是记作0处理
# finalscore = n1*0.5 + n2*0.3 + n3*0.2
data3["finalscore"]=0.5*data3["cp_weibo_1"]+0.3*data3["cp_weibo_2"]+0.2*data3["cp_B"]
print(data3.head())
# 导出数据作为gephi的原始数据
writer = pd.ExcelWriter('athlete cp.xlsx')
data3.to_excel(writer,index=False)
writer.save()




