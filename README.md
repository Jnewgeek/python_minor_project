# 基于Python的数据分析实战项目
详细介绍了数十个数据分析相关的实战项目,大量使用pandas、numpy、matplotlib、seaborn以及bokeh等包,少量涉及sklearn中机器学习相关包,对一些诸如蒙特卡罗模拟思想使用代码加以实现,并详细讲述实现细节以及注意要点。
# 目录

* [1 商铺数据加载及存储](#1-商铺数据加载及存储)
   * [1.1 项目要求](#11-项目要求)
   * [1.2 原始数据展示](#12-原始数据展示)
   * [1.3 实际操作](#13-实际操作)
      * [1.3.1 读取数据](#131-读取数据)
      * [1.3.2 数据清洗](#132-数据清洗)
      * [1.3.3 拆分点评字段](#133-拆分点评字段)
      * [1.3.4 解析数据](#134-解析数据)
* [2 基于Python的算法函数创建](#2-基于Python的算法函数创建)
   * [2.1 项目要求](#2.1-项目要求)
   * [2.2 习题](#2.2-习题)
      * [2.2.1 无重复数字](#2.2.1-无重复数字)
      * [2.4.2 排序](#2.4.5-排序)
      * [2.2.3 统计字符个数](#2.2.3-统计字符个数)
      * [2.2.4 猴子吃桃问题](#2.2.4-猴子吃桃问题)
      * [2.4.5 猜数字问题](#2.4.5-猜数字问题)

## 1 商铺数据加载及存储

### 1.1 项目要求
1. 成功读取“商铺数据.csv”文件
2. 解析数据，存成列表字典格式：[{'var1':value1,'var2':value2,'var3':values,...},...,{}]
3. 数据清洗：
    * comment，price两个字段清洗成数字
    * 清除字段缺失的数据
    * commentlist拆分成三个字段，并且清洗成数字
4. 结果存为.pkl文件

### 1.2 原始数据展示
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

#### 1.3.1 读取数据

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

#### 1.3.2 数据清洗

这里的数据清洗与一般意义上的去除异常值、处理缺失值等不同,更偏向于文本数据的清洗,即将文本数据整理地更规整便于后续分析使用,这里我将按照不同的处理方式分别定义匿名函数，具体代码如下所示：

(1) 直接去除多余空格,其实本例更为简单的做法是使用pandas数据框自带的方法,df['字段1'].str.replace(' ',''),处理效果与使用apply函数调用以下匿名函数完全相同:
```python
# 简单清洗，去除多余的空格
remove_blank=lambda x:str(x).replace(" ","")   # 简单删除空格
```
<br/>
(2) 提取评论人数,涉及字符串分割知识即str.split(特定字符):
```python
# 清洗评论人数
remove_blank_com=lambda x:int(str(x).replace(" ","").split("条")[0]) if "条" in str(x) else None     # 提取评论人数
```
<br/>
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
<br/>
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
<br/>
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

#### 1.3.3 拆分点评字段

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

#### 1.3.4 解析数据

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

[项目链接](https://github.com/Jnewgeek/python_minor_project/tree/master/%E9%A1%B9%E7%9B%AE1_%E5%95%86%E9%93%BA%E6%95%B0%E6%8D%AE%E5%8A%A0%E8%BD%BD%E5%8F%8A%E5%AD%98%E5%82%A8 "商铺数据加载及存储")<br/>
[返回目录](#目录 "返回目录")


## 2 基于Python的算法函数创建

### 2.1 项目要求
1. 根据题意完成函数的创建实现相应的功能。

### 2.2 习题

#### 2.2.1 无重复数字 
有1、2、3、4共四个数字，能组成多少个互不相同且无重复数字的两位数？都是多少？

排列组合公式:<br/>
$$ C_{4}^2 = 12 $$


代码实现(构建集合,嵌套循环):
```python
num=set()
for i in range(1,5):
    for j in range(1,5):
        num.add(i*10+j)

print("互不相同的两位数个数: ",len(num))
print("分别是: \n",sorted(num))
```

#### 2.2.2 排序
输入三个整数x,y,z，请把这三个数由小到大输出。
> 提示：判断是否为数字：.isdigit()
> 该题目需要创建函数


代码实现:
```python
def my_sort(x,y,z):
    '''
    从小到大
    '''
    if x.isdigit() and y.isdigit() and z.isdigit():
        x,y,z=int(x),int(y),int(z)
        if y<=x:
            x,y=y,x
        if z<=x:
            x,z=z,x
        if z<=y:
            y,z=z,y
        return x,y,z
    else:
        return None,None,None

xx=input("请输入3个整数(','隔开):").split(",")
x,y,z=my_sort(xx[0],xx[1],xx[2])
if x==None:
    print("输入数据格式错误!")
else:
    print("从小到大输出为: %d,%d,%d"%(x,y,z))
```

#### 2.2.3 统计字符个数
输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。
字符类型判断函数:
1. is.alpha() 是否是字母
2. is.digit() 是否是数字
3. 正则表达式: 
    * '\d'(数字)等价于[0-9],'\D'(非数字)
    * '\w'(字母或数字或下划线或汉字,能否显示汉字取决于操作系统)等价于,'\W'(非可显示字符)
    * '\s'(空白字符),'\S'(非空白字符)

代码实现:
```python
def count_str(x):
    # 字母个数
    alpha_cnt=sum(i.isalpha() for i in x)
    # 空格
    blank_cnt=sum(i==" " for i in x)
    # 数字
    digit_cnt=sum(i.isdigit() for i in x)
    # 其他
    others_cnt=len(x)-alpha_cnt-blank_cnt-digit_cnt
    print('''
    总个数: %d
    字母个数: %d
    空格个数: %d
    数字个数: %d
    其他个数: %d
    '''%(len(x),alpha_cnt,blank_cnt,digit_cnt,others_cnt))

count_str("Jghjadjg dgh dghg;;%$^hdh  267 277h267  gsu")
```

#### 2.2.4 猴子吃桃问题
猴子第一天摘下若干个桃子，当即吃了一半，还不瘾，又多吃了一个,第二天早上又将剩下的桃子吃掉一半，又多吃了一个。 
以后每天早上都吃了前一天剩下的一半零一个。到第10天早上想再吃时，见只剩下一个桃子了。求第一天共摘了多少?
> 提示：采取逆向思维的方法，从后往前推断。
> 该题目不需要创建函数

代码实现:
```python
peach_after=1
for i in range(9,0,-1):
    peach_before=(peach_after+1)*2
    print("第{}天，总数{}个，剩余{}个".format(i,peach_before,peach_after))
    peach_after=peach_before
print(peach_before)
```

#### 2.4.5 猜数字问题
1. 随机生成一个整数
2. 猜一个数字并输入
3. 判断是大是小，直到猜正确
4. 判断时间
> 提示：需要用time模块、random模块

代码实现:
```python
import time
import random

num=random.randint(1,100)
print("游戏开始!请输入1到100内的整数:\n")
time1=time.mktime(time.localtime())

cnt=1
while True:
    x=input(">> 第%d次尝试: "%(cnt))
    cnt+=1
    time2=time.mktime(time.localtime())
    timestamp=time2-time1
    m, s = divmod(timestamp, 60)
    h, m = divmod(m, 60)
    difftime = "%02d时%02d分%02d秒" % (h, m, s)
    if x.isdigit():
        x=int(x)
        if x==num:
            time2=time.localtime()
            print("正确！耗时: {}".format(difftime))
            break
        elif x>num:
            print("太大了！")
        else:
            print("太小了！")
```

[项目链接](https://github.com/Jnewgeek/python_minor_project/tree/master/%E9%A1%B9%E7%9B%AE2_%E5%9F%BA%E4%BA%8EPython%E7%9A%84%E7%AE%97%E6%B3%95%E5%87%BD%E6%95%B0%E5%88%9B%E5%BB%BA "基于Python的算法函数创建")<br/>
[返回目录](#目录 "返回目录")
