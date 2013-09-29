#!/usr/bin/python
#-*- coding: utf-8 -*-

#   Author: Ryan
#   Datetime: 2013-09-29
#   Address: Shanghai
#   Company: DeliveryHeroChina
#   Version: 0.1
#   This is a logfile analysis script of python.

import sys
from os import stat
from os.path import exists
import glob
import string
from optparse import OptionParser

class LogAnalysis(object):
    """
    Documentation & Discription
    """

    def __init__(self, logfile):
        """
        Initialize
        """
        self.logfile = logfile
        self.total_num = 0
        self.error_num = 0
        self.warning_num = 0
        self.info_num = 0
        print "get file",self.logfile

#    def __iter__(self):
#        return self


    def _readlines(self):
        """
        Read log file in lines
        """
        self.logc = open(self.logfile)
        self.logs = self.logc.readlines()
        print self.logs
        print "#"*100
#        return self.logs
        return [line for line in self.logs]

    def read(self):
        lines = self._readlines()
        print lines
        if lines:
            print "read file"
            return "".join(lines)
        else:
            return None

    def _filehandle(self):
        pass

    def __del__(self):
        if self.logc:
            print "close file"
            self.logc.close()

if __name__ == "__main__":
    aa = LogAnalysis("/tmp/test002.log")
    print aa.read()
