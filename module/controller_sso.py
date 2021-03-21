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
import dao
import const
import urllib
from datetime import datetime
import log as logpy
import pymysql
import service_sso
import utils
from flask import Flask, Response, render_template, request, redirect, jsonify, send_from_directory, url_for, make_response
from threading import Timer,Thread,Event
from flask_restful import Resource
from datetime import datetime

log = logpy.logging.getLogger(__name__)

def setup_route(api):
    api.add_resource(Login, '/customized/login_test/')
    api.add_resource(SSOLogin, '/customized/SSOLogin')
    api.add_resource(SSOVerify, '/customized/SSOVerify')
    api.add_resource(ManageUser, '/customized/ManageUser')
    api.add_resource(GetWholeRobotId, '/customized/getWholeRobotId')
    api.add_resource(GetRoleList, '/customized/getRoleList')
    api.add_resource(GetUserList, '/customized/getUserList')
    api.add_resource(DeleteUser, '/customized/deleteUser')

class Login(Resource):
    log.debug('check health')
    def get(self):
        return send_from_directory('./resource', 'login_test.html')

class SSOLogin(Resource):
    def get(self):
        try:
            TOKEN = request.cookies.get('TOKEN')
            WSSOID = request.cookies.get('WSSOID')
            ACCTID = request.cookies.get('ACCTID')
            UserIP = request.remote_addr
            if request.args.get('userip') != None:
                UserIP = request.args.get('userip')
            URL = request.cookies.get('URL')
            log.info(request.cookies)
            # if TOKEN == None or WSSOID == None or ACCTID == None:
                # return encode({"ReturnStatus":"400|missing necessary parameter TOKEN, WSSOID, ACCTID"}, 400)
            log.info('TOKEN: ' + str(TOKEN) + ', WSSOID: ' + str(WSSOID) + ', UserIP:' + str(UserIP) + ', URL:' +  str(URL))

            # Verify SSO_Token
            url = const.SSO_VERIFY_API
            headers = { "Content-Type": "text/plain", "Accept":"text/plain" }
            if request.headers.getlist("X-Forwarded-For"):
                UserIP = request.headers.getlist("X-Forwarded-For")[0]
            else:
                UserIP = request.remote_addr
            # UserIP='10.86.53.26'
            url = url + '?pszWSSOToken='+ str(TOKEN) + '&pszWSSOID=' + str(WSSOID) + '&pszUserIP=' + str(UserIP) + '&pszURL=' + str('botu.kgibank.com')
            log.info('call sso verify api url:::' + url)

            try: 
                callApi=service_sso.CallApi()
                response = callApi.get_request(url, headers)
                log.info(str(response))
                if str(response) != '<Response [200]>':
                    return errorPage('call verify token api fail')
                    # return encode({"ReturnStatus":"400|call verify token api fail"},400)
                log.info(response.text)
                verify_token_return_code=''
                regex = re.search('^(Code=){1}(\d{3})(&){1}', response.text)
                if regex:
                    verify_token_return_code=regex.group(2)
                log.info('verify_token_return_code:' + str(verify_token_return_code))
                log.info(const.VERIFY_TOKEN_STATUS.get(verify_token_return_code))
                if str(verify_token_return_code) != '100':
                    return errorPage('ReturnStatus: ' + str(verify_token_return_code) + ', message: ' + const.VERIFY_TOKEN_STATUS.get(verify_token_return_code) )
                    # return encode({"ReturnStatus": str(verify_token_return_code) + "|" + const.VERIFY_TOKEN_STATUS.get(verify_token_return_code)},400)

            except Exception as e:
                log.error("call verify token api occurring error: " + utils.except_raise(e))
                return errorPage("call verify token api occurring error: " + utils.except_raise(e))
                # return encode({'ReturnStatus': '403|'+str(e.args[0]) }, 403)

            # if dic_resp['status'] != 200:
            #     return {'status': 204,'result': 'SSO verify fail'}, 204

            url = "http://{host_ip}/auth/v3/login".format(host_ip=const.MANAGE_USER_API_IP)
            headers = { "Content-Type": "application/x-www-form-urlencoded" }
            data = {"account": ACCTID, "passwd": utils.md5(const.SSO_DEFAULT_PWD)}
            callApi=service_sso.CallApi()
            response = callApi.post_request(url, headers, data)
            dic_resp = json.loads(response.text)
            # log.info(dic_resp)
            token = dic_resp.get('result').get('token')
            redirect_url = const.BFOP_SSO_LOGIN_URL + token
            log.info(redirect_url)
            return redirect(redirect_url,302)
            # response = make_response(redirect(const.BFOP_SSO_LOGIN_URL + token))
            # response.headers.add('Access-Control-Allow-Credentials', 'true')
            # response.headers["Authorization"] = "Bearer " + token

            # log.info(response.headers)
            # return response

        except Exception as e:
            log.error("SSOLogin process error: " + utils.except_raise(e))
            return errorPage('SSOLogin process error')
            # return encode({'ReturnStatus': '403|' + str(e.args[0])}, 403)

