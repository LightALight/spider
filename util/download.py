import os

import requests


def download_way_image1(img_url, path, headers):
    r = requests.get(img_url, headers=headers, stream=True)
    f = open(path, "wb")
    for chunk in r.iter_content(chunk_size=512):  # 按照块的大小读取
        # for chunk in r.iter_lines():    # 按照一行一行的读取
        if chunk:
            f.write(chunk)
    f.close()


def download_image(image_url,save_path, headers):
    save_dir = os.path.dirname(save_path)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    print(f"img_url:{image_url}")
    print(f"save_path:{save_path}")
    status_code = 100
    while status_code != 200:
        r = requests.get(image_url, headers=headers, stream=True)
        status_code = r.status_code
        print(status_code)  # 返回状态码
        if status_code == 200:
            with open(save_path, "wb") as f:
                # 将内容写入图片
                print(f"path:{save_path}")
                f.write(r.content)
            print("done")
        else:
            print("error")