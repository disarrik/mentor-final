import sqlite3
import os
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

storage = os.getenv('STORAGE_DIR')
print(storage)

def __with_cursor(f):
    connection = sqlite3.connect(storage + '/' + 'shorten.db')
    cursor = connection.cursor()
    result = f(cursor)
    connection.commit()
    connection.close()
    return result

__with_cursor(lambda cursor: cursor.execute('''
CREATE TABLE IF NOT EXISTS URL (
id INTEGER PRIMARY KEY,
long TEXT NOT NULL
)
'''))

class Url(BaseModel):
    url: str

class Short(BaseModel):
    id: int

app = FastAPI(docs_url="/docs")

class Url(BaseModel):
    url: str

app = FastAPI()

def __save(long, cursor):
    cursor.execute("INSERT INTO URL (long) VALUES (?)", (long,))
    return cursor.lastrowid

@app.post("/shorten", response_model=Short)
def post(body: Url) -> Short:
    return Short(id = __with_cursor(lambda cur: __save(body.url, cur)))

def __get(short, cursor):
    cursor.execute("SELECT long FROM URL WHERE id = ?", (short,))
    result = cursor.fetchone()
    return result[0]

@app.get('/{shortId}')
def get(shortId: int):
    url = __with_cursor(lambda cur: __get(shortId, cur))
    return RedirectResponse(url)

@app.get('/stats/{shortId}', response_model=Url)
def get_stats(shortId: int):
    url = __with_cursor(lambda cur: __get(shortId, cur))
    return Url(url=url)
    
