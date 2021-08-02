#!/usr/bin/env python

"""
-------------------------------------------------
@date：         2021/7/28 15:27
@Author :
@File Name：    fund.py.py
@Description :
-------------------------------------------------
"""
import time
from decimal import Decimal

import requests
import json
import re
from bs4 import BeautifulSoup


# 浏览器头
from util.mysql_conn import MysqlConn

headers = {
    'content-type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
db_info = {
    "host": "",
    "port": 3306,
    "user": "",
    "password": "",
    "db_name": "",
}


def get_funds_code():
    url = "http://fund.eastmoney.com/js/fundcode_search.js"
    rsp = requests.get(url=url, headers=headers)
    content = rsp.text
    fund_info_list = re.findall(
        r'\[".+?\]',
        content,
        re.M | re.I)
    fund_info_list = [eval(fund_info) for fund_info in fund_info_list]
    return fund_info_list


def get_fund_info(fund_code, return_format="easy"):
    """

    :param fund_code: string 基金代码
    :return:
    """
    if return_format == "easy":
        url = f"http://fundgz.1234567.com.cn/js/{fund_code}.js?rt={int(round(time.time() * 1000))}"
        rsp = requests.get(url=url, headers=headers)
        content = rsp.text
        # 查找结果
        search = re.findall(r'\{.*\}', content, re.M | re.I)
        for i in search:
            data = json.loads(i)
            return {
                "fund_code": data.get('fundcode'),
                "name": data.get('name'),
                "last_date": data.get('jzrq'),
                "last_net_value": data.get('dwjz'),
                "now_date": data.get('gztime'),
                "expect_net_value": data.get('gsz'),
                "expect_earning_rate": data.get('gszzl'),
            }
    else:
        url = f"http://fund.eastmoney.com/pingzhongdata/{fund_code}.js?v={time.strftime('%Y%m%d%H%M%S', time.localtime())}"
        rsp = requests.get(url=url, headers=headers)
        print(rsp.text)


def get_fund_stock_info(fund_code):
    """ 获取基金股票信息

    :param fund_code:
    :return:
    """
    print(f"开始获取基金{fund_code}")
    # 获取年份信息
    years_url = f"http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={fund_code}&topline=1000&year=1970&month=&rt=0.21822537857648627"
    rsp = requests.get(url=years_url, headers=headers)
    content = rsp.text
    search = re.findall(r'[1-2][0-9]{3}', content, re.M | re.I)
    # 去掉冗余数据
    year_list = search[:-1]
    if not year_list:
        print("未获取到基金年限,该基金可能暂停申购")
        print(f"### {years_url} ###")
        print(content)
        # raise Exception("未获取到基金年限")
    fund_info = []
    for year in year_list:
        # 获取每一年的数据
        year_url = f"http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={fund_code}&topline=1000&year={year}&month=&rt=0.21822537857648627"
        print(f"获取基金{fund_code}:{year}年")
        year_data = ""
        count = 0
        while not year_data and count < 5:
            # 请求获取不到数据,重新请求直到超过五次
            rsp = requests.get(url=year_url, headers=headers)
            content = rsp.text
            bs = BeautifulSoup(content, "html.parser")
            # 获取年度的数据
            year_data = bs.select(".box")
            count += 1
            if count == 5:
                print(year_url)
                print(year_data)
                raise Exception("年度数据为空")

        for period in year_data:
            # 解析每一季度的数据
            fund_name = period.select_one("h4 > label.left > a").text
            fund_page = period.select_one("h4 > label.left > a").get("href")
            fund_date = period.select_one("h4 > label.right > font").text
            print(f"获取基金{fund_code}:{year}年 {fund_date} ")
            period_data = period.select("table > tbody > tr")
            if not period_data:
                print(period)
                raise Exception("季度数据为空")
            for record in period_data:
                # 解析基金包含每只股票(一般为前十名)
                stock_code = record.select_one("td:nth-child(2)").text
                stock_name = record.select_one("td:nth-child(3)").text
                fund_proportion = record.select_one("td:nth-child(5)").text
                stock_value = record.select_one("td:nth-child(7)").text
                if "%" in stock_value:
                    # 如果数据的位置不对,进行位置调整
                    fund_proportion = record.select_one("td:nth-child(7)").text
                    stock_value = record.select_one("td:nth-child(9)").text

                # 进行数据格式转化
                if "-" in stock_value:
                    continue
                else:
                    # 不为空
                    stock_value = int(Decimal(stock_value.replace(",", "")) * 10000)

                if "-" in fund_proportion:
                    fund_proportion = 0
                else:
                    # 不为空
                    fund_proportion = Decimal(fund_proportion.rstrip("%")) / Decimal('100')
                fund_info.append(
                    {
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "stock_value": stock_value,
                        "fund_proportion": fund_proportion,
                        "fund_code": fund_code,
                        "fund_name": fund_name,
                        "fund_page": fund_page,
                        "fund_date": fund_date,
                    }
                )
    return fund_info


def get_stock_of_fund():
    # 获取所有基金的信息
    fund_info_list = get_funds_code()
    stock_info = []
    # 获取基金中的股票信息
    for fund_info in fund_info_list:
        print()
        fund_code = fund_info[0]
        stock_info += get_fund_stock_info(fund_code)
    # 转换成sql存储起来
    update_sql_list = []
    for stock in stock_info:
        columns_info = ",".join(stock.keys())
        values_info = ""
        for value_name in stock.values():
            if isinstance(value_name, str):
                values_info += "\'" + value_name + "\',"
            else:
                values_info += str(value_name) + ","
        update_sql = f"INSERT INTO tbl_stock_of_fund ({columns_info}) VALUES ({values_info});"
        update_sql_list.append(update_sql)
    # 存储数据库
    MysqlConn(**db_info).insert_by_sql(list_sql=update_sql_list)


if __name__ == "__main__":
    get_stock_of_fund()
