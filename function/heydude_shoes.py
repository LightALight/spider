#!/usr/bin/env python

"""
-------------------------------------------------
@date：         2021/7/30 10:41
@Author :
@File Name：
@Description : 爬取网站信息 https://heydude.shoes
-------------------------------------------------
"""
import multiprocessing
import os
import bs4
import requests
from config.target_url import hey_dude_url
from util.download import download_image

headers = {
    'content-type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
}


def get_image_info(page, type):
    params = {
        'p': page,
    }

    response = requests.get(f"{hey_dude_url}{type}", headers=headers,
                            params=params)
    content = response.text
    soup = bs4.BeautifulSoup(content, "html.parser")
    image_list = soup.select("div > div.left-block > div > a > img")
    image_dict = {image.get("alt").replace(" ", "-") +
                  ".jpg": image.get("src") for image in image_list}
    return image_dict


def process(page_no, type):
    image_info = get_image_info(page_no, type)
    for image_name, image_url in image_info.items():
        save_path = os.path.join("..", type, str(page_no))
        download_image(
            image_url,
            os.path.join(
                save_path,
                image_name),
            headers=headers)


def main():
    hey_collect_list = {
        "8-men": {
            "page": 19,
        },
        "6-women": {
            "page": 7,
        },
        "97-kids": {
            "page": 1,
        },
    }
    # 开启3个进程，传入爬取的页码范围
    pool = multiprocessing.Pool(processes=3)
    for item, value in hey_collect_list.items():
        page = value.get("page")
        for page_no in range(1, page + 1):
            # 维持执行的进程总数为10，当一个进程执行完毕后会添加新的进程进去
            print(
                f"page{page_no} \n  item:{item}")
            pool.apply_async(process, args=(page_no, item))
            print('======apply_async======')
    # 关闭进程池，表示不能在往进程池中添加进程
    pool.close()
    # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    pool.join()


if __name__ == '__main__':
    main()
