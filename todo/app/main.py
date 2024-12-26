import sqlite3
import os
from pydantic import BaseModel
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse, JSONResponse

storage = os.getenv('STORAGE_DIR')

def __with_cursor(f):
    connection = sqlite3.connect(storage + '/' + 'tasks.db')
    cursor = connection.cursor()
    result = f(cursor)
    connection.commit()
    connection.close()
    return result

__with_cursor(lambda cursor: cursor.execute('''
CREATE TABLE IF NOT EXISTS Items (
id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
description TEXT,
completed BOOLEAN DEFAULT False
)
'''))

class Item(BaseModel):
    id: int
    title: str
    description: str = None
    completed: bool = False

app = FastAPI(docs_url="/docs")

def __save(title, description, completed, cursor):
    cursor.execute("INSERT INTO Items (title, description, completed) VALUES (?, ?, ?)", (title, description, completed))
    return cursor.lastrowid

@app.post("/items", response_model=Item)
def post_item(body: Item):
    if body.completed is None:
        body.completed = False
    return Item(
        id=__with_cursor(lambda cur: __save(body.title, body.description, body.completed, cur)),
        title=body.title,
        description=body.description,
        completed=body.completed
    )

def __get_item(item_id, cursor):
    cursor.execute("SELECT id, title, description, completed FROM Items WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    return result

def __get_items(cursor):
    cursor.execute("SELECT id, title, description, completed FROM Items")
    result = cursor.fetchall()
    return result

@app.get('/items')
def get_items():
    items = []
    for item in __with_cursor(lambda cur: __get_items(cur)):
        items.append(Item(id=item[0], title=item[1], description=item[2], completed=item[3]))
    return items

@app.get('/items/{item_id}', response_model=Item)
def get_item(item_id: int):
    item = __with_cursor(lambda cur: __get_item(item_id, cur))
    if item is None:
        return status.HTTP_404_NOT_FOUND
    return Item(id=item[0], title=item[1], description=item[2], completed=item[3])

def __update_item(item_id, title, description, completed, cursor):
    cursor.execute("UPDATE Items SET title = ?, description = ?, completed = ? WHERE id = ?", (title, description, completed, item_id))
    return True

@app.put('/items/{item_id}', response_model=Item)
def put_item(item_id: int, body: Item):
    __with_cursor(lambda cur: __update_item(item_id, body.title, body.description, body.completed, cur))
    return body

def __delete_item(item_id, cursor):
    cursor.execute("DELETE FROM Items WHERE id = ?", (item_id,))
    return True

@app.delete('/items/{item_id}')
def delete_item(item_id: int) -> bool:
    deleted = __with_cursor(lambda cur: __delete_item(item_id, cur))
    return deleted