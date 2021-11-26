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
from bs4 import BeautifulSoup
from config.target_url import *
from util.tools import from_thousandth_format, from_percentage_format

# 浏览器头
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


def get_stock_value_to_earn_table(total_assets, account_type, start_date):
    """ 获取市值收益表

    :param total_assets: int 总市值（单位万）
    :param account_type: string 枚举 double_open/ke_chuang/chuang_ye/double_closed
    :param start_date: string 计算收益的起始日期
    :return: dict 收益字典
    """

    value_to_earn_table = {}
    params = {
        "total_assets": total_assets,
        "account_count": 1,
        "start_date": start_date,
    }
    if account_type in ("chuang_ye", "double_closed"):
        # 创业板 或 双不开
        params["no_kcb"] = 1
    if account_type in ("ke_chuang", "double_closed"):
        # 科创板 或 双不开
        params["no_second"] = 1

    url = "https://www.jisilu.cn/data/new_stock/winning/"
    rsp = requests.get(url=url, headers=headers, params=params)
    content = rsp.text
    bs = BeautifulSoup(content, "html.parser")
    # 获取各个证券所市值数据
    shanghai_value_to_earn_table = bs.select(
        "#calcForm > div.query_tables > table:nth-child(1) > tr")
    shenzhen_value_to_earn_table = bs.select(
        "#calcForm > div.query_tables > table:nth-child(2) > tr")
    if len(shanghai_value_to_earn_table) > 0:
        value_to_earn_table["shanghai"] = []
    if len(shenzhen_value_to_earn_table) > 0:
        value_to_earn_table["shenzhen"] = []
    for index, record in enumerate(shanghai_value_to_earn_table):
        if index > 0:
            record = record.select("td")
            value_to_earn_table["shanghai"].append({
                "交易所": record[0].text,
                "市值配置(元)": from_thousandth_format(record[1].text),
                "理论总收益(元)": from_thousandth_format(record[2].text),
                "理论总收益率": from_percentage_format(record[3].text),
                "理论增量收益率": from_percentage_format(record[4].text),
                "理论年化": from_percentage_format(record[5].text),
                "理论增量年化": from_percentage_format(record[6].text),
            })
    for index, record in enumerate(shenzhen_value_to_earn_table):
        if index > 0:
            record = record.select("td")
            value_to_earn_table["shenzhen"].append({
                "交易所": record[0].text,
                "市值配置(元)": from_thousandth_format(record[1].text),
                "理论总收益(元)": from_thousandth_format(record[2].text),
                "理论总收益率": from_percentage_format(record[3].text),
                "理论增量收益率": from_percentage_format(record[4].text),
                "理论年化": from_percentage_format(record[5].text),
                "理论增量年化": from_percentage_format(record[6].text),
            })
    return value_to_earn_table


def get_stock_value_to_earn(money, table):
    """

    :param money: int 打新股市值
    :param table: list 打新股市值配置/收益
    :return:
    """
    for record in table:
        if money <= record.get("市值配置(元)"):
            return record


def get_stock_distribution(total_assets, account_config, start_date):
    """获取打新最佳市值分配

    :param total_assets: string 总市值
    :param account_config: dict 账户配置
    :param start_date:string 计算开始时间
    :return:
    """
    # 初始化账户数据
    account_stock_config = []
    index = 0
    for account_type, num in account_config.items():
        # 获取账户类型的市值收益信息
        value_table = get_stock_value_to_earn_table(total_assets,
                                                    account_type,
                                                    start_date)
        for one in range(num):
            index += 1
            for place, table in value_table.items():
                if len(table) > 0:
                    account_stock_config.append(
                        {
                            "账户名称": f"账户{index}",
                            "账户类型": account_type,
                            "证券所": place,
                            "市值配置(元)": 0,
                            "理论总收益(元)": 0,
                            "理论增量年化": 0.0,
                            "table": table,
                        }
                    )
    # 根据每种账户类型的市值收益信息,计算合适比例
    for index in range(total_assets):
        # 对每个账户的市值配置增加一万元,然后获取对应的理论增量年化进行降序排序,
        account_stock_config = sorted(
            account_stock_config,
            key=lambda x: get_stock_value_to_earn(
                x.get("市值配置(元)") + 10000,
                x.get("table")).get("理论增量年化"),
            reverse=True)
        # 一万元分配给理论增量年化最高的
        account_stock_config[0]["市值配置(元)"] += 10000

    # 更新数据
    for record in account_stock_config:
        config = get_stock_value_to_earn(
            record.get("市值配置(元)"), record.get("table"))
        record["理论总收益(元)"] = config.get("理论总收益(元)")
        record["理论增量年化"] = config.get("理论增量年化")
        del record["table"]
    return account_stock_config


if __name__ == "__main__":
    account_config = {
        "double_open": 1,
        "ke_chuang": 0,  # 科创板
        "chuang_ye": 0,  # 创业板
        "double_closed": 2,  # 双不开
    }
    print(get_stock_distribution(42, account_config, start_date='2021-01-01'))
    total = 0
    for record in get_stock_distribution(50, account_config,
                                         start_date='2021-01-01'):
        total += record.get("理论总收益(元)")
    print(total / 420000)