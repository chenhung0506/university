import const
from datetime import datetime, timedelta
from opencc import OpenCC
import re
import log
import json
import requests
import math
import time
import utils
import uuid 

log = log.logging.getLogger(__name__)

class CallApi(object):
    def getChatRecords(self, uuid):
        url = str(const.API_CHAT_RECORDS)
        data = {"uuid": [uuid]}
        try:
            headers = {
                'X-Enterprise': const.ENTERPRISE,
                'Content-Type': 'application/json'
            }
            log.info("call api: " + url + "\nwith data: " + str(data) + "\nheader: " + str(headers))
            response = requests.request("POST", url, data=json.dumps(data), headers=headers)
            if response.status_code != 200:
                raise Exception('Response status: ' + str(response.status_code) + ', message: ' + response.text)
            return json.loads(response.text)
        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)

    def getTagByCallId(self, callID):
        url = str(const.API_CALL_RESULT)
        data={"session_id": callID}
        try:
            headers = {
                'X-Enterprise': const.ENTERPRISE,
                'Content-Type': 'application/json'
            }
            log.info("call api: " + url + "\nwith data: " + str(data))
            response = requests.request("POST", url, data=json.dumps(data), headers=headers)
            if response.status_code != 200:
                raise Exception('Response status: ' + str(response.status_code) + ', message: ' + response.text)
            return json.loads(response.text)
        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)

    def getCallResult(self, pageSize, pageNumber, request):
        try:
            data={}
            if request == None:
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                startTime = datetime.fromtimestamp(timestamp - 3600 * float(const.START_TIME)).strftime("%Y-%m-%d %H:%M:%S")
                endTime = datetime.fromtimestamp(timestamp - 3600 * float(const.END_TIME)).strftime("%Y-%m-%d %H:%M:%S")
                # startTime = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d') + ' 00:00:00'
                # endTime = datetime.strftime(datetime.now(), '%Y-%m-%d') + ' 00:00:00'
                log.debug("startTime: " + startTime + ", endTime: " + endTime)
                data = {
                         "start_time": startTime,
                         "end_time": endTime,
                         "call_direction": const.CALL_DIRECTION,
                         "page_size": int(pageSize),
                         "page_number": int(pageNumber)
                       }
                if str(const.IS_TAG_API_V1)=='true':
                    data['phone_number']='66155400'
            else:
                log.debug("inputRequest:"+str(request))
                args = request.args
                # if args.get('page_size') == None : raise Exception("necessary param 'page_size'")
                data={"call_direction": const.CALL_DIRECTION}
                data['page_size']=int(pageSize)
                if args.get('start_time') != None : data['start_time'] = args.get('start_time')
                if args.get('end_time') != None : data['end_time'] = args.get('end_time')
                if args.get('call_direction') != None : data['call_direction'] = args.get('call_direction')
                if args.get('page_number') != None : data['page_number'] = int(args.get('page_number'))
                if args.get('session_id') != None : data['session_id'] = args.get('session_id')
                if str(const.IS_TAG_API_V1)=='true':
                    data['phone_number']='66155400'

            headers = {
                        'X-Enterprise': const.ENTERPRISE,
                        'X-UserID': const.USER_ID,
                        'Content-Type': "application/json",
                        'Connection': "keep-alive",
                        'cache-control': "no-cache"
                      }
            log.info("call api: " + const.GET_TAG_API + "\nwith data: " + str(data))
            response = requests.request("POST", const.GET_TAG_API, data=json.dumps(data), headers=headers)
            if response.status_code != 200:
                raise Exception('Response status: ' + str(response.status_code) + ', message: ' + response.text)
            const.CSV_FILE_BEG_TIME=data['start_time']
            const.CSV_FILE_END_TIME=data['end_time']

            return json.loads(response.text)
        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)

    def getTag(self, request):
        try:
            totalResult = []
            totalSize=0
            resultForTotalSize = self.getCallResult(1,1,request)
            #calculate necessary call api number of times
            totalSize=resultForTotalSize['result']['total_size']
            log.info("total_size:" + str(totalSize))
            for i in range(1, (math.ceil(totalSize/20))+1):
                log.info("page_number:"+ str(i))
                result = self.getCallResult('20',i,request)
                if result['status']!=0:
                    return("Call api: " + const.GET_TAG_API + ", got wrong status: " + str(result['status']) + ", message: " + result['message'])
                for val in result['result']['data']:
                    totalResult.append(val)
        except Exception as e:
            log.error(utils.except_raise(e))
            raise e
        log.debug(totalResult)
        return totalResult