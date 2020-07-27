import json
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, Body
from fastapi.encoders import jsonable_encoder
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
    progress: int
    isbn: str
    tip: str
    data: Optional[dict] = None


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
async def input(user: str, books: Optional[List[Book]] = Body(..., embed=True)):
    for book in books:
        BookInfo = BookObject(book.isbn)
        book.data = BookInfo.info_dict
    with open(name_get(user), 'w+') as f:
        f.write(json.dumps(jsonable_encoder(books)))
    return {'code': 1, 'msg': 'Update success.'}


if __name__ == '__main__':
    uvicorn.run(app='api:app', host='0.0.0.0', port=4000, debug=False)
