import requests
import json

def get_book(isbn:str):
    url = "https://api.douban.com/v2/book/isbn/"
    api_key = "0b2bdeda43b5688921839c8ecb20399b"

    def get_cache():
        with open('../data/books/{}'.format(isbn),'r+') as f:
            ...

    def add_cache():
        req = json.loads(requests.get(url+isbn,params={"apikey":api_key}).content)

