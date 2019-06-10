# -*- coding: utf-8 -*-
"""
Created on Mon May 13 15:55:28 2019

@author: Administrator
"""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(font='SimHei')
plt.rcParams['font.sans-serif'] = ['SimHei']  
# Matplotlib中设置字体-黑体，解决Matplotlib中文乱码问题
plt.rcParams['axes.unicode_minus'] = False    
# 解决Matplotlib坐标轴负号'-'显示为方块的问题
import warnings
warnings.filterwarnings("ignore")
import os
os.chdir(os.getcwd())
# 自动创建文件夹
for i in ['./img','./data','./html']:
    if not os.path.exists(i):
        os.mkdir(i)

###############################################################################
############################ 任务1 构建随机数据看分布 #############################
##############################################################################
print("             《项目14：婚恋配对实验》\n")
print(">>>>>>>>>>>>> 任务1 构建随机数据看分布 <<<<<<<<<<<<\n")
# 生成随机数据
np.random.seed(100)     # 随机种子
np.random.randint(10)

class MarriageMatch():
    '''婚姻配对模型.'''
    
    def __init__(self,n=10000,mean=60,std=15,seed=100,randoms=False):
        '''初始化参数.'''
        self.n=n
        self.mean=mean
        self.std=std
        self.seed=seed
        self.randoms=randoms
        
    def create_data(self,gender='m'):
        '''生成模拟数据，即男性和女性的模拟分值.'''
        # 创建模拟数据
        # 财富、内涵、外貌
        if self.randoms==False:             # 当randoms为默认的False时，为假随机，结果可以复现
            np.random.seed(self.seed if gender=='f' else 2*self.seed)       # 随机种子
        wealth=np.random.exponential(scale=self.std, size=self.n) + self.mean-self.std  # 财富符合指数分布
        intension=np.random.normal(loc=self.mean, scale=self.std, size=self.n)     # 内涵符合正态分布
        if self.randoms==False:
            np.random.seed(self.seed+1 if gender=='f' else 2*self.seed+1)     # 随机种子
        appearance=np.random.normal(loc=self.mean, scale=self.std, size=self.n)     # 内涵符合正态分布
        # 整体的数据
        data=pd.DataFrame({"财富":wealth,"内涵":intension,"外貌":appearance,"均分":(wealth+intension+appearance)/3},
                               index=[gender+str(i) for i in range(1,self.n+1)],columns=['外貌','内涵','财富','均分'])
        return data
        
    '''
    配对策略
    ** 择偶策略1：门当户对，要求双方三项指标加和的总分接近，差值不超过20分；
    ** 择偶策略2：男才女貌，男性要求女性的外貌分比自己高出至少10分，女性要求男性的财富分比自己
    高出至少10分；
    ** 择偶策略3：志趣相投、适度引领，要求对方的内涵得分在比自己低10分~高10分的区间内，且外貌
    和财富两项与自己的得分差值都在5分以内 
    '''
    def match_one(self,male_score,female_score,stratege_type):
        '''通过计算传入的男女三项指标,并根据选择的策略进行配对,配对成功返回True,否则返回False.
        
        :param male_score:男性指标得分,外貌、内涵、财富
        :param female_score：女性指标得分，外貌、内涵、财富
        :param stratege_type: 策略选择，1：门当户对，2：男才女貌，3：志趣相投，这里默认以男性作为策略选择方。
        '''
        if stratege_type==1 and abs(sum(male_score)-sum(female_score))<=20:
            return True
        elif stratege_type==2 and female_score[0]-male_score[0]>=10 and male_score[2]-female_score[2]>=10:
            return True
        elif stratege_type==3 and abs(male_score[1]-female_score[1])<=10 and abs(male_score[0]-female_score[0])<=5 and abs(male_score[2]-female_score[2])<=5: 
            return True
        else:
            return False
            
    def set_stratege_type(self):
        '''为男性设置策略'''
        if self.randoms==False:       # 设置随机种子
            np.random.seed(self.seed)
        self.stratege_type=[1,2,3]*int(self.n/3)
        np.random.shuffle(self.stratege_type)
        # 因为后续的模拟中存在一个删除记录的过程，所以策略存存贮为按索引遍历的列表不合适，设置为字典更符合实际情况
        self.stratege_type=dict(zip(("m%d"%i for i in range(1,self.n)),self.stratege_type))
        self.stratege1_id=[i for i in self.stratege_type if self.stratege_type[i]==1]  # 选择策略1的男性id
        self.stratege2_id=[i for i in self.stratege_type if self.stratege_type[i]==2]  # 选择策略2的男性id
        self.stratege3_id=[i for i in self.stratege_type if self.stratege_type[i]==3]  # 选择策略3的男性id
        
    def match_simulate(self,male,female):
        '''模拟配对主函数.'''
        # 设置随机策略
        self.set_stratege_type()
        # 创建一个数据框，记录第i轮的匹配结果
        result=pd.DataFrame(columns=['m','f','round_n','stratege_type'])
        round_n=1    # 初始为1轮
        # 设置标记，当某一轮游戏中全部策略均无配对成功，则模拟结束
        flag1=flag2=flag3=True
        
        # 特定策略的匹配函数
        def special_match(round_n,male,female,stratege_id,stratege_type,flag,result=result):
            '''分别进行策略1、2、3的配对模拟.'''
            mf_list=dict()       # 这里以女性id为键，建立字典，值为当前最好的男性匹配对象及其指标均分即：  女性id:[男性id,指标均分]
            
            # 随机分配名额
            round_n_m=male[male.index.isin(stratege_id)].reset_index().rename(columns={'index':'m'})   # 本轮的男性样本数据
            round_n_f=female.reset_index().rename(columns={'index':'f'})                             # 本轮的女性样本数据
            round_n_m['choice']=np.random.choice(female.index.tolist(),len(round_n_m))  # 随机选择女性
            round_n_m['strategy']=round_n_m['m'].apply(lambda x:stratege_type[x])  # 男性策略
            # 连表
            round_n_match=pd.merge(round_n_m,round_n_f,how='left',left_on='choice',right_on='f').reset_index()
            # 按照策略进行选择,获得匹配结果
            round_n_match['match_result']=pd.Series(map(lambda a_x,c_x,f_x,a_y,c_y,f_y,s:self.match_one([a_x,c_x,f_x],[a_y,c_y,f_y],s),round_n_match['外貌_x'],
            round_n_match['内涵_x'],round_n_match['财富_x'],round_n_match['外貌_y'],round_n_match['内涵_y'],round_n_match['财富_y'],round_n_match['strategy']))
            # 修改标记,只要有匹配成功的,标记变为True
            flag=round_n_match['match_result'].sum()
            # 处理那些多名男性选择同一女性的情况,原则是保留综合表现最好的男性
            round_n_match_success=round_n_match[round_n_match['match_result']==True].reset_index()  # 成功配对的结果数据
            for i in round_n_match_success.index:
                if (mf_list.get(round_n_match_success['f'][i])==None) or (mf_list.get(round_n_match_success['f'][i])!=None and float(round_n_match_success["均分_x"][i])>mf_list[round_n_match_success['f'][i]][1]):   # 没有配对，或者已经有配对但新的男性比之前的更优秀,果断抢走！！！
                    mf_list[round_n_match_success['f'][i]]=[round_n_match_success['m'][i],float(round_n_match_success["均分_x"][i])]
        
            # 剔除匹配成功的男性和女性记录
            for f in mf_list:
                if mf_list[f][0] in male.index:
                    male.drop(mf_list[f][0],inplace=True)
                if f in female.index:
                    female.drop(f,inplace=True)
                # 如果有成功配对的，则将数据存入结果数据框中  
                result.loc[len(result)]=[mf_list[f][0],f,round_n,stratege_type[mf_list[f][0]]]  # 男性id,女性id,模拟轮次,策略类型
            stratege_id=[i for i in stratege_id if i not in [mf_list[j][0] for j in mf_list]]  # 去除掉已经匹配到的男性id
            # 返回匹配结束后的数据
            return male,female,stratege_id,result,flag
            
        while (flag1+flag2+flag3):     # 只要有配对成功的就会继续模拟
            time1=time.time()
            flag1=flag2=flag3=False     # 每一轮开始初始化标记,之所以这里设置为False,是因为只要又一次配对,就可以设置为True,实现更方便
            # 策略1的匹配
            #print(">> 策略1——门当户对.")
            male,female,self.stratege1_id,result,flag1=special_match(round_n,male,female,self.stratege1_id,self.stratege_type,flag1)
            # 策略2的匹配
            #print(">> 策略2——男才女貌.")
            male,female,self.stratege2_id,result,flag2=special_match(round_n,male,female,self.stratege2_id,self.stratege_type,flag2)
            # 策略3的匹配
            #print(">> 策略3——志趣相投.")
            male,female,self.stratege3_id,result,flag3=special_match(round_n,male,female,self.stratege3_id,self.stratege_type,flag3)
            time2=time.time()
            if round_n==1 or (round_n<50 and round_n%4==0) or (round_n>50 and round_n%10==0):   # 每4轮打印一次时间
                print(">> 第%d轮模拟结束,用时：%.2fs"%(round_n,time2-time1))
            # 模拟轮次+1
            round_n+=1
        # 返回配对结果 
        return result
        
