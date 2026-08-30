import sqlite3
from typing import Any

from .api.schemas.shipment import ShipmentCreate, ShipmentUpdate


class Database:
    def connect_to_db(self):
        self.conn = sqlite3.connect(
            "sqlite.db", check_same_thread=False
        )  # make connection with database
        self.cur = self.conn.cursor()  # get cursor to execute and fetch data

    def create_table(self, name: str):
        # 1. create a table
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY, 
            content TEXT, 
            weight REAL, 
            status TEXT
            )
        """)

    def create(self, shipment: ShipmentCreate) -> int:
        # find a new id
        self.cur.execute("SELECT MAX(id) FROM shipments")
        result = self.cur.fetchone()

        new_id = (result[0] + 1) if result[0] is not None else 1

        # insert values in the table
        self.cur.execute(
            """
            INSERT INTO shipments
            VALUES (:id, :content, :weight, :status)
        """,
            {"id": new_id, **shipment.model_dump(), "status": "placed"},
        )

        # commit the chagnes to the database
        self.conn.commit()

        return new_id

    def get(self, id: int) -> dict[str, Any] | None:
        self.cur.execute(
            """
            SELECT * FROM shipments
            WHERE id = ?
        """,
            (id,),
        )
        row = self.cur.fetchone()

        if row is None:
            return None

        return {"id": row[0], "content": row[1], "weight": row[2], "status": row[3]}

    def update(self, id: int, shipment: ShipmentUpdate) -> dict[str, Any] | None:
        self.cur.execute(
            """
            UPDATE shipments SET status = :status
            WHERE id = :id
        """,
            {"id": id, **shipment.model_dump()},
        )

        self.conn.commit()

        return self.get(id)

    def delete(self, id: int):
        self.cur.execute(
            """
            DELETE FROM shipments
            WHERE id = ?
        """,
            (id,),
        )

        self.conn.commit()

    def close(self):
        self.conn.close()

    def __enter__(self):
        self.connect_to_db()
        self.create_table()
        return self

    def __exit__(self, *arg):
        self.close()


# usage
def managed_db():
    db = Database()
    # setup
    print("Enter setup")
    db.connect_to_db()
    db.create_table()

    yield db

    print("Exit the context")
    # dispose
    db.close()


with managed_db() as db:
    db.get(12701)
    db.get(12703)


# run this command python -m learning2.database then we can use database as context manager.
