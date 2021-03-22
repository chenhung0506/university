# coding=UTF-8
import os
import requests
import json
import time
import logging 
import threading
import base64
import hmac
import hashlib 
import binascii
import re
from datetime import datetime
from flask import Flask, Response, render_template, request, redirect, jsonify, send_from_directory, url_for, make_response
from threading import Timer,Thread,Event
from flask_restful import Resource
import const
import utils
import jwt
import dao_university
import log as logpy
from urllib.parse import urlencode
from urllib.request import urlopen

log = logpy.logging.getLogger(__name__)
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif', 'MP4'])


# https://stackoverflow.com/questions/46393162/how-to-validate-a-recaptcha-response-server-side-with-python
# https://codesandbox.io/s/n3p4y?file=/src/App.vue

def setup_route(api):
    api.add_resource(GetUniversity, '/university/getUniversity')
    api.add_resource(EditUniversity, '/university/editUniversity')
    api.add_resource(AddUniversity, '/university/addUniversity')
    api.add_resource(DelUniversity, '/university/delUniversity')
    api.add_resource(UploadPdf, '/university/uploadPdf')
    api.add_resource(JWT, '/university/jwt')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class UploadPdf(Resource):
    def post(self):
        file = request.files['file']
        log.info(file.content_length)
        if file and allowed_file(file.filename):
            filename_ok = utils.clean_filename(file.filename)
            log.info('file name: ' + filename_ok)
            file.save(os.path.join('./university/upload', filename_ok))
            return {"data":filename_ok, "status": 200, "message":"success"}, 200
        else:
            log.info('valid sub filename')
            return {"status": 400, "message":"錯誤檔案格式"}, 200

class GetUniversity(Resource):
    def post(self):
        try:
            data = {}
            if request.data :
                input_data = json.loads(request.data)
                if input_data.get("u_id"):
                    log.info(input_data)
                    data = dao_university.Database().getUniversity(input_data)
            else:
                data = dao_university.Database().getUniversity(None)
            log.info(data)
            # return {"data":data},200
            return {"data":data, "status": 200, "message":"success"}, 200
        except Exception as e:
            log.error("GetUniversity error: "+utils.except_raise(e))
            return {"status":400, "message":"get data error: {}".format(e)}, 200

class EditUniversity(Resource):
    def post(self):
        try:
            input_data = json.loads(request.data)
            log.info(input_data)
            univerList = dao_university.Database().getUniversity(input_data)
            if len(univerList) < 1:
                return {"status":400, "message":"更新失敗，學校 [ "+input_data.get('u_name')+" ] 不存在"},200
            result = dao_university.Database().editUniversity(input_data)
            log.info('edit result:' + str(result))
            if result:
                data = dao_university.Database().getUniversity(input_data)
                log.info(data)
                return {"data":data, "status": 200, "message":"success"}, 200
        except Exception as e:
            log.error("EditUniversity error: "+utils.except_raise(e))
            return {"status":400, "message":"edit error: {}".format(e)}, 200

class AddUniversity(Resource):
    def post(self):
        try:
            input_data = json.loads(request.data)
            log.info(input_data)
            univerList = dao_university.Database().getUniversity(input_data)
            if len(univerList) > 0:
                return {"status":400, "message":"新增失敗，學校 [ "+input_data.get('u_name')+" ] 已存在"},200
            result = dao_university.Database().addUniversity(input_data)
            if result:
                data = dao_university.Database().getUniversity(None)
                return {"data":data, "status": 200, "message":"success"}, 200
        except Exception as e:
            log.error("AddUniversity error: "+utils.except_raise(e))
            return {"status":400, "message":"insert error: {}".format(e)}, 200

class DelUniversity(Resource):
    def post(self):
        try:
            input_data = json.loads(request.data)
            log.info(input_data)
            data = dao_university.Database().delUniversity(input_data)
            log.info(data)
            if data:
                return {"status": 200, "message":"success"}, 200
            else:
                return {"status": 401, "message":"delete fail"}, 401
        except Exception as e:
            log.error("DelUniversity error: "+utils.except_raise(e))
            return {"status":400, "message":"delete error: {}".format(e)}, 200

# https://medium.com/mr-efacani-teatime/%E6%B7%BA%E8%AB%87jwt%E7%9A%84%E5%AE%89%E5%85%A8%E6%80%A7%E8%88%87%E9%81%A9%E7%94%A8%E6%83%85%E5%A2%83-301b5491b60e
# https://myapollo.com.tw/zh-tw/python-json-web-token/
class JWT(Resource):
    def post(self):
        try:
            key='super-secret'
            payload={"id":"1","email":"myemail@gmail.com" }
            token = jwt.encode(payload, key)
            log.info (token)
            # decoded = jwt.decode(token, verify=False) 
            decoded = jwt.decode(token, options={"verify_signature": False}) # works in PyJWT >= v2.0
            log.info(decoded)
            log.info(decoded["user"])

        except Exception as e:
            log.error("Recaptcha error: "+utils.except_raise(e))
            return 'false'


# def secure_filename(filename):
#     if isinstance(filename, text_type):
#         from unicodedata import normalize
#         filename = normalize("NFKD", filename).encode("utf-8", "ignore")
#         if not PY2:
#             filename = filename.decode("utf-8")
#     for sep in os.path.sep, os.path.altsep:
#         if sep:
#             filename = filename.replace(sep, " ")
#     _filename_ascii_add_strip_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF.-]')
#     filename = str(_filename_ascii_add_strip_re.sub('', '_'.join(filename.split()))).strip('._')
#     if (
#         os.name == "nt"
#         and filename
#         and filename.split(".")[0].upper() in _windows_device_files
#     ):
#         filename = "_" + filename

#     return filename