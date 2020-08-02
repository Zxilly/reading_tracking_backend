import json
from functools import reduce

import requests

base_url = '/data/books/img/'


class BookObject(object):
    def __init__(self, isbn: str):
        self.isbn = isbn
        self.url = "https://api.douban.com/v2/book/isbn/"
        self.api_key = "0b2bdeda43b5688921839c8ecb20399b"
        try:
            self.get_cache()
        except:
            self.add_cache()
        self.info_dict = {
            'isbn': self.isbn,
            'title': self.title,
            # 'sub_title': self.sub_title,
            'pic_url': self.pic_url,
            'page_total': self.page_total,
            'author_str': self.author_str
        }

    def get_cache(self):
        with open('../data/books/{}'.format(self.isbn) + '.json', 'r+', encoding='UTF-8') as f:
            data = json.loads(f.read())
            self.title = data['title']
            # self.sub_title = data['sub_title']
            self.pic_url = data['pic_url']
            self.page_total = data['page_total']
            self.author_str = data['author_str']

    def add_cache(self):
        data = json.loads(requests.get(self.url + self.isbn, params={"apikey": self.api_key}).content)
        self.title = data['title']
        # self.sub_title = data['subtitle']
        # self.pic_url = 'data:image/jpg;base64,' + base64.b64encode(requests.get(data['images']['medium'].content))
        self.pic_url = base_url + self.isbn + '.jpg'
        with open('../data/books/img/' + self.isbn + '.jpg', 'wb') as f:
            f.write(requests.get(data['images']['medium']).content)
        self.page_total = data['pages']
        try:
            self.author_str = reduce(lambda str, list_one: str + '; ' + list_one, data['author'])
        except:
            self.author_str = ''
        with open('../data/books/{}'.format(self.isbn) + '.json', 'w+', encoding='UTF-8') as f:
            f.write(json.dumps({
                'title': self.title,
                # 'sub_title': self.sub_title,
                'pic_url': self.pic_url,
                'page_total': self.page_total,
                'author_str': self.author_str
            }, ensure_ascii=False))