print(">> 婚恋配对模型准备就绪.")


# 运行模型，获的模拟数据
test=MarriageMatch()
male=test.create_data()   # 男性数据
female=test.create_data(gender='f')  # 女性数据
print(">> %d名男性和%d名女性模拟数据生成."%(test.n,test.n))

############################# 可视化  ##########################################
# 分布图
def plot_hist(df,title='内涵服从正态分布'):
    fig=plt.figure(figsize=(8,4))
    ax=fig.add_subplot(111)
    df.hist(bins=20,edgecolor='black',ax=ax)
    plt.grid(linestyle='--')
    plt.title(title)
    plt.savefig('./img/%s'%title,dpi=100)
# 内涵
plot_hist(male["内涵"])
# 外貌
plot_hist(male["外貌"],"外貌服从正态分布")
# 财富
plot_hist(male["财富"],"财富服从指数分布")
print(">> 3项指标的分布图导出完成.")

# 查看n名男性和女性的指标图
def plot_bar(df,n=50,gender='男性'):
    fig=plt.figure(figsize=(10,4))
    ax=fig.add_subplot(111)
    df.plot(kind='bar',stacked=True,colormap='Blues_r' if gender=='男性' else 'Oranges_r',
            edgecolor='black',ax=ax)
    plt.legend(ncol=3)
    plt.title('%d名%s3项指标分值.'%(n,gender))
    plt.xticks(rotation=45)
    plt.savefig('./img/%d名%s3项指标分值.png'%(n,gender),dpi=100)
