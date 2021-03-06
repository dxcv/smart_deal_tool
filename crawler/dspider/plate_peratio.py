#coding=utf-8
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__))))
sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
import const as ct
from cmysql import CMySQL
from common import create_redis_obj
class PlatePERatioCrawler(object):
    def __init__(self, dbinfo = ct.DB_INFO, redis_host = None):
        self.dbname = self.get_dbname()
        self.redis = create_redis_obj() if redis_host is None else create_redis_obj(host = redis_host)
        self.mysql_client = CMySQL(dbinfo, self.dbname, iredis = self.redis)
        if not self.mysql_client.create_db(self.dbname): raise Exception("init pledge database failed")

    @staticmethod
    def get_dbname():
        return "plate_pe"

    def create_table(self, table):
        import pdb
        pdb.set_trace()
        sql = 'create table if not exists %s(date varchar(10) not null,\
                                             code varchar(10) not null,\
                                             name varchar(50),\
                                             pledge_counts int,\
                                             unlimited_pledge_stocks float,\
                                             limited_pledge_stocks float,\
                                             total_stocks float,\
                                             pledge_ratio float,\
                                             PRIMARY KEY(date, code))' % table
        return True if table in self.mysql_client.get_all_tables() else self.mysql_client.create(sql, table)
