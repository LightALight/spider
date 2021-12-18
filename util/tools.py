#!/usr/bin/env python

"""
-------------------------------------------------
@date：         2021/8/4 10:39
@Author :
@File Name：    tools.py
@Description :
-------------------------------------------------
"""
from datetime import datetime
import datetime
import decimal
from dateutil.relativedelta import relativedelta
from config.config import db_info
from util.mysql_conn import MysqlConn


def error_info_write(info):
    """写日志

    :param info:
    :return:
    """
    with open("error.log", "a+", encoding="utf-8") as f:
        f.write(info)


def store_records(table_name, records_info, db_info=db_info):
    """ 存储数据库信息

    :param table_name: stirng 存储的表
    :param records_info:list 需要存储的数据
    :param db_info: dict 数据库信息
    :return:
    """
    update_sql_list = []
    for record in records_info:
        columns_key_info = ",".join(record.keys())
        columns_values_info = ""
        for columns_value in record.values():
            if isinstance(columns_value, (int, decimal.Decimal, float)):
                columns_values_info += str(columns_value) + ","
            else:
                columns_values_info += "\"" + str(columns_value) + "\","
        update_sql = f'REPLACE INTO {table_name} ({columns_key_info}) VALUES ({columns_values_info.rstrip(",")});'
        update_sql_list.append(update_sql)

    # 存储数据库
    mysql_conn = MysqlConn(**db_info)
    # print(update_sql_list)
    mysql_conn.insert_by_sql(list_sql=update_sql_list)


def create_partition(tbl_name, start_date, time_interval, time_unit):
    """ 创建分区

    :param tbl_name: string 表名
    :param start_date: string 开始时间
    :param time_interval: int 分区的时间间隔
    :param time_unit: string 时间间隔单位 month
    :return:
    """
    # 获取分区起始点
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    now = datetime.date.today()
    sql_list = []
    while now > start_date.date():
        # 获取分区名称
        partition_name = datetime.datetime.strftime(start_date, '%Y%m%d')
        # 获取分区截止点
        deadline = start_date + datetime.timedelta(days=1)
        deadline = datetime.datetime.strftime(deadline, '%Y%m%d')
        # 构造分区sql
        # sql = f"alter TABLE `{tbl_name}` add PARTITION( PARTITION p_{partition_name} VALUES LESS THAN ({deadline})) ENGINE = InnoDB);"
        sql = f"PARTITION p_{partition_name} VALUES LESS THAN ({deadline}) ENGINE = InnoDB,"
        sql_list.append(sql)
        # 增加三个月
        if time_unit == "month":
            start_date = start_date + relativedelta(months=+time_interval)
        else:
            start_date = start_date + relativedelta(days=+time_interval)
    partition_sql = f"ALTER TABLE {tbl_name} PARTITION by RANGE(to_days(fund_date)) ("
    for sql in sql_list:
        partition_sql += sql
    partition_sql = partition_sql.rstrip(",") + ");"
    return partition_sql


def compute_data(sql_summary, value_colunm_name,
                 day_colunm_name, table_name, sep_colunm_name=None):
    """

    :param sql_summary:
    :param value_colunm_name:
    :param day_colunm_name:
    :return:
    """
    mysql_conn = MysqlConn(**db_info)
    records_info = mysql_conn.select_sql_get_all(
        sql=sql_summary, return_format="dict")
    length = len(records_info)
    for index in range(-1, -length - 1, -1):
        # 从最近一期开始获取记录
        now_record = records_info[index]
        if index == -length:
            # 最后一条
            stock_increase = now_record.get(value_colunm_name)
            stock_increase_rate = 0
            interval_day = 0
        else:
            # 上一期的记录
            last_record = records_info[index - 1]
            if sep_colunm_name and now_record.get(
                    sep_colunm_name) != last_record.get(sep_colunm_name):
                # 如果存在分割字段的值不一样,说明已经不是同一类别
                stock_increase = now_record.get(value_colunm_name)
                stock_increase_rate = 0
                interval_day = 0
            else:
                stock_increase = now_record.get(
                    value_colunm_name) - last_record.get(value_colunm_name)
                if last_record.get(value_colunm_name) == 0:
                    # 上一条记录的值为零,增长率就为零
                    stock_increase_rate = 0
                else:
                    stock_increase_rate = stock_increase / \
                        last_record.get(value_colunm_name)
                interval_day = (now_record.get(
                    day_colunm_name) - last_record.get(day_colunm_name)).days
        now_record["stock_increase"] = stock_increase
        now_record["stock_increase_rate"] = stock_increase_rate
        now_record["interval_day"] = interval_day
    store_records(table_name, records_info)


def from_percentage_format(str_number):
    # 百分比转换数字
    return float(decimal.Decimal(str_number.rstrip("%")) /
                 decimal.Decimal("100"))


def percentage_format(number_str):
    """ 字符串小数转换成百分比

    :param number_str:
    :return:
    """
    if number_str:
        return '{:.2%}'.format(float(number_str) / 100)


def thousandth_format(str_number):
    """ 数字转换千分位

    :param str_number:
    :return:
    """
    if "." in str_number:
        # 如果存在小数点,拆分整数和小数部分
        str_int = str_number[:str_number.index(".")]
        str_decimal = str_number[str_number.index("."):]
    else:
        str_int = str_number
        str_decimal = ""

    length = len(str_int)
    if length <= 3:
        return str_number

    str_number_list = list(str_int)
    insert_postion = -3
    for number in range(0, length // 3):
        str_number_list.insert(insert_postion, ",")
        insert_postion += -4
    str_number = "".join(str_number_list) + str_decimal
    return str_number


def from_thousandth_format(str_number):
    """ 千分位转换数字

    :param str_number:
    :return:
    """
    return float(str_number.replace(",", ""))


def get_last_days_time(day):
    """ 获取前几天的日期

    :param day: int 天数
    :return:
    """
    today = datetime.date.today()
    one_year = datetime.timedelta(days=day)
    last_year = today - one_year
    return last_year


if __name__ == "__main__":
    print(str(get_last_days_time(365)))
