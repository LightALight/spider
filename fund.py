#!/usr/bin/env python

"""
-------------------------------------------------
@date：         2021/7/28 15:27
@Author :
@File Name：    fund.py.py
@Description :
-------------------------------------------------
"""
import datetime
import os
import subprocess
from multiprocessing import Manager, Pool, current_process
import time
from decimal import Decimal
import requests
import json
import re
from bs4 import BeautifulSoup
from util.mysql_conn import MysqlConn

# 浏览器头
headers = {
    'content-type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
}
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


def store_stock_of_fund(stock_info):
    update_sql_list = []
    for stock in stock_info:
        columns_info = ",".join(stock.keys())
        values_info = ""
        for value_name in stock.values():
            if isinstance(value_name, str):
                values_info += "\"" + value_name + "\","
            else:
                values_info += str(value_name) + ","
        update_sql = f'REPLACE INTO tbl_stock_of_fund ({columns_info}) VALUES ({values_info.rstrip(",")});'
        update_sql_list.append(update_sql)

    # 存储数据库
    mysql_conn = MysqlConn(**db_info)
    # print(update_sql_list)
    mysql_conn.insert_by_sql(list_sql=update_sql_list)


def error_info_write(info):
    with open("error.log", "a+", encoding="utf-8") as f:
        f.write(info)


def get_fund_stock_info(fund_code, share_lock):
    """ 获取基金股票信息
    :param fund_code:
    :return:
    """
    print(f"开始获取基金{fund_code}")
    stock_info = []
    # 获取年份信息
    years_url = f"http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={fund_code}&topline=1000&year=1970&month=&rt=0.21822537857648627"
    rsp = requests.get(url=years_url, headers=headers)
    content = rsp.text
    search = re.findall(r'[1-2][0-9]{3}', content, re.M | re.I)
    # 去掉冗余数据
    year_list = search[:-1]
    if not year_list:
        print(f"1.未获取到基金 {fund_code}年限,该基金可能暂停申购")
        print(f"years_url: {years_url} ")
        # error_info_write(f"content: {content}\n")
        # raise Exception("未获取到基金年限")
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
            if count == 10:
                error_info_write(f"2.获取基金{fund_code}:{year}年")
                error_info_write(f"years_url: {year_url} ")
                error_info_write(f"year_data: {year_data}\n")
                raise Exception("年度数据为空")

        for period in year_data:
            # 解析每一季度的数据
            fund_name = period.select_one("h4 > label.left > a").text
            fund_page = period.select_one("h4 > label.left > a").get("href")
            fund_date = period.select_one("h4 > label.right > font").text
            print(f"获取基金{fund_code}:{year}年 {fund_date} ")
            period_data = period.select("table > tbody > tr")
            if not period_data:
                error_info_write(f"3.获取基金{fund_code}:{year}年 {fund_date} ")
                error_info_write(f"period: {period}\n")
                raise Exception("季度数据为空")
            for record in period_data:
                # 解析基金包含每只股票(一般为前十名)
                stock_code = record.select_one("td:nth-child(2)").text
                stock_name = record.select_one("td:nth-child(3)").text
                fund_proportion = record.select_one("td:nth-child(5)").text
                stock_value = record.select_one("td:nth-child(7)")

                if not stock_value:
                    # 未解析到股票
                    child_record = record.select("td:nth-child(4) > td")
                    if child_record:
                        fund_proportion = child_record[0].text
                        stock_value = child_record[2].text
                    else:
                        error_info_write(
                            f"4.获取基金{fund_code}:{year}年 {fund_date} ")
                        error_info_write(f"record: {record}\n")
                        raise Exception("未解析到数据")
                elif "%" in stock_value.text:
                    # 如果数据的位置不对,进行位置调整
                    fund_proportion = record.select_one("td:nth-child(7)").text
                    stock_value = record.select_one("td:nth-child(9)").text
                else:
                    stock_value = stock_value.text

                if not stock_code or not stock_value:
                    # 未解析到股票抛异常
                    error_info_write(
                        f"5.获取基金{fund_code}:{year}年 {fund_date} ")
                    error_info_write(f"period: {period} ")
                    error_info_write(
                        f"stock_code: {stock_code} stock_value {stock_value} ")
                    raise Exception("未解析到数据")

                # 进行数据格式转化
                if "-" in stock_value:
                    continue
                else:
                    # 不为空
                    stock_value = int(
                        Decimal(
                            stock_value.replace(
                                ",", "")) * 10000)

                if "-" in fund_proportion or not fund_proportion:
                    fund_proportion = 0
                else:
                    # 不为空
                    fund_proportion = Decimal(
                        fund_proportion.rstrip("%")) / Decimal('100')
                stock_info.append(
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
    # return stock_info
    # 存储数据库
    if stock_info:
        share_lock.acquire()
        store_stock_of_fund(stock_info)
        share_lock.release()
    print(f"获取基金{fund_code}完成\n")


def throw_exception(name):
    print(f'子进程{name}发生异常,进程号为{os.getpid()}')
    # 子进程异常会导致所有进程僵死
    cmd = f'taskkill /im {str(os.getpid())} /F'
    res = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    print(res.stdout.read())
    print(res.stderr.read())
    time.sleep(2)


def get_stock_of_fund():
    # 获取所有基金的信息
    fund_info_list = get_funds_code()
    share_lock = Manager().Lock()

    # 开启3个进程，传入爬取的页码范围
    with Pool(processes=40) as pool:
        for index, fund_info in enumerate(fund_info_list):
            start_time_fp = datetime.datetime.now()
            fund_code = fund_info[0]
            print(f"第 {index} 个基金:{fund_code}")
            # 异步非阻塞
            pool.apply_async(
                func=get_fund_stock_info,
                args=(fund_code, share_lock),
                error_callback=throw_exception
            )
            over_time_fp = datetime.datetime.now()
            total_time = (over_time_fp - start_time_fp).total_seconds()
        print(f'加载进程数共计{total_time}秒')
        print('-------------------')
        print('这是主进程在子进程后执行的部分:{}'.format(time.time()))
        print('-------------------')
        # 关闭进程池，表示不能在往进程池中添加进程
        pool.close()
        # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
        pool.join()
        print('主进程结束:{}'.format(time.time()))

    # 获取基金中的股票信息
    # for fund_info in fund_info_list[7885:7886]:
    #     fund_code = fund_info[0]
    #     get_fund_stock_info(fund_code, share_lock)


if __name__ == "__main__":
    get_stock_of_fund()
