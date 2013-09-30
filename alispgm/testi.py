#!/usr/bin/python
from testreadlog import Readlog
import sys
logs = Readlog("test01.log")
for i in logs:
    if 'INFO' not in i and  'WARNING' not in i:
        sys.stdout.write(i)
