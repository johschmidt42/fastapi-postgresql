import reflex as rx

from app.table import custom_table

user_table = custom_table(url="http://localhost:9000/users")
profession_table = custom_table(url="http://localhost:9000/professions")
company_table = custom_table(url="http://localhost:9000/companies")

TAB_TABLE_MAPPING = {
    "users": user_table,
    "professions": profession_table,
    "companies": company_table,
}


class TabsState(rx.State):
    @rx.event
    async def handle_tab_change(self, value: str):
        table = TAB_TABLE_MAPPING[value]

        yield table.State.set_page(page=1)


def tabbed_tables():
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Users", value="users"),
            rx.tabs.trigger("Professions", value="professions"),
            rx.tabs.trigger("Companies", value="companies"),
        ),
        rx.tabs.content(
            user_table,
            value="users",
        ),
        rx.tabs.content(
            profession_table,
            value="professions",
        ),
        rx.tabs.content(
            company_table,
            value="companies",
        ),
        default_value="users",
        on_change=TabsState.handle_tab_change,
    )


def index():
    return rx.vstack(
        rx.heading("FASTAPI POSTGRESQL"),
        tabbed_tables(),
        align="center",
        justify="center",
        id="page",
    )


app = rx.App()
app.add_page(index, on_load=TabsState.handle_tab_change("users"))
