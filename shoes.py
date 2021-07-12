# -*- coding:utf-8 -*-
import multiprocessing
import os
import re
import requests

headers = {
    'Host': 'cdn.shopify.com',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}


def get_image_info(page, collection_scope):
    params = {
        't': '1625711440862',
        '_': 'pf',
        'shop': 'heydudeshoes.myshopify.com',
        'page': page,
        'limit': '100',
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
        r'"\d":"(https://cdn.shopify.com/s/files/1/.*?)",',
        content,
        re.M | re.I)
    name_list = re.findall(
        r'"\d":"https://cdn.shopify.com/s/files/1/\d+/\d+/products/(.*?)\?v=\d+",',
        content,
        re.M | re.I)
    image_dict = {name: image for image, name in zip(image_list, name_list)}
    return image_dict


def download_image(img_url, path):
    print(img_url)
    status_code = 100
    while status_code != 200:
        r = requests.get(img_url, headers=headers, stream=True)
        status_code = r.status_code
        print(status_code)  # 返回状态码
        if status_code == 200:
            with open(path, "wb") as f:
                # 将内容写入图片
                print(f"path:{path}")
                f.write(r.content)
            print("done")


def download_image1(img_url, path):
    r = requests.get(img_url, headers=headers, stream=True)
    f = open(path, "wb")
    for chunk in r.iter_content(chunk_size=512):  # 按照块的大小读取
        # for chunk in r.iter_lines():    # 按照一行一行的读取
        if chunk:
            f.write(chunk)
    f.close()


def process(page_no, collection_scope, type):
    image_info = get_image_info(page_no, collection_scope)
    for image_name, image_url in image_info.items():
        save_path = os.path.join(".", type, str(page_no))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        download_image(image_url, os.path.join(save_path, image_name))


def main():
    collect_list = {
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
    # 开启3个进程，传入爬取的页码范围
    pool = multiprocessing.Pool(processes=7)
    for item, value in collect_list.items():
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