class SSOVerify(Resource):
    def post(self):
        json_from_request = json.loads(request.stream.read().decode('utf-8'))
        log.info(json_from_request)
        return {
            'status': 200,
            'result': 'verify success'
        }, 200

class GetUserList(Resource):
    def get(self):
        return getUserList(request)

class DeleteUser(Resource):
    def get(self):
        return deleteUser(request)

class ManageUser(Resource):
    def get(self):
        try:
            refreshBearToken(request)
            args = request.args
            log.info('execute ManagerUser with ActionType:' + args.get('ActionType'))
            if args.get('ActionType') == u'ADD' or args.get('ActionType') == u'EDIT':
                checkArgsList=['Userid', 'UserCName', 'UserEmail', 'Role', 'ActionType']
                for arg in checkArgsList:
                    if args.get(arg) == None:
                        return encode({'ReturnStatus':'400|error, missing necessary parameter [{arg}]'.format(arg=arg),}, 400)
                # 如果UserList中找得到該帳號表示該帳號之前被隱藏，需把帳號打開並更改ActionType為EDIT，走一遍EDIT流程
                log.info(args.get('ActionType'))
                if args.get('ActionType') == u'ADD':
                    user_uuid = getUserList(request).get(args.get('Userid'))
                    if user_uuid != None:
                        hide_resp = hide_user(request, 1)
                        hide_resp_code = hide_resp.status_code
                        log.info(hide_resp_code)
                        if hide_resp_code != 200:
                            return hide_resp
                        new_args = utils.editImmutableMultiDic(args, 'ActionType', u'EDIT')
                        request.args = new_args
                return add_update_user(request)
            elif args.get('ActionType') == u'QUERY':
                checkArgsList=['ActionType', 'objectType']
                for arg in checkArgsList:
                    if args.get(arg) == None:
                        return encode({'ReturnStatus':'400|error, missing necessary parameter [{arg}]'.format(arg=arg)}, 400)
                result = getUserList(request)
                log.info(result)
                return result
            elif args.get('ActionType') == u'DEL':
                checkArgsList=['Userid', 'ActionType']
                for arg in checkArgsList:
                    if args.get(arg) == None:
                        return encode({'ReturnStatus':'400|error, missing necessary parameter [{arg}]'.format(arg=arg)}, 400)
                status = 0
                if args.get('STATUS') == 'SHOW':
                    status = 1
                return hide_user(request, status)
            else:
                return encode({'ReturnStatus':'400|ActionType error'}, 400)
        except Exception as e:
            log.error("ManageUser error: "+utils.except_raise(e))
            return encode({'ReturnStatus':'500|'+utils.except_raise(e)}, 500)

class GetWholeRobotId(Resource):
    def get(self):
        return {
            'status': 200,
            'result': getRobotIdList(request)
        }, 200

class GetRoleList(Resource):
    def get(self):
        return {
            'status': 200,
            'result': getRoleList(request)
        }, 200

def encode(input,input_status):
    log.info(input)
    resp = Response(
        response=urllib.parse.urlencode(input, safe='=|&'),
        status=input_status,
        mimetype="text/plain"
    )
    return resp

