import os
import requests
import re
import time
from urllib.parse import urlencode

COUNT = 0


def get_query_urls(offset, keyword):
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab',
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None


def get_one_page(url):
    headers = {
        'user-agent':
        'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/67.0.3396.62 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.ConnectionError:
        return None


def get_images(json):
    data = json.get('data')
    if data:
        for item in data:
            title = item.get('title')
            article_url = item.get('item_id')
            if article_url:
                image_html = get_one_page('http://toutiao.com/group/' +
                                          article_url + '/')
                pattern = re.compile(
                    r'\\"uri\\":\\"origin\\\\/pgc-image\\\\/(.*?)\\",', re.S)
                items_id_list = re.findall(pattern, str(image_html))
                if len(items_id_list) > 0:
                    for imageIndex in range(len(items_id_list)):
                        yield {
                            'image': items_id_list[imageIndex],
                            'title': title
                        }


def save_image(item):
    global COUNT
    if not os.path.exists('./examples/' + str(COUNT) + '_' +
                          item.get('title')):
        os.mkdir('./examples/' + str(COUNT) + '_' + item.get('title'))
    try:
        local_image_url = item.get('image')
        new_image_url = 'http://p1.pstatp.com/origin/pgc-image/' + local_image_url
        response = requests.get(new_image_url)
        if response.status_code == 200:
            file_path = './examples/{0}/{1}.{2}'.format(
                str(COUNT) + '_' + item.get('title'), local_image_url, 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print('Download Done!')
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to save image')


def main(offset, keyword):
    global COUNT
    json = get_query_urls(offset, keyword)
    ss1 = ''
    for item in get_images(json):
        print(item)
        ss2 = item.get('title')
        if ss1 != ss2:
            COUNT = COUNT + 1
            ss1 = ss2
        save_image(item)
        time.sleep(1)


if __name__ == '__main__':
    keyword = input("请输入关键字：")
    for x in range(3):
        main(x * 20, keyword)