# 男性
plot_bar(male.iloc[:50,:-1])
# 女性
plot_bar(female.iloc[:50,:-1],gender='女性')
print(">> 50名男性、女性3项指标的柱状图导出完成.")

###############################################################################
############################ 任务2 构建择偶策略算法 ##############################
##############################################################################
print("\n>>>>>>>>>>>>> 任务2 构建择偶策略算法 <<<<<<<<<<<<\n")
filename="./data/match_result_9999.csv"
n,N=99,101
if os.path.exists(filename):
    result=pd.read_csv(filename,engine="python",encoding="utf-8")
    print(">> 本地数据%s读取完成,共%d行"%(filename.replace("./data/","").replace(".csv",''),result.shape[0]))
else:
    time1=time.time()
    result=pd.DataFrame()
    # 生成99个男女的数据
    test=MarriageMatch(n=n*N,randoms=True)     # 真随机
    male_99=test.create_data()   # 男性数据
    female_99=test.create_data(gender='f')  # 女性数据
    print(">> %d名男性和%d名女性模拟数据生成,开始模拟实验:"%(test.n,test.n))
    result1=test.match_simulate(male_99.copy(),female_99.copy())  # 择偶模拟结果
    # 匹配数据，为每个男性、女性补充三项指标的分值
    result1=pd.merge(result1,male_99,how='left',left_on='m',right_index=True)
    result1=pd.merge(result1,female_99,how='left',left_on='f',right_index=True)
    result=pd.concat([result,result1])
    time2=time.time()
    print('婚恋模拟结束,总用时：%.2fs'%(time2-time1))
    # 保存数据
    result.to_csv(filename,index=False,encoding="utf-8")
