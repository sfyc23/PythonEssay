# 一键获取 P 站视频下载链接

众所周知：P 站是一个学习视频。  

每当感觉自己找不着方向的时候，就会去里面找找学习的视频，总能给予我能量。

![](https://raw.githubusercontent.com/sfyc23/image/master/vlog/P%E7%AB%99%E5%AD%A6%E4%B9%A0%E4%B8%BB%E9%A1%B5.png)

缓存下载，以及时时观看。但最近 P 站最近改规律了，没法通过 Ctrl + F 找到下载链接。这让我感觉很难过。但谁也不能让我停止学习。  

——————


查看页面源代码，搜索：mp4 

![](https://raw.githubusercontent.com/sfyc23/image/master/vlog/P%E7%AB%99%E9%A1%B5%E9%9D%A2%E6%BA%90%E4%BB%A3%E7%A0%81.png)

所以很明显，P 站对原来的 url 全放在这段 JS 代码里了。  

怎么做的处理，并不清楚。还以为要对 JS 来回做复杂的处理时，在控制台执行了这个变量，神奇的事情发生了。 

![](https://raw.githubusercontent.com/sfyc23/image/master/vlog/P%E7%AB%99%E5%AD%A6%E4%B9%A0%E8%B4%B4.png)

使用 eval(flashvars_195251821)，返回一个字典，包含了视频信息。

然后事情就简单了。

使用 selenium ，加载页面，通过正则匹配关键词 flashvars_XXXX 。使用 execute_script 执行 JS 代码： eval(flashvars_XXXX) 。从返回字典中得到数据。

核心代码：
```
from selenium import webdriver
import re

url = 'https://www.pornhub.com/view_video.php?viewkey=ph5c07b7ed1777b'
browser = webdriver.PhantomJS()
browser.get(url)

key = re.findall(r"flashvars_\d{1,}", browser.page_source)[0]
datas = browser.execute_script('return eval(arguments[0])', key)

for md in datas['mediaDefinitions']:
    video_url = md['videoUrl']
    quality = md['quality']
    _format = md['format']
    if _format == "mp4":
        print("清晰度：{}P，视频地址：{}".format(quality, video_url))
```
输出：
```
清晰度：480P，视频地址：https://cv.phncdn.com/videos/201812/05/195251821/480P_2000K_195251821.mp4?T7IvoYL4dUbaDNkTlIbaxrdKJGVjUAqQgI98LdqBaoZN3PCauYuz97R2vTWPXTP-C0qucnm5iM8Fc_TXhP5RaJg-odpkEGJWKXZsaRkctBWoCnhcCcOBN_a4OVBrwQb3PjVHnQdhGltTNj7hlckIyAkZBz51CT3vxe7ogzdqdmR9AKY-nA2xCpfcbNW8Nmxh4cR8hSXQQquw
清晰度：240P，视频地址：https://cv.phncdn.com/videos/201812/05/195251821/240P_400K_195251821.mp4?XZ_MA8gz1XKPIlQPkh5qu1KJ9dpK3xtsxRg7XuJmZLhbUuxdA0OJRS_7ERGD3TQXmaV7WNKdDcSHqAr194_C3kS5YkR3pJcVus_NTdKZyJrxEgWNDyg0euPxiL3df_ekBXJq1RUWXzNjd-GWDEun43xlHahrLGbpnexujuPR8mGcASYufgl49ZzaGgW_vCK3C3pzldoFhi0
```

顺手获取一下视频的标题：

![](https://raw.githubusercontent.com/sfyc23/image/master/vlog/%E8%8E%B7%E5%8F%96%E6%A0%87%E9%A2%98.png)

class 名为 "inlineFree" 节点就一个，所以那就简单了。

```
voide_title = browser.find_element_by_class_name("inlineFree").text
```
 
留下的也就没什么好说的了。（P 站没有梯子是过不去的）  
 
 ---  
 
项目完整代码地址： https://github.com/sfyc23/PythonEssay/tree/master/pronhub_download_url  
 
项目运行：  
```
python pronhub_url.py "https://www.pornhub.com/view_video.php?viewkey=ph5c07b7ed1777b"
```
运行结果：

![](https://raw.githubusercontent.com/sfyc23/image/master/vlog/P%E7%AB%99%E5%AD%A6%E4%B9%A0%E8%BF%90%E8%A1%8C.png)

---

文章与代码参考：https://mp.weixin.qq.com/s/yMxyYOcdQZMseMqhjCploQ  

如果你觉得用代码比较麻烦也有谷歌插件一键下载。地址：http://1t.click/bpmG  

