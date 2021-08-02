#!/usr/bin/env python

"""
-------------------------------------------------
@date：         2019/4/17 10:45
@Author :
@File Name：    mysql_conn.py
@Description :
-------------------------------------------------
"""
import pymysql
import pymysql.cursors


class MysqlConn(object):
    """mysql方法类"""

    def __init__(self, db_name, host, user, password, port):
        self.db_name = db_name
        self.host = host
        self.user = user
        self.password = password
        self.port = int(port)

        self.config = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'db': self.db_name,
            'charset': 'utf8mb4',
        }
        self.conn = None

    def __enter__(self):
        try:
            self.conn = pymysql.connect(**self.config)
            if self.conn:
                self.conn.commit()
                return self.conn
        except pymysql.OperationalError as e:
            print("连接数据库失败,Mysql Error %d:%s" % (e.args[0], e.args[1]))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def select_sql_get_all(self, sql, params=None, return_format=None):
        """ 查询数据库返回所有查询结果数据，为list中包含多条dict数据类型

        :param sql:    string 查询使用sql
        :param params: list   想要映射到sql的参数
        :param return_format: string   返回格式，默认位tuple，如果输入dict，返回单条记录格式为字典
        :return:       tuple  返回所有查询结果数据
                       None   查询不到
        """
        # print('当前查询sql:{0}'.format(sql))
        if return_format == "dict":
            return_format = pymysql.cursors.DictCursor
        with MysqlConn(self.db_name, self.host, self.user, self.password, self.port) as dbconnect:
            with dbconnect.cursor(cursor=return_format) as dbcursor:
                dbcursor.execute(sql, params)
                return dbcursor.fetchall()

    def select_sql_get_one(self, sql, params=None, return_format=None):
        """ 查询数据库返回查询结果第1条数据，为dict类型

        :param sql:    string 查询使用sql
        :param params: list   想要映射到sql的参数
        :param return_format: string   返回格式，默认位tuple，如果输入dict，返回字典格式
        :return:       tuple  返回所有查询结果数据的第一条
                       None   查询不到
        """
        # print('当前查询sql:{0}'.format(sql))
        if return_format == "dict":
            return_format = pymysql.cursors.DictCursor
        with MysqlConn(self.db_name, self.host, self.user, self.password, self.port) as dbconnect:
            with dbconnect.cursor(cursor=return_format) as dbcursor:
                dbcursor.execute(sql, params)
                return dbcursor.fetchone()

    def delete_sql_by_condition(self, sql, params=None):
        """根据条件删除数据库记录

        :param sql:        string 查询使用sql
        :param params:     list   想要映射到sql的参数
        :return:           bool   删除成功为True，失败为Fasle
        """
        # print('当前删除sql:{0}'.format(sql.lower()))
        with MysqlConn(self.db_name, self.host, self.user, self.password, self.port) as dbconnect:
            with dbconnect.cursor() as dbcursor:
                sql = sql.lower()
                if "where" in sql:  # 需要带查询条件
                    dbcursor.execute(sql, params)

                    query_sql = "select count(1) from" + sql.split("from")[
                        1].split("where")[0]
                    # print('构造查询sql:{0}'.format(query_sql))
                    dbcursor.execute(query_sql)  # 查询下删除后记录条数
                    dbconnect.commit()
                    return True

                    # if dbcursor.fetchone()[0] > 0:
                    #     dbconnect.commit()
                    #     return True
                    # else:
                    #     print("删除记录过多,开始回滚")
                    #     # 回滚
                    #     dbconnect.rollback()
                return False

    def insert_by_sql(self, list_sql):
        """根据sql插入数据库记录

        :param list_sql:        list   想要插入的sql命令列表
        :return:
        """
        with MysqlConn(self.db_name, self.host, self.user, self.password,
                       self.port) as dbconnect:
            with dbconnect.cursor() as dbcursor:
                for one_sql in list_sql:
                    dbcursor.execute(one_sql)
                dbconnect.commit()


if __name__ == '__main__':
    pass