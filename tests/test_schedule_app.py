from typing import Callable

import pytest
import sqlalchemy as sa
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from schedule_app import db, main

engine = sa.create_engine("sqlite://", echo=True)
db.create_table(engine)


def get_test_engine() -> sa.engine.Connectable:
    return engine


main.app.dependency_overrides[main.get_engine] = get_test_engine

client = TestClient(main.app)


@pytest.fixture
def setup_db():
    db.delete_all(engine)
    yield


def test_empty_schedule(setup_db: Callable[[], None]) -> None:
    """何も追加していない場合は予定が表示されていない"""
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert len(soup.find_all(class_="schedule-item")) == 0


def test_post_schedule(setup_db: Callable[[], None]) -> None:
    """追加した予定が表示される"""
    title = "test test"
    response = client.post(
        "/add",
        data={
            "title": title,
            "body": "",
            "begin_at": "2021-04-30T13:00",
            "end_at": "2021-04-30T14:00",
        },
    )
    assert response.status_code == 201
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    schedule_all = soup.find_all(class_="schedule-title")
    assert len(schedule_all) == 1
    assert schedule_all[0].get_text() == title


def test_post_schedule_title_of_zero_length(setup_db: Callable[[], None]) -> None:
    """空のタイトルでは追加できない"""
    title = ""
    response = client.post(
        "/add",
        data={
            "title": title,
            "body": "",
            "begin_at": "2021-04-30T13:00",
            "end_at": "2021-04-30T14:00",
        },
    )
    assert response.status_code == 400
    soup = BeautifulSoup(response.content, "html.parser")
    assert soup.find(id="error").get_text() == "必須データが足りません"
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert len(soup.find_all(class_="schedule-item")) == 0


def test_post_too_long_schedule_title(setup_db: Callable[[], None]) -> None:
    """長すぎるタイトルでは追加できない"""
    title = "1234567890123456789012345678901"
    response = client.post(
        "/add",
        data={
            "title": title,
            "body": "",
            "begin_at": "2021-04-30T13:00",
            "end_at": "2021-04-30T14:00",
        },
    )
    assert response.status_code == 400
    soup = BeautifulSoup(response.content, "html.parser")
    assert soup.find(id="error").get_text() == "タイトルは30文字までです"
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert len(soup.find_all(class_="schedule-item")) == 0


def test_post_end_to_begin(setup_db: Callable[[], None]) -> None:
    """開始日時より終了日時が早かったら追加できない"""
    title = "test"
    response = client.post(
        "/add",
        data={
            "title": title,
            "body": "",
            "begin_at": "2021-04-30T14:00",
            "end_at": "2021-04-30T13:00",
        },
    )
    assert response.status_code == 400
    soup = BeautifulSoup(response.content, "html.parser")
    assert soup.find(id="error").get_text() == "終了日時を開始日時より前にすることはできません"
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert len(soup.find_all(class_="schedule-item")) == 0
