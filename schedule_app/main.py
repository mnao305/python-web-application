from datetime import datetime

import sqlalchemy as sqla
from fastapi import FastAPI, Form, Request
from fastapi.param_functions import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from schedule_app import db
from schedule_app.config import Settings
from schedule_app.models import Schedule

app = FastAPI()


templates = Jinja2Templates(directory="templates")


settings = Settings()
db_engine = sqla.create_engine(settings.database_url, echo=True)
db.create_table(db_engine)


def string2Datetime(strDate: str):
    """ISO 8601形式の文字列をdatetimeに変換します"""
    return datetime.fromisoformat(strDate)


def get_engine() -> sqla.engine.Connectable:
    return db_engine


@app.get("/")
async def read_root_page(request: Request):
    """一覧を表示する"""
    return {"message": "TODO"}


@app.get("/add", response_class=HTMLResponse)
async def read_post_page(request: Request):
    """新規アイテム追加ページの表示"""
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add")
async def post_new_item(
    request: Request,
    engine: sqla.engine.Connectable = Depends(get_engine),
    title: str = Form(""),
    body: str = Form(""),
    begin_at: str = Form(None),
    end_at: str = Form(None),
):
    """新規アイテムの追加"""
    beginAt = string2Datetime(begin_at)
    endAt = string2Datetime(end_at)

    db.add_item(
        engine, Schedule(title=title, body=body, begin_at=beginAt, end_at=endAt)
    )
    return {
        "message": "TODO",
        "title": title,
        "body": body,
        "begin_at": begin_at,
        "end_at": end_at,
    }


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})
