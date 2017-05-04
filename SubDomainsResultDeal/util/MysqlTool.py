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
            exist = 0
        return exist

    def execute(self, sql):
        try:
            logging.info(sql)
            result = self.cur.execute(sql)
            for r in self.cur.fetchmany(result):
                logging.info(r)
            self.db.commit()
        except Exception, e:
            self.db.rollback()
            raise e
    def executemany(self,sql, data):
        try:
            result = self.cur.executemany(sql, data)
            for r in self.cur.fetchmany(result):
                logging.info(r)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e




if __name__ == '__main__':
    db = MysqlTool(host="127.0.0.1", port=3307, user="root", password="root")
    db.check_db("test22")
    db.execute("select * from dvwa.users limit 1")
    create_db = "create database myipdb"
    create_tb1 = """
            create table myip(
                id int unsigned auto_increment primary key,
                ip varchar(15),
                isp varchar(30)
                );
            """
    create_tb2 = """
            create table myport(
                id int unsigned auto_increment primary key,
                ip_id int unsigned,
                foreign key (ip_id) references myip (id),
                port smallint unsigned,
                name varchar(20),
                banner varchar(40),
                http_title varchar(40),
                c_time timestamp,
                u_time timestamp
                );
            """
    # db.execute(create_db)
    db.execute("use myipdb;")
    # db.execute(create_tb1)
    db.execute(create_tb2)


