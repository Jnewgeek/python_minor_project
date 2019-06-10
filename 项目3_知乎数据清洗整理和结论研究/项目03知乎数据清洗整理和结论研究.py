# coding: utf-8

import os
import pandas as pd
import numpy as np
os.chdir(os.getcwd())
data=pd.read_csv("知乎数据_201701.csv",encoding="utf-8")
print(data.head())

# 1、数据清洗 - 去除空值
# 要求：创建函数
# 提示：fillna方法填充缺失数据，注意inplace参数

data.columns=['_id', '关注的收藏夹', '关注', '关注者', '关注的问题', '关注的话题', '关注的专栏', '职业1', '职业2',
       '回答', '提问', '收藏', '个人简介', '居住地', '所在行业', '教育经历', '职业经历']
# 查看数据缺失情况
#1、数据清洗 - 去除空值
# 填充缺失值
data.fillna("缺失数据",inplace=True)
data.isnull().sum()


#2、问题1 知友全国地域分布情况，分析出TOP20
# ① 按照地域统计 知友数量、知友密度（知友数量/城市常住人口），不要求创建函数
# ② 知友数量，知友密度，标准化处理，取值0-100，要求创建函数
# ③ 通过多系列柱状图，做图表可视化
# 提示：
# ① 标准化计算方法 = (X - Xmin) / (Xmax - Xmin)
# ② 可自行设置图表风格
# 标准化
def max_min(s):
    """
    将传入的数据进行标准化
    """
    return (s-min(s))/(max(s)-min(s))*100

target_data=data[data["居住地"]!="缺失数据"][["_id","居住地"]].groupby(by="居住地").count()
target_data=target_data.sort_values(by="_id",ascending=False)
target_data.index=list(i.replace("省","").replace("市","").replace("自治区","").replace("回","").replace("壮","").                       replace("维吾尔","").replace("族","").strip() for i in target_data.index)
target_data.columns=["知友人数"]
#target_data.head()
# 首先读入地区数据，并建立一个省份对应的省份、城市字典，将全部地区都转换为省份直辖市的形式
loction_data=pd.read_csv("六普常住人口数.csv",encoding="utf-8")
loction_data.columns=['省', '地区', '结尾', '常住人口']
loction_data=loction_data.dropna()
# 保存常住人口数量
people_num=pd.DataFrame(columns=["省份","常住人口数"])
# 仅保留每个列中数值最大的记录
for i in loction_data["省"].unique():
    people_num.loc[len(people_num)]=list(loction_data[loction_data["省"]==i].sort_values(by="常住人口",ascending=False).reset_index().loc[0,["省","常住人口"]])
people_num["省份"]=people_num["省份"].apply(lambda x:x.replace("省","").replace("市","").replace("自治区","").replace("壮","").replace("回","").                                        replace("维吾尔","").replace("族","").strip())
#people_num.head()
#连表
target_data=pd.merge(target_data,people_num,how="inner",left_index=True,right_on="省份").set_index("省份")
#target_data.head()
# 计算知友密度
target_data["知友密度"]=target_data["知友人数"]/target_data["常住人口数"]
# 标准化
target_data["知友密度_n"]=max_min(target_data["知友密度"])
target_data["知友人数_n"]=max_min(target_data["知友人数"])
#target_data

# 3.学校分布
target_data1=data[data["教育经历"]!="缺失数据"][["关注者","关注","教育经历"]].groupby(by="教育经历").sum().sort_values(by="关注",ascending=False)
for i in ["大学","大学生","本科","本科生","高中","研究生","硕士","本科毕业生","博士","大学本科",'医学',
 '为往圣继绝学','我的老師，是山川和大地','重庆第一工程尸培养基地','吃喝玩乐']:
    target_data1.drop(i,inplace=True)
target_data1.columns=["粉丝数","关注人数"]
#print(target_data1)

# 绘图
import matplotlib.pyplot as plt
import matplotlib as mpl
myfont = mpl.font_manager.FontProperties(fname='C:/Windows/Fonts/SimHei.ttf')  
mpl.rcParams['axes.unicode_minus'] = False
get_ipython().run_line_magic('matplotlib', 'inline')

