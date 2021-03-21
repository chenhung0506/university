import log as logpy
import sys
import traceback
import service
import const
import os
import csv
import smtplib, ssl
import pysftp
import paramiko
import hashlib
import re
import unicodedata
import string
from ftplib import FTP
from base64 import decodebytes
from threading import Timer,Thread,Event
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header
from werkzeug.datastructures import ImmutableMultiDict

log = logpy.logging.getLogger(__name__)

def except_raise(e):
    error_class = e.__class__.__name__ #取得錯誤類型
    detail = e.args[0] #取得詳細內容
    cl, exc, tb = sys.exc_info() #取得Call Stack
    lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
    #print(tb)
    fileName = lastCallStack[0] #取得發生的檔案名稱
    lineNum = lastCallStack[1] #取得發生的行號
    funcName = lastCallStack[2] #取得發生的函數名稱
    errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
    return errMsg

sched = BackgroundScheduler()

def prepare_batch_blocking(job,args):
    # sched.shutdown()
    sched.add_job(job, CronTrigger.from_crontab(const.TRANSMIT_CRON))
    sched.start()
    return "Start scheduler id: " + str(sched.get_jobs())

def stop_batch():
    sched.remove_all_jobs()
    # sched.remove_all_jobs(jobstore=None)
    # sched.shutdown()
    return "Stop scheduler id: " + str(sched.get_jobs())

def prepare_batch_background(job,cronStr):
    sched.add_job(job, CronTrigger.from_crontab(cronStr))
    try: 
        sched.start()
    except Exception as e:
        log.info(e)
    return "Start scheduler id: " + str(sched.get_jobs())

def setLogFileName():
    try:
        if not os.path.exists(const.LOG_FOLDER_PATH):
            os.makedirs(const.LOG_FOLDER_PATH)
    except OSError as e:
        print(e)
    conf={}
    conf['name'] = datetime.today().strftime('%Y-%m-%d') + '-log.log'
    conf['verbose'] = const.LOG_LEVEL
    conf['log_path'] = const.LOG_FOLDER_PATH
    conf['log_file'] = conf['log_path'] + conf['name']
    print(conf['log_file'])
    logpy.setup_logging(conf)
    log.info("change log file name to:" + conf['name'])

def arrayToList(array):
    list=[]
    for str in array:
        list.append(str)
    return list

def sendEmail(receiver,msg):
    smtpUserName = "emotibot.alert.mail@gmail.com"
    smtpUserPassword = "Emotibot@1"
    senderEmail = "emotibot.alert.mail@gmail.com"
    receiverEmail = receiver
    subject = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d %H:%M:%S') + " AICC transmit to Arms Alert Mail"
    mail_msg = "<p>" + subject + "</p>" + msg 
    log.info(mail_msg)
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = Header("emotibot.alert.mail", "utf-8")
    message['To'] = Header("chenhunglin@emotibot.com", "utf-8")
    message['Subject'] = Header(subject, "utf-8")
    # smtpObj = smtplib.SMTP( [host [, post [, local_hostname]]])
    try:
        smtpObj = smtplib.SMTP("smtp.gmail.com", 587)
        # smtpObj = smtplib.SMTP()
        print ("SMTP Init")
        smtpObj.connect("smtp.gmail.com", 587)
        print ("SMTP Connect")
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        print ("SMTP ehlo")
        smtpObj.login(smtpUserName, smtpUserPassword)
        print ("SMTP Login")
        smtpObj.sendmail(senderEmail, receiverEmail, message.as_string())
        print ("Email Sent")
    except smtplib.SMTPException as error:
        print (str(error))
        print ("Error: Cannot Send Email")

def exportCsv(path, data):
    with open(path, 'w', newline='', encoding='Big5') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for row in data:
            writer.writerow(row)

