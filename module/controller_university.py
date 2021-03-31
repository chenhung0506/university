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
from datetime import datetime, timedelta
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class UploadPdf(Resource):
    def post(self):
        token = request.cookies.get('access_token')
        log.info(token)
        if utils.JWTdecode(token) == False:
            return redirect("/login", code=302)
        file = request.files['file']
        log.info(file.content_length)
        if file and allowed_file(file.filename):
            filename_ok = utils.clean_filename(file.filename)
            log.info('file name: ' + filename_ok)
            file.save(os.path.join('./university/upload', filename_ok))
            return {"data":filename_ok, "status": 200, "message":"success"}, 200
        else:
            log.info('valid sub filename')
            # return Response({"status": 400, "message":"錯誤檔案格式"},status=500)
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
            token = request.cookies.get('access_token')
            log.info(token)
            if utils.JWTdecode(token) == False:
                return redirect("/login", code=302)
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
            token = request.cookies.get('access_token')
            log.info(token)
            if utils.JWTdecode(token) == False:
                return redirect("/login", code=302)
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
            token = request.cookies.get('access_token')
            log.info(token)
            if utils.JWTdecode(token) == False:
                return redirect("/login", code=302)
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
            user = json.loads(request.data).get("user")
            key='super-secret'
            algorithm = "HS256"
            payload={
                "iss":"university", # (Issuer) Token 的發行者
                "sub": user, # (Subject) 也就是使用該 Token 的使用者
                'exp': datetime.utcnow(), # (Expiration Time) Token 的過期時間
                'nbf': datetime.utcnow(), # (Not Before) Token 的生效時間
                'iat': datetime.utcnow(), # (Issued At) Token 的發行時間
                }
            log.info(datetime.utcnow())
            log.info(payload)
            token = jwt.encode(payload, key, algorithm)
            log.info (token)
            # de_token = jwt.decode(token, 'key', audience='www.example.com', issuer='university', algorithm=algorithm, verify=True)
            de_token = jwt.decode(token, key ,algorithm)
            log.info(de_token)

        except Exception as e:
            log.error("JWT error: "+utils.except_raise(e))
            return 'false'

# curl --location --request POST 'http://localhost:8336/university/jwt' --header 'Content-Type: application/json' --data '{"user":"deployer"}'
# curl --location --request POST 'http://localhost:8336/university/jwt/encode' --header 'Content-Type: application/json' --data '{"user":"deployer"}'
# curl --location --request POST 'http://localhost:8336/university/jwt/decode' --header 'Content-Type: application/json' --data '{"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxMjcuMC4wLjEiLCJzdWIiOiJkZXBsb3llciIsImV4cCI6MTYxNjU1MjcwMiwibmJmIjoxNjE2NTUyNjQyLCJpYXQiOjE2MTY1NTI2NDJ9.i_Dwb-si0GMJfN6GPiUZyOpCHmL6iyTVZZaPHlCXiZI"}'

