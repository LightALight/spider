#!/usr/bin/env python

"""
-------------------------------------------------
@date：         2021/8/16 15:40
@Author :
@File Name：    stock.py
@Description :
-------------------------------------------------
"""
import re
import requests

# 浏览器头
from config.target_url import *

headers = {
    'content-type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
}


def add_stock_exchange(stock_code):
    """补充交易所信息

    :param stock_code:
    :return:
    """
    if len(stock_code) != 6:
        return "非法股票"

    if stock_code[0] in ("6", "7"):
        # 6开头是沪市,7是沪市新股
        stock_code = "sh" + stock_code
    elif stock_code[0] in ("0", "2", "3"):
        # 000开头的股票是深证A股，001、002开头的股票也都属于深证A股，其中002开头的股票是深证A股中小企业股票；
        # 200开头的股票是深证B股；
        # 300开头的股票是创业板股票
        stock_code = "sz" + stock_code
    else:
        return "非法股票"
    return stock_code


def get_realtime_stock(stock_code_list):
    """得到股票的实时信息

    :param stock_code_list:
    :return:
    """
    if not isinstance(stock_code_list, (list, set, tuple)
                      ) or len(stock_code_list) == 0:
        return "非法股票代码"
    stock_realtime_info_dict = {

    }
    stock_info_key = [
        "股票名字",
        "今日开盘价",  # 单位元
        "昨日收盘价",  # 单位元
        "当前价格",  # 单位元
        "今日最高价",  # 单位元
        "今日最低价",  # 单位元
        "竞买价",  # 单位元
        "竞卖价",  # 单位元
        "成交的股票数量",  # 股
        "成交金额",  # 单位元
        "买一数量",  # 股
        "买一报价",  # 单位元
        "买二数量",  # 股
        "买二报价",  # 单位元
        "买三数量",  # 股
        "买三报价",  # 单位元
        "买四数量",  # 股
        "买四报价",  # 单位元
        "买五数量",  # 股
        "买五报价",  # 单位元
        "卖一数量",  # 股
        "卖一报价",  # 单位元
        "卖二数量",  # 股
        "卖二报价",  # 单位元
        "卖三数量",  # 股
        "卖三报价",  # 单位元
        "卖四数量",  # 股
        "卖四报价",  # 单位元
        "卖五数量",  # 股
        "卖五报价",  # 单位元
        "数据日期",
        "数据时间",
    ]
    for stock_code in stock_code_list:
        url = f"http://hq.sinajs.cn/list={add_stock_exchange(stock_code)}"
        resp = requests.get(url=url, headers=headers)
        content = resp.text
        search = re.findall(r'=\"(.+?)\";', content, re.M | re.I)
        if search:
            stock_info = search[0].split(",")
            stock_realtime_info_dict[stock_code] = dict(
                zip(stock_info_key, stock_info))
            print(stock_realtime_info_dict)
        else:
            raise Exception("匹配不到数据")
    return stock_realtime_info_dict


def get_history_stock(stock_code_list, start_date, end_date):
    """获取股票历史数据

    :param stock_code: string 格式
    :param start_date: string 格式 20160414
    :param end_date: string 格式 20160414
    :return:
    """
    if not isinstance(stock_code_list, (list, set, tuple)
                      ) or len(stock_code_list) == 0:
        return "非法股票代码"
    stock_history_info_dict = {

    }
    stock_info_key = [
        "日期",
        "今日开盘价",  # 单位元
        "昨日收盘价",  # 单位元
        "涨跌幅度",  # 单位元
        "涨跌百分比",  # 单位元
        "今日最低价",  # 单位元
        "今日最高价",  # 单位元
        "今日成交股票手数",  # 单位元
        "今日成交金额",  # 单位万
        "今日换手率",
    ]
    for stock_code in stock_code_list:
        params = {
            "code": "cn_" + stock_code,
            "start": start_date,
            "end": end_date,
        }
        resp = requests.get(url=stock_soho_url, headers=headers, params=params)
        stocks = resp.json()
        for stock in stocks:
            stock_history_info_dict[stock.get("code")] = [dict(
                zip(stock_info_key, record))for record in stock.get("hq")]
        return stock_history_info_dict


if __name__ == "__main__":
    print(thousandth_format("12211212.000"))
