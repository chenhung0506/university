# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__), '.')  
dotenv_path = os.path.join(APP_ROOT, '../docker/test.env')
load_dotenv(dotenv_path)
print( os.getenv('IS_LOADED') + ", .env file path: " + dotenv_path )

PORT=os.environ.get('PORT', os.getenv('PORT'))
LOG_LEVEL=os.environ.get('LOG_LEVEL', os.getenv('LOG_LEVEL'))

DB_HOST=os.environ.get('DB_HOST', os.getenv('DB_HOST'))
DB_ACCOUNT=os.environ.get('DB_ACCOUNT', os.getenv('DB_ACCOUNT'))
DB_PASSWORD=os.environ.get('DB_PASSWORD', os.getenv('DB_PASSWORD'))

START_TIME=os.environ.get('START_TIME', os.getenv('START_TIME'))
END_TIME=os.environ.get('END_TIME', os.getenv('END_TIME'))
CALL_DIRECTION=os.environ.get('CALL_DIRECTION', os.getenv('CALL_DIRECTION'))
GET_TAG_API=os.environ.get('GET_TAG_API', os.getenv('GET_TAG_API'))
ENTERPRISE=os.environ.get('ENTERPRISE', os.getenv('ENTERPRISE'))
USER_ID=os.environ.get('USER_ID', os.getenv('USER_ID'))
TRANSMIT_CRON=os.environ.get('TRANSMIT_CRON', os.getenv('TRANSMIT_CRON'))
LOG_FOLDER_PATH=os.environ.get('LOG_FOLDER_PATH', os.getenv('LOG_FOLDER_PATH'))
TRANSMIT_ARMS_SLEEP_TIME=os.environ.get('TRANSMIT_ARMS_SLEEP_TIME', os.getenv('TRANSMIT_ARMS_SLEEP_TIME'))
TRANSMIT_ERROR_EMAIL_LIST=os.environ.get('TRANSMIT_ERROR_EMAIL_LIST', os.getenv('TRANSMIT_ERROR_EMAIL_LIST'))

SFTP_HOST_NAME=os.environ.get('SFTP_HOST_NAME', os.getenv('SFTP_HOST_NAME'))
SFTP_USER_NAME=os.environ.get('SFTP_USER_NAME', os.getenv('SFTP_USER_NAME'))
SFTP_PASS_WORD=os.environ.get('SFTP_PASS_WORD', os.getenv('SFTP_PASS_WORD'))
SFTP_CONE_PORT=os.environ.get('SFTP_CONE_PORT', os.getenv('SFTP_CONE_PORT'))
SFTP_UPLO_PATH=os.environ.get('SFTP_UPLO_PATH', os.getenv('SFTP_UPLO_PATH'))
SFTP_REMO_PATH=os.environ.get('SFTP_REMO_PATH', os.getenv('SFTP_REMO_PATH'))
SFTP_ANONYMOUS=os.environ.get('SFTP_ANONYMOUS', os.getenv('SFTP_ANONYMOUS'))
PUBLIC_KEY_HOST=os.environ.get('PUBLIC_KEY_HOST', os.getenv('PUBLIC_KEY_HOST'))
PUBLIC_KEY_HASH=os.environ.get('PUBLIC_KEY_HASH', os.getenv('PUBLIC_KEY_HASH'))
PUBLIC_KEY_DATA=os.environ.get('PUBLIC_KEY_DATA', os.getenv('PUBLIC_KEY_DATA')).replace("'", "")
IS_TAG_API_V1=os.environ.get('IS_TAG_API_V1', os.getenv('IS_TAG_API_V1'))
IS_FTP_UPLOAD=os.environ.get('IS_FTP_UPLOAD', os.getenv('IS_FTP_UPLOAD'))

SCENARIO_KEY=os.environ.get('SCENARIO_KEY', os.getenv('SCENARIO_KEY'))
SCEN_VAL_LEN=os.environ.get('SCEN_VAL_LEN', os.getenv('SCEN_VAL_LEN'))

