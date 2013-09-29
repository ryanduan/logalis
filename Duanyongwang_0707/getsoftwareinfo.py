from subprocess import Popen, PIPE

def getOSInfo():
    p = Popen('lsb_release -a', stdout = PIPE, shell = True)
    out, err = p.communicate()
    osinfo = {}
    oslist = [ i for i in out.split('\n')]
    for x in oslist:
	if ':' in x and 'LSB Version' not in x:
	    k,v = [ f.strip() for f in x.split(':')]
	    osinfo[k] = v

    return osinfo

def getHostname():
    p = Popen('hostname', stdout = PIPE, shell = True)
    out, err = p.communicate()
    return out

print getOSInfo()
	
