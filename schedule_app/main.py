from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()


templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root_page(request: Request):
    """一覧を表示する"""
    return {"message": "TODO"}


@app.get("/add")
async def read_post_page(request: Request):
    """新規アイテム追加ページの表示"""
    return {"message": "TODO"}


@app.post("/add")
async def post_new_item(request: Request):
    """新規アイテムの追加"""
    return {"message": "TODO"}


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})