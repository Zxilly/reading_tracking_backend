import json
from typing import Optional

import uvicorn
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
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


class Book(BaseModel):
    progress: Optional[int] = None
    isbn: str
    tip: Optional[str] = None


def name_get(user: str):
    return '../data/user/' + user + '.json'


@app.get('/api')
async def output(user: str):
    try:
        with open(name_get(user), 'r+') as f:
            return {'code': 1, 'data': json.loads(f.read())}
    except:
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
        }
    用户文件结构
    user
    books:[
    {
        isbn
        title
        subtitle
        img_url
        author
        page_total
    },{...}
        ]
    """
    if (len(book.isbn) != 13):
        return {'code': 0, 'msg': 'ISBN输入错误'}

    if (method == 'add'):
        try:
            with open(name_get(user), 'r+') as f:
                file_obj = json.loads(f.read())
        except:
            file_obj = None
        book_obj = BookObject(book.isbn)
        book_obj.info_dict['progress'] = book.progress
        book_obj.info_dict['tip'] = book.tip
        book_progress = book.progress
        book_tip = book.tip
        if (file_obj):
            file_obj['books'].append(book_obj.info_dict)
        else:
            file_obj = {}
            file_obj['user'] = user
            file_obj['books'] = []
            file_obj['books'].append(book_obj.info_dict)
        with open(name_get(user), 'w+') as f:
            f.write(json.dumps(file_obj, ensure_ascii=False))
        return {'code': 1, 'msg': '{} 已开始跟踪'.format(book_obj.title)}

    if(method == 'update'):
        with open(name_get(user), 'r+') as f:
            file_obj = json.loads(f.read())
            for one_book in file_obj['books']:
                if(one_book['isbn']==book.isbn):
                    one_book['progress'] = book.progress
                    one_book['tip'] = book.tip
                    book_name = one_book['title']
            f.write(json.dumps(file_obj,ensure_ascii=False))
        return {'code': 2, 'msg': '{} 状态已更新'.format(book_name)}


    if (method == 'delete'):
        with open(name_get(user), 'w+') as f:
            file_obj = json.loads(f.read())
            book_obj = BookObject(book.isbn)
            file_obj['books'].remove(book_obj.info_dict)
            f.write(json.dumps(file_obj))
        return {'code': 3, 'msg': '{} 已不再追踪'.format(book_obj.title)}


if __name__ == '__main__':
    uvicorn.run(app='api:app', host='0.0.0.0', port=4000, debug=False)
