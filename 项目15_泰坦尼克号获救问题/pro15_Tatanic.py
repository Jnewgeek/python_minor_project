# -*- coding: utf-8 -*-
"""
Created on Fri May 24 19:58:07 2019

@author: HASEE
项目15：泰坦尼克号获救问题
"""
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
os.chdir(r"F:\pythondata\Python微专业\【非常重要】课程资料\python_minor_project\项目7_15\项目15泰坦尼克号获救问题")
# 创建文件夹
for i in ["./data","./img"]:
    if not os.path.exists(i):
        os.mkdir(i)
########################################################################################
################################# 任务1 存活情况 ########################################
########################################################################################
print("             《项目15：泰坦尼克号获救问题》\n")
print(">>>>>>>>>>>>>>     任务1 存活情况         <<<<<<<<<<<<<<\n")
train=pd.read_csv('./data/train.csv',engine='python',encoding='utf-8')
# 可视化存活情况
s=train.Survived.value_counts()
fig=plt.figure()
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
plt.title('存活占比')
plt.savefig("./img/存活占比.png",dpi=200)

########################################################################################
################################# 任务2 分析原因 ########################################
########################################################################################
print(">>>>>>>>>>>>>>     任务2 分析原因         <<<<<<<<<<<<<<\n")
# 年龄分布
age_des=train[train.Age.notnull()]['Age'].describe()
print(">> 总体年龄分布: 去掉缺失值后样本有%d个,平均年龄约为%d岁,标准差为%d岁,最小年龄为%.2f岁,最大年龄为%d岁."%(len(train[train.Age.notnull()]),
                    int(age_des['mean']),int(age_des['std']),float(age_des['min']),int(age_des['max'])))
print('-'*40)
print(age_des)

# 直方图和箱型图
fig=plt.figure()
train[train.Age.notnull()]['Age'].hist(bins=40)
plt.title('年龄分布直方图')
plt.savefig('./img/年龄分布直方图.png',dpi=200)
# 
fig=plt.figure()
train[train.Age.notnull()][['Age']].boxplot()
plt.title('年龄分布箱型图')
plt.savefig('./img/年龄分布箱型图.png',dpi=200)

# 男性和女性的存活情况
train_gender=train[(train.Sex.notnull())&(train.Survived.notnull())][['Sex','Survived']]
train_gender['num']=1
gender_sur=train_gender.groupby(by=['Sex','Survived']).sum()
print('>> 不同性别的存活情况:\n')
print('-'*40)
print(gender_sur)
fig=plt.figure()
sns.barplot(x='Sex',y='num',hue='Survived',data=gender_sur.reset_index())
plt.ylabel('')
plt.xlabel('')
plt.title('不同性别的存活情况')
plt.savefig('./img/不同性别的存活情况.png',dpi=200)
female_cnt=gender_sur.loc[('female',1)]/(gender_sur.loc[('female',0)]+gender_sur.loc[('female',1)])
male_cnt=gender_sur.loc[('male',1)]/(gender_sur.loc[('male',0)]+gender_sur.loc[('male',1)])
print('>> 女性存活率为%.2f%%,男性存活率为%.2f%%'%(float(female_cnt)*100,float(male_cnt)*100))

# 按照船仓级和不同性别的年龄小提琴图
fig,ax=plt.subplots(1,2,figsize=(12,6))
train_pclass_age=train[(train.Pclass.notnull())&(train.Survived.notnull())&(train.Age.notnull())][['Pclass','Survived','Age']]
train_sex_age=train[(train.Sex.notnull())&(train.Survived.notnull())&(train.Age.notnull())][['Sex','Survived','Age']]
sns.violinplot(x='Pclass',y='Age',hue='Survived',data=train_pclass_age,split=True,inner="quartile",ax=ax[0])
ax[0].set_title('Pclass and Ages V/S Survived')
sns.violinplot(x='Sex',y='Age',hue='Survived',data=train_sex_age,split=True,inner="quartile",ax=ax[1])
ax[1].set_title('Sex and Ages V/S Survived')
plt.savefig('./img/不同因素的年龄分布.png',dpi=200)

print('>> 按照不同船舱等级划分 ——> 船舱等级越高,存活者年龄越大,船舱等级1存活者年龄集中在20-40岁,船舱等级2/3中有较多年龄较小的存活者.')
print('>> 按照性别划分 ——> 男性女性存活者年龄主要分布在20-40岁,且均有较多年龄较小的乘客,其中女性存活更多.')

