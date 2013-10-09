#!/usr/bin/python
#-*- coding: utf-8 -*-
#
# Author: Ryan

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from readlog import Readlog, analysislog

# This is the absolute path of the log file
logpath = '/var/log/testlog/d.log'

#
logconts = Readlog(logpath)

ntime, ninfo, nwarn, nerror, errors = analysislog(logconts)

longerror = ''.join(errors)

msglog = "%s\nINFO:%s\nWARNING:%s\nERROR:%s\n%s" % (ntime, ninfo, nwarn, nerror, longerror)

fromaddr = 'sendemailaddress'
toadds = 'receiveemailaddress'
username = 'username'
password = 'password'
subject = 'Log analysis'
smtps = smtplib.SMTP('smtp.gmail.com:587')
smtps.starttls()
smtps.login(username, password)
msg = MIMEText(msglog, 'plain', 'utf-8')
msg['Subject'] = Header(subject, 'utf-8')
smtps.sendmail(fromaddr, toadds, msg.as_string())
smtps.quit()
