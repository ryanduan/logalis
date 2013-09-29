#encoding=utf-8

import LogQuery

#定义多个主机，用户名@主机,登录密码
myhosts = [('rootman@192.168.2.228','123'),('rootman@192.168.2.229','123'),('rootman@192.168.2.219','123')]
LogQuery.hosts(myhosts)

'''
案例1：
查询有哪些域名被抓取过，使用query方法，会返回所有符合规则的数据
预期返回：
www.163.com
www.yahoo.com
...
'''
res = LogQuery.query('\(.*crawled http:\/\/\)\([^\/]*\)\(\/.*\)',myhosts[0][0],'gcrawler.*.log',unique=True,sort=None,output=None,pattern=r'\2',path='/home/workspace/Case/trunk/src/gcrawler/log')
'''
上一行代码解读：
第一个参数指定了表示抓取的日志正则表达式，并且将其分组（为了提取域名），分组的括号用\(，\)表示，第二组是域名的提取。
第二个参数指定了要查询那一台主机上的日志
第三个参数指定了要分析的日志文件名，*表示任何字符
第四个参数unique，是否对返回的条目进行排重，例如：日志中发现多个www.163.com,只算一个
第五个参数sort，是否需要对抽取的条目进行排序，1：正序、-1：倒序，这里为None，即不需要排序
第六个参数output，可以指定运行结果输出到某个文件，在这里不需要输出，为None
第七个参数pattern，是指从正则表达式中抽取哪个分组，默认是第一组，这里用r'\2'指定第二组
第八个参数path指定了日志在操作系统上所在的目录
以下的count、aggregate方法使用的参数和query都是一样的意义
'''

'''
案例2：
统计被抓取过的域名有几个，使用count方法，会返回所有符合规则的统计总数
预期返回：4
...
'''
res = LogQuery.count('\(.*crawled http:\/\/\)\([^\/]*\)\(\/.*\)',myhosts[1][0],'gcrawler.*.log',unique=True,sort=None,output=None,pattern=r'\2',path='/home/workspace/Case/trunk/src/gcrawler/log')

'''
案例3：
分别统计每个域名被抓取的数量
返回的结果：
域名1,统计数字
域名2,统计数字
...
'''
res = LogQuery.aggregate('\(.*crawled http:\/\/\)\([^\/]*\)\(\/.*\)',myhosts[2][0],'gcrawler.*.log',output=None,pattern=r'\2',path='/home/workspace/Case/trunk/src/gcrawler/log')#这里是分类统计就没必要指定unique和sort了。
#打印分组统计的情况
for i in res:
    domain,count = i.split(',')
    total += int(count)
    print domain,'=>',count