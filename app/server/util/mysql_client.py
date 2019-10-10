

import pymysql
from pymysql import cursors
from logger import logger

import pandas as pd
from pymysqlpool import ConnectionPool

config1 = {
 'pool_name': 'qly_v2_pool',
 'host': 'rm-bp10k71o67q5649x235950.mysql.rds.aliyuncs.com',
 'port': 3306,
 'user': 'tts_qly',
 'password': 'NWfs9pwnlyA8txcc',
 'database': 'tts_tob_qly_v2'
}

config2 = {
 'pool_name': 'qly_analysis_pool',
 'host': 'rm-bp10k71o67q5649x235950.mysql.rds.aliyuncs.com',
 'port': 3306,
 'user': 'tts_qly',
 'password': 'NWfs9pwnlyA8txcc',
 'database': 'tts_qly_analysis'
}

config3 = {
 'pool_name': 'tts_douyin_pool',
 'host': 'rm-bp10k71o67q5649x235950.mysql.rds.aliyuncs.com',
 'port': 3306,
 'user': 'tts_douyin',
 'password': 'Nafs9pwnly2AtxBc',
 'database': 'tts_douyin'
}

class MysqlClient(object):

    # init the mysql database
    def __init__(self, db):
        if db == 'tts_tob_qly_v2':
            self.pool = ConnectionPool(**config1)
        elif db == 'tts_qly_analysis':
            self.pool = ConnectionPool(**config2)
        elif db == 'tts_douyin':
            self.pool = ConnectionPool(**config3)
        self.pool.connect()

    def find_qlypv_history(self):
        SQL = "select rdate, num from qly_stat_day where stat_type='plugin_pv' order by rdate"
        return self.query(SQL)

    def find_order(self):
        SQL = "select date_format(modify_time, '%Y-%m-%d') as rdate, sum(pay_amount)/100 as sum_pay, count(*) as count from t_tob_zhishu100_user_order where order_status in (2, 3, 5) and shop_id not in (11211211) and pay_amount>100 group by date_format(modify_time, '%Y-%m-%d')"
        return self.query(SQL)

    def find_web_report(self,starttime,endtime):
        SQL = 'SELECT * from douyin_web_report  where rdate>=' + '"' + starttime + '"' +  ' and rdate <= ' + '"' + endtime + '"'
        return self.query(SQL)

    def find_plugin_hour(self):
        SQL = "SELECT * from plugin_hour_analyse order by ctime"
        return self.query(SQL)

    def find_plugin_day(self):
        SQL = "SELECT * from plugin_day_analyse order by ctime"
        return self.query(SQL)

    def query(self, sql):
        result = []
        try:
            connection = self.pool.borrow_connection()
            result = pd.read_sql(sql, connection)
        except Exception as e:
            logger.error(str(e))
        finally:
            self.pool.return_connection(connection)
        return result
# 实例
# mysql_client=mysqlClient(host='192.168.3.58',port=3306,username='hongjun',
#                           password='hongjun654321wr',db_name='tts_tob_qly_v2')



# if __name__=='__main__':
#
#     print(mysql_client.find_all_update_shops())
