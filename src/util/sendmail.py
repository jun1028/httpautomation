# -*- coding: UTF-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import os
import smtplib
import sys

DEFAULTTOMAILRECEIVERFILE = 'conf' + os.sep + 'receiver.txt'
USEDEFAULTMAIL            = False
SENDER = 'zhangzhijun@***.com'
SMTPSERVER = 'smtp.gmail.com'
USERNAME = 'zhangzhijun@***.com'
PWD = '123456'


#from email.mime.image import MIMEImage
def getToMaillist(receiverfile=None):
    receiverList = []
    if not receiverfile:
        receiverfile = DEFAULTTOMAILRECEIVERFILE
    fp = open(receiverfile)
    lines = fp.readlines()
    fp.close()
    for line in lines:
        if line.find('#') > -1:
            continue
        for receiver in line.split(';'):
            if len(receiver) > 1:
                receiverList.append(receiver)
    return receiverList


def genAttchment(attachment, name='test_report.html'):
    att = MIMEText(open(attachment, 'rb').read(), 'html', 'utf-8')
    att["Content-Type"] = 'application/octet-stream'
    att["Content-Disposition"] = 'attachment; filename=%s' % name
    return att


def sendmail(subject, text, attachment1=None, \
             attachment2=None, receiver='zhangzhijun@odianyun.com'):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    content = MIMEText('<b>' + text + '</b>', 'html')
    msgRoot.attach(content)
    if attachment1 and os.path.exists(attachment1):
        msgRoot.attach(genAttchment(attachment1))
    smtp = smtplib.SMTP_SSL()
    try:
        smtp.connect(SMTPSERVER)
    except:
        print 'can not connect'
        return
    smtp.login(USERNAME, PWD)
    if USEDEFAULTMAIL:
        try:
            receivers = getToMaillist()
        except Exception, e:
            print 'get mail list fail!'
            print e
            sys.exit()
    else:
        if receiver.find('@') > -1:
            receivers = receiver.split(';')
        else:
            return
    smtp.sendmail(SENDER, receivers, msgRoot.as_string())
    print 'send ok, please check your mail'
    #time.sleep(10)
    smtp.quit()

if __name__ == '__main__':
    sendmail(' test report', 'This E-mail sent automatically by the automation testing platform!', \
             attachment1 = 'x.html')