# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 20:12:00 2019

@author: HASEE
"""

import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import os
os.chdir(os.getcwd())

#####################################################################################################
#########################      1. 各个品牌都有多少商品参加了双十一活动？    ###########################
#####################################################################################################
filename="双十一淘宝美妆数据_处理1"
if os.path.exists("%s.xlsx"%filename):
    print("读取本地数据: %s."%filename)
    data=pd.read_excel("%s.xlsx"%filename,index_col=0)
else:
    data=pd.read_excel("双十一淘宝美妆数据.xlsx",index_col=0)   # 读取数据,索引就是时间序列
    # 1. 将商品按照不同的销售节奏分为7类
    # 构建商品销售节奏字典
    goods_id=data["id"].unique()     # 商品唯一序列
    goods_sale_rhythm=dict.fromkeys(goods_id,"")
    #   A. 11.11前后及当天都在售 → 一直在售
    #   B. 11.11之后停止销售 → 双十一后停止销售
    #   C. 11.11开始销售并当天不停止 → 双十一当天上架并持续在售
    #   D. 11.11开始销售且当天停止 → 仅双十一当天有售
    #   E. 11.5 - 11.10 → 双十一前停止销售
    #   F. 仅11.11当天停止销售 → 仅双十一当天停止销售
    #   G. 11.12开始销售 → 双十一后上架
    # 循环遍历goods_id，为每一个 id 添加商品销售节奏标签
    for _id in goods_id:
        data_new=data[data["id"]==_id]         # 筛选出 _id 的商品记录
        time=["-".join(str(i).split()[0].split("-")[1:]) for i in data_new.index.tolist()]  # 提取销售时间
        # 设置条件
        sale_before=True if len([i for i in time if i<"11-11"])>0 else False    # 11.11 之前在售
        sale_on=True if "11-11" in time else False                              # 11.11 当天在售
        sale_after=True if len([i for i in time if i>"11-11"])>0 else False     # 11.11 之后在售
        if sale_before and sale_on and sale_after:            # A. 11.11前后及当天都在售 → 一直在售
            kind="A"
        elif sale_before and sale_on and sale_after==False:                   # B. 11.11之后停止销售 → 双十一后停止销售
            kind="B"
        elif sale_before==False and sale_on and sale_after:   # C. 11.11开始销售并当天不停止 → 双十一当天上架并持续在售
            kind="C"
        elif sale_before==False and sale_on and sale_after==False:  # D. 11.11开始销售且当天停止 → 仅双十一当天有售
            kind="D"
        elif sale_before and sale_on==False and sale_after==False:  # E. 11.5 - 11.10 → 双十一前停止销售
            kind="E"
        elif sale_before and sale_on==False and sale_after:         # F. 仅11.11当天停止销售 → 仅双十一当天停止销售
            kind="F"
        else:                                                       # G. 11.12开始销售 → 双十一后上架
            kind="G"       # 理论上有8种情况，但实际上没有前中后都不出售的情况，所以可以直接设置 else.
        goods_sale_rhythm[_id]=kind    # 分配类型，这里先使用 kind 完全是为了减少代码字数...哈哈哈

    # 将销售节奏匹配到原始数据中
    data["销售类型"]=data["id"].apply(lambda x:goods_sale_rhythm[x])
    
    # 2. 为商品添加预售标签，用来提取之前被归入未参与 11.11 活动的商品
    data["预售"]=data["title"].str.contains("预售").replace({False:"否",True:"是"}) # 通过查找title中的"预售"字符，并对bool值进行替换
    # 为了避免将 ABCD 类型中的商品再次标记为预售商品，需要将这部分被标记为"是"的改为"否"
    data["预售"]=pd.Series(map(lambda x,y:"否" if x in list("ABCD") else y,data["销售类型"],data["预售"]),index=data.index)
    # 3. 为商品添加是否真正参与 11.11 活动的标签
    # 真正参加活动的商品 = 双十一当天在售的商品 + 预售商品  即：销售类型= A B C D 以及 带预售标签的商品都是
    data["真正参与双11"]=pd.Series(map(lambda x,y:"是" if x in list("ABCD") or y=="是" else "否",data["销售类型"],data["预售"]),
    index=data.index)
    # 导出清洗后的数据
    data.to_excel("%s.xlsx"%filename)
    
###################################################  可视化  ###################################################

################### 1. 按销售类型绘制饼图
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
sns.set(font="SimHei")

s = data[["id","销售类型"]].drop_duplicates()["销售类型"].value_counts()
# 调整index顺序，避免饼图数字显示重叠严重
s=s.reindex(list("AGFEDBC"))
#fig=plt.figure(figsize=(6,6))
plt.axis('equal')  # 保证长宽相等
plt.pie(s,
       explode = [0.1]+[0.02]*(len(s)-1),        # 设置偏移
       labels = s.index,
       #colormap = 'Set2',
       autopct='%.1f%%',
       pctdistance=0.6,
       labeldistance = 1.05,
       shadow = False,
       startangle=-90,
       radius=1.2,
       frame=False)
plt.title("7种销售类型商品占比情况")
plt.savefig("7种销售类型商品占比情况.png",dpi=200)
plt.show()

############################ 2. 计算各店铺真正参与双11的商品数量，叠加柱状图

from bokeh.plotting import figure,show,output_file
from bokeh.models import ColumnDataSource
from bokeh.core.properties import value  # 显示 legend
from bokeh.models import HoverTool      # 十字标签

output_file("双11各品牌参与度.html")

# 准备可视化数据
filename="双11各品牌参与度"
if os.path.exists("%s.xlsx"%filename):
    print("读取本地数据: %s."%filename)
    df=pd.read_excel("%s.xlsx"%filename,index_col=0)
else:
    brand_id_num=data[data["真正参与双11"]=="是"][["id","店名","销售类型","预售"]].drop_duplicates().reset_index(drop=True)
    # 因为之前做过一次去重，所以brand_id_num中销售类型为"ABCD"任意一种的预售标签均为"否" ，下面的print语句可做测试
    # print(brand_id_num[brand_id_num["销售类型"].isin(list("ABCD"))]["预售"].unique())
    # 使用 pd.pivot_table 作数据透视表
    df=brand_id_num[["店名","预售"]]
    df["num"]=1
    df=pd.pivot_table(df,columns="预售",index="店名",values="num",aggfunc='sum').rename(columns={"否":"sale_on_11","是":"presell"})
    df["total"]=df["sale_on_11"]+df["presell"]    # 计算总值，用来对数据进行排序
    df.sort_values(by="total",ascending=False,inplace=True)
    df["brand"]=df.index
    # 保存数据
    df.to_excel("%s.xlsx"%filename)

## 品牌名称
brand = df.index.tolist()
category=["sale_on_11","presell"]
colors = ["DeepSkyBlue", "HotPink"]
source = ColumnDataSource(data=df)

# 设置标签
hover = HoverTool(tooltips=[
                            ("品牌", "@brand"),
                            ("双11当天参与活动的商品数量", "@sale_on_11"),
                            ("预售商品数量", "@presell"),
                            ("参与双11活动商品总数", "@total"),
                        ])

TOOLS = [hover,"xpan,xwheel_zoom,save,reset,crosshair"]   # 横向拉伸

p = figure(x_range=brand, plot_width=800,plot_height=350, title="各个品牌参与双十一活动的商品数量分布",tools=TOOLS)
renderers = p.vbar_stack(category,          # 设置堆叠值，这里source中包含了不同年份的值，years变量用于识别不同堆叠层
                         x='brand',        # 设置x坐标
                         source=source,
                         width=0.9, color=colors,
                         legend=[value(x) for x in category], name=category)
# 绘制堆叠图

p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.location = "top_right"
p.legend.orientation = "horizontal"
# 设置其他参数
p.legend.click_policy="hide"   # 点击隐藏

show(p)

#####################################################################################################
##############################      2、哪些商品真的在打折呢？    #####################################
#####################################################################################################
# 读取商品文件
filename="双11各品牌商品打折力度"
if os.path.exists("%s.xlsx"%filename):
    print("读取本地数据: %s."%filename)
    discount_new=pd.read_excel("%s.xlsx"%filename)
else:
    data1=pd.read_excel("双十一淘宝美妆数据_处理1.xlsx",index_col=0)
    # 分组查看各商品打折情况
    # 首先将时间划分为双11前，双11中，双11后
    # 封箱
    min_=data1.index.min()    # 最小时间
    max_=data1.index.max()    # 最大时间
    before_11=pd.Timestamp("%d-%d-%d"%(min_.year,11,min_.day-1))  # 因为区间是左开右闭，所以起始日期要-1
    on_11=pd.Timestamp("%d-%d-%d"%(min_.year,11,10))  # 双11当天
    on_12=pd.Timestamp("%d-%d-%d"%(min_.year,11,11))  # 12
    bins=[before_11,on_11,on_12,max_]    # 箱子
    # 设置时间
    data1["date"]=pd.cut(data1.index,bins,labels=["双11前","双11当天","双11后"])
    # 低价分组
    temp=data1[['id','price','date']].groupby(['id','price']).min().reset_index()
    # 查看真打折与不打折商品的占比情况
    temp_new=temp["id"].value_counts()
    print("真打折商品数量为 %d,占比为 %.2f%%"%(len(temp_new[temp_new>1]),len(temp_new[temp_new>1])/len(temp_new)*100))
    # 此处计算并不完全合理，因为从后面的计算来看，双11前无销售记录或双11当天无销售记录的商品未剔除，所以此处的866是大于实际值的
    # 正确的结果应该是 789 个。
    
    ##### 计算折扣率，因为双11之前的商品可能有多个价格，因此需要按照id,date对商品价格先求平均值，再计算折扣率
    # 真正打折的id即 temp_new 中计数结果大于1的 id
    id_=list(temp_new[temp_new>1].index)
    temp1=data1[data1["id"].isin(id_)][['id','price','date']].groupby(['id','date']).mean().reset_index()
    temp1["price"].fillna(0,inplace=True)  # 填补缺失值
    # 计算折扣率
    discount=pd.DataFrame(columns=["id","discount"])
    for i in id_:  # 循环遍历真正打折的商品，计算其双11的折扣率
        price_before=float(temp1[(temp1["id"]==i)&(temp1["date"]=="双11前")]["price"])   # 双11之前的价格
        price_on_11=float(temp1[(temp1["id"]==i)&(temp1["date"]=="双11当天")]["price"])  # 双11当天的价格
        if price_before!=0 and price_on_11!=0:            # 剔除双11前无出售记录或者双11当天无销售记录的商品
            dis=price_on_11/price_before
            discount.loc[len(discount)]=[i,round(dis,2)]  # 添加进数据框
        else:
            continue
    # 经过上面的计算，可以发现有些商品在双11当天的价格反而比之前要高，并且还存在一些双11前无销售记录的商品
    # 为了绘制散点图，需要先去除折扣率大于0.95的商品
    discount_new=discount[discount["discount"]<=0.95]
    # 分箱
    import numpy as np
    bins=np.arange(-0.05,0.96,0.05)
    discount_new["discount_n"]=pd.cut(discount_new["discount"],bins)
    # 和原始表进行连接，获取每个商品对应的品牌
    id_brand=data1[["id","店名"]].drop_duplicates()    # 商品id-品牌
    discount_new=pd.merge(discount_new,id_brand,on="id")
    # 保存结果
    discount_new.to_excel("%s.xlsx"%filename,index=False)
    

#############################################  可视化  ####################################################

output_file("双11各商品折扣率统计.html")
# 1.折线图
# 十字标签
df=discount_new[["id","discount_n"]].groupby("discount_n").count().reset_index().rename(columns={"id":"count"})
 # 各个打折区间的频次统计
df["percent"]=df["count"]/df["count"].sum()
dis=df["discount_n"].tolist()
source = ColumnDataSource(data=df)

# 设置标签
hover = HoverTool(tooltips=[
                            ("折扣区间", "@discount_n"),
                            ("商品数量", "@count"),
                            ("占比", "@percent")
                        ])

TOOLS = [hover,"pan,box_zoom,wheel_zoom,box_select,save,reset,crosshair"]   # 横向拉伸

df.index.name = 'index'
# 转化为ColumnDataSource对象
# 这里注意了，index和columns都必须有名称字段

p = figure(x_range=dis, plot_width=800,plot_height=350, title="商品折扣率统计",tools=TOOLS)
p.line(x='discount_n',y='count',source = source,     # 设置x，y值, source → 数据源
       line_width=1, line_alpha = 0.8, line_color = 'black',line_dash = [10,4])   # 线型基本设置
# 绘制折线图
p.circle(x='discount_n',y='count',source = source, 
         size = 5,color = 'red',alpha = 0.8)
p.xgrid.grid_line_color = None
# 绘制折点
show(p)

# 2.绘制各品牌折扣率散点图
output_file("双11不同品牌折扣率情况.html")

# 设置调色盘
from bokeh.palettes import brewer
n = 8
colormap2 = brewer['Blues'][n]

df=discount_new[["discount","店名"]].rename(columns={"店名":"brand"})
brand=list(df["brand"].value_counts().index)  # 按照品牌出现次数排序
# 为每一个品牌的折扣率设置颜色
# 设置颜色字典
dis_col={}
for brand_ in brand:
    sort_dis=df[df["brand"]==brand_]["discount"].value_counts().index.tolist()[::-1]  # 升序，颜色由浅到深
    # 越靠前的表明该折扣出现次数越多，则颜色应该越深
    color_n=[colormap2[int(i/len(sort_dis)*(n-1))] for i in range(len(sort_dis),0,-1)]
    dis_col[brand_]=dict(zip(sort_dis,color_n))
# 为该品牌下的折扣率设置颜色
df["color"]=pd.Series(map(lambda dis,brand:dis_col[brand][dis],df["discount"],df["brand"]))

# 保存数据


source = ColumnDataSource(data=df)

# 设置标签
hover = HoverTool(tooltips=[
                            ("品牌", "@brand"),
                            ("折扣率", "@discount")
                        ])

TOOLS = [hover,"pan,box_zoom,wheel_zoom,box_select,save,reset,crosshair"]   # 横向拉伸

df.index.name = 'index'
# 转化为ColumnDataSource对象
# 这里注意了，index和columns都必须有名称字段

p = figure(x_range=[0,1],y_range=brand, plot_width=800,plot_height=600, title="不同品牌折扣率情况",tools=TOOLS)

# 浮动设置
from bokeh.transform import jitter

p.circle(x='discount',y=jitter('brand', width=0.6, range=p.y_range),source = source, 
         size = 3,color = df["color"],alpha = 0.8)

p.ygrid.grid_line_color = None
# 绘制折点

show(p)

#####################################################################################################
##################################      3、商家营销套路挖掘？    #####################################
#####################################################################################################
# 读取数据
filename="双11商家营销套路数据"
if os.path.exists("%s.xlsx"%filename):
    print("读取本地数据: %s."%filename)
    df=pd.read_excel("%s.xlsx"%filename,index_col=0)
else:
    # 各品牌全部数据
    data=pd.read_excel("双十一淘宝美妆数据.xlsx")[["id","店名"]].rename(columns={"店名":"brand"}).drop_duplicates()
    # 读取 双11不同品牌折扣率情况 数据
    brand_discount=pd.read_excel("双11各品牌商品打折力度.xlsx")[["id","discount","店名"]].rename(columns={"店名":"brand"})
    # 合并表表，计算统计量： 品牌、平均折扣率、商品总数、打折商品占比
    goods_num=data.groupby(by="brand").count().rename(columns={"id":"goods_num"})         # 品牌下商品总数
    discount_mean=brand_discount[["brand","discount"]].groupby(by="brand").mean()         # 平均折扣率
    goods_dis_num=brand_discount[["brand","id"]].groupby(by="brand").count().rename(columns={"id":"goods_dis_num"})
    # 品牌下打折商品数量
    # 连表
    df=pd.concat([pd.concat([goods_num,discount_mean],axis=1),goods_dis_num],axis=1).dropna()
    # 打折商品占比
    df["dis_per"]=df["goods_dis_num"]/df["goods_num"]
    # 保存数据
    df.to_excel("%s.xlsx"%filename,index=True)
    
########################################## 可视化 ###################################################
output_file("双11各个品牌打折套路解析.html")

df["brand"]=df.index
source = ColumnDataSource(data=df)

# 设置标签
hover = HoverTool(tooltips=[
                            ("品牌", "@brand"),
                            ("折扣率", "@discount"),
                            ("商品总数", "@goods_num"),
                            ("参与打折商品比例", "@dis_per")
                        ])

TOOLS = [hover,"pan,box_zoom,wheel_zoom,box_select,save,reset,crosshair"]   # 横向拉伸

df.index.name = 'index'
# 转化为ColumnDataSource对象
# 这里注意了，index和columns都必须有名称字段

p = figure(x_range=[-0.04,0.8], y_range=[0.4,0.9],plot_width=800,plot_height=600, title="各个品牌打折套路解析",tools=TOOLS)

p.circle_x(x='dis_per',y='discount',source = source,
         line_color = 'black',   # 设置点边线为黑色
         line_dash="dashed",
         fill_color = "Red",fill_alpha = 0.6,   # 设置内部填充颜色，这里用到了颜色字段
         size = df["goods_num"]/df["goods_num"].max()*70,alpha = 0.8)

# 网格设置
p.ygrid.grid_line_alpha = 0.8
p.ygrid.grid_line_dash = "dashed"
p.xgrid.grid_line_alpha = 0.8
p.xgrid.grid_line_dash = "dashed"

# 添加辅助线
from bokeh.models.annotations import Span
# 辅助线1： 平均折扣率
mean_discount=df["discount"].mean()
# 辅助线2：平均打折商品占比
mean_disper=df["dis_per"].mean()

# 横向的：平均折扣率
width = Span(location=mean_discount,           # 设置位置，对应坐标值
             dimension='width',    # 设置方向，width为横向，height为纵向  
             line_color='olive', line_width=3,   # 设置线颜色、线宽
             line_dash="dashed"
            )
p.add_layout(width)

# 纵向的：平均打折占比
height = Span(location=mean_disper,           # 设置位置，对应坐标值
             dimension='height',    # 设置方向，width为横向，height为纵向  
             line_color='olive', line_width=3,   # 设置线颜色、线宽
             line_dash="dashed"
            )
p.add_layout(height)

# 辅助矩形
from bokeh.models.annotations import BoxAnnotation

# 象限1：左上
left_up = BoxAnnotation(bottom=mean_discount,right=mean_disper,  # 设置矩形四边位置
                       fill_alpha=0.1, fill_color='olive'        # 设置透明度、颜色
                      )
p.add_layout(left_up)

# 象限2：右上
right_up = BoxAnnotation(bottom=mean_discount,left=mean_disper,  # 设置矩形四边位置
                       fill_alpha=0.1, fill_color='firebrick'        # 设置透明度、颜色
                      )
p.add_layout(right_up)

# 象限3：左下
left_down = BoxAnnotation(top=mean_discount,right=mean_disper,  # 设置矩形四边位置
                       fill_alpha=0.1, fill_color='firebrick'        # 设置透明度、颜色
                      )
p.add_layout(left_down)

# 象限4：右下
right_down = BoxAnnotation(top=mean_discount,left=mean_disper,  # 设置矩形四边位置
                       fill_alpha=0.1, fill_color='olive'        # 设置透明度、颜色
                      )
p.add_layout(right_down)

## 添加注释
from bokeh.models.annotations import Label

# 设置四个注释的位置

label1 = Label(x=0.1, y=0.8,       # 标注注释位置
              #x_offset=12,    # x偏移，同理y_offset
              text="少量少打折",      # 注释内容
              text_font_size="12pt",    # 字体大小
             )
p.add_layout(label1)

label2 = Label(x=0.5, y=0.8,       # 标注注释位置
              #x_offset=12,    # x偏移，同理y_offset
              text="少量少打折",      # 注释内容
              text_font_size="12pt",    # 字体大小
             )
p.add_layout(label2)

label3 = Label(x=0.1, y=0.55,       # 标注注释位置
              #x_offset=12,    # x偏移，同理y_offset
              text="少量大打折",      # 注释内容
              text_font_size="12pt",    # 字体大小
             )
p.add_layout(label3)

label4 = Label(x=0.5, y=0.55,       # 标注注释位置
              #x_offset=12,    # x偏移，同理y_offset
              text="大量大打折",      # 注释内容
              text_font_size="12pt",    # 字体大小
             )
p.add_layout(label4)

show(p)







