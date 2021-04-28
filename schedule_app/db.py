from datetime import datetime

import sqlalchemy as sqla

metadata = sqla.MetaData()
schedules_table = sqla.Table(
    "schedules",
    metadata,
    sqla.Column("id", sqla.Integer, primary_key=True, autoincrement=True),
    sqla.Column("title", sqla.String(256), nullable=False),
    sqla.Column("body", sqla.Text, nullable=True),
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


def add_item(
    engine: sqla.engine.Connectable, title: str, body: str, begin_at: datetime, end_at: datetime
):
    """新規アイテムをテーブルにインサートするよ"""
    q = schedules_table.insert()
    engine.connect().execute(
        q, title=title, body=body, begin_at=begin_at, end_at=end_at
    )
