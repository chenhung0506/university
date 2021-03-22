# -*- coding: utf-8 -*-
from flask import Flask
# from flask_cors import CORS
import log as logpy
import re
import os
import const
import controller
import controller_recaptcha
import controller_university
#import controller_ccui
import flask_restful
import utils
import json
import service
from flask_restful import Api
from flask_restful import Resource
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

utils.setLogFileName()
log = logpy.logging.getLogger(__name__)
template_dir = os.path.abspath('./resource/university/') # setting for render_template
app = Flask(__name__, template_folder=template_dir)
# app.config['UPLOAD_FOLDER'] = './univer/upload'
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024  # 16MB
api = Api(app)
controller.setup_route(api)
controller_recaptcha.setup_route(api)
controller_university.setup_route(api)
# setting for send_from_directory
# app.static_folder = os.path.abspath("resource/university/")
# app.static_url_path = os.path.abspath("resource/university/")
app.config['CORS_HEADERS'] = 'Content-Type'

if __name__=="__main__":
    # utils.setLogFileName()
    try:
        if not os.path.exists("./data_for_KG/"):
            os.makedirs("./data_for_KG/")
    except OSError as e:
        log.info(e)
    sched = BackgroundScheduler()
    sched.start()
    sched.add_job(utils.setLogFileName, CronTrigger.from_crontab('59 23 * * *'))
    # controller.transmitProcess(None)
    # sched.add_job(controller.transmitProcess, CronTrigger.from_crontab(const.TRANSMIT_CRON), [None])
    app.run(host="0.0.0.0", port=const.PORT, debug=True, use_reloader=False)