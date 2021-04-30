from datetime import datetime

import sqlalchemy as sqla
from fastapi import FastAPI, Form, Request, status
from fastapi.param_functions import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

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


@app.get("/", response_class=HTMLResponse)
async def read_root_page(
    request: Request,
    engine: sqla.engine.Connectable = Depends(get_engine),
):
    """一覧を表示する"""
    schedules = db.get_all_item(engine)
    return templates.TemplateResponse(
        "list.html", {"request": request, "schedules": schedules}
    )


@app.get("/add", response_class=HTMLResponse)
async def read_post_page(request: Request):
    """新規アイテム追加ページの表示"""
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add")
async def post_new_item(
    request: Request,
    response: Response,
    engine: sqla.engine.Connectable = Depends(get_engine),
    title: str = Form(""),
    body: str = Form(""),
    begin_at: str = Form(None),
    end_at: str = Form(None),
):
    """新規アイテムの追加"""
    if not title or not begin_at or not end_at:
        # 必須データが足りなかったらエラーを返す
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "error"}

    beginAt = string2Datetime(begin_at)
    endAt = string2Datetime(end_at)

    if beginAt > endAt:
        # 開始日時より終了日時が早かったらエラーを返す
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "error"}

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
