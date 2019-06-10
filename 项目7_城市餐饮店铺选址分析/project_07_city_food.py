# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 20:56:10 2019

@author: HASEE
"""

import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import os
os.chdir(os.getcwd())


#####################################################################################################
####################################      1. 餐饮类型指标统计     ####################################
#####################################################################################################

if os.path.exists("不同餐饮类型的得分情况.csv"):
    print("读取本地数据.")
    result=pd.read_csv("不同餐饮类型的得分情况.csv",engine="python",encoding="utf-8")
else:
    # 读取餐饮数据
    data=pd.read_excel("上海餐饮数据.xlsx",sheet_name=0)
    # 新建dataframe,取子段： 类别、口味、环境、服务、人均消费,去除缺失值
    data1=data[["类别","口味","环境","服务","人均消费"]].dropna()
    # 去除零
    data2=data1[(data1["口味"]>0)&(data1["环境"]>0)&(data1["服务"]>0)&(data1["人均消费"]>0)]
    # 计算性价比
    data2["性价比"]=(data2["口味"]+data2["环境"]+data2["服务"])/data2["人均消费"]           
    # 去除异常值，按照外限： 即 mi-3*iqr <=x<= ma+3*iqr, 其中 mi为下四分位点，ma为上四分位点，iqr=ma-mi
    # 分别对 口味、性价比、人均消费 去异常值，再merge合并
    def remove_strange(data,col,cate="类别"):
        """去除外限以外的异常值"""
        s=data[col].describe()            # 数据统计
        mi=s["25%"]
        ma=s["75%"]
        iqr=ma-mi
        target=data[(data[col]>=mi-3*iqr)&(data[col]<=ma+3*iqr)][[col,cate]]    # 保证返回的是一个数据框
        return target
                
    # 去除异常值后的结果
    taste=remove_strange(data2,"口味").groupby(by="类别").mean()
    consumption=remove_strange(data2,"人均消费").groupby(by="类别").mean()
    cost_performance=remove_strange(data2,"性价比").groupby(by="类别").mean()
    # 合并结果
    result=pd.merge(pd.merge(taste,consumption,left_index=True,right_index=True),cost_performance,
                    left_index=True,right_index=True)
    # 标准化
    def min_max(df):
        """计算min-max标准化结果"""
        min_=df.min()
        max_=df.max()
        return (df-min_)/(max_-min_)
    result["性价比_n"]=min_max(result["性价比"])
    result["口味_n"]=min_max(result["口味"])
    result["人均消费_n"]=min_max(result["人均消费"])
    
    # 导出文件
    result.to_csv("不同餐饮类型的得分情况.csv",index=False,encoding="utf-8")

######################################### 可视化  #########################################
from bokeh.plotting import figure,show,output_file

output_file("不同餐饮类型的得分情况.html")
# 绘制散点图
# 十字标签
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool

df = pd.DataFrame({'A':result["人均消费"],
                  'B':result["性价比_n"],
                  'C':result["口味_n"],
                  'type':result.index},index=result.index)         # 直接使用index无法显示。

df.index.name = 'index'
df=df.sort_values(by="B",ascending=False)         # 按性价比得分降序排列
source = ColumnDataSource(df)

hover = HoverTool(tooltips=[
                            ("餐饮类型", "@type"),
                            ("人均消费", "@A"),
                            ("性价比得分", "@B"),
                            ("口味得分", "@C"),
                        ])

TOOLS = [hover,"pan,box_zoom,wheel_zoom,box_select,lasso_select,save,reset,crosshair"]

s1 = figure(plot_width=800, plot_height=220,
           tools=TOOLS,
           toolbar_location='right',     # 工具栏位置："above"，"below"，"left"，"right"
           x_axis_label = '人均消费', y_axis_label = '性价比得分',    # X,Y轴label
           y_range = [0,1.1],        # X,Y轴范围
           title="餐饮类型得分情况"                       # 设置图表title
           )
s1.circle(x = 'A',y = 'B',source = source,size=[i*25 for i in source.data["C"]],
         fill_color = 'blue',fill_alpha = 0.6, # 填充的颜色、透明度
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

# 柱状图

def plot_bar(source,col,color,title):
    """柱状图"""
    
    p = figure(x_range=source.data["index"].tolist(), y_range=(0,1.1),plot_width=800,plot_height=220, title=title,tools=TOOLS)
    
    p.vbar(x='index', top=col, source=source,    # 加载数据另一个方式
           width=0.9, alpha = 0.8,
           color = color,#factor_cmap('fruits', palette=Spectral6, factors=fruits),    # 设置颜色
           )
    
    p.xgrid.grid_line_color = None
    p.legend.orientation = "horizontal"
    # 其他参数设置
    
    return p

# 口味得分
s2=plot_bar(source,"C","red","口味得分")
# 性价比得分
s3=plot_bar(source,"B","green","性价比得分")

# 如何拼接起来
from bokeh.layouts import gridplot

p = gridplot([[s1],[s2],[s3]])
show(p)


#####################################################################################################
####################################        2. 店铺选址分析       ####################################
#####################################################################################################
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import os
os.chdir(r"F:\pythondata\Python微专业\【非常重要】课程资料\python_minor_project\项目7_15\项目07城市餐饮店铺选址分析\导出四项指标")
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool


kind="素菜"                                         # 选择类别
if os.path.exists("../店铺选址各坐标点得分.csv"):
    print("读取本地数据.")
    result=pd.read_csv("../店铺选址各坐标点得分.csv",engine="python",encoding="utf-8")
else:
    # 选择一个餐饮类型作为目标
    all_kind=data[["类别","Lng","Lat"]]
    vegetable_plate=data[data["类别"]==kind][["类别","Lng","Lat"]]
    # 导出csv文件
    all_kind.to_csv("餐饮热度poi.csv",index=False,encoding="utf-8")
    vegetable_plate.to_csv("同类竞品poi.csv",index=False,encoding="utf-8")
    
    # 读取四项指标数据
    people_md=pd.read_csv("人口密度指标.csv",engine="python",encoding="utf-8")    # 人口密度
    road_md=pd.read_csv("道路密度指标.csv",engine="python",encoding="utf-8")      # 道路密度
    food_md=pd.read_csv("餐饮热度指标.csv",engine="python",encoding="utf-8")      # 餐饮热度
    compete_md=pd.read_csv("同类竞品指标.csv",engine="python",encoding="utf-8")   # 同类竞品
    
    # 缺失值处理
    people_md=people_md[["X","Y","Z"]].rename(columns={"Z":"人口密度"}).fillna(0)  # 人口密度
    road_md=road_md[["X","Y","长度"]].rename(columns={"长度":"道路密度"}).fillna(0)  # 道路密度
    food_md=food_md[["X","Y","PNTCNT"]].rename(columns={"PNTCNT":"餐饮密度"}).fillna(0)  # 人口密度
    compete_md=compete_md[["X","Y","PNTCNT"]].rename(columns={"PNTCNT":"竞品密度"}).fillna(0)  # 人口密度
    
    # 标准化
    people_md["人口密度_n"]=min_max(people_md["人口密度"])
    road_md["道路密度_n"]=min_max(road_md["道路密度"])
    food_md["餐饮密度_n"]=min_max(food_md["餐饮密度"])
    compete_md["竞品密度_n"]=1-min_max(compete_md["竞品密度"])                        # 竞品密度指标越小越好
    # 连表
    result=pd.merge(people_md.iloc[:,[0,1,3]],road_md.iloc[:,[0,1,3]],on=["X","Y"])  # 只保留坐标和标准化后的结果
    result=pd.merge(result,food_md.iloc[:,[0,1,3]],on=["X","Y"])  # 只保留坐标和标准化后的结果
    result=pd.merge(result,compete_md.iloc[:,[0,1,3]],on=["X","Y"])  # 只保留坐标和标准化后的结果
    
    # 计算指标  参考公式： 综合指标 = 人口密度指标*0.4 + 餐饮热度指标*0.3 + 道路密度指标*0.2 +同类竞品指标*0.1
    # 因为要求同类竞品指标越低越好，因此作为负值传入
    result["final_score"]=result["人口密度_n"]*0.4+result["道路密度_n"]*0.3+result["餐饮密度_n"]*0.2+result["竞品密度_n"]*0.1
    # 按得分降序排列
    result=result.sort_values(by="final_score",ascending=False)
    # 保存文件
    result.to_csv("../店铺选址各坐标点得分.csv",index=False,encoding="utf-8")       # 保存至上级目录
    
######################################### 可视化  #########################################
from bokeh.palettes import brewer
n = 8
colormap = brewer['Greens'][n]                  # 绿色渐变
# 绘制散点图
output_file("../店铺选址可视化结果.html")

df = result[["X","Y","final_score"]]              # 可视化需要的图表
# 将final_score分级
color_range=(df["final_score"]/df["final_score"].max()*(n-1)).apply(int)
df['color'] = [colormap[x] for x in color_range]           # 调色盘
df['color'][:10]="red"                                           # Top 10 单独设置红色

df.index.name = 'index'
source = ColumnDataSource(df)

hover = HoverTool(tooltips=[
                            ("经度", "@X"),
                            ("纬度", "@Y"),
                            ("综合得分", "@final_score"),
                        ])

TOOLS = [hover,"pan,box_zoom,wheel_zoom,box_select,lasso_select,save,reset,crosshair"]

s4 = figure(plot_width=700, plot_height=700,
           tools=TOOLS,
           toolbar_location='right',     # 工具栏位置："above"，"below"，"left"，"right"
           x_axis_label = '经度', y_axis_label = '纬度',    # X,Y轴label
           title="%s选址情况"%kind                       # 设置图表title
           )
s4.square(x = 'X',y = 'Y',source = source,size=[i*25 for i in source.data["final_score"]],
         fill_color = df["color"],fill_alpha = 0.8, # 填充的颜色、透明度
         line_color = 'white',line_alpha = 0.8,line_width = 2,   # 点边线的颜色、透明度、虚线、宽度
         )

s4.xaxis.axis_line_width = 3
s4.yaxis.axis_line_width = 3
s4.xaxis.axis_label_text_font_style = "italic"
s4.yaxis.axis_label_text_font_style = "italic"
s4.ygrid.grid_line_alpha = 0.8
s4.ygrid.grid_line_dash = "dashed"
s4.xgrid.grid_line_alpha = 0.8
s4.xgrid.grid_line_dash = "dashed"

show(s4)