# 各个策略的均值
stratege_mean=result[["stratege_type","财富_x","内涵_x","外貌_x"]].groupby(by="stratege_type").mean()
stratege_mean.index=["择偶策略"+str(i) for i in stratege_mean.index]
stratege_mean.columns=[i.strip('_x')+"均值" for i in stratege_mean.columns]
#stratege_type=test.stratege_type    # 择偶策略
print('''%.2f%%的样本数据匹配到了对象.
----------------
择偶策略1的匹配成功率为为%.2f%%.
择偶策略2的匹配成功率为为%.2f%%.
择偶策略3的匹配成功率为为%.2f%%.

----------------
择偶策略1的男性 ——> 财富均值为%.2f,内涵均值为%.2f,外貌均值为%.2f.
择偶策略2的男性 ——> 财富均值为%.2f,内涵均值为%.2f,外貌均值为%.2f.
择偶策略3的男性 ——> 财富均值为%.2f,内涵均值为%.2f,外貌均值为%.2f.'''%(len(result)/(n*N)*100,
len(result[result["stratege_type"]==1])/(n/3*N)*100,len(result[result["stratege_type"]==2])/(n/3*N)*100,
len(result[result["stratege_type"]==3])/(n/3*N)*100,stratege_mean.loc["择偶策略1","财富均值"],
stratege_mean.loc["择偶策略1","内涵均值"],stratege_mean.loc["择偶策略1","外貌均值"],
stratege_mean.loc["择偶策略2","财富均值"],stratege_mean.loc["择偶策略2","内涵均值"],
stratege_mean.loc["择偶策略2","外貌均值"],stratege_mean.loc["择偶策略3","财富均值"],
stratege_mean.loc["择偶策略3","内涵均值"],stratege_mean.loc["择偶策略3","外貌均值"]))
################################## 可视化 ######################################
# 箱型图
fig,ax=plt.subplots(1,3,sharey=True,figsize=(9,6))
# 绘图函数
def plot_box(df,title,fig,ax_id):
    #ax=fig.add_subplot(1,3,ax_id)
    sns.boxplot(x="stratege_type",y=title,data=df,ax=ax_id)
    #plt.xticks(rotation=45)
    ax_id.set_xticklabels(['门当户对','男才女貌','志趣相投'])
    ax_id.set_xlabel('')
    ax_id.set_ylabel('')
    ax_id.set_title(title.strip('_x'))
# 分别绘制子图
plot_box(result[["stratege_type","财富_x"]],"财富_x",fig,ax[0])
plot_box(result[["stratege_type","内涵_x"]],"内涵_x",fig,ax[1])
plot_box(result[["stratege_type","外貌_x"]],"外貌_x",fig,ax[2])
plt.tight_layout()
plt.savefig('./img/不同择偶策略的男性三项指标箱型图.png',dpi=100)
print(">> 不同择偶策略的男性指标箱型图绘制完成.")

###############################################################################
############################ 任务3 匹配折线图 ###################################
##############################################################################
print("\n>>>>>>>>>>>>> 任务3 匹配折线图 <<<<<<<<<<<<\n")
filename="./data/match_result_99_line.csv"
if os.path.exists(filename):
    df=pd.read_csv(filename,engine="python",encoding="utf-8")
    print(">> 本地数据%s读取完成,共%d行"%(filename.replace("./data/","").replace(".csv",''),df.shape[0]))
else:
    import copy
    test=MarriageMatch(n=99,randoms=True)     # 真随机
    male_99=test.create_data()   # 男性数据
    female_99=test.create_data(gender='f')  # 女性数据
    print(">> %d名男性和%d名女性模拟数据生成,开始模拟实验:"%(test.n,test.n))
    result1=test.match_simulate(copy.deepcopy(male_99),copy.deepcopy(female_99))  # 择偶模拟结果
    # 匹配数据，为每个男性补充三项指标的分值
    # 男性均分
    result1=pd.merge(result1,female_99,how='left',left_on='f',right_index=True).rename(columns={"均分":"score_x"})
    # 女性均分
    result1=pd.merge(result1[['m','f','round_n','stratege_type','score_x']],male_99,how='left',left_on='m',right_index=True).rename(columns={"均分":"score_y"})
    # 只选择前4轮的配对结果
    df=result1[result1["round_n"]<=4][['m','f','round_n','stratege_type','score_x',
       'score_y']]
    # 调色盘
    from bokeh.palettes import brewer
    n = 6
    colormap2 = brewer['Blues'][n]
    # 颜色
    df["color"]=df["round_n"].apply(lambda x:colormap2[x-1])
    df.to_csv(filename,index=False,encoding="utf-8")

################################## 可视化  #####################################
from bokeh.plotting import figure,show,output_file

output_file("./html/配对实验过程模拟示意.html")

TOOLS = ["pan,wheel_zoom,save,reset"]   # 横向拉伸

# 转化为ColumnDataSource对象
# 这里注意了，index和columns都必须有名称字段
# 设置坐标
# 男性坐标
df["x"]=df["f"].apply(lambda x:[0,int(str(x).strip("f")),int(str(x).strip("f"))])
# 女性坐标
df["y"]=df["m"].apply(lambda x:[int(str(x).strip("m")),int(str(x).strip("m")),0])