CSV_FILE_BEG_TIME=''
CSV_FILE_END_TIME=''

API_CALL_RESULT=os.environ.get('API_CALL_RESULT', os.getenv('API_CALL_RESULT'))
API_CHAT_RECORDS=os.environ.get('API_CHAT_RECORDS', os.getenv('API_CHAT_RECORDS'))
ENTER_CCBOT_URL=str(os.environ.get('ENTER_CCBOT_URL', os.getenv('ENTER_CCBOT_URL'))).replace("'", "")

MANAGE_USER_API_IP=os.environ.get('MANAGE_USER_API_IP', os.getenv('MANAGE_USER_API_IP'))
ENTERPRISE_SERIAL=os.environ.get('ENTERPRISE_SERIAL', os.getenv('ENTERPRISE_SERIAL'))
SSO_VERIFY_API=os.environ.get('SSO_VERIFY_API', os.getenv('SSO_VERIFY_API'))
SSO_DEFAULT_PWD=str(os.environ.get('SSO_DEFAULT_PWD', os.getenv('SSO_DEFAULT_PWD'))).replace("'", "")
BEARER_TOKEN=''
BFOP_SSO_LOGIN_URL=str(os.environ.get('BFOP_SSO_LOGIN_URL', os.getenv('BFOP_SSO_LOGIN_URL'))).replace("'", "")
REDIRECT_PATH=str(os.environ.get('REDIRECT_PATH', os.getenv('REDIRECT_PATH'))).replace("'", "")

EXTERNAL_IP=str(os.environ.get('EXTERNAL_IP', os.getenv('EXTERNAL_IP'))).replace("'", "")
LEAST_AUTH_USERNAME=str(os.environ.get('LEAST_AUTH_USERNAME', os.getenv('LEAST_AUTH_USERNAME'))).replace("'", "")
LEAST_AUTH_PASSWORD=str(os.environ.get('LEAST_AUTH_PASSWORD', os.getenv('LEAST_AUTH_PASSWORD'))).replace("'", "")

VERIFY_TOKEN_STATUS={
  "100" : "Success",
  "101" : "Log組態檔不存在 (Config File_WSSOVerifyCookies.xml)",
  "102" : "參數pszWSSOToken可能有空白或是不存在",
  "103" : "參數pszWSSOID可能有空白或是不存在",
  "104" : "參數pszUserIP可能有空白或是不存在",
  "105" : "參數pszURL可能有空白或是不存在",
  "106" : "INI檔不存在 (setting.ini)",
  "107" : "INI檔案讀取錯誤(讀取欄位沒定義或是沒有值?))",
  "108" : "無法在LDAP裡搜尋到傳入的帳號 ",
  "109" : "無法在帳號下裡搜尋到用戶IP位址 ",
  "110" : "入口網站TOKEN生命週期已過,請重新登入入口網站再使用行內網路系統",
  "111" : "入口網站TOKEN已超過期限,請重新登入入口網站再使用行內網路系統 ",
  "112" : "查詢LDAP時發生錯誤 (可能是在setting.ini裡的LDAP IP,PORT,帳號,密碼可能有錯誤)",
  "113" : "對WSSOToken做Base64解碼發生錯誤 ",
  "114" : "執行解密時發生錯誤,WSSOToken內容可能有錯誤造成無法解密 ",
  "115" : "此帳號無權限存取此系統",
  "116" : "此IP無權限存取此系統",
  "117" : "此帳號尚未啟用",
  "118" : "此帳號已停用",
  "119" : "員工已離職",
  "120" : "取得帳號狀態發生錯誤或帳號狀態無法辨別",
  "121" : "此Resource無法使用",
  "122" : "此Resource已停用",
  "123" : "取得Resource狀態發生錯誤或Resource狀態無法辨別",
  "124" : "此Resource要求的認證型態比目前用戶的認證型態要高",
  "125" : "取得Token Policy Info時發生錯誤",
  "126" : "帳號與TOKEN內帳號不符",
  "127" : "無法開啟LOG資料庫",
  "128" : "發生錯誤, 請查詢LOG"
}
