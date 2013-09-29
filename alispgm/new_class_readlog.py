#!/usr/bin/python
#conding:utf8
#author:ryan


class OpenLogFile(object):
    
    def __init__(self,filename):
        pass        #open logfile and read file content

    def getError(self,filecontent):
        pass        #read log file content and get the ERROR infomations

    def getWarning(self,filecontent):
        pass        #read log file content and get the Warning infomations

    def getInfo(self,filecontent):
        pass        #read log file content and get the Info infomations

    def __del__(self)
        pass        #close the opening files

