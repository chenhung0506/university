import log
import pymysql
import datetime
import json
import const
import utils

log = log.logging.getLogger(__name__)


class Database(object):
    conn = {}
    def __init__(self):
        log.info(const.DB_PORT)
        log.info(const.DB_HOST)
        log.info(const.DB_ACCOUNT)
        log.info(const.DB_PASSWORD)
        conn = pymysql.Connect(host=const.DB_HOST, port=int(const.DB_PORT), user=const.DB_ACCOUNT, passwd=const.DB_PASSWORD, db='university',charset='utf8')
        # conn = pymysql.Connect(host='172.105.230.31', user='root', passwd='password', db='university',charset='utf8')
        # conn = pymysql.Connect(host='172.105.230.31',user='root',passwd='password',db='university',charset='utf8')
        self.conn = conn
    def getUniversity(self,data):
        cursor = self.conn.cursor()
        try:
            if data == None:
                cursor.execute("select * from `university`.`university`;")
            elif data.get("u_id"):
                cursor.execute("select * from `university`.`university` where u_id = %s;", (data.get('u_id')))
            else:
                cursor.execute("select * from `university`.`university` where u_name = %s and kind = %s;", (data.get('u_name'), data.get('kind')))
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
            log.info( "getUniversity error: " + cursor._executed)
            raise e
        finally:
            cursor.close()
            self.conn.close()

    def addUniversity(self,data):
        cursor = self.conn.cursor()
        sql = "INSERT INTO university.university (u_name, kind, descri, pdf1_path, pdf2_path, url_path, reward, medal1, medal2, medal3, medal4, medal5) \
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (data.get('u_name'), data.get('kind'), data.get('descri'), utils.clean_filename(data.get('pdf1_path')), utils.clean_filename(data.get('pdf2_path')), data.get('url_path'), data.get('reward'), data.get('medal1'), data.get('medal2'), data.get('medal3'), data.get('medal4'), data.get('medal5'))
        log.info(val)
        try:
            cursor.execute(sql, val)
            self.conn.commit()
            return True
        except Exception as e:
            log.info("query '{}' with params {} failed with {}".format(sql, val, e))
            log.info(cursor._executed)
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
            self.conn.close()

    def editUniversity(self,data):
        cursor = self.conn.cursor()
        sql = "UPDATE university.university SET u_name = %s, kind = %s, descri = %s, pdf1_path = %s, pdf2_path = %s, url_path = %s, reward = %s, medal1 = %s, medal2 = %s, medal3 = %s, medal4 = %s, medal5 = %s WHERE u_id = %s"
        val = (data.get('u_name'), data.get('kind'), data.get('descri'), utils.clean_filename(data.get('pdf1_path')), utils.clean_filename(data.get('pdf2_path')), data.get('url_path'), data.get('reward'), data.get('medal1'), data.get('medal2'), data.get('medal3'), data.get('medal4'), data.get('medal5'), int(data.get("u_id")))
        log.info(val)
        try:
            cursor.execute(sql, val)
            self.conn.commit()
            return True
        except Exception as e:
            log.info("query '{}' with params {} failed with {}".format(sql, val, e))
            log.info(cursor._executed)
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
            self.conn.close()

    def delUniversity(self,data):
        cursor = self.conn.cursor()
        sql = "DELETE FROM university.university WHERE u_id = %s"
        val = (data.get('u_id'))
        try:
            cursor.execute(sql, val)
            self.conn.commit()
            log.info(cursor.rowcount)
            return True
        except Exception as e:
            log.info( "delUniversity error: " + cursor._executed)
            raise e
        finally:
            cursor.close()
            self.conn.close()