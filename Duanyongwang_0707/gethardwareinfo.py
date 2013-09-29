#!/usr/bin/python
from subprocess import Popen, PIPE
import re

def getDmiInfo():
    p = Popen('dmidecode', stdout = PIPE, shell = True)
    out,err = p.communicate()
    return out

def getIfInfo():
    p = Popen('ifconfig',stdout = PIPE, shell = True)
    out , err = p.communicate()
    return out

def getIpInfo(out):
    gs = [ i for i in out.split('\n\n') if i and not i.startswith('lo')]
    ifname = re.compile(r'^([a-z]{3,4}\d)')
    ipaddr = re.compile(r'.*inet addr:([\d.]{7,15})?')
    ip_info = []
    for g in gs:
        ifn = {}
        lines =  g.split('\n')
        for line in lines:
            m_ifname = ifname.match(line)
            m_ipaddr = ipaddr.match(line)
            if m_ifname:
                ifn['name'] = m_ifname.groups()[0]
            if m_ipaddr:
                ifn['ip'] = m_ipaddr.groups()[0]
        ip_info.append(ifn)
    return ip_info


def getSysInfo(dminfo):
    pl = []
    line_in = False
    for line in dminfo.split('\n'):
	if line.startswith('System Information'):
	    line_in = True
	    continue
	if line.startswith('\t') and line_in:
	    pd = [i.strip() for i in line.split(':')]
	    pl.append(pd)
	else :
	    line_in = False
    return pl

def getCPUInfo(dminfo):
    pd = {}
    line_in = False
    for line in dminfo.split('\n'):
	if line.startswith('Processor Information'):
	    line_in = True
	    continue
	if line.startswith('\t') and line_in:
	    for l in [l for l in line.split('\t')]:
		if l and ':' in l:
		    k,v = [i for i in l.split(':')]
		    if v:
		        pd[k] = v
	else :
	    line_in = False
    return pd
    
def getMemInfo():
    p = Popen('free | grep Mem', stdout = PIPE, shell = True)
    stdout,err = p.communicate()
    memlist = [m for m in stdout.strip().split(' ') if m]
    mem = int(round(float(memlist[1])/1000000))
    return mem

