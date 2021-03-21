import log
import pymysql
import datetime
import json

log = log.logging.getLogger(__name__)


class Database(object):
    def __init__(self):
        conn = pymysql.Connect(host='192.168.3.155',user='root',passwd='password',db='vote',charset='utf8')
        self.conn = conn
    def queryOptions(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select * from `vote`.`option`;")
            data = []
            for row in cursor.fetchall():
                obj = {}
                for i, value in enumerate(row):
                    log.debug(cursor.description[i][0] + ':'+ str(value))
                    obj[cursor.description[i][0]]= value.strftime("%Y/%m/%d %H:%M:%S") if type(value) is datetime.date else str(value)
                data.append(obj)
            # r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
            return data
        except Exception as e:
            raise e

    def queryBallots(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select * from `vote`.`ballot`;")
            data = []
            for row in cursor.fetchall():
                obj = {}
                for i, value in enumerate(row):
                    log.debug(cursor.description[i][0] + ':'+ str(value))
                    obj[cursor.description[i][0]]= value.strftime("%Y/%m/%d %H:%M:%S") if type(value) is datetime.date else str(value)
                data.append(obj)
            return data
        except Exception as e:
            raise e
        finally:
            self.conn.close
    
    def insertTransmit(self,dataForRakuten):
        cursor = self.conn.cursor()
        try:
            for record in dataForRakuten['data']:
                sql = "INSERT INTO db.transmit_record (session_id, transmit_date, transmit_status) \
    	  	            VALUES ( %s, CURDATE(), %s)ON DUPLICATE KEY UPDATE transmit_date=CURDATE(), transmit_status= %s ;"
                val = (record['session_id'], str(record['transmit_status']), str(record['transmit_status']))

                try:
                    cursor.execute(sql, val)
                except Exception as e:
                    log.info("query '{}' with params {} failed with {}".format(sql, val, e))
                    log.info( "\n executed sql: " + cursor._executed)
                    self.conn.rollback()
                # if cursor.rowcount != 1:
                log.info("insert success: " + record['session_id'])
                self.conn.commit()
        except Exception as e:
            raise str(e) 