def refreshBearToken(request):
    try:
        log.info('Refresh BearToken')
        url = "http://{host_ip}/auth/v3/login".format(host_ip=const.MANAGE_USER_API_IP)
        headers = { "Content-Type": "application/x-www-form-urlencoded" }
        data = {"account": "deployer", "passwd": "7e2ba10110f719dd65a0403305770b08"}
        callApi=service_sso.CallApi()
        response = callApi.post_request(url, headers, data)
        dic_resp = json.loads(response.text)
        token = dic_resp.get('result').get('token')
        log.debug(token)
        const.BEARER_TOKEN = token
    except Exception as e:
        log.error("refreshBearToken error: "+utils.except_raise(e))
        return utils.except_raise(e)

def getBearerToken(request):
    if const.BEARER_TOKEN == '':
        refreshBearToken(request)
    return const.BEARER_TOKEN

def errorPage(message):
    # 懶得寫regex
    message = message.replace("'","\'")
    message = message.replace('"','\"')
    message = message.replace('\n','')
    resp = make_response(render_template('login.html', message=message, redirect_path=const.REDIRECT_PATH))
    resp.headers['Content-type'] = 'text/html; charset=big-5'
    return resp

def getRobotIdList(request):
    try:
        url = "http://{host_ip}/auth/v4/enterprise/{enterprise}/apps".format(host_ip=const.MANAGE_USER_API_IP, enterprise=const.ENTERPRISE)
        log.info('getWholeRobotId: ' + url)
        headers={
          "Content-Type": "application/json",
          "Authorization": "Bearer " + getBearerToken(request)
        }
        # data = {"enterpriseId": const.ENTERPRISE}
        callApi=service_sso.CallApi()
        response = callApi.get_request(url, headers)
        dic_resp = json.loads(response.text)
        log.debug(dic_resp.get('result'))
        robot_id_list=[]
        for robot in dic_resp.get('result'):
            robot_id_list.append(robot.get('id'))
        return robot_id_list
    except Exception as e:
        log.error("getRobotIdList error: "+utils.except_raise(e))
        return utils.except_raise(e)

def getRoleList(request):
    try:
        url = "http://{host_ip}/permit/roles/{enterprise}".format(host_ip=const.MANAGE_USER_API_IP, enterprise=const.ENTERPRISE)
        log.info('getWholeRobotId: ' + url)
        headers={
          "Content-Type": "application/json",
          "Authorization": "Bearer " + getBearerToken(request)
        }
        # data = {"enterpriseId": const.ENTERPRISE}
        callApi=service_sso.CallApi()
        response = callApi.get_request(url, headers)
        dic_resp = json.loads(response.text)
        log.debug(dic_resp.get('result'))
        return dic_resp.get('result')
    except Exception as e:
        log.error("getRoleList error: "+utils.except_raise(e))
        return utils.except_raise(e)

def deleteUser(request):
    try:
        args = request.args
        Userid = getUserList(request)[args.get('Userid')]
        if request.args.get('Userid') == None:
            return encode({"status":"400|missing necessary key Userid"},400)
        url = "http://{host_ip}/permit/enterprise/{enterprise}/user/{Userid}/delete_user".format(host_ip=const.MANAGE_USER_API_IP, enterprise=const.ENTERPRISE, Userid=request.args.get('Userid'))
        log.info('deleteUser url: ' + url)
        headers={
          "Content-Type": "application/json",
          "Authorization": "Bearer " + getBearerToken(request)
        }
        data = {"id":request.args.get('Userid'),"status":0}
        callApi=service_sso.CallApi()
        response = callApi.post_request(url, headers, data)
        log.info(response.text)
        dic_resp = json.loads(response.text)
        log.info(dic_resp.get('result'))
        return dic_resp.get('result')
    except Exception as e:
        log.error("getRoleList error: "+utils.except_raise(e))
        return utils.except_raise(e)

