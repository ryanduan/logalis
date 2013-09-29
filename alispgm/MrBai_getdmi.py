#!/usr/bin/env python


from subprocess import Popen, PIPE


def getDMI():
    p = Popen('dmidecode', stdout=PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout


def parserDMI(dmidata):
    pd = {}
    line_in = False
    for line in dmidata.split('\n'):
        if line.startswith('System Information'):
             line_in = True 
             continue
        if line.startswith('\t') and line_in:
                 k,v = [i.strip() for i in line.split(':')]
                 pd[k] = v
        else:
            line_in = False
    return pd

if __name__ == "__main__":
    dmidata = getDMI()
    print parserDMI(dmidata)
        
