import reflex as rx

from app.user_table import UserTableState, UserDataTable


def index():
    return rx.vstack(
        rx.heading("FASTAPI POSTGRESQL"),
        UserDataTable.get_components(),
        width="80vw",
        height="50vh",
        align="center",
        justify="center",
        id="page",
        margin_left="10vw",
        margin_right="10vw",
    )


app = rx.App()
app.add_page(index, on_load=UserTableState.set_page(page=1))