def valid_update_role(request):
    try:
        url = "http://{host_ip}/permit/enterprise/{enterprise}/users".format(host_ip=const.MANAGE_USER_API_IP, enterprise=const.ENTERPRISE)
        log.info('getUserList: ' + url)
        headers={
          "Content-Type": "application/json",
          "Authorization": "Bearer " + getBearerToken(request)
        }
        # data = {"enterpriseId": const.ENTERPRISE}
        callApi=service_sso.CallApi()
        response = callApi.get_request(url, headers)
        dic_resp = json.loads(response.text)
        log.debug(str(json.dumps(dic_resp.get('result'))))

        args = request.args
        input_role = args.get('Role')

        result=''
        role=''
        for user in dic_resp.get('result'):
            if user.get('user_name') == args.get('Userid'):
                result = user
        log.debug(str(json.dumps(result)))
        if result == '':
            return False
        if result.get('type') == 1:
            role = "ADMIN"
        elif result.get('type') == 2:
            role = 'MEMBER'
            for roleObj in result.get('organization')[0].get('products')[1].get('roles').get('items'):
                if roleObj.get('rolename') == 'CC_BOT_MANAGER':
                    role = 'MANAGER'
        else:
            return False

        log.info('input_role: '+ str(input_role) + ', original_role: ' + str(role))

        if input_role == 'ADMIN' and role == 'MANAGER':
            return False
        elif input_role == 'ADMIN' and role == 'MEMBER':
            return False
        elif input_role == 'MANAGER' and role == 'ADMIN':
            return False
        elif input_role == 'MEMBER' and role == 'ADMIN':
            return False
        else:
            return True
    except Exception as e:
        log.error("getUserList error: "+utils.except_raise(e))
        return utils.except_raise(e)

def getUserList(request):
    try:
        url = "http://{host_ip}/permit/enterprise/{enterprise}/users".format(host_ip=const.MANAGE_USER_API_IP, enterprise=const.ENTERPRISE)
        log.info('getUserList: ' + url)
        headers={
          "Content-Type": "application/json",
          "Authorization": "Bearer " + getBearerToken(request)
        }
        # data = {"enterpriseId": const.ENTERPRISE}
        callApi=service_sso.CallApi()
        response = callApi.get_request(url, headers)
        dic_resp = json.loads(response.text)
        log.debug(str(json.dumps(dic_resp.get('result'))))

        args = request.args

        log.info('getUserList with objectType:'+ str(args.get('objectType')) +', Userid:' + str(args.get('Userid')))
        
        if args.get('objectType') == None or args.get('objectType') == u'User':
            user_map={}
            for user in dic_resp.get('result'):
                user_map[user.get('user_name')]=user.get('id')
            return user_map
        if args.get('objectType') == u'UserAuth':
            result=''
            for user in dic_resp.get('result'):
                if user.get('user_name') == args.get('Userid'):
                    result = user
            log.debug(str(json.dumps(result)))
            if result == '':
                return encode({'ReturnStatus':'403|Userid not exist'}, 403)

            if result.get('type') == 1:
                return encode({'ReturnStatus':'0|success','Role':'ADMIN'}, 200)
            elif result.get('type') == 2:
                role = 'MEMBER'
                for roleObj in result.get('organization')[0].get('products')[1].get('roles').get('items'):
                    if roleObj.get('rolename') == 'CC_BOT_MANAGER':
                        role = 'MANAGER'
                return encode({'ReturnStatus':'0|success','Role':role}, 200)
            else:
                return encode({'ReturnStatus':'403|invalid user'}, 403)
        elif args.get('objectType') == u'RoleAuth':
            # return encode({'ReturnStatus':0}) + '&' + encode({'Role':'ADMIN'}) + '&' + encode({'Role':'MANAGER'}) + '&' + encode({'Role':'MEMBER'}, 200)
            resp = Response(
                response="ReturnStatus=0|success&Role=MANAGER|MANAGER&Role=MEMBER|MEMBER",
                status=200,
                mimetype="text/plain"
            )
            return resp

    except Exception as e:
        log.error("getUserList error: "+utils.except_raise(e))
        return utils.except_raise(e)

# status: 0 hide user, status: 1 show user
def hide_user(request, status):
    try:
        args = request.args
        user_uuid = getUserList(request)[args.get('Userid')]
        log.info('user_uuid:' + user_uuid)
        url = "http://{host_ip}/permit/enterprise/{enterprise}/user/{user_uuid}/put_status".format(host_ip=const.MANAGE_USER_API_IP, enterprise=const.ENTERPRISE, user_uuid=user_uuid)
        log.info('disable user url: ' + url)
        headers={
          "Content-Type": "application/json",
          "Authorization": "Bearer " + getBearerToken(request)
        }

        data = {"id":user_uuid,"status":status}
        callApi=service_sso.CallApi()
        response = callApi.post_request(url, headers, data)
        log.info(response.text)
        dic_resp = json.loads(response.text)
        if dic_resp.get('status') == 0:
            return encode({'ReturnStatus':'0|success'}, 200)
        elif dic_resp.get('status') == -1:
            return encode({'ReturnStatus':'403|delete user fail'},403)
        else:
            return encode({'ReturnStatus':str(dic_resp.get('status')) + '|' + dic_resp.get('result')},dic_resp.get('status'))
    except Exception as e:
        log.error("delete_user error: "+utils.except_raise(e))
        return encode({'ReturnStatus': '500|' + utils.except_raise(e)},500)

