# Python 自动追更小说并发送至微信

## 项目介绍

### 来源

偶尔也看网络小说，但是追更还是比较麻烦的。  
所以就想着何不自己撸一个呢。  

### 项目地址

Github: https://github.com/sfyc23/PythonEssay/tree/master/novel_update

### 数据来源

笔趣阁：https://www.5atxt.com/    
选它的原因：  
1. 百度出来第一个就是它啊; 
2. 小说数量挺多；
3. 也没有做防爬处理。

### 最终功能

每隔半小时（时间可自设）自动刷新小说目录，判断小说是否已更新。  
如果有更新，则把更新后的小说内容，发送到微信的绑定邮箱中，并使用微信查看。


![](https://raw.githubusercontent.com/sfyc23/image/master/vlog/%E6%95%88%E6%9E%9C%E5%9B%BE3.png)


## 实现  

以小说《诡秘之主》举例：

### 搜索页面

从搜索页面找到小说对应的详情页。

![](https://raw.githubusercontent.com/sfyc23/image/master/vlog/%E6%90%9C%E7%B4%A2%E9%A1%B5%E9%9D%A2.png)

```
base_url = 'https://www.5atxt.com'
novel_name = '诡秘之主'
data = {'name': novel_name}
resp = requests.post("https://www.5atxt.com/index.php?s=/web/index/search", data=data)
if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, "lxml")
    nh = soup.find('span', class_='s2', text=novel_name)   
    href = nh.a.get('href')
    home_url = "{}{}".format(base_url, href)
    print(home_url)
    
```

得到详情页地址：https://www.5atxt.com/1_1409/

### 详情页面

在详情页面获取最新章节：

![](https://raw.githubusercontent.com/sfyc23/image/master/vlog/%E8%AF%A6%E6%83%85%E9%A1%B51.png)

```
base_url = 'https://www.5atxt.com'
home_url = "https://www.5atxt.com/1_1409/"
resp = requests.get(home_url)
if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, "lxml")
    latest_chapter_a = soup.select("div#info > p:nth-last-child(1)")[0].a
    latest_chapter_name = latest_chapter_a.text.strip()  # 最新章节名称
    latest_chapter_url = latest_chapter_a['href']  # 最新章节地址
    latest_chapter_url = "{}{}".format(base_url, latest_chapter_url)
    print(latest_chapter_name, latest_chapter_url)
```
得到：  
章节名：第五部总结兼请假兼求保底月票   
章节地址：https://www.5atxt.com/1_1409/14584779.html  


### 小说阅读页

从小说阅读页爬虫小说内容：
![](https://raw.githubusercontent.com/sfyc23/image/master/vlog/%E5%B0%8F%E8%AF%B4%E9%98%85%E8%AF%BB%E9%A1%B5png.png)
```
novel_url = 'https://www.5atxt.com/1_1409/14584779.html'
resp = requests.get(novel_url)
if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, "lxml")
    aa = soup.find('div', id='content', deep="3")
    if aa.p:
        # 用于删除多余信息：天才一秒记住本站地址：[笔趣阁] ……
        aa.p.decompose()
    if aa.div:
        # 删除：章节错误,点此报送(免注册)……
        aa.div.decompose()
    print(aa.text)
```

### 把更新内容发送到邮箱
```
email_user = '代理@qq.com'
email_password = '代理密码'
email_host = '代理host' # 例如：smtp.qq.com
to_emails = ['xx@qq.com']  # 需要发送的邮箱，可以写多个。
yag = yagmail.SMTP(user=email_user, password=email_password, host=email_host)
yag.send(to_emails, title, content) # title：小说章节名，content:小说内容
```

### 开启定时查询

```
from apscheduler.schedulers.blocking import BlockingScheduler
scheduler = BlockingScheduler()
scheduler.add_job(update_novel, 'interval', minutes=30, misfire_grace_time=600, jitter=300)
scheduler.start()
```
每 30 分钟查询一次，时间抖动 300 秒（防止时间太过固定）。  


简意的流程就是这样。

其他的一些细节：  
1. 第一次请求得到详情页后保存起来，下一次可直接访问；
2. 保存最新的章节的名称，进行对比，然后更新；
3. 一次更新可能会有多个章节更新，得做处理（详情查看完整代码）；
4. 使用 fake_useragent 做简单的防爬；
