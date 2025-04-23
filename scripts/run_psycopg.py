import asyncio
from typing import Optional

from psycopg import AsyncConnection
from psycopg.conninfo import make_conninfo

from app_psycopg.db.db import Database
from app_psycopg.db.db_models import OrderInput, User, UserInput, Order, UserUpdate


async def main(conn_info: str) -> None:
    async with await AsyncConnection.connect(
        conninfo=conn_info, autocommit=True
    ) as conn:
        db: Database = Database(connection=conn)

        user_input_1: UserInput = UserInput(name="Dan")
        user_input_2: UserInput = UserInput(name="Ann")
        user_input_3: UserInput = UserInput(name="John")

        # insert
        user_id_1: str = await db.insert_user(user_input_1)
        user_id_2: str = await db.insert_user(user_input_2)
        user_id_3: str = await db.insert_user(user_input_3)

        # get
        user_1: Optional[User] = await db.get_user(user_id_1)
        user_2: Optional[User] = await db.get_user(user_id_2)
        user_3: Optional[User] = await db.get_user(user_id_3)
        user_4: Optional[User] = await db.get_user("123")  # None

        # update
        await db.update_user(id=user_id_1, update=UserUpdate(name="NewDan"))

        # delete
        await db.delete_user(id=user_id_3)

        print(user_1.model_dump())
        print(user_2.model_dump())
        print(user_3.model_dump())
        print(user_4)

        # order
        order_input: OrderInput = OrderInput(
            amount=10, payer_id=user_1.id, payee_id=user_2.id
        )
        order_id: str = await db.insert_order(order_input)

        order: Order = await db.get_order(order_id)

        print(order.model_dump())


if __name__ == "__main__":
    conn_info: str = make_conninfo(
        host="localhost", port=5432, dbname="postgres", password="admin", user="admin"
    )

    asyncio.run(main(conn_info=conn_info))