# 不同年龄的存活情况
fig=plt.figure(figsize=(18,6))
ax=fig.add_subplot(111)
data=train[(train.Survived.notnull())&(train.Age<=80)][['Survived','Age']]
data['Age']=data['Age'].apply(int)
data['num']=1
age_survived=data.groupby(by='Age').sum()
age_survived['pnt']=age_survived['Survived']/age_survived['num']
sns.barplot(x='Age',y='pnt',data=age_survived.reset_index(),ax=ax)
plt.title('不同年龄的存活率')
plt.savefig('./img/不同年龄的存活率.png',dpi=200)

print('>> 灾难中,老人和小孩更容易活下来.')

########################################################################################
########################## 任务3 亲人数量与存活关系 #####################################
########################################################################################
print(">>>>>>>>>>>>>>     任务3 亲人数量与存活关系         <<<<<<<<<<<<<<\n")

# 饼图
train_sibsp_parch=train[(train.SibSp.notnull())&(train.Parch.notnull())][['SibSp','Parch','Survived']]
train_sibsp_parch['SibSp']=train_sibsp_parch['SibSp'].apply(lambda x:'sibsp' if x>0 else 'no_sibsp')
train_sibsp_parch['Parch']=train_sibsp_parch['Parch'].apply(lambda x:'parch' if x>0 else 'no_parch')
train_sibsp_parch['Survived']=train_sibsp_parch['Survived'].apply(lambda x:'Survived' if x==1 else 'No Survived')

def plot_pie(data,col,c,ax,colors=['white','blue']):
    s1=data[data[col]==c]['Survived'].value_counts()
    s1=s1/s1.sum()

    plt.axis('equal')  # 保证长宽相等
    ax.pie(s1, explode = [0.1]+[0.02]*(len(s)-1),        # 设置偏移
       labels = s1.index,autopct='%.1f%%',
       colors = colors,wedgeprops = { 'linewidth': 0.2, 'edgecolor': 'black'},
       pctdistance=0.6,labeldistance = 1.05,
       shadow = False,radius=1,frame=False)
    ax.set_title(c)

fig,ax=plt.subplots(1,4,figsize=(16,4))
# 兄弟姐妹
plot_pie(train_sibsp_parch,'SibSp','sibsp',ax[0])
plot_pie(train_sibsp_parch,'SibSp','no_sibsp',ax[1])
# 父母
plot_pie(train_sibsp_parch,'Parch','parch',ax[2],['#FDF5E6','#8B008B'])
plot_pie(train_sibsp_parch,'Parch','no_parch',ax[3],['#FDF5E6','#8B008B'])

plt.tight_layout()
plt.savefig('./img/亲人与存活的关系.png',dpi=200)

################# 兄弟姐妹数量 父辈人数与存活率的关系
train_sibsp_parch_num=train[(train.SibSp.notnull())&(train.Parch.notnull())][['SibSp','Parch','Survived']]
train_sibsp_parch_num['num']=1
train_sibsp_parch_num['family_size']=train_sibsp_parch_num['SibSp']+train_sibsp_parch_num['Parch']
# 兄弟姐妹人数
train_sibsp_parch_num_1=train_sibsp_parch_num[['Parch','Survived','num']].groupby(by='Parch').sum()
train_sibsp_parch_num_1['pnt']=train_sibsp_parch_num_1['Survived']/train_sibsp_parch_num_1['num']
# 父辈
train_sibsp_parch_num_2=train_sibsp_parch_num[['SibSp','Survived','num']].groupby(by='SibSp').sum()
train_sibsp_parch_num_2['pnt']=train_sibsp_parch_num_2['Survived']/train_sibsp_parch_num_2['num']
# 家庭成员
train_sibsp_parch_num_3=train_sibsp_parch_num[['family_size','Survived','num']].groupby(by='family_size').sum()
train_sibsp_parch_num_3['pnt']=train_sibsp_parch_num_3['Survived']/train_sibsp_parch_num_3['num']

#### 可视化
fig=plt.figure(figsize=(12,8))
# 兄弟姐妹
ax1=fig.add_subplot(2,2,1)
train_sibsp_parch_num_1['pnt'].plot(kind='bar',ax=ax1)
ax1.set_title('Parch and Survived')
# 父辈
ax2=fig.add_subplot(2,2,2)
train_sibsp_parch_num_2['pnt'].plot(kind='bar',ax=ax2)
ax2.set_title('SibSp and Survived')
# 家庭成员
ax3=fig.add_subplot(2,1,2)
train_sibsp_parch_num_3['pnt'].plot(kind='bar',ax=ax3)
ax3.set_title('FamilySize and Survived')

