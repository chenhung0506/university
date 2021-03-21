import const
from datetime import datetime, timedelta
from opencc import OpenCC
from urllib import parse
import re
import log
import json
import requests
import math
import time
import utils
import uuid
from hashlib import sha256
from Crypto.Cipher import AES
import base64

log = log.logging.getLogger(__name__)

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

class CallApi(object):
    def post_request(self, url, headers, data):
        try:
            if headers.get("Content-Type") == "application/json":
                log.debug("application/json")
                data = json.dumps(data)
            elif headers.get("Content-Type") == "application/x-www-form-urlencoded":
                log.debug("application/x-www-form-urlencoded")
                data = parse.urlencode(data)

            log.info("call api: " + str(url) + "\nwith data: " + str(json.dumps(data)))
            log.info("header: " + str(json.dumps(headers)))
            response = requests.request("POST", url, data=data, headers=headers)
            if response.status_code != 200:
                raise Exception('Response status: ' + str(response.status_code) + ', message: ' + response.text)
            return response

        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)

    def get_request(self, url, headers):
        try:
            log.info("call api: " + url)
            log.debug("header: " + str(headers))
            response = requests.request("GET", url, headers=headers)
            if response.status_code != 200:
                raise Exception('Response status: ' + str(response.status_code) + ', message: ' + response.text)
            return response

        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)

    def get_auth_token(self, account, password):
        url = "http://{host_ip}/auth/v3/login".format(host_ip=const.MANAGE_USER_API_IP)
        headers = { "Content-Type": "application/x-www-form-urlencoded" }
        data = {"account": account, "passwd": utils.md5(password)}

        response = self.post_request(url, headers, data)
        dic_resp = json.loads(response.text)
        log.info(dic_resp)
        token = dic_resp.get('result').get('token')
        return token

    def encrypt_aes_ecb(self, msg, key):
        sha = sha256(key.encode()).hexdigest()[:16]
        raw = pad(msg)
        log.info('msg = '+ msg + ', key = ' + key + ', sha = ' + sha)
        cipher = AES.new(sha, AES.MODE_ECB)
#        log.info(base64.b64encode(cipher.encrypt(raw)).decode('utf-8')) #
        enc = base64.urlsafe_b64encode(cipher.encrypt(raw)).decode('utf-8')
        log.info(enc)
        return enc
