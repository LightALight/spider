#!/usr/bin/env python

"""
-------------------------------------------------
@date：         2021/7/28 15:27
@Author :
@File Name：    fund.py.py
@Description : 爬取基金中的股票信息
-------------------------------------------------
"""
import datetime
from multiprocessing import Manager, Pool
import os
import subprocess
import time
from decimal import Decimal
import requests
import json
import re
from bs4 import BeautifulSoup
from util.tools import store_records, error_info_write

# 浏览器头
headers = {
    'content-type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
}


def get_fund_info(info_type="code"):
    """获取所有基金基本信息

    :param info_type:
    :return:
    """
    if info_type == "code":
        url = "http://fund.eastmoney.com/js/fundcode_search.js"
        rsp = requests.get(url=url, headers=headers)
        content = rsp.text
        fund_info_list = re.findall(
            r'\[".+?\]',
            content,
            re.M | re.I)
        fund_info_list = [eval(fund_info) for fund_info in fund_info_list]
        return fund_info_list
    elif info_type == "company":
        url = f"http://fund.eastmoney.com/js/jjjz_gs.js?rt={int(round(time.time() * 1000))}"
        rsp = requests.get(url=url, headers=headers)
        content = rsp.text
        # 查找结果
        search = re.findall(r'\[\".+?\"\]', content, re.M | re.I)
        for record in search:
            data = json.loads(record)
            return {
                "fund_company_code": data[0],
                "fund_company_name": data[1],
            }
        else:
            return "未找到信息"


def get_fund_info_by_code(fund_code, return_format="rate"):
    """ 通过基金编号获取基金的信息

    :param fund_code: string 基金编号
    :param return_format: string rate 实时利率/detail 返回信息详细程度
    :return:
    """
    if return_format == "rate":
        url = f"http://fundgz.1234567.com.cn/js/{fund_code}.js?rt={int(round(time.time() * 1000))}"
        rsp = requests.get(url=url, headers=headers)
        content = rsp.text
        # 查找结果
        search = re.findall(r'\{.*\}', content, re.M | re.I)
        if search:
            data = json.loads(search[0])
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
            return "未找到信息"

    else:
        # 页面:http://fund.eastmoney.com/000001.html?spm=search
        url = f"http://fund.eastmoney.com/pingzhongdata/{fund_code}.js?v={time.strftime('%Y%m%d%H%M%S', time.localtime())}"
        rsp = requests.get(url=url, headers=headers)
        content = rsp.text
        # 查找结果
        print(content)
        # 基金名称
        fund_name = re.findall(r'fS_name = "(.+?)"', content, re.M | re.I)[0]
        # 基金现有费率
        fund_rate = re.findall(r'fund_Rate="(.+?)"', content, re.M | re.I)[0]
        # 基金最小申购金额
        fund_min_amount = re.findall(r'fund_minsg="(.+?)"', content, re.M | re.I)[0]
        # 基金持有股票
        fund_stock_codes = re.findall(r'stockCodesNew =(\[.+?\])', content, re.M | re.I)
        if fund_stock_codes:
            fund_stock_code_list = json.loads(fund_stock_codes[0])
            fund_stock_code_list = [stock_code[2:] for stock_code in fund_stock_code_list]
        else:
            fund_stock_code_list = []
        # 基金持有债券
        fund_bond_codes = re.findall(r'zqCodesNew =(\[.+?\])', content, re.M | re.I)
        if fund_bond_codes:
            fund_bond_code_list = json.loads(fund_bond_codes[0])
            fund_bond_code_list = [bond_code.ltrip("0.").ltrip("1.") for bond_code in fund_bond_code_list]
        else:
            fund_bond_code_list = []
        # 基金阶段性收益率
        fund_interest_rate_1y = re.findall(r'syl_1n="(.+?)"', content, re.M | re.I)[0]
        fund_interest_rate_6m = re.findall(r'syl_6y="(.+?)"', content, re.M | re.I)[0]
        fund_interest_rate_3m = re.findall(r'syl_3y="(.+?)"', content, re.M | re.I)[0]
        fund_interest_rate_1m = re.findall(r'syl_1y="(.+?)"', content, re.M | re.I)[0]

        fund_info = {
            "fund_name": fund_name,
            "fund_code": fund_code,
            "fund_rate": '{:.2%}'.format(float(fund_rate)/100),
            "fund_min_amount": fund_min_amount,
            "fund_stock_code_list": fund_stock_code_list,
            "fund_bond_code_list": fund_bond_code_list,
            "fund_interest_rate_1m":'{:.2%}'.format(float(fund_interest_rate_1m)/100),
            "fund_interest_rate_3m":'{:.2%}'.format(float(fund_interest_rate_3m)/100),
            "fund_interest_rate_6m":'{:.2%}'.format(float(fund_interest_rate_6m)/100),
            "fund_interest_rate_1y":'{:.2%}'.format(float(fund_interest_rate_1y)/100),
        }

        print(fund_info)
        # 单位净值走势
        fund_value_pattern = r'{"x":[0-9]{13},"y":.+?,"equityReturn":.+?,"unitMoney":".*?"}'
        # 累计净值走势
        fund_cumulative_value_pattern = r'Data_ACWorthTrend = \[.*?\];/*累计收益率走势*/'
        # 累计收益率走势
        fund_cumulative_value_pattern = r'Data_grandTotal = \[.*?\];/*累计收益率走势*/'
        fund_value_records = re.findall(
            fund_value_pattern, content, re.M | re.I)
        fund_cumulative_value_records = re.findall(
            fund_cumulative_value_pattern, content, re.M | re.I)
        for index, fund_value_record in enumerate(fund_value_records):
            value_data = json.loads(fund_value_records[index])
            cumulative_value_data = json.loads(fund_cumulative_value_records[index])
            fund_value_records[index] = {
                "fund_date": time.strftime("%Y-%m-%d",time.localtime(value_data.get("x")/1000)),  # 日期
                "fund_value": value_data.get("y"),  # 净值
                "fund_cumulative_value": cumulative_value_data[1],  # 累计净值
                "fund_return": value_data.get("equityReturn"),  # 净值回报
                "fund_money": value_data.get("unitMoney"),  # 每份派送金
            }
        print(fund_value_records)
        return fund_value_records


def get_fund_stock_info(fund_code, table_name, share_lock):
    """ 获取基金历史持有股票信息并写入数据库
    :param fund_code: sting 基金编号
    :param table_name: string 表名
    :param share_lock: lock 共享锁
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
                if "." in stock_code:
                    split_index = stock_code.index(".")
                    stock_code, exchange = stock_code[:split_index], stock_code[split_index + 1:]
                else:
                    exchange = ""
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
                        "exchange": exchange,
                    }
                )
    # 存储数据库
    if stock_info:
        share_lock.acquire()
        store_records(table_name, stock_info)
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
    fund_info_list = get_fund_info()
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
                args=(fund_code, "tbl_fund_stock_info", share_lock),
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
    # for fund_info in fund_info_list[11200:]:
    #     fund_code = fund_info[0]
    #     get_fund_stock_info(fund_code, share_lock)


if __name__ == "__main__":
    get_fund_info_by_code("000001", "company")
