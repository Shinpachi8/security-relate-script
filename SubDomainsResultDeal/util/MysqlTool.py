#!/usr/bin/env python
# coding=utf-8

import MySQLdb
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(filename)s [line:%(lineno)d] %(message)s')

class MysqlTool(object):
    """docstring for MysqlTool"""
    def __init__(self, host, port,  user, password):
        super(MysqlTool, self).__init__()
        self.db =MySQLdb.connect(host=host,  port=port, user=user, passwd=password)
        self.cur = self.db.cursor()


    def check_db(self, dbname):
        exist = 0
        try:
            # self.cur.execute("create table if not exists like {}".format(dbname))
            # self.cur.execute("select `TABLE_NAME` from `INFORMATION_SCHEMA`.`TABLES` where `TABLE_SCHEMA`='{}'' and `TABLE_NAME`='{}'".format())
            exist = self.cur.execute("select 1 from information_schema.schemata where schema_name = '{}'".format(dbname))
            # self.db.commit()
        except Exception, e:
            raise
        return exist

    def execute(self, sql):
        try:
            result = self.cur.execute(sql)
            for r in self.cur.fetchmany(result):
                logging.info(r)
            self.db.commit()
        except Exception, e:
            raise e



if __name__ == '__main__':
    db = MysqlTool(host="127.0.0.1", port=3307, user="root", password="root")
    db.check_db("test22")
    db.execute("select * from dvwa.users limit 1")
