# coding=UTF-8
import requests
import json
import time
import re
import ast
import logging
import os
import math
import time
import ctypes 
import threading
from datetime import datetime
from flask import Flask, Response, render_template, request, redirect, jsonify, send_from_directory, url_for, make_response
from threading import Timer,Thread,Event
import const
from flask_restful import Resource
import log as logpy
import pymysql
import service
import service_sso
import utils
from datetime import datetime

log = logpy.logging.getLogger(__name__)

def setup_route(api):
    api.add_resource(HealthCheck, '/healthCheck')
    # api.add_resource(Default, '/')
    api.add_resource(Login, '/login')
    api.add_resource(Admin, '/admin/')
    api.add_resource(University, '/')
    api.add_resource(UniversityStaticResource, '/<path:filename>')
    api.add_resource(AdminStaticResource, '/admin/<path:filename>')
    api.add_resource(UploadStaticResource, '/university/upload/<path:filename>')
    api.add_resource(ValidUser, '/university/valid')
    api.add_resource(LogOut, '/university/logout')

class HealthCheck(Resource):
    log.debug('check health')
    def get(self):
        return {"status": "200","message": "success"}, 200

# class Default(Resource):
#     def get(self):
#         return redirect(url_for('university'))

class AdminStaticResource(Resource):
    def get(self, filename):
        log.info(filename)
        token = request.cookies.get('access_token')
        log.info(token)
        if utils.JWTdecode(token):
            return send_from_directory('./resource/admin',  filename )
        else:
            return redirect("/login", code=302)
        

class Admin(Resource):
    log.debug('check health')
    def get(self):
        token = request.cookies.get('access_token')
        log.info(token)
        if utils.JWTdecode(token):
            return send_from_directory('./resource/admin', 'index.html')
        else:
            return redirect("/login", code=302)

class Login(Resource):
    log.debug('check health')
    def get(self):
        return send_from_directory('./resource', 'login.html')

class UniversityStaticResource(Resource):
    def get(self, filename):
        # root_dir = os.path.dirname(os.getcwd())
        # return send_from_directory( os.path.join(root_dir,'static'), filename)
        log.info(filename)
        return send_from_directory('./resource',  filename )

class UploadStaticResource(Resource):
    def get(self, filename):
        log.info(filename)
        return send_from_directory('./university/upload',  filename )

class University(Resource):
    def get(self):
        return send_from_directory('./resource', 'index.html')

class LogOut(Resource):
    def post(self):
        try:
            r = Response(json.dumps({"data": "log out success"}), mimetype='application/json')
            r.set_cookie('access_token', '', expires=0)
            return r
        except Exception as e:
            log.error("validate JWT error: "+utils.except_raise(e))
            return redirect("/login", code=302)
class ValidUser(Resource):
    def post(self):
        try:
            user = json.loads(request.data).get("account")
            password = json.loads(request.data).get("password")
            if utils.validUser(user,password):
                log.info('login success')
                token = utils.JWTencode(user, request.remote_addr)
                r = Response(json.dumps({"data": "login success"}), mimetype='application/json')
                r.set_cookie(key='access_token', value=token, expires=time.time()+60*60*1)
                return r
            return redirect("/login", code=302)
            # return Response(json.dumps({"status": "200","data": "Login fail, account or password mistake!"}), mimetype='application/json',status=400)

        except Exception as e:
            log.error("validate JWT error: "+utils.except_raise(e))
            return redirect("/login", code=302)