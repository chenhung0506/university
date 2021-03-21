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
    api.add_resource(Default, '/university/')
    api.add_resource(HealthCheck, '/healthCheck')
    api.add_resource(GetChatRecords, '/getChatRecords')
    api.add_resource(StaticResource, '/university/<path:filename>')

class StaticResource(Resource):
    def get(self, filename):
        # root_dir = os.path.dirname(os.getcwd())
        # return send_from_directory( os.path.join(root_dir,'static'), filename)
        log.info(filename)
        return send_from_directory('./resource/university',  filename )

class Default(Resource):
    log.debug('check health')
    def get(self):
        return send_from_directory('./resource/university', 'index.html')

class HealthCheck(Resource):
    log.debug('check health')
    def get(self):
        return {"status": "200","message": "success"}, 200

class GetChatRecords(Resource):
    def get(self):
        callApi=service.CallApi()
        log.info('GetChatRecords api start')
        response = callApi.getChatRecords("1e8fc05f-6c04-4333-a5b9-436fd5663f7b")
        log.info(response)
        return {
            'message': str(response)
        }, 200
    def post(self):
        callApi=service.CallApi()
        log.info('GetChatRecords api start')
        response = callApi.getChatRecords("1e8fc05f-6c04-4333-a5b9-436fd5663f7b")
        log.info(response)
        return {
            'message': str(response)
        }, 200