fig,axes = plt.subplots(2,1,figsize = (10,8))

df1=target_data.sort_values(by="知友人数",ascending=False)["知友人数_n"][:20]
df2=target_data.sort_values(by="知友密度",ascending=False)["知友密度_n"][:20]
df1.plot(kind="bar",ylim=[0,110],width=0.9,alpha=0.8,rot = 45,title = '知友数量Top20',color='salmon',ax=axes[0],)
df2.plot(kind="bar",ylim=[0,110],width=0.9,alpha=0.8,rot = 45,title = '知友密度Top20',color='purple',ax=axes[1])
# 去除边框
for i in axes:
    i.tick_params(bottom='on',top='off',left='off',right='off')
    i.spines['right'].set_visible(False)
    i.spines['top'].set_visible(False)
    i.set_xlabel("")
# 添加标签
for (i,j) in zip(range(len(df1.index)),df1.values):
    axes[0].text(i-0.4,j+2,round(j,1),color="red")
for (i,j) in zip(range(len(df2.index)),df2.values):
    axes[1].text(i-0.4,j+2,round(j,1),color="blue")
plt.savefig("知友地域统计.png",dpi=400)


# 散点大小
s=(target_data1["粉丝数"]+target_data1["关注人数"]).tolist()[:20]
fig=plt.figure(figsize=(10,6))
plt.scatter(target_data1["关注人数"].tolist()[:20],target_data1["粉丝数"].tolist()[:20],marker="o",alpha=0.8,
            color="blue",s=s/max(s)*100,label="学校")
plt.axvline(np.mean(target_data1["关注人数"].tolist()[:20]),linewidth=1,color="r",linestyle="--",label="平均关注人数:%d人"%np.mean(target_data1["关注人数"].tolist()[:20]))
plt.axhline(np.mean(target_data1["粉丝数"].tolist()[:20]),linewidth=1,color="k",linestyle="--",label="平均粉丝数:%d人"%np.mean(target_data1["粉丝数"].tolist()[:20]))
plt.legend(loc="upper left")
for i,j in enumerate(zip(target_data1["关注人数"].tolist()[:20],target_data1["粉丝数"].tolist()[:20])):
    plt.text(j[0]*1.01,j[1]*1.01,list(target_data1.index)[i],fontsize="x-small")
plt.title("粉丝数Top20高校关注人数&粉丝数散点图")
plt.xlabel("关注人数")
plt.ylabel("粉丝数")
plt.savefig("粉丝数Top20高校.png",dpi=400)


# # 建立省——地区对应字典，用来清洗知乎数据中的地区
# province_city={}
# for pro in loction_data["省"].unique():
#     # 以省作为键，地区和常住人口分别作为值
#     # 各个省单独的数据
#     target_prodata=loction_data[loction_data["省"]==pro]
#     target_prodata.index=range(target_prodata.shape[0])
#     pro=pro.replace("省","").replace("市","").replace("自治区","").replace("壮族","").replace("维吾尔","").strip()
#     province_city[pro]={}
#     province_city[pro]["people_num"]=int(target_prodata[target_prodata["结尾"]=="市"]["常住人口"].sum())
#     province_city[pro]["region"]=[]
#     # 将全部地区提取出来放入省份——地区字典中,为了避免用户输入的地区为去除了省、市关键字，特地将该字去除
#     province_city[pro]["region"].extend(list(i.replace("省","").replace("市","").strip() for i in target_prodata["地区"]))
# #province_city

