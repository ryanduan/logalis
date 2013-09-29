import urllib,urllib2
from gethardwareinfo import *
from getsoftwareinfo import *

# This is a dict for upload infomation
upinfo = {}
# Get preparation infomation
dmiinfo = getDmiInfo()
ifinfo = getIfInfo()
# Get basic infomation
ipinfo = getIpInfo(ifinfo)
sysinfo = getSysInfo(dmiinfo)
cpuinfo = getCPUInfo(dmiinfo)
osinfo = getOSInfo()
# Get memory infomation
upinfo['memory'] = getMemInfo()
# Get accurate infomation
# Get IPAddress infomation
allip = []
for i in ipinfo:
    try :
        i['ip']
    except KeyError , w:
        i['ip'] = None
    if i['ip']:
	allip.append(i['ip'])
upinfo['ipaddr'] = ':'.join(allip)
# Get system infomation
for i in sysinfo:
    sd = {}
    if 'Manufacturer' in i[0] :
        upinfo['vendor'] = i[1]
    if 'Product Name' in i[0] :
	upinfo['product'] = i[1]
    if 'Serial Number' in i[0]:
	upinfo['sn'] = i[1]
# Get CPU infomation
upinfo['cpu_num'] = cpuinfo['Core Count']
upinfo['cpu_model'] = cpuinfo['Family']
# Get os infomation
upinfo['osver'] = osinfo['Description']
# Get hostname
upinfo['hostname'] = getHostname().strip()
# Upload infomation
#d1 = urllib.urlencode(upinfo)
#req = urllib2.urlopen('http://127.0.0.1:8000/api/collect', d1)
print upinfo
