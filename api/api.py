import json
from typing import Optional

import uvicorn
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from book import BookObject

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/data/books/img", StaticFiles(directory="../data/books/img"), name="static")


class Book(BaseModel):
    progress: Optional[int] = None
    isbn: str
    tip: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    page: Optional[str] = None


def name_get(user: str):
    return '../data/user/' + user + '.json'


@app.get('/api')
async def output(user: str):
    try:
        # print('code=1')
        with open(name_get(user), 'r+', encoding='UTF-8') as f:
            data = json.loads(f.read())
            if (len(data['books']) != 0):
                return {'code': 1, 'data': data}
            else:
                return {'code': 0, 'msg': 'No book is tracking'}
    except:
        # print(('code=0'))
        # print(traceback.format_exc())
        return {'code': 0, 'msg': 'Can not find any record. Please add your tracking first.'}


@app.post('/api')
async def input(user: str, method: str = Body(...), book: Book = Body(..., embed=True)):
    """
    请求结构
    user
    method
    book:{
        progress
        isbn
        tip
        title
        author
        page
        }
    用户文件结构
    user
    books:[
    {
        isbn
        title
        subtitle
        img_url
        author_str
        page_total
    },{...}
        ]
    """
    if len(book.isbn) != 13:
        return {'code': 5, 'msg': 'ISBN错误'}

    if user == '':
        return {'code': 6, 'msg': '用户名为空'}

    if (method == 'add'):
        try:
            with open(name_get(user), 'r+', encoding='UTF-8') as f:
                file_obj = json.loads(f.read())
            for one_book in file_obj['books']:
                if (one_book['isbn'] == book.isbn):
                    return {'code': 4, 'msg': '{} 已在跟踪中'.format(one_book['title'])}
        except:
            file_obj = None
        try:
            book_obj = BookObject(book.isbn)
        except:
            return {'code': 5, 'msg': 'ISBN错误'}
        book_obj.info_dict['progress'] = book.progress
        book_obj.info_dict['tip'] = book.tip
        if (file_obj):
            file_obj['books'].append(book_obj.info_dict)
        else:
            file_obj = {}
            file_obj['user'] = user
            file_obj['books'] = []
            file_obj['books'].append(book_obj.info_dict)
        with open(name_get(user), 'w+', encoding='UTF-8') as f:
            f.write(json.dumps(file_obj, ensure_ascii=False))
        return {'code': 1, 'msg': '{} 已开始跟踪'.format(book_obj.title)}

    if (method == 'update'):
        with open(name_get(user), 'r+', encoding='UTF-8') as f:
            file_obj = json.loads(f.read())
            for one_book in file_obj['books']:
                if (one_book['isbn'] == book.isbn):
                    one_book['progress'] = book.progress
                    one_book['tip'] = book.tip
                    book_name = one_book['title']
        with open(name_get(user), 'w+', encoding='UTF-8') as f:
            f.write(json.dumps(file_obj, ensure_ascii=False))
        return {'code': 2, 'msg': '{} 状态已更新'.format(book_name)}

    if (method == 'edit'):
        with open(name_get(user), 'r+', encoding='UTF-8') as f:
            file_obj = json.loads(f.read())
            for one_book in file_obj['books']:
                if (one_book['isbn'] == book.isbn):
                    one_book['title'] = book.title
                    one_book['author_str'] = book.author
                    one_book['page_total'] = book.page
                    book_name = one_book['title']
        with open(name_get(user), 'w+', encoding='UTF-8') as f:
            f.write(json.dumps(file_obj, ensure_ascii=False))
        return {'code': 7, 'msg': '{} 信息已编辑'.format(book_name)}

    if (method == 'delete'):
        with open(name_get(user), 'r+', encoding='UTF-8') as f:
            file_obj = json.loads(f.read())
            book_obj = BookObject(book.isbn)
            for one_book in file_obj['books']:
                if (one_book['isbn'] == book.isbn):
                    file_obj['books'].remove(one_book)
        with open(name_get(user), 'w+', encoding='UTF-8') as f:
            f.write(json.dumps(file_obj, ensure_ascii=False))
        return {'code': 3, 'msg': '{} 已不再追踪'.format(book_obj.title)}


if __name__ == '__main__':
    uvicorn.run(app='api:app', host='0.0.0.0', port=4000, debug=True)