# # 为保证精确，再将一些地区的简称以及特殊称号添加进字典中
# #lst=[]
# import json
# s='{"北京（京）、天津（津）、黑龙江（黑）、吉林（吉）、辽宁（辽）、河北（冀）、河南（豫）、山东（鲁）、山西（晋）、陕西（陕）、内蒙古（内蒙古）、宁夏（宁）、甘肃（陇、甘）、新疆（新）、青海（青）、西藏（藏）、湖北（鄂）、安徽（皖）、江苏（苏）、上海（沪）、浙江（浙）、福建（闵）、湖南（湘）、江西（赣）、四川（川、蜀）、重庆（渝）、贵州（黔、贵）、云南（滇、云）、广东（粤）、广西（桂）、海南（琼）、香港（港）、澳门（澳）、台湾（台）}'
# s=s.replace("（","\":\"").replace("）、","\",\"").replace("）}","\"}")
# region_keys=json.loads(s)
# # 将简称添加进字典
# # 将简称添加进省份——地区字典当中
# for pro in region_keys.keys():
#     # 保证程序出错之后能跳过
#     if pro in province_city.keys():
#         # 兼容包含多个简称的地区
#         key=region_keys[pro] if "、" not in region_keys[pro] else region_keys[pro].split("、")
#         if isinstance(key,str):
#             province_city[pro]["region"].append(key)
#         else:
#             province_city[pro]["region"].extend(key)
#     else:
#         continue
        
# # 各省市的别称
# # '{"广州：花城、羊城；重庆：山城；湘潭：莲城；长沙：星城、潭城；成都：蓉城、锦城；昆明：春城、花城；武汉：江城；金华：婺城；莆田：荔城；潮州：凤城；济宁：任城；徐州：彭城；大同：平城；嘉兴：禾城；安庆：宜城；西昌：月城；扬州：芜城；温州：鹿城；衢州：柯城；蚌埠：珠城；泉州：锦城；漳州：芗城；许昌：烟城；惠州：鹅城；柳州：龙城；泸州：酒城；内江：甜城；青岛：岛城；烟台：港城；曲阜：圣城；东营：油城；衡阳：雁城；福州：榕城；大连：滨城；长春：车城；苏州：水城；厦门：鹭城；鞍山：钢城；呼市：青城；哈尔滨：冰城；齐齐哈尔：鹤城；潍坊：风筝城；石狮：服装城；拉萨：日光城；绍兴：蠡城；济南：泉城、历城；南昌：洪城、英雄城；南京：石头城、金陵"}'
# s1='{"广东：花城、羊城、凤城、鹅城、服装城；重庆：山城；湖南：莲城、雁城、星城、潭城；四川：蓉城、酒城、甜城、月城；云南：春城；湖北：江城；\
# 浙江：婺城、禾城、蠡城、鹿城、柯城；福建：荔城、榕城；山东：任城；安徽：彭城、珠城、宜城；山西：平城；江苏：芜城、水城、石头城、金陵；\
# 福建：锦城、芗城、鹭城；河南：烟城；广西：龙城；山东：岛城、港城、圣城、油城、风筝城、泉城、历城；辽宁：滨城、钢城；吉林：车城；辽宁：钢城；\
# 内蒙古：青城；黑龙江：冰城、鹤城；西藏：日光城；江西：洪城、英雄城"}'
# s1=s1.replace("：","\":\"").replace("；","\",\"")
# city_nick=json.loads(s1)

# # 将简称添加进字典
# # 将简称添加进省份——地区字典当中
# for pro in city_nick.keys():
#     # 保证程序出错之后能跳过
#     if pro in province_city.keys():
#         # 兼容包含多个简称的地区
#         key=city_nick[pro] if "、" not in city_nick[pro] else city_nick[pro].split("、")
#         if isinstance(key,str):
#             province_city[pro]["region"].append(key)
#         else:
#             province_city[pro]["region"].extend(key)
#     else:
#         continue

