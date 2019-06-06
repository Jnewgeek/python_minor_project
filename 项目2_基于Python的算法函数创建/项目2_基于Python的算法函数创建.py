#coding:utf-8
'''
使用Python完成习题.
'''

'''
题目1：有1、2、3、4共四个数字，能组成多少个互不相同且无重复数字的两位数？都是多少？
# 该题目不用创建函数
'''
print("统计学公式: 2**4-C4取1,2**4=16,16-4=12个")

num=set()
for i in range(1,5):
    for j in range(1,5):
        num.add(i*10+j)

print("互不相同的两位数个数: ",len(num))
print("分别是: \n",sorted(num))

'''
题目2：输入三个整数x,y,z，请把这三个数由小到大输出，可调用input()。（需要加判断：判断输入数据是否为数字）

# 提示：判断是否为数字：.isdigit()
# 该题目需要创建函数
'''
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


'''
题目3：输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。

# 提示：利用while语句.
# 该题目不需要创建函数
'''
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

'''
题目4：猴子吃桃问题：猴子第一天摘下若干个桃子，当即吃了一半，还不瘾，又多吃了一个,第二天早上又将剩下的桃子吃掉一半，又多吃了一个。 
以后每天早上都吃了前一天剩下的一半零一个。到第10天早上想再吃时，见只剩下一个桃子了。求第一天共摘了多少?
# 提示：采取逆向思维的方法，从后往前推断。
# 该题目不需要创建函数
'''
peach_after=1
for i in range(9,0,-1):
    peach_before=(peach_after+1)*2
    print("第{}天，总数{}个，剩余{}个".format(i,peach_before,peach_after))
    peach_after=peach_before
print(peach_before)

'''
题目5：猜数字问题，要求如下：
① 随机生成一个整数
② 猜一个数字并输入
③ 判断是大是小，直到猜正确
④ 判断时间
# 提示：需要用time模块、random模块
'''
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