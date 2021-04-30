from datetime import datetime, timedelta

import sqlalchemy as sqla
from sqlalchemy import and_, or_

from schedule_app.models import Schedule

metadata = sqla.MetaData()
schedules_table = sqla.Table(
    "schedules",
    metadata,
    sqla.Column("id", sqla.Integer, primary_key=True, autoincrement=True),
    sqla.Column("title", sqla.String(256), nullable=False),
    sqla.Column("body", sqla.Text, nullable=False),
    sqla.Column("begin_at", sqla.DateTime, nullable=False),
    sqla.Column("end_at", sqla.DateTime, nullable=False),
    sqla.Column(
        "created_at",
        sqla.DateTime,
        nullable=False,
        server_default=sqla.sql.functions.current_timestamp(),
    ),
    sqla.Column(
        "updated_at",
        sqla.DateTime,
        nullable=False,
        server_default=sqla.sql.functions.current_timestamp(),
        onupdate=sqla.sql.functions.current_timestamp(),
    ),
)


def create_table(engine: sqla.engine.Connectable):
    metadata.create_all(engine)


def get_today_all_item(engine: sqla.engine.Connectable):
    """全ての今日の予定を取得する"""

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    # テーブル指定で全て取ってきたかったけど、createdAtとかラベルつけんといかんしこうなった
    # まぁやりようはある気がするけどとりあえずよし
    q = (
        sqla.sql.select(
            (
                schedules_table.c.id,
                schedules_table.c.title,
                schedules_table.c.body,
                schedules_table.c.begin_at,
                schedules_table.c.end_at,
                schedules_table.c.created_at.label("createdAt"),
                schedules_table.c.updated_at.label("updateAt"),
            )
        )
        .where(
            or_(
                and_(
                    schedules_table.c.begin_at > today,
                    schedules_table.c.begin_at < tomorrow,
                ),
                and_(
                    schedules_table.c.end_at > today,
                    schedules_table.c.end_at < tomorrow,
                ),
            )
        )
        .order_by(schedules_table.c.begin_at)
    )
    return [Schedule(**m) for m in engine.connect().execute(q)]


def get_item_from_id(engine: sqla.engine.Connectable, id: int):
    """idを元に予定を取得する"""
    q = sqla.sql.select(
        (
            schedules_table.c.id,
            schedules_table.c.title,
            schedules_table.c.body,
            schedules_table.c.begin_at,
            schedules_table.c.end_at,
            schedules_table.c.created_at.label("createdAt"),
            schedules_table.c.updated_at.label("updateAt"),
        )
    ).where(schedules_table.c.id == id)
    return [Schedule(**m) for m in engine.connect().execute(q)][0]


def add_item(engine: sqla.engine.Connectable, schedule: Schedule):
    """新規アイテムをテーブルにインサートするよ"""
    q = schedules_table.insert()
    engine.connect().execute(q, schedule.dict())


def delete_all(engine: sqla.engine.Connectable) -> None:
    """予定をすべて消す（テスト用）"""
    with engine.connect() as connection:
        connection.execute(schedules_table.delete())