# # 地区拼音
# region_pinyin={"安徽":["Anhui","Anqing","Bengbu","Guozhou","Chaohu","Chizhou","Zhangzhou","Fuyang","Hefei","Huaibei","Huainan","Huangshan",
#               "Jieshou","Luan","Maanshan","Mingguang","Ningguo","Tianchang","Tongcheng","Tongling","Wuhu","Suzhou","Xuancheng"],
#               "北京":["Beijing"],
#               "福建":["Fuan","Fuding","Fujian","Fuqing","Fuzhou","Jianye","Jianyang","Jinjiang","Longhai","Longyan","Nanan","Nanping",
#                     "Ningde","Putian","Quanzhou","Sanming","Xiamen","Shao Wu","Stone lion","Wuyishan","Yongan","Muping","Zhangzhou",
#                     "Changle","Fujian"],
#               "甘肃":["Baiyin","Dingxi","Dunhuang","Gansu","Cooperation","Jiayuguan","Jinchang","Jiuquan","Lanzhou","Linxia","Weinan",
#                     "Pingliang","Qingyang","Tianshui","Wuwei","Yumen","Zhang Wei","Gansu"],
#               "广东":["Chaozhou","Conghua","Dongguan","Enping","Foshan","Gaoyao","Gaozhou","Guangdong","Guangzhou","Heyuan","Heshan",
#                     "Huazhou","Huizhou","Jiangmen","Jieyang","Kaiping","Lechang","Leizhou","Lianzhou","Lianjiang","Lu Feng","Luoding",
#                     "Maoming","Meizhou","Nanxiong","Puning","Qingyuan","Shantou","Shanwei","Shaoguan","Shenzhen","Sihui","Taishan",
#                     "Wu Chuan","Xinyi","Xingning","spring","Yangjiang","Yingde","Yunfu","Zengcheng","Zhanjiang","Zhaoqing","Zhongshan",
#                     "Zhuhai","Guangdong"],
#               "广西":["Baise","Beihai","Beiliu","Cenxi","Chongzuo","Dongxing","Fangchenggang","Guigang","Guilin","Guiping","Heshan","Hechi",
#                     "Hezhou","guest","Liuzhou","Nanning","Pingxiang","Qinzhou","Zhangzhou","Yizhou","Yulin","Guangxi"],
#               "贵州":["Anshun","Bijie","Chishui","Duyun","Fuquan","Guiyang","Guizhou","Carey","Liupanshui","Qingzhen","Ren Huai","Tongren",
#                     "Xingyi","Zunyi","Guizhou"],
#               "海南":["Zhangzhou","East","Haikou","Hainan","Qiong Hai","Sanya","Wanning","Wenchang","Wuzhishan","Hainan"],
#                "河北":["Anguo","Bazhou","Baoding","Botou","Zhangzhou","Chengde","Dingzhou","Gaobeidian","Yucheng","Handan","Hebei","Hejian",
#                      "Hengshui","Huanghua","Jizhou","Jinzhou","Langfang","Luquan","Nangong","Qianan","Qinhuangdao","RenQiu","Sanhe","Shahe",
#                      "Shenzhou","Shijiazhuang","Tangshan","Wuan","Xinji","Xinyue","Xingtai","Zhangjiakou","Zhuzhou","Zunhua","Heibei"],
#                "河南":["Anyang","Dengfeng","Dengzhou","GongYi","Henan","Hebi","Huixian","Jiyuan","Jiaozuo","Kaifeng","Linzhou","Lingbao",
#                      "Luoyang","Luohe","Mengzhou","Nanyang","Pingdingshan","Fuyang","Fuyang","Zhangzhou","Sanmenxia","Shangqiu","WeiHui",
#                      "Wugang","Xiangcheng","Xinmi","Xinxiang","Xinzheng","Xinyang","XuChang","Yanshi","Yima","Fuyang","Yongcheng","Zhangzhou",
#                      "Changge","Zhengzhou","Zhoukou","Zhumadian","Henan"],
#                "黑龙江":["Anda","Beian","Daqing","Fujin","Harbin","Hailin","Helen","Hegang","Heihe","Heilongjiang","Hulin","Jixi","Jiamusi",
#                       "Mishan","Mudanjiang","Mu Ling","Nehe","Ningan","Qitaihe","Qiqihaer","Shang Zhi","Twin city","Shuangyashan","Suifenhe",
#                       "Suihua","Iron force","Tongjiang","Wuchang","Wudalianchi","Yichun","Jidong","Heilongjiang"],
#                "湖北":["Anlu","Chibi","Daye","Danjiangkou","Dangyang","Ezhou","Enshi","Guangshui","Hanchuan","Honghu","Hubei","Huanggang",
#                      "Yellowstone","Jingmen","Jingzhou","Laohekou","Icheon","Macheng","Qianjiang","Shiyan","Stone head","Songzi","Suizhou",
#                      "Tianmen","Wuhan","Wuxue","Xiantao","Xianning","Xiangfan","Xiaogan","Yichang","Yicheng","Yidu","Yingcheng","Zaoyang",
#                      "Zhijiang","ZhongXiang","Hubei"],
#                "湖南":["Changde","Changning","Zhangzhou","Miluo","Hengyang","HongJiang","Hunan","Huaihua","Jishou","Jingshi","Fuyang",
#                      "Lengshuijiang","Fuling","Wuyuan","Linxiang","Liuyang","Bottom","Lushan","Shaoyang","Wugang","Xiangtan","Xiangxiang",
#                      "Yiyang","Yongzhou","Lijiang","YueYang","Zhangjiajie","Changsha","Zhuzhou","Zixing","Hunan"],
#                "吉林":["Baicheng","Baishan","Daan","Dehui","Dunhua","Gongzhuling","Helong","Huadian","Hunchun","Jilin","Jilin","Jian",
#                      "Jiaohe","Jiutai","Liaoyuan","Linjiang","Longjing","Meihekou","Meteorite","Shulan","Shuangliao","Siping","Matsubara",
#                      "Weinan","Tonghua","Tumen","Yanji","Yushu","Changchun","Jilin"],
#                "江苏":["Changshu","Changzhou","Dafeng","Danyang","Dongtai","Gaoyou","Haimen","Huaian","Jiangdu","Jiangsu","Jiangyin",
#                      "Jiang Yan","Jintan","Jingjiang","Jurong","Kunshan","Fuyang","Lianyungang","Nanjing","Nantong","Zhangzhou","Qidong",
#                      "Rugao","Suzhou","Taicang","Taixing","Taizhou","Wuxi","Wu Jiang","New","Xinghua","Suqian","Xuzhou","Yancheng",
#                      "Yangzhong","Yangzhou","Yizheng","Yixing","Zhangjiagang","Zhenjiang","Jiangsu"],
#                "江西":["Dexing","Fengcheng","Fuzhou","Ganzhou","Gao An","Guixi","Jian","Jiangxi","Jinggangshan","Jingdezhen","Jiujiang",
#                      "Leping","Nanchang","Nankang","Pingxiang","Ruichang","Ruijin","Shangrao","Xinyu","Yichun","Yingtan","Eucalyptus","Jiangxi"],
#                "辽宁":["Anshan","Beipiao","North town","Benxi","Chaoyang","Dalian","Dashiqiao","Dandong","lighthouse","Donggang",
#                      "Fengcheng","Fushun","Fuxin","Gaizhou","Haicheng","Huludao","Jinzhou","Kaiyuan","Liaoning","Liaoyang","Ling Hai",
#                      "Lingyuan","Panjin","Pulandian","Shenyang","Tiaobingshan","Tieling","Wafangdian","Xinmin","Xingcheng","Yingkou",
#                      "Zhuanghe","Liaoning"],
#                "内蒙古":["Aershan","Bayannaoer","Baotou","Chifeng","eerguna","Eerduosi","Erlianhaote","Fengzhen","Genhe","Huhehaote",
#                       "Hulunbeier","Huolinguolei","Manzhouli","Tongliao","Wuhai","Wulanchabu","Wulanhaote","Xilinhaote","Yakeshi",
#                       "Zhalantun","Neimenggu"],
#                "青海":["Delingha","Geermu","Guyuan","Lingwu","Qinghai","Qingtongxia","Shizuishan","Wu Zhong","Xining","Yinchuan","Zhongwei"],
#                "山东":["Anqiu","Binzhou","Changyi","Dezhou","Dongying","Feicheng","high density","Haiyang","Heze","Jimo","Jinan","Jining",
#                      "Jiaonan","Jiaozhou","Laiwu","Lacey","Laiyang","Laizhou","Leling","Liaocheng","Linqing","Linxi","Longkou","Penglai",
#                      "Pingdu","Qixia","Qingdao","Qingzhou","Qufu","Rizhao","Rongcheng","Rushan","Shandong","Shouguang","Taian","Tengzhou",
#                      "Weihai","Weifang","Wendeng","Xintai","Yantai","Yanzhou","Yucheng","Zaozhuang","ZhangQiu","Zhaoyuan","Zhucheng","Zibo",
#                      "ZouCheng","Shandong"],
#                "山西":["Datong","Fuyang","Gao Ping","Ancient cross","Kawazu","Houma","Huozhou","Jiexiu","Jincheng","Jinzhong","Linfen",
#                      "Lucheng","LvLiang","Shanxi","Zhangzhou","Taiyuan","Xiaoyi","Zhangzhou","Yangquan","Yongji","Yuanping","Yuncheng",
#                      "Changzhi","Shanxi"],
#                "陕西":["Ankang","Baoji","Hancheng","Hanzhong","Huayin","Shaanxi","Shangluo","Tongchuan","Weinan","Xian","Xianyang","Xingping",
#                      "Yanan","Yulin","Shanxi"],
#                "上海":["Shanghai"],
#                "四川":["Bazhong","Chengdu","Chongzhou","Dazhou","Deyang","Dujiangyan","Emeishan","Guang'an","Guanghan","Guangyuan","HuaYing",
#                      "Jianyang","Jiangyou","Langzhong","Leshan","Luzhou","Meishan","Mianyang","Mianzhu","Nanchong","Neijiang","Panzhihua",
#                      "Pengzhou","Qionglai","Shifang","Sichuan","Suining","Wanyuan","Xichang","Yaan","Yibin","Ziyang","Zigong","Sichuan"],
#                "天津":["Tianjin"],
#                "西藏":["Lasa","Rikaze","Xizang"],
#                "新疆":["Akesu","Alaer","Aletai","Atushi","Bole","Changji","Fukang","Hami","Hetian","Kashi","Kalamayi","Kuerle","Kuitun",
#                      "Shihezi","Tacheng","Tumushuke","Tuerfan","Wulumuqi","Usu","Wujiaqu","Yining","Xinjiang"],
#                "云南":["Anning","Baoshan","Chuxiong","Dali","Gejiu","Jinghong","Kaiyuan","Kunming","Lijiang","Lincang","Luxi","Puer",
#                      "Qujing","Ruili","Xuanwei","Yuxi","Yunnan","Zhaotong","Yunnan"],
#                "浙江":["Cixi","Dongyang","Fenghua","Fuyang","Haining","Hangzhou","Huzhou","Jiaxing","Jiande","country","Jinhua","Lanxi",
#                      "Yueqing","Lishui","Linan","Linhai","Longquan","Ningbo","Pinghu","Zhangzhou","Ryan","Captain","Shaoxing","Zhangzhou",
#                      "Taizhou","Tongxiang","Wenling","Wenzhou","Yiwu","Yongkang","Yuyao","Zhejiang","Zhoushan","Zhuji","Zhejiang"],
#                "重庆":["Chongqing"]}
        
# # 将拼音添加进字典
# # 将简称添加进省份——地区字典当中
# for pro in region_pinyin.keys():
#     # 保证程序出错之后能跳过
#     if pro in province_city.keys():
#         province_city[pro]["region"].extend(region_pinyin[pro])
#     else:
#         continue

# province_city
# # 清洗知乎数据中的地区字段数据
# def clean_region(x):
#     '''
#     将地区信息传入该函数，通过遍历的方式获取较为准确的省份
#     '''
#     for pro in province_city.keys():
#         # 一旦匹配，立即停止遍历，此过程会存在一定程度的错判
#         for key in province_city[pro]["region"]:
#             if key.lower().replace(" ","") in x.lower().replace(" ",""):
#                 # 该省的关键字（包括省市名称、简称、别称）
#                 return pro
#             else:
#                 continue
#     return "缺失数据"
# data["居住地_清洗后"]=data["居住地"].apply(clean_region)
# # 添加人口数据
# # data["常住人口数"]=data["居住地_清洗后"].apply(lambda x:province_city[x]["people_num"] if x in province_city.keys() else "缺失数据")