def add_update_user(request):
    try:
        log.info('process add_update_user')
        args = request.args
        md5_password = utils.md5(const.SSO_DEFAULT_PWD)
        log.debug(md5_password)

        callApi=service_sso.CallApi()
        url = ''
        log.info('ActionType: ' + args.get('ActionType'))

        if args.get('ActionType') == u'ADD':
            url = "http://{host_ip}/permit/enterprise/{enterprise}/user".format(host_ip=const.MANAGE_USER_API_IP, enterprise=const.ENTERPRISE)
        elif args.get('ActionType') == u'EDIT':
            valid = valid_update_role(request)
            log.info('valid_update_role: ' + str(valid))
            if valid == False:
                return encode({'ReturnStatus':'403|illegal operation change role fail'},403)

            user_uuid = getUserList(request).get(args.get('Userid'))
            if user_uuid == None:
                return encode({'ReturnStatus':'403|UserId does not exist'},403)
            log.info('user_uuid:' + str(user_uuid))
            url = "http://{host_ip}/permit/enterprise/{enterprise}/user/{user_uuid}/put_user".format(host_ip=const.MANAGE_USER_API_IP, enterprise=const.ENTERPRISE,user_uuid=user_uuid)

        log.info('register user api: ' + url)

        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + getBearerToken(request)
        }

        organization = getOrganization(request, args.get('Role'))

        log.info(organization)
        # args.get('UserCName') 凱基中文名稱懶得轉碼直接 Userid 當中文名稱
        data = {
                  "type": 2,
                  "username": args.get('Userid'),
                  "name": args.get('Userid'),
                  "email": checkEmail(args.get('UserEmail')),
                  "phone": args.get('UserTel'),
                  "password": md5_password,
                  "status": 1,
                  "organization": getOrganization(request, args.get('Role'))
                }
        if args.get('ActionType') == u'EDIT':
            user_uuid = getUserList(request).get(args.get('Userid'))
            log.info('user_uuid:' + str(user_uuid))
            data['id'] = user_uuid
            del data['password']

        if args.get('Role') == u'ADMIN':
            data['type'] = 1

        response = callApi.post_request(url, headers, data)
        log.info("bfop permit response:")
        log.info(response.text)
        dic_resp = json.loads(response.text)
        log.info(dic_resp.get('message'))
        log.info(dic_resp.get('status'))
        log.info(dic_resp.get('result'))
        if dic_resp.get('status') == 0:
            return encode({'ReturnStatus':'0|success'},200)
        elif dic_resp.get('status') == -1:
            if dic_resp.get('message').find("同名用户已存在") != -1:
                return encode({'ReturnStatus':'403|user exist'},403)
            elif dic_resp.get('message').find("更新用户失败") != -1:
                return encode({'ReturnStatus':'403|updated user fail'},403)
            else:
                return encode({'ReturnStatus':'403|registered or updated user fail'},403)
        else:
            return encode({'ReturnStatus':str(dic_resp.get('status')) + '|' + dic_resp.get('result')},dic_resp.get('status'))
    except Exception as e:
        log.error("add_update_user error: "+utils.except_raise(e))
        return encode({'ReturnStatus':'500|' + utils.except_raise(e)},500)

def checkEmail(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):
        print("Valid Email")
        return email
    else:
        print("Invalid Email")
        return 'default@kgibank.com'