def sftpUpload(uploadFileList):
    try:
        sHostName = str(const.SFTP_HOST_NAME)
        sUserName = str(const.SFTP_USER_NAME)
        sPassWord = str(const.SFTP_PASS_WORD)
        ConecPort = int(const.SFTP_CONE_PORT)

        keydata = bytes(const.PUBLIC_KEY_DATA, 'utf-8')
        key = paramiko.RSAKey(data=decodebytes(keydata))
        cnopts = pysftp.CnOpts()
        # cnopts = pysftp.CnOpts(knownhosts='known_hosts')
        cnopts.hostkeys.add(const.PUBLIC_KEY_HOST, const.PUBLIC_KEY_HASH, key)

        # pysftp.CnOpts(knownhosts='known_hosts')
        cnopts.hostkeys = None

        with pysftp.Connection(sHostName, username=sUserName, password=sPassWord, cnopts=cnopts, port=ConecPort) as sftp:
            sftp.cwd(const.SFTP_REMO_PATH)
            # sftp.put_d(uploadData,const.SFTP_REMO_PATH)
            for file in uploadFileList:
                log.info("ftp upload file: " + file)
                try:
                    sftp.put(file)
                except Exception as e:
                    log.error("sftp upload error: " + except_raise(e))
                    return except_raise(e)
        sftp.close()

    except Exception as e:
        log.error("transmitProcess error: " + except_raise(e))
        return except_raise(e)

def ftpUpload(uploadFileList):
    log.info(uploadFileList)
    sHostName = str(const.SFTP_HOST_NAME)
    ConecPort = int(const.SFTP_CONE_PORT)
    sUserName = str(const.SFTP_USER_NAME)
    sPassWord = str(const.SFTP_PASS_WORD)
    anonymous = str(const.SFTP_ANONYMOUS)

    try:
        ftp=FTP() 
        ftp.set_debuglevel(2) 
        ftp.connect(sHostName,ConecPort) 
        log.info('login ftp server')
        if anonymous == 'true':
            ftp.login()
        else:
            ftp.login(sUserName,sPassWord)
        log.info('change folder')
        ftp.cwd(const.SFTP_REMO_PATH) 
        for file_path in uploadFileList:
            log.info('upload file: ' + file_path)
            ftp.storbinary('STOR ' + os.path.basename(file_path), open(file_path,'rb'), 1024)  
        ftp.set_debuglevel(0) 
        ftp.quit 
    except Exception as e:
        log.error("transmitProcess error: " + except_raise(e))
        return except_raise(e)

def cleanFolder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            log.error("transmitProcess error: " + except_raise(e))
            return except_raise(e)

def md5(input):
    m = hashlib.md5()
    m.update(input.encode("utf-8"))
    return m.hexdigest()

def editImmutableMultiDic(input_imd, key, value):
    try:
        log.info('before:')
        log.info(input_imd)
        dic_args = input_imd.to_dict()
        dic_args[key] = value
        new_imd = ImmutableMultiDict(dic_args)
        log.info('after:')
        log.info(new_imd)
        return new_imd
    except Exception as e:
        log.error("editImmutableMultiDic error: " + except_raise(e))
        return except_raise(e)



valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

def clean_filename(filename, whitelist=valid_filename_chars, replace=' '):
    # replace spaces
    for r in replace:
        filename = filename.replace(r,'_')
    
    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('utf-8', 'ignore').decode()
    log.info(cleaned_filename)
    # keep only whitelisted chars
    # cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    _filename_ascii_add_strip_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF.-]')
    cleaned_filename = str(_filename_ascii_add_strip_re.sub('', '_'.join( cleaned_filename.split()))).strip(':_')
    log.info(cleaned_filename)
    if len(cleaned_filename)>char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]
    #'fake_folder/\[]}{}|~`"\':;,/? abcABC 0123 !@#$%^&*()_+ clᐖﯫⅺຶ 讀ϯՋ㉘ ⅮRㇻᎠ⍩ 𝁱C ℿ؛ἂeuឃC ᅕ ᑉﺜͧ bⓝ s⡽Հᛕ\ue063 牢𐐥er ᐛŴ n წş .ھڱ                                 df                                         df                                  dsfsdfgsg!zip'