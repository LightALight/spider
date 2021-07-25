import os

import requests


download_headers = {
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
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}


def download_way_image(img_url, path, headers):
    print(f"img_url:{img_url}")
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
        else:
            print("error")


def download_way_image1(img_url, path, headers):
    r = requests.get(img_url, headers=headers, stream=True)
    f = open(path, "wb")
    for chunk in r.iter_content(chunk_size=512):  # 按照块的大小读取
        # for chunk in r.iter_lines():    # 按照一行一行的读取
        if chunk:
            f.write(chunk)
    f.close()


def download_image(image_info, headers=download_headers):
    for image_name, image_url in image_info.items():
        save_path = os.path.dirname(image_url)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        download_way_image(image_url, image_url, headers)
