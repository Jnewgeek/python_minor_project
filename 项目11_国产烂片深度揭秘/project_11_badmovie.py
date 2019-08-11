# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 14:38:06 2019

@author: HASEE
项目11国产烂片深度揭秘
"""
import pandas as pd
#import warnings
#warnings.filterwarnings("ignore")
import os
os.chdir(r"F:\pythondata\Python微专业\【非常重要】课程资料\python_minor_project\项目7_15\项目11国产烂片深度揭秘")
for i in ["./img","./data","./html"]:
    if not os.path.exists(i):
        os.mkdir(i)
# 读取原始数据
movie_data=pd.read_excel("moviedata.xlsx")

##################################################################################
############################ 1、评分分布，烂片 ####################################
##################################################################################
print("               《项目10: 国产烂片深度揭秘》\n")
print(">>>>>>>>>>>>>>>>>>>>> 任务1. 评分分布，烂片 <<<<<<<<<<<<<<<<<<<\n")
filename="./data/movie_data1.xlsx"
if os.path.exists(filename):
    movie_data1=pd.read_excel(filename)
    print(">> 读取清洗后的本地数据 ———— %s,数据量为: %d行"%(filename.replace("./data/","").strip(".xlsx"),movie_data1.shape[0]))
else:
    # 去除电影名称、豆瓣评分为空的数据
    movie_data1=movie_data[(movie_data["电影名称"].notnull())&(movie_data["豆瓣评分"].notnull())][["电影名称","豆瓣评分","导演","主演"]]
    movie_data1.to_excel(filename,index=False,encoding="utf-8")
    print(">> moviedata 原始数据量: %d行,去除缺失值后: %d行."%(movie_data.shape[0],movie_data1.shape[0]))

##### 可视化
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")
plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体设置-黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
sns.set(font='SimHei')  # 解决Seaborn中文显示问题
# 直方图
fig=plt.figure(figsize=(8,6))
sns.distplot(movie_data1["豆瓣评分"],bins=20,hist = True,kde = False,
            norm_hist=False,rug = False,vertical = False,
            color = 'y',axlabel = '')
plt.title("豆瓣评分-直方图")
plt.savefig("./img/豆瓣评分_直方图.png",dpi=200)

# 箱型图
fig=plt.figure(figsize=(8,6))
sns.boxplot(x="豆瓣评分", data=movie_data1,
            linewidth = 2,   # 线宽
            #width = 0.8,     # 箱之间的间隔比例
            fliersize = 3,   # 异常点大小
            palette = 'hls', # 设置调色板
            whis = 1.5,      # 设置IQR 
           )
plt.ylabel("豆瓣评分")
plt.xlabel("")
plt.title("豆瓣评分-箱型图")
plt.savefig("./img/豆瓣评分_箱型图.png",dpi=200)

# 烂片标准
badmovie_score=movie_data1["豆瓣评分"].describe()["25%"]
print(">> 经过计算得到,评分低于%.1f的电影定义为烂片."%badmovie_score)

# 筛选烂片电影前20
bad_movie_20=movie_data1[movie_data1["豆瓣评分"]<badmovie_score][["电影名称",
"豆瓣评分","导演","主演"]].sort_values(by="豆瓣评分").reset_index(drop=True)[:20]
bad_movie_20.to_excel("./data/烂片Top20.xlsx",index=False)
print(">> Top20烂片导出完成.")

##################################################################################
############################ 2、什么题材烂片最多 ##################################
##################################################################################
# 根据某个合并在一起的类别，进行拆分，举例： 多个分类的电影拆分为单个的分类
def split_data(data,col,sep,badmovie_score=badmovie_score):
    """将多个类型的数据拆分成单一类型.
    data: 原数据
    col: 原始合并在一起的类型
    sep: 分隔符
    badmovie_score: 烂片标准，由任务1计算得出
    """
    movie_type=data[col].str.strip().str.split(sep,expand=True)
    movie_type.columns=["%s_"%col+str(i) for i in movie_type.columns]
    data=data.join(movie_type)  # 连接数据
    # 将拆分后的数据全部设置相应的豆瓣评分
    def get_type_score(data,cols):
        result=pd.DataFrame(columns=["typename","score"])
        for i in cols:
            df=data[data[i].notnull()][[i,"score"]]
            df.columns=["typename","score"]
            result=pd.concat([result,df],axis=0)
            result.index=range(len(result))
        return result
    # 拆分后的数据
    movie_type_score=get_type_score(data,movie_type.columns)
    # 去除空格
    movie_type_score["typename"]=movie_type_score["typename"].str.strip()
    print(">> 电影的%s已经重新拆分,数据量为: %d行"%(col,movie_type_score.shape[0]))
    # 将各类型的电影打上标签
    movie_type_score["lp"]=movie_type_score["score"].map(lambda x:1 if x<badmovie_score else 0)
    # 按照类型进行汇总
    # 烂片数量
    bad_num=pd.DataFrame(movie_type_score[["typename","lp"]].groupby(by="typename").sum())
    # 数量
    num=pd.DataFrame(movie_type_score["typename"].value_counts())
    movie_type_score=num.join(bad_num).reset_index()      # 汇总后的结果
    movie_type_score.columns=["typename","typecount","type_lp_pre"]
    # 烂片比例
    movie_type_score["type_lp_pre"]=movie_type_score["type_lp_pre"]/movie_type_score["typecount"]
    # 修改列名
    movie_type_score.columns=[i.replace("type",col) for i in movie_type_score.columns]   
    # 按照烂片比例降序排列
    movie_type_score=movie_type_score.sort_values(by="%s_lp_pre"%col,ascending=False).reset_index(drop=True)

    return movie_type_score

print("\n>>>>>>>>>>>>>>>>>>>> 任务2. 什么题材烂片最多 <<<<<<<<<<<<<<<<<<\n")
filename="./data/movie_type_score.xlsx"
if os.path.exists(filename):
    movie_type_score=pd.read_excel(filename)
    print(">> 读取清洗后的本地数据 ———— %s,数据量为: %d行"%(filename.replace("./data/","").strip(".xlsx"),movie_type_score.shape[0]))
else:
    # 去除类型，豆瓣评分为空的数据
    movie_data2=movie_data[(movie_data["类型"].notnull())&(movie_data["豆瓣评分"].notnull())][["类型","豆瓣评分"]]
    movie_data2.columns=["type","score"]
    print(">> moviedata 原始数据量: %d行,去除缺失值后: %d行."%(movie_data.shape[0],movie_data2.shape[0]))
    # 清洗数据,拆分数据
    movie_type_score=split_data(movie_data2,col="type",sep=" / ")
    # 导出结果
    movie_type_score.to_excel(filename,index=False,encoding="utf-8")
    print(">> 各类型的烂片比例导出完成,共%d行."%movie_type_score.shape[0])
    
############################## 可视化 bokeh 散点图  ###############################
from bokeh.plotting import figure,show,output_file

output_file("./html/不同电影题材烂片比例.html")
# 绘制散点图
# 十字标签
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool

df = movie_type_score[:20]  # Top20的数据

df.index.name = 'index'
df["size"]=df["typecount"].map(lambda x:x**0.5*2)
source = ColumnDataSource(df)

hover = HoverTool(tooltips=[
                            ("电影类型", "@typename"),
                            ("数据量", "@typecount"),
                            ("烂片比例", "@type_lp_pre")
                        ])

TOOLS = [hover,"pan,box_zoom,wheel_zoom,box_select,lasso_select,save,reset,crosshair"]

s1 = figure(x_range=source.data["typename"].tolist(),y_range=[0.1,0.65],
            plot_width=800, plot_height=400,
           tools=TOOLS,
           toolbar_location='above',     # 工具栏位置："above"，"below"，"left"，"right"
           x_axis_label = '电影类型', y_axis_label = '烂片比例',    # X,Y轴label
           #y_range = [0,1.1],        # X,Y轴范围
           title="不同电影题材烂片比例"                       # 设置图表title
           )
s1.circle(x = 'typename',y = 'type_lp_pre',source = source,size="size",
         fill_color = 'red',fill_alpha = 0.6, # 填充的颜色、透明度
         line_color = 'black',line_alpha = 0.8,line_dash = 'dashed',line_width = 2,   # 点边线的颜色、透明度、虚线、宽度
         )


s1.xaxis.axis_line_width = 3
s1.yaxis.axis_line_width = 3
s1.xaxis.axis_label_text_font_style = "italic"
s1.yaxis.axis_label_text_font_style = "italic"
s1.ygrid.grid_line_alpha = 0.8
s1.ygrid.grid_line_dash = "dashed"
s1.xgrid.grid_line_alpha = 0.8
s1.xgrid.grid_line_dash = "dashed"

show(s1)

##################################################################################
######################### 3、和什么国家拍最容易出烂片 ##############################
##################################################################################
print("\n>>>>>>>>>>>>>>> 任务3. 和什么国家拍最容易出烂片 <<<<<<<<<<<<<<<\n")
filename="./data/movie_loc_score.xlsx"
if os.path.exists(filename):
    movie_loc_score=pd.read_excel(filename)
    print(">> 读取清洗后的本地数据 ———— %s,数据量为: %d行"%(filename.replace("./data/","").strip(".xlsx"),movie_loc_score.shape[0]))
else:
    # 去除制片国家为空或不包含中国大陆的数据
    movie_data3=movie_data[(movie_data["制片国家/地区"].notnull())&(movie_data["制片国家/地区"].str.contains("中国"))&(
                            movie_data["豆瓣评分"].notnull())][["制片国家/地区","豆瓣评分"]]
    movie_data3.columns=["loc","score"]
    print(">> moviedata 原始数据量: %d行,去除缺失值后: %d行."%(movie_data.shape[0],movie_data3.shape[0]))
    # 进一步筛选
    # 1. 将空格和中国大陆去掉
    movie_data3["loc"]=movie_data3["loc"].str.replace("中国大陆","").str.replace("中国",
    "").str.replace(" /  / "," / ")
    movie_data3["loc"]=movie_data3["loc"].str.replace(" /","/").str.replace("/ ","/").str.strip(" /")
    # 2. 去除loc为空的、台湾、香港的数据
    movie_data3=movie_data3[[movie_data3["loc"][i] not in ("","香港","台湾","香港/台湾","台湾/香港") 
    for i in movie_data3.index]]
    
    # 将制片国家/地区进行拆分，过程与之前的电影类型相同
    movie_loc_score=split_data(movie_data3,col="loc",sep="/")
    # 再次去掉香港和台湾
    movie_loc_score=movie_loc_score[[movie_loc_score["locname"][i] not in ("香港","台湾") for i in 
            movie_loc_score.index]].reset_index(drop=True)
    movie_loc_score.to_excel(filename,index=False,encoding="utf-8")
    print(">> 与其他国家合拍的烂片比例导出完成,共%d行."%movie_loc_score.shape[0])

##################################################################################
############################## 4. 卡司数量与烂片比例 ##############################
##################################################################################
print("\n>>>>>>>>>>>>>>>>>> 任务4. 卡司数量与烂片比例 <<<<<<<<<<<<<<<<<<\n")
# 烂片比例与主演人数的关系
filename="./data/movie_num_score.xlsx"
if os.path.exists(filename):
    movie_num_score=pd.read_excel(filename)
    print(">> 读取清洗后的本地数据 ———— %s,数据量为: %d行"%(filename.replace("./data/","").strip(".xlsx"),movie_num_score.shape[0]))
else:
    # 去除电影名称、主演、豆瓣评分为空的数据
    movie_data4=movie_data[(movie_data["电影名称"].notnull())&(movie_data["主演"].notnull())&(movie_data["豆瓣评分"].notnull())][["电影名称","主演","豆瓣评分"]]
    print(">> moviedata 原始数据量: %d行,去除缺失值后: %d行."%(movie_data.shape[0],movie_data4.shape[0]))
    actor=movie_data4["主演"].str.strip().str.split(" / ",expand=True)
    # 演员人数
    actor["num"]=actor.count(axis=1)
    # 数据分组
    # '1-2人','3-4人','5-6人','7-9人','10以上'
    import numpy as np
    movie_data4["主演人数分类"]=pd.cut(actor["num"],bins=[0,2,4,6,10,np.inf],labels=['1-2人','3-4人','5-6人','7-9人','10以上'])
    # 分组计算
    # 将各类型的电影打上标签
    movie_data4["lp"]=movie_data4["豆瓣评分"].map(lambda x:1 if x<badmovie_score else 0)
    # 导出movie_data4,以备后用
    movie_data4.to_excel("./data/movie_data4.xlsx",index=False,encoding="utf-8")
    # 烂片数量
    bad_num=pd.DataFrame(movie_data4[["主演人数分类","lp"]].groupby(by="主演人数分类").sum())
    # 数量
    num=pd.DataFrame(movie_data4["主演人数分类"].value_counts())
    movie_num_score=num.join(bad_num).reset_index()      # 汇总后的结果
    movie_num_score.columns=["主演人数分类","电影数量","烂片数量"]
    # 烂片比例
    movie_num_score["烂片比例"]=movie_num_score["烂片数量"]/movie_num_score["电影数量"]
    movie_num_score=movie_num_score.sort_values(by="主演人数分类").reset_index(drop=True)
    movie_num_score.to_excel(filename,index=False,encoding="utf-8")
    print(">> 各主演人数分类的烂片比例导出完成,共%d行."%movie_num_score.shape[0])

# 烂片比例最多的明星Top20
# 依靠的数据源是movie_data4
filename="./data/movie_actor_score.xlsx"
if os.path.exists(filename):
    movie_actor_score=pd.read_excel(filename)
    print(">> 读取清洗后的本地数据 ———— %s,数据量为: %d行"%(filename.replace("./data/","").strip(".xlsx"),movie_actor_score.shape[0]))
else:
    movie_actor_score=movie_data4[["主演","豆瓣评分"]]
    # 修改列名
    movie_actor_score.columns=["role","score"]
    movie_actor_score=split_data(movie_actor_score,col="role",sep=" / ")
    # 进行一些筛选，去除那些拍电影数量太少的演员：少于3个的都去掉
    movie_actor_score=movie_actor_score[movie_actor_score["rolecount"]>=3]
    # 导出结果
    movie_actor_score.to_excel(filename,index=False,encoding="utf-8")
    print(">> 各演员的烂片比例导出完成(去除那些参演电影少于3部的演员),共%d行."%movie_actor_score.shape[0])

"""
小记: 烂片比例最多的明星计算结果显示，一些小众演员的烂片比例很高，所以吴亦凡一类的票房毒药就不会出现在
Top20中，如果有一张当红明星的标签表的话，可以对结果数据进一步筛选，目前的情况只能筛选到这里为止。
"""

##################################################################################
########################## 5. 不同导演每年电影产量情况 ############################
##################################################################################
print("\n>>>>>>>>>>>>>>> 任务5. 不同导演每年电影产量情况 <<<<<<<<<<<<<<<\n")
# 烂片比例与主演人数的关系
filename="./data/target_dir_num_score.xlsx"
if os.path.exists(filename):
    target_dir_num_score=pd.read_excel(filename)
    print(">> 读取清洗后的本地数据 ———— %s,数据量为: %d行"%(filename.replace("./data/","").strip(".xlsx"),target_dir_num_score.shape[0]))
else:
    # 数据清洗
    # 清洗日期
    if os.path.exists("./data/movie_data5.xlsx"):
        movie_data5=pd.read_excel("./data/movie_data5.xlsx")
    else:
        # 去除电影名称、导演、豆瓣评分、上映日期为空的数据
        movie_data5=movie_data[(movie_data["电影名称"].notnull())&(movie_data["导演"].notnull())&
                            (movie_data["豆瓣评分"].notnull())&(movie_data["上映日期"].notnull())][["电影名称","导演","豆瓣评分","上映日期"]]
        import re
        pattern=re.compile(r"\d+")   # 只提取数字，为了直接提取年份
        # 考虑到日期里可能有多个日期，因为会在不同的地方上映，这里只考虑第一个时间
        date=pd.DataFrame(movie_data5["上映日期"].str.strip().str.split(" / ",expand=True).loc[:,0])
        date.columns=["上映日期"]
        # 正则提取
        date["year"]=date["上映日期"].map(lambda x:pattern.findall(x)[0] if pattern.findall(x) else "")
        # 去除无年份的记录
        movie_data5=movie_data5.join(date[["year"]])
        movie_data5=movie_data5[(movie_data5["year"]>="2007")&(movie_data5["year"]<="2017")][["电影名称","导演","豆瓣评分","year"]]
        movie_data5.to_excel("./data/movie_data5.xlsx",index=False,encoding="utf-8")
        print(">> moviedata 原始数据量: %d行,去除缺失值后: %d行."%(movie_data.shape[0],movie_data5.shape[0]))
    
    # 计算每个导演的烂片比例
    movie_dir_score=movie_data5[["导演","豆瓣评分"]]
    movie_dir_score.columns=["dir","score"]
    movie_dir_score=split_data(movie_dir_score,col="dir",sep=" / ")
    # 进一步筛选数据，去除作品少于10部的导演,去除没有烂片的导演
    movie_dir_score=movie_dir_score[(movie_dir_score["dircount"]>=10)&(movie_dir_score["dir_lp_pre"]>0)].reset_index(drop=True)
    # 选定的导演历年的作品数量及其电影均分
    target_dir_num_score=pd.DataFrame()
    for i in movie_dir_score["dirname"]:
        # 遍历movie_data5的数据，将包含该导演的电影数据进行汇总计算
        df=movie_data5[movie_data5["导演"].str.contains(i)]
        # 电影数量
        num=pd.DataFrame(df[["电影名称","year"]].groupby(by="year").count())
        # 电影评分
        score=pd.DataFrame(df[["豆瓣评分","year"]].groupby(by="year").mean())
        # 连表
        result=num.join(score)
        result.columns=["dirnum","dirscore"]
        result["director"]=i
        target_dir_num_score=pd.concat([target_dir_num_score,result],axis=0)
    # 修改索引
    target_dir_num_score=target_dir_num_score.reset_index().fillna(0)
    target_dir_num_score.to_excel(filename,index=False,encoding="utf-8")
    print(">> 特定导演历年的作品数量及平均得分导出完成,共%d个导演,数据量为: %d行."%(movie_dir_score.shape[0],target_dir_num_score.shape[0]))

########################################### 可视化 ###################################################
from bokeh.plotting import figure,show,output_file

output_file("./html/不同导演每年的电影产量及均分.html")
# 绘制散点图
# 十字标签
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.palettes import Spectral4

target_dir_num_score["year"]=target_dir_num_score["year"].map(str)
target_dir_num_score.index.name = 'index'

def get_source(data,director):
    """获取特定导演的数据."""
    df = data[data["director"]==director][["year","dirnum","dirscore"]]
    source = ColumnDataSource(df)
    return source 

hover = HoverTool(tooltips=[
                            ("该年电影均分", "@dirscore"),
                            ("该年电影产量", "@dirnum"),
                        ])

TOOLS = [hover,"pan,box_zoom,wheel_zoom,box_select,lasso_select,save,reset,crosshair"]

p = figure(x_range=target_dir_num_score["year"].unique().tolist(),
            plot_width=800, plot_height=400,
           tools=TOOLS,
           toolbar_location='above',     # 工具栏位置："above"，"below"，"left"，"right"
           x_axis_label = '年份', y_axis_label = '电影均分',    # X,Y轴label
           #y_range = [0,1.1],        # X,Y轴范围
           title="不同导演每年的电影产量及均分"                       # 设置图表title
           )
# 点的系数
point_size=5

director="王晶"
source1=get_source(target_dir_num_score,director)  # 王晶
p.circle(x = 'year',y = 'dirscore',source = source1,size=[i*point_size for i in source1.data["dirnum"]],
     color = Spectral4[0],fill_alpha = 0.6, # 填充的颜色、透明度
     legend=director
     )

director="周伟"
source2=get_source(target_dir_num_score,director)  # 周伟
p.circle(x = 'year',y = 'dirscore',source = source2,size=[i*point_size for i in source2.data["dirnum"]],
     color = Spectral4[1],fill_alpha = 0.6, # 填充的颜色、透明度
     legend=director
     )

director="邓衍成"
source3=get_source(target_dir_num_score,director)  # 邓衍成
p.circle(x = 'year',y = 'dirscore',source = source3,size=[i*point_size for i in source3.data["dirnum"]],
     color = Spectral4[2],fill_alpha = 0.6, # 填充的颜色、透明度
     legend=director
     )

# 绘制矩形
from bokeh.models.annotations import BoxAnnotation

bg=BoxAnnotation(top=badmovie_score,fill_alpha=0.1,fill_color="red")
p.add_layout(bg) 

p.xaxis.axis_line_width = 3
p.yaxis.axis_line_width = 3
p.xaxis.axis_label_text_font_style = "italic"
p.yaxis.axis_label_text_font_style = "italic"
p.ygrid.grid_line_alpha = 0.8
p.ygrid.grid_line_dash = "dashed"
p.xgrid.grid_line_alpha = 0.8
p.xgrid.grid_line_dash = "dashed"

p.legend.location = "top_right"
p.legend.click_policy="hide"

show(p)

print("\n全部任务完成.")





