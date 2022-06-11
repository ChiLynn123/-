# 一、服务器搭建mysql容器-Ubuntu

### Step1： 安装docker环境

**更新源地址**

```pgsql
sudo apt-get update
```

**安装docker主程序**

```routeros
sudo apt-get install docker
```

**安装docker.io**

```routeros
sudo apt-get install docker.io -y
```

> 如果长时间卡住不动，可以按Ctrl+c放弃本次操作，再重新输入指令尝试。

**安装docker-registry**

```routeros
sudo apt-get install docker-registry -y
```

**检查docker运行状态**

```ebnf
service docker status
```

**拉取官方MySQL镜像**

```ebnf
sudo docker pull mysql
```

### Step2 启动MySQL镜像

**通过docker run命令启动mysql镜像实例**

```routeros
docker run --name=onlinemysql -it -p 0.0.0.0:3306:3306  -e MYSQL_ROOT_PASSWORD=123456 -d mysql
```

> 参数说明：
> --name 指定镜像实例的名称，不可与当前已创建实例重复
> -t 让docker分配一个伪终端并绑定到容器的标准输入上
> -i 让容器的标准输入保持打开
> -p 绑定容器实例的3306端口到主机的3306端口（0.0.0.0代表本机的所有IP）（我使用的服务器外网开放端口是53377）
> -e 用来给容器内传递环境变量，指定mysql登录密码，
> -d 表示后台运行容器，返回容器ID

### 通过Navicat验证数据库状态

通过Navicat验证数据库是否启动正常，只需要填写你的云主机IP及端口号即可

## 说明：前端机搭建mysql容器

安装过程：https://segmentfault.com/a/1190000039133152

​                 https://www.jb51.net/article/207911.htm

## 前端机：

```
前端机器外部：	113.31.114.239	53378	root	 206D-Ab56VzfPqq}V20	
内部ip：10.23.16.142	
搭建mysql容器：3306映射到外部53377

```

注：

映射到外部的端口要保证开放到互联网，否则外网navicat无法链接；

navicat需要先连ssh 再连数据库

# 二、脚本chuangyu_selenium.py执行说明：

```
由于创宇对selenium的指纹特征已经进行了反爬，所以不能直接调用chrome插，需要手动开启浏览器，避免因为使用爬虫打开网页它被检测到。
方法：
1、手动开启chrome做法，在chrome的安装目录下，运行CMD命令：chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenum\AutomationProfile"

2、这时候会自动打开一个chrome浏览器，这样会被认定为是人工打开，打开待爬取的网页，打开网址
https://www.seebug.org/vuldb/vulnerabilities

3、然后在代码修改自己的chrome_driver路径，运行脚本即可
注意：它会直接在你打开的页面进行翻页，所以最开始爬的时候要切换到第一页再爬取，如果中间断掉也可以在断掉的网页直接往后爬取
```