p = figure(x_range=[-4,100],y_range=[-4,100],plot_width=700, plot_height=700,
           tools=TOOLS,
           toolbar_location='right',     # 工具栏位置："above"，"below"，"left"，"right"
           x_axis_label = '女性ID', y_axis_label = '男性ID',    
           title="配对实验过程模拟示意")

# 设置数据
for i in df.values:
    # 绘制折线
    p.line(i[-2],i[-1],legend="round %d"%i[2],line_color=i[-3], line_dash=[8,2], line_width=2)
    # 绘制点
    p.circle(i[-2],i[-1],legend="round %d"%i[2],color=i[-3],size=5)
    
# 网格设置
p.ygrid.grid_line_alpha = 0.6
p.ygrid.grid_line_dash = "dashed"
p.xgrid.grid_line_alpha = 0.6
p.xgrid.grid_line_dash = "dashed"     
p.legend.location = "top_right"
p.legend.click_policy="hide"
 
show(p)
        
###############################################################################
######################## 任务4 不同类型男女配对成功率 #############################
##############################################################################
print("\n>>>>>>>>>>>>> 任务4 不同类型男女配对成功率 <<<<<<<<<<<<\n")
filename='./data/match_result_9999_types.csv'
if os.path.exists(filename):
    df=pd.read_csv(filename,engine="python",encoding="utf-8")
    print(">> 本地数据%s读取完成,共%d行"%(filename.replace("./data/","").replace(".csv",''),df.shape[0]))
else:
    # 数据分箱
    def to_type(df,bins=[0,50,70,100],labels=['低','中','高'],types='财'):
        df_new=pd.cut(df,bins=bins,labels=[types+i for i in labels]).astype(str)
        df_new=df_new.str.replace('nan','%s高'%types)
        return df_new
    # 划分类别
    for i in [('财富','财'),('内涵','品'),('外貌','颜')]:
        result['%s_m'%i[0]]=to_type(result['%s_x'%i[0]],types=i[1])  # 男性
        result['%s_f'%i[0]]=to_type(result['%s_y'%i[0]],types=i[1])  # 女性
    # 合并三个指标
    result['type_m']=result['财富_m']+result['内涵_m']+result['外貌_m']  # 男性
    result['type_f']=result['财富_f']+result['内涵_f']+result['外貌_f']  # 男性    
    # 保留指定的数据
    df=result[['type_m','type_f','m','f']].copy()   
    df['type_mf']=result['type_m']+result['type_f']    
    # 计算匹配成功率——>即每种组合的占比情况
    type_pnt=df['type_mf'].value_counts().reset_index().rename(columns={'type_mf':'chance'})
    df=pd.merge(df,type_pnt,how='left',left_on='type_mf',right_on='index')        
    df['chance']=df['chance']/len(df)        
    # 设置透明度
    df['alpha']=(df['chance']-df['chance'].min())/(df['chance'].max()-df['chance'].min())*8        
    # 保存数据
    df=df[['type_m','type_f','chance','alpha']].drop_duplicates()
    df.to_csv(filename,index=False,encoding='utf-8')
    
################################### 可视化 ########################################
from bokeh.plotting import figure,show,output_file

output_file("./html/不同男女类型配对成功率.html")

from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool

# 设置范围
df['type_m']=df[['type_m']].astype(str)
df['type_f']=df[['type_f']].astype(str)
mlst = df['type_m'].value_counts().index.tolist()
flst = df['type_f'].value_counts().index.tolist()

source = ColumnDataSource(df)

hover = HoverTool(tooltips=[
                            ("男性类别", "@type_m"),
                            ("男性类别", "@type_f"),
                            ("匹配成功率", "@chance")
                        ])


p = figure(x_range=mlst,y_range=flst,plot_width=700, plot_height=700,
           tools=[hover,'reset,wheel_zoom,pan,lasso_select,crosshair'],
           toolbar_location='right',     # 工具栏位置："above"，"below"，"left"，"right"
           x_axis_label = '男', y_axis_label = '女',    # X,Y轴label
           title="不同男女类型配对成功率"                       # 设置图表title
           )
p.square_cross(x = 'type_m',y = 'type_f',source=source,size=18,
         color = 'red',alpha = 'alpha') # 填充的颜色、透明度

p.ygrid.grid_line_dash = [6, 4]
p.xgrid.grid_line_dash = [6, 4]
p.xaxis.major_label_orientation = "vertical"

show(p)

print(">> 项目14 婚恋模拟实验全部任务完成.")