def getOrganization(request, Role):
    try:
        bf_privilegeSet, bf_rolesList, bf_str_value, cc_privilegeSet, cc_rolesList, cc_roleids = parsingRoleListForAddUserAPI( getRoleList(request), getRobotIdList(request), Role )
        organization =[
                        {
                          "value": int(const.ENTERPRISE_SERIAL),
                          "label": "凱基銀行電銷機器人",
                          "type": 1,
                          "products": [
                            {
                              "productid": 1,
                              "productname": "機器人平台",
                              "privilegeSet": bf_privilegeSet,
                              "rolesList": bf_rolesList,
                              "roleids": [],
                              "value": bf_str_value
                            },
                            {
                              "productid": 2,
                              "productname": "電話機器人",
                              "privilegeSet": cc_privilegeSet,
                              "rolesList": cc_rolesList,
                              "roleids": cc_roleids,
                              "value": "{\"apps\":{},\"groups\":{}}"
                            }
                          ],
                          "orgid": int(const.ENTERPRISE_SERIAL),
                          "orgtype": 1
                        }
                      ]

        return organization
    except Exception as e:
        log.error("transmitProcess error: "+utils.except_raise(e))
        return utils.except_raise(e)

def parsingRoleListForAddUserAPI(input_roleList, robotIdList, ROLE):
    roleIdMappingName={}
    for input_role in input_roleList:
        if input_role.get('product') != 1:
            continue
        roleIdMappingName[input_role.get('name')]=input_role.get('uuid')
    log.debug("roleIdMappingName: " + str(roleIdMappingName))

    bf_privilegeSet=[]
    if ROLE == 'ADMIN':
        bf_privilegeSet=[{"id": "","role_ccbot": 2}]
    else:
        for robotId in robotIdList:
            record={"id":robotId, "role_bf": roleIdMappingName.get('BF_BOT_' + ROLE)}
            bf_privilegeSet.append(record)
    log.debug("bf_privilegeSet: " + str(bf_privilegeSet))

    bf_value = {"apps":{}, "groups":{}}
    if ROLE != 'ADMIN':
        for data in bf_privilegeSet:
            bf_value.get("apps")[data.get("id")]=[data.get("role_bf")]
    bf_str_value = json.dumps(bf_value)
    log.debug(bf_str_value)

    bf_rolesList=[]
    for input_role in input_roleList: 
        if input_role.get('uuid') == None:
            continue
        role = {
            "value": input_role.get('uuid'),
            "label": input_role.get('name'),
            "product": input_role.get('product'),
            "roleid": input_role.get('roleid'),
            "disabled": "false"
        }
        bf_rolesList.append(role)
    log.debug(bf_rolesList)

    cc_privilegeSet=[]
    log.info(ROLE)
    if ROLE == 'MANAGER' or ROLE == 'ADMIN':
        for input_role in input_roleList:
            if input_role.get('product') != 2 or input_role.get('name') != 'CC_BOT_MANAGER':
                continue
            record = {"id": "","role_ccbot": input_role.get('roleid')}
            cc_privilegeSet.append(record)
    elif ROLE == 'MEMBER':
        for input_role in input_roleList:
            if input_role.get('product') != 2 or input_role.get('name') != 'CC_BOT_MEMBER':
                continue
            record = {"id": "","role_ccbot": input_role.get('roleid')}
            cc_privilegeSet.append(record)
    log.debug(cc_privilegeSet)

    # roleList 無論哪個 Role 都長一樣
    cc_rolesList=[]
    for input_role in input_roleList:
        if input_role.get('product') != 2:
            continue
        record = {
          "value": input_role.get('roleid'),
          "label": input_role.get('name'),
          "product": input_role.get('product'),
          "roleid": input_role.get('roleid'),
          "disabled": "false"
        }
        cc_rolesList.append(record)
    log.debug(cc_rolesList)

    cc_roleids=[]
    if ROLE == 'MANAGER' or ROLE == 'ADMIN' :
        for input_role in input_roleList:
            if input_role.get('product') != 2 or input_role.get('name') != 'CC_BOT_MANAGER':
                continue
            cc_roleids.append(input_role.get('roleid'))
    elif ROLE == 'MEMBER':
        for input_role in input_roleList:
            if input_role.get('product') != 2 or input_role.get('name') != 'CC_BOT_MEMBER':
                continue
            cc_roleids.append(input_role.get('roleid'))
    log.debug(cc_roleids)

    return bf_privilegeSet, bf_rolesList, bf_str_value, cc_privilegeSet, cc_rolesList, cc_roleids