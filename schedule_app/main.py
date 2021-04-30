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
    # 今日の予定をとる
    # きっとsqlでwhereとか使ってやるのがいいんだろうなぁの気持ち
    now = datetime.now()
    s = [
        schedule for schedule in schedules if schedule.begin_at < now < schedule.end_at
    ]
    return templates.TemplateResponse("list.html", {"request": request, "schedules": s})


@app.get("/add", response_class=HTMLResponse)
async def read_post_page(request: Request):
    """新規アイテム追加ページの表示"""
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add", response_class=HTMLResponse)
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
        return templates.TemplateResponse(
            "add.html",
            {"request": request, "error": "必須データが足りません"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if len(title) > 30:
        return templates.TemplateResponse(
            "add.html",
            {"request": request, "error": "タイトルは30文字までです"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    beginAt = string2Datetime(begin_at)
    endAt = string2Datetime(end_at)

    if beginAt > endAt:
        # 開始日時より終了日時が早かったらエラーを返す
        return templates.TemplateResponse(
            "add.html",
            {"request": request, "error": "終了日時を開始日時より前にすることはできません"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    db.add_item(
        engine, Schedule(title=title, body=body, begin_at=beginAt, end_at=endAt)
    )
    return templates.TemplateResponse(
        "add.html",
        {"request": request, "success": "予定を追加しました"},
        status_code=status.HTTP_201_CREATED,
    )


@app.get("/schedule/{id}", response_class=HTMLResponse)
async def read_item(
    request: Request,
    engine: sqla.engine.Connectable = Depends(get_engine),
    id: str = "0",
):
    schedule = db.get_item_from_id(engine, int(id))
    return templates.TemplateResponse(
        "schedule.html", {"request": request, "schedule": schedule}
    )
