# 基于Python的数据分析实战项目
详细介绍了数十个数据分析相关的实战项目,大量使用pandas、numpy、matplotlib、seaborn以及bokeh等包,少量涉及sklearn中机器学习相关包,对一些诸如蒙特卡罗模拟思想使用代码加以实现,并详细讲述实现细节以及注意要点。
# 目录

* [1 项目1 商铺数据加载及存储](#1项目1-商铺数据加载及存储)
   * [1.1 项目要求](#11-项目要求)
   * [1.2 原始数据展示](#12-原始数据展示(部分))
   * [1.3 实际操作](#13-实际操作)

## 1 项目1 商铺数据加载及存储

### 1.1 项目要求
1. 成功读取“商铺数据.csv”文件
2. 解析数据，存成列表字典格式：[{'var1':value1,'var2':value2,'var3':values,...},...,{}]
3. 数据清洗：
    * comment，price两个字段清洗成数字
    * 清除字段缺失的数据
    * commentlist拆分成三个字段，并且清洗成数字
4. 结果存为.pkl文件

### 1.2 原始数据展示(部分)
通过爬虫在某点评APP上获取一下店铺数据,包含了7个字段,字段名及其对应的含义分别是：classify(店铺类别),name(店铺名),comment(点评人数),star(星级),price(平均消费),address(地址),commentlist(特定指标评分),以下为部分数据展示：

classify | name | comment | star | price | address | commentlist
----- | ----- | ----- | ----- | ----- | ----- | -----
美食 | 望蓉城老坛酸菜鱼(合生汇店)	| 我要点评 | 该商户暂无星级 | 人均 ￥125 | 翔殷路1099号合生汇5F |	口味8.3 环境8.4 服务8.5
美食 | 泰国街边料理 | 74 条点评 | 准四星商户 | 人均 ￥48 | 黄兴路合生汇B2美食集市内 | 口味7.4 环境7.6 服务7.4
美食 | 壹面如故(苏宁生活广场店) | 265 条点评 | 准四星商户 | 人均 ￥21 | 邯郸路585号苏宁生活广场B1层 | 口味7.0 环境7.2 服务7.2

因为直接获取回来的数据并未进行数据清洗,因此存在以下几个问题：
1. 文本数据存在多余的空格(或不可显示的制表符等),需要清除;
2. 部分可以量化的指标需要转化为数值格式如星级等,另外平均消费字段中的价格也有多余的文本信息需要删除;
3. 可选操作：通过将csv文件转存为pkl文件,不仅可以减少文件大小还可以一定程度对文件内容进行加密。

### 1.3 实际操作

**1. 读取数据**

基于python有多种文件读取方式,其中较为常用的读取文本数据的方式如下所示：
```python
with open(文件路径,'r',encoding='utf-8') as f:
    for i in f.readlines():
        print(i)
```
其中第二个参数是指定文件操作方式：r(读取,rb二进制文件读取),w(写入,wb二进制文件写入),encoding参数为文件编码格式,一般包含中文的都选用'utf-8'编码格式。

另一种读取文件的方式是采用pandas提供的读取csv、xlsx等表格文件的方式:pd.read_csv(),pd.read_excel(),此外pandas还包含多种读取文件的方式如pd.read_sql()可以直接从数据库读取特定sql查询结果的数据,这里不做展开。

本项目我们采用read_csv方式快速读取原始数据,由于windows系统打开csv文件时会在文件开头添加一些字符,因此如果在用Python读取文件前打开过原始数据,则再次读取数据后第一个字段名就不再是原来的字段了,比如说第一个字段名是classify,那么在windows上使用office等软件打开过一次的文件第一个字段名将不再是 classify
,而是前面还有一个字符,因此我们应该尽量避免直接打开csv文件,或者在读取文件后重命名字段列表,如下所示：

```python
import os
import pandas as pd
os.chdir(os.getcwd())
data=pd.read_csv("商铺数据.csv",encoding="utf-8")
data.columns=['classify', 'name', 'comment', 'star', 'price', 'address',
       'commentlist']
print(data.head())
```
代码中的os.chdir(os.getcwd())作用是将工作路径设置为脚本所在绝对路径,这在项目所在文件夹进行移动复制的时候尤为管用,不论文件夹在何处,只要文件夹内各文件与脚本的相对位置不变,脚本都可以正确执行,而不用手工设置工作路径。

**2. 数据清洗**

这里的数据清洗与一般意义上的去除异常值、处理缺失值等不同,更偏向于文本数据的清洗,即将文本数据整理地更规整便于后续分析使用,这里我将按照不同的处理方式分别定义匿名函数，具体代码如下所示：

(1) 直接去除多余空格,其实本例更为简单的做法是使用pandas数据框自带的方法,df['字段1'].str.replace(' ',''),处理效果与使用apply函数调用以下匿名函数完全相同:
```python
# 简单清洗，去除多余的空格
remove_blank=lambda x:str(x).replace(" ","")   # 简单删除空格
```
(2) 提取评论人数,涉及字符串分割知识即str.split(特定字符):
```python
# 清洗评论人数
remove_blank_com=lambda x:int(str(x).replace(" ","").split("条")[0]) if "条" in str(x) else None     # 提取评论人数
```
(3) 这里想法是将中文一到五转化为阿拉伯数字1到5,并不考虑准N星与N星的区别,即星级只有整数无小数情况,具体实现过程为构建一一对应的字典,并将原始数据与字典的键进行匹配:
```python
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
```
(4) 清洗价格主要是提取文本信息中的数字部分,并剔除货币符号:
```python
# 清洗价格
remove_blank_pri=lambda x:round(float(str(x).replace(" ","").split("￥")[1]),2) if "￥" in str(x) else None   # 提取价钱
```
除了以下的实现方式外,还可以考虑使用正则表达式进行匹配,如:
```python
import re
pattern_price=re.compile(r'\d+\.*\d+')     # 提取价格,包含整数和小数形式
remove_blank_pri=lambda x:round(float(pattern_price.findall(x)[0]),2) if pattern_price.findall(x) else None   # 提取价钱
```
(5) 点评详情数据中有大量多余空格并且数量不一致,因此可以通过以下匿名函数实现清洗工作,该函数为经验得到无特殊思路:
```python
# 清洗点评详情
remove_blank_comlist=lambda x:str(x).replace("   ","").replace("  ",",").replace(",,",",")
```
定义完匿名函数,通过apply函数即可轻松将其应用到整个数据框中,最后再去除缺失值即可,调用方法如下所示:
```python
# 清洗 'classify', 'name', 'address'
data[['classify', 'name', 'address']]=data[['classify', 'name', 'address']].applymap(remove_blank)
data["comment"]=data["comment"].apply(remove_blank_com)
data["star"]=data["star"].apply(remove_blank_star)
data["price"]=data["price"].apply(remove_blank_pri)
data["commentlist"]=data["commentlist"].apply(remove_blank_comlist)

# 清除缺失值
data.dropna(inplace=True)
data.index=range(data.shape[0])
```

**3. 拆分点评字段**

我们注意到commentlist(点评字段)包含了3个评分,因此我们需要将其拆分,为简化处理至设置3个指标——口味、环境和服务,具体代码如下所示：

```python
# 拆分点评数据
data["口味"]=pd.Series(map(lambda x:round(float(str(x).split(",")[0][2:]),1),data["commentlist"]))   # 常数不可迭代，因此不能将 0,1,2作为参数传入lambda
data["环境"]=pd.Series(map(lambda x:round(float(str(x).split(",")[1][2:]),1),data["commentlist"]))
data["服务"]=pd.Series(map(lambda x:round(float(str(x).split(",")[2][2:]),1),data["commentlist"]))
#data=data[['classify', 'name', 'comment', 'star', 'price', 'address',"口味","环境","服务"]]
print(data.head())
```
或者采用以下更为简洁的形式,其中enumerate()为枚举类型,返回结果为一个元组——(index,value),代表了索引位置和实际值:

```python
def new_comm(x,i=0):
    # 以逗号分割，取第i个，再截取3位之后的数字并转换数据类型
    return float(str(x).split(",")[i][2:])
for j,col in enumerate(['口味','环境','服务']):
    data[col]=data["commentlist"].apply(new_comm,i=j)
```

**4. 解析数据**

最后解析数据较为简单,即将数据框转换为Json格式再转存pkl文件,Json格式的数据可以看做是字典列表,是网页数据常见的数据结构,具体实现过程如下：

```python
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
```
