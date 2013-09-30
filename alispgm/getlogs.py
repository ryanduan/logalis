#!/usr/bin/python
#-*- coding: utf-8 -*-
# Author: Ryan

import sys
from readlog import Readlog

class Getlogs(object):
    
    def __init__(self, filename):
        self.Error_num = 0
        self.Warning_num = 0
        self.Info_num = 0
        self.filename = filename
        self.logs = Readlog(filename)


    def _getInfo_num(self, log):
        _info_num = 0
        if 'INFO' in log:
            _info_num += 1
            return _info_num

    def _getWarning_num(self, log):
        _warning_num = 0
        if 'WARNING' in log:
            _warning_num += 1
            return _warning_num

    def _getError_num(self, log):
        _error_num = 0
        if 'ERROR' in log:
            _error_num += 1
            return _error_num

    def _getError(self, log):
        if 'INFO' not in log and 'WARNING' not in log:
            sys.stdout.write(log)
    def getlog(self, self.logs):
        return self.logs

    def getl(self):
        logs = getlog()
        for log in logs:
            print log
        
