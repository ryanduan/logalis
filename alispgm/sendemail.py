#!/usr/bin/python
#-*- coding: utf-8 -*-


import smtplib
from email.mime.text import MIMEText
from email.header import Header

sender = 'ryan@deliveryherochina.com'
receiver = 'dyw564!@126.com'
subject = 'testemail'
smtpserver = 'smtp.googlemail.com'
username = 'ryan@deliveryherochina.com'
password = 'dyw564!@#'
msg = MIMEText('hello world', 'plain', 'utf-8')
msg['Subject'] = Header(subject, 'utf-8')

smtp = smtplib.SMTP()
smtp.connect('smtp.googlemail.com')
smtp.login(username, password)
smtp.sendmail(sender, receiver, msg.as_string())
smtp.quit()




#   This is gmail's sendmail solution
#
#import smtplib
#
#
#mail_server = 'smtp.gmail.com'
#mail_server_port = 587                                         #not importent
#gmail = smtplib.SMTP(mail_server, mail_server_port)            #can user gmail.connect(mail_server)
#gmail.set_debuglevel(1)
#gmail.ehlo()
#gmail.starttls()
#gmail.login(username,password)
#gmail.sendmail(sender,receiver,msg)
#