plt.tight_layout()
plt.savefig('./img/亲属与存活的关系.png',dpi=200)

print('若独自一人其存活率较低,但亲友数量太多存活率也较低.')


########################################################################################
########################## 任务4 票价与存活的关系 #######################################
########################################################################################
print(">>>>>>>>>>>>>>     任务4 票价与存活的关系         <<<<<<<<<<<<<<\n")
# 票价分布
fig=plt.figure(figsize=(12,8))
ax1=fig.add_subplot(2,2,1)
train['Fare'].dropna().hist(bins=40,ax=ax1)
ax1.set_title('Fare Hist')

# 去除异常值
fare=train['Fare'].dropna().describe()
iqr=fare.loc['75%']-fare.loc['25%']
mean=fare.loc['mean']
train_fare=train[(train['Fare']>mean-3*iqr)&(train['Fare']<mean+3*iqr)]
print('>> 原始票价数据共%d行,去除异常值后剩余%d行.'%(len(train['Fare'].dropna()),len(train_fare)))

# 不同等级船舱的票价箱型图
ax2=fig.add_subplot(2,2,2)
sns.boxplot(x='Pclass',y='Fare',data=train_fare[['Pclass','Fare']],ax=ax2)
ax2.set_title('Fare by Pclass')
ax2.set_xlabel('')
ax2.set_ylabel('')
# 生还情况与票价的关系
ax3=fig.add_subplot(2,1,2)
sns.boxplot(x='Survived',y='Fare',data=train_fare[['Survived','Fare']],ax=ax3)
ax3.set_title('Fare by Pclass')
ax3.set_xlabel('')
ax3.set_ylabel('')

plt.tight_layout()
plt.savefig('./img/票价与存活的关系.png',dpi=200)

########################################################################################
########################## 任务5 KNN 预测生还情况 #######################################
########################################################################################
print(">>>>>>>>>>>>>>     任务5 KNN 预测生还情况         <<<<<<<<<<<<<<\n")
# 票价分布
train['Family_Size']=train['SibSp']+train['Parch']
train_knn=train[['Survived','Pclass','Sex','Age','Fare','Family_Size']].dropna()
train_knn['Sex']=train_knn['Sex'].apply(lambda x:1 if x=='male' else 0)
print('>> 训练数据共%d行.'%len(train_knn))

# 读取测试数据
test=pd.read_csv('./data/test.csv',engine='python',encoding='utf-8')
test['Family_Size']=test['SibSp']+test['Parch']
test_knn=test[['PassengerId','Pclass','Sex','Age','Fare','Family_Size']]
test_knn['Sex']=test_knn['Sex'].apply(lambda x:1 if x=='male' else 0)
# 查看缺失值,填补缺失值
print("缺失值情况:")
print(test_knn.isnull().sum())
# 填补的缺失值
female_meanage=test_knn[test_knn.Sex==0]['Age'].dropna().mean()   # 女性平均年龄
male_meanage=test_knn[test_knn.Sex==1]['Age'].dropna().mean()
print('>> 男女的平均年龄差不多,因此用平均年龄填补缺失值.')
# 年龄 
test_knn.Age.fillna(int(male_meanage),inplace=True)
# 票价填补缺失值
fare_na=test_knn[test_knn.Fare.isnull()]
print(">> 缺失票价的乘客位于3级船舱,填补该等级船舱的平均票价")
test_knn.Fare.fillna(int(test_knn[test_knn.Pclass==3]['Fare'].mean()),inplace=True)

print('>> 测试数据共%d行.'%len(test_knn))

##################################  knn 分类预测  ######################################
from sklearn import neighbors  # 导入KNN分类模块
import warnings
warnings.filterwarnings('ignore') 

knn = neighbors.KNeighborsClassifier()   # 取得knn分类器
knn.fit(train_knn[['Pclass','Sex','Age','Fare','Family_Size']], train_knn['Survived'])
# 建立分类模型
test_knn['Survived']=knn.predict(test_knn[['Pclass','Sex','Age','Fare','Family_Size']])

#导出预测结果
test_knn[['PassengerId','Survived']].to_csv('./data/knn预测结果.csv',index=False,encoding='utf-8')

print('项目15 全部完成.')
































