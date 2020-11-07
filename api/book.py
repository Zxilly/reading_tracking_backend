import json
from functools import reduce

import requests
from bs4 import BeautifulSoup

base_url = '/data/books/img/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}


class BookObject(object):
    def __init__(self, isbn: str):
        self.isbn = isbn
        self.url = "https://api.douban.com/v2/book/isbn/"
        self.parser_url = "https://book.douban.com/isbn/"
        self.api_key = "0b2bdeda43b5688921839c8ecb20399b"
        self.title = ''
        # self.sub_title = data['sub_title']
        self.pic_url = ''
        self.page_total = 0
        self.author_str = ''
        try:
            self.get_cache()
        except:
            self.add_cache_parser()
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
        # print("data is" + data)
        self.title = data['title']
        # self.sub_title = data['subtitle']
        # self.pic_url = 'data:image/jpg;base64,' + base64.b64encode(requests.get(data['images']['medium'].content))
        self.pic_url = base_url + self.isbn + '.jpg'
        with open('../data/books/img/' + self.isbn + '.jpg', 'wb') as f:
            f.write(requests.get(data['image']).content)
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

    def add_cache_parser(self):
        html = requests.get(self.parser_url + self.isbn, headers=headers).content.decode(encoding='UTF-8')
        html_object = BeautifulSoup(html, "lxml")
        info = html_object.find(id="info")
        # with open('a.html', 'w+', encoding='UTF-8') as f:
        #     f.write(info.__str__())
        book_name = html_object.find(name='h1').find(name='span').string
        book_cover = html_object.find(class_='nbg')['href']
        try:
            author_name = \
                info.find(name='span', string=" 作者").parent.get_text().replace(" ", "").replace("\n", "") \
                    .split("作者:")[1]
        except:
            try:
                author_name = ''
                author_pointer = info.find(name='span', string="作者:").next_sibling
                while True:
                    author_pointer = author_pointer.next_sibling
                    # print(author_pointer)
                    # print(author_pointer.name)
                    if author_pointer.name != 'br':
                        if author_pointer.name == 'a':
                            author_name += author_pointer.get_text(strip=True) + '/'
                            # print('author is ' + author_name)
                    else:
                        author_name = author_name.rstrip('/')
                        break
            except:
                # print('error')
                author_name = ""

        try:
            page_num = info.find(name='span', string="页数:").next_sibling.replace(" ", "")
        except:
            page_num = 0
        self.title = book_name
        print(book_cover.find("update_image"))
        if book_cover.find("update_image") == -1:
            self.pic_url = base_url + self.isbn + '.jpg'
            with open('../data/books/img/' + self.isbn + '.jpg', 'wb') as f:
                f.write(requests.get(book_cover).content)
        else:
            self.pic_url = ''
        self.page_total = int(page_num)
        self.author_str = author_name

        with open('../data/books/{}'.format(self.isbn) + '.json', 'w+', encoding='UTF-8') as f:
            f.write(json.dumps({
                'title': self.title,
                # 'sub_title': self.sub_title,
                'pic_url': self.pic_url,
                'page_total': self.page_total,
                'author_str': self.author_str
            }, ensure_ascii=False))


if __name__ == '__main__':
    a = BookObject("9787040511420")
