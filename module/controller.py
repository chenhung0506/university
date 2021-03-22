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
import dao
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
    api.add_resource(Default, '/')
    api.add_resource(Admin, '/admin/')
    api.add_resource(University, '/university/')
    api.add_resource(AdminStaticResource, '/admin/<path:filename>')
    api.add_resource(UniversityStaticResource, '/university/<path:filename>')
    api.add_resource(UploadStaticResource, '/university/upload/<path:filename>')

class HealthCheck(Resource):
    log.debug('check health')
    def get(self):
        return {"status": "200","message": "success"}, 200


class AdminStaticResource(Resource):
    def get(self, filename):
        # root_dir = os.path.dirname(os.getcwd())
        # return send_from_directory( os.path.join(root_dir,'static'), filename)
        log.info(filename)
        return send_from_directory('./resource/admin',  filename )

class Admin(Resource):
    log.debug('check health')
    def get(self):
        return send_from_directory('./resource/admin', 'index.html')

class UniversityStaticResource(Resource):
    def get(self, filename):
        # root_dir = os.path.dirname(os.getcwd())
        # return send_from_directory( os.path.join(root_dir,'static'), filename)
        log.info(filename)
        return send_from_directory('./resource/university',  filename )

class UploadStaticResource(Resource):
    def get(self, filename):
        log.info(filename)
        return send_from_directory('./university/upload',  filename )

class University(Resource):
    def get(self):
        return send_from_directory('./resource/university', 'index.html')

class Default(Resource):
    def get(self):
        return redirect(url_for('university'))