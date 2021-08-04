#!/usr/bin/env python

"""
-------------------------------------------------
@date：         2021/7/30 10:41
@Author :
@File Name：
@Description : 爬取网站信息
-------------------------------------------------
"""
import multiprocessing
import os
import re
import requests
from util.download import download_image

headers = {
    # 'Host': 'cdn.shopify.com',
    'Host': 'services.mybcapps.com',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # 'Sec-Fetch-Site': 'none',
    # 'Sec-Fetch-Mode': 'navigate',
    # 'Sec-Fetch-User': '?1',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Dest': 'script',
    'Referer': 'https://www.uinfootwear.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}


def get_image_info(page, collection_scope):
    params = {
        't': '1627191096129',
        '_': 'pf',
        # 'shop': 'heydudeshoes.myshopify.com',  # https://www.heydudeshoesusa.com/
        # https://www.uinfootwear.com/
        'shop': 'uin-footwear-official-store.myshopify.com',
        'page': page,
        'limit': 40,
        'sort': 'manual',
        'display': 'grid',
        'collection_scope': collection_scope,
        'tag': '',
        'product_available': 'true',
        'variant_available': 'true',
        'build_filter_tree': 'true',
        'check_cache': 'true',
        'sort_first': 'available',
        'callback': 'BoostPFSFilterCallback',
        'event_type': 'init'
    }

    response = requests.get(
        "https://services.mybcapps.com/bc-sf-filter/filter", headers=headers,
        params=params)
    content = response.text

    image_list = re.findall(
        r'"\d":"(https://cdn.shopify.com/s/files/1/.*?)"+?',
        content,
        re.M | re.I)
    print(f"获取链接数量:{len(image_list)}")
    for i, j in enumerate(image_list):
        if "\"" in image_list:
            print(i)
            print(j)
    name_list = re.findall(
        # r'"\d":"https://cdn.shopify.com/s/files/1/\d+/\d+/products/(.*?)\?v=\d+",',
        # # https://www.heydudeshoesusa.com/
        # https://www.uinfootwear.com/
        r'"\d":"https://cdn.shopify.com/s/files/1/\d+/\d+/\d+/products/(.*?)\?v=\d+"+?',
        content,
        re.M | re.I)
    for i, j in enumerate(name_list):
        if "\"" in name_list:
            print(i)
            print(j)
            print(response.text)
            raise Exception
    # for i, j in enumerate(name_list):
    #     print(i)
    #     print(j)
    print(f"获取名字数量:{len(name_list)}")
    image_dict = {name: image for image, name in zip(image_list, name_list)}
    return image_dict


def process(page_no, collection_scope, type):
    image_info = get_image_info(page_no, collection_scope)
    for image_name, image_url in image_info.items():
        save_path = os.path.join("..", type, str(page_no))
        image_info[image_name] = os.path.join(save_path, image_name)
        download_image(image_info)


def main():
    # https://www.heydudeshoesusa.com/
    hey_collect_list = {
        "women": {
            "page": 3,
            "collection_scope": 26778261,
        },
        "men": {
            "page": 3,
            "collection_scope": 26778249,
        },
        "youth": {
            "page": 1,
            "collection_scope": 154960199747,
        },
    }
    # https://www.uinfootwear.com/
    uin_collect_list = {
        "women": {
            "page": 10,
            "collection_scope": 91020558390,
        },
        "men": {
            "page": 8,
            "collection_scope": 166455148657,
        },
        "kids": {
            "page": 3,
            "collection_scope": 91021344822,
        },
    }
    # 开启3个进程，传入爬取的页码范围
    pool = multiprocessing.Pool(processes=21)
    for item, value in uin_collect_list.items():
        page = value.get("page")
        collection_scope = value.get("collection_scope")
        for page_no in range(1, page + 1):
            # 维持执行的进程总数为10，当一个进程执行完毕后会添加新的进程进去
            print(
                f"page{page_no} \n collection_scope:{ collection_scope}\n item:{item}")
            pool.apply_async(process, args=(page_no, collection_scope, item))
            print('======apply_async======')
    # 关闭进程池，表示不能在往进程池中添加进程
    pool.close()
    # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    pool.join()


if __name__ == '__main__':
    main()
