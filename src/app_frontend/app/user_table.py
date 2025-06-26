from typing import List, Dict, Any, Optional

import httpx
import reflex as rx
from starlette import status


class UserTableState(rx.State):
    URL: str = "http://localhost:9000/users"

    success: bool = False

    # Store data
    data: List[Dict[str, str]] = []
    pagination_data: Dict[str, Any] = {}
    header: List[str] = []

    # Flag to indicate if data is loading
    is_loading: bool = False

    # Error message if fetch fails
    error: Optional[str] = None

    # pagination
    pages: List[int] = []
    current_page: Optional[int] = None
    first_page: Optional[int] = None
    last_page: Optional[int] = None
    limit: int = 10

    @staticmethod
    def get_total_pages(total_count: int, limit: int):
        return (total_count + limit - 1) // limit

    @staticmethod
    def get_offset_and_limit(page: int, limit: int) -> str:
        offset = (page - 1) * limit
        return f"limit={limit}&offset={offset}"

    @rx.event
    async def fetch_data(
        self, url: str, expected_status_code: int = status.HTTP_200_OK
    ):
        """Fetch data from the backend API."""
        self.is_loading: bool = True
        self.error: Optional[str] = None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url)
                if response.status_code == expected_status_code:
                    self.success: bool = True
                    json_data: dict = response.json()
                    flat_data = [
                        {k: str(v) for k, v in item.items()}
                        for item in json_data["items"]
                    ]
                    self.pagination_data = {
                        k: v for k, v in json_data.items() if k != "items"
                    }
                    total_num_pages = self.get_total_pages(
                        total_count=self.pagination_data["total_count"],
                        limit=self.pagination_data["limit"],
                    )
                    self.pages = list(range(1, total_num_pages + 1))
                    self.first_page = self.pages[0] if self.pages else None
                    self.last_page = self.pages[-1] if self.pages else None
                    self.data = flat_data if flat_data else []
                    header = list(json_data["items"][0].keys()) if json_data else []

                    self.header = header
                else:
                    self.error: str = f"Error fetching data: {response.status_code}"
        except Exception as e:
            self.error: str = f"Error: {str(e)}"
        finally:
            self.is_loading = False

    @rx.event
    async def clear_data(self) -> None:
        self.error: Optional[str] = None
        self.data: List[Dict[str, str]] = []
        self.header: List[str] = []
        self.pagination_data: Dict[str, Any] = {}
        self.pages: List[int] = []
        self.first_page: Optional[int] = None
        self.last_page: Optional[int] = None
        self.current_page: Optional[int] = None

    @rx.event
    async def set_page(self, page: int):
        print("Setting page", page)
        self.current_page: int = page

        yield type(self).fetch_data(
            url=f"{self.URL}?{self.get_offset_and_limit(self.current_page, limit=self.limit)}"
        )

    @rx.event
    async def set_rows_per_page(self, num_rows: int):
        print("Setting rows per page", num_rows)
        self.limit = num_rows

        self.current_page: int = 1

        yield type(self).fetch_data(
            url=f"{self.URL}?{self.get_offset_and_limit(self.current_page, limit=self.limit)}"
        )


class UserDataTable:
    @staticmethod
    def get_row_per_page_drop_down():
        return rx.menu.root(
            rx.menu.trigger(
                rx.button(
                    "Rows per page: ",
                    rx.text(
                        UserTableState.limit,
                        font_weight="bold",
                        color="#163FAA",
                        align="center",
                    ),
                    variant="soft",
                ),
            ),
            rx.menu.content(
                rx.menu.item("10", on_click=UserTableState.set_rows_per_page(10)),
                rx.menu.item("20", on_click=UserTableState.set_rows_per_page(20)),
                rx.menu.item("30", on_click=UserTableState.set_rows_per_page(30)),
                rx.menu.item("40", on_click=UserTableState.set_rows_per_page(40)),
                rx.menu.item("50", on_click=UserTableState.set_rows_per_page(50)),
            ),
        )

    @staticmethod
    def render_header(item: str):
        return rx.table.column_header_cell(item)

    @staticmethod
    def render_value(v: List):
        return rx.match(
            v[0],
            (
                "id",
                rx.table.cell(
                    rx.text(
                        v[1],
                        font_weight="bold",
                        border_radius="8px",
                        background_color="#ECEAFD",
                        color="#163FAA",
                        align="center",
                    )
                ),
            ),
            rx.table.cell(
                rx.flex(
                    rx.text(v[1], justify="center", align="center"),
                    justify="start",
                    align="center",
                )
            ),
        )

    @staticmethod
    def render_row(row: rx.Var[Dict[str, str]]):
        return rx.table.row(
            rx.foreach(
                row,
                UserDataTable.render_value,
            )
        )

    @staticmethod
    def get_page_button(num: int):
        return rx.cond(
            UserTableState.current_page == num,
            rx.button(num, on_click=UserTableState.set_page(num), color_scheme="red"),
            rx.button(num, on_click=UserTableState.set_page(num), color_scheme="blue"),
        )

    @staticmethod
    def get_first_page_button():
        return rx.cond(
            UserTableState.current_page != UserTableState.first_page,
            rx.button("«", on_click=UserTableState.set_page(UserTableState.first_page)),
            rx.button(
                "«",
                on_click=UserTableState.set_page(UserTableState.first_page),
                disabled=True,
            ),
        )

    @staticmethod
    def get_last_page_button():
        return rx.cond(
            UserTableState.current_page != UserTableState.last_page,
            rx.button("»", on_click=UserTableState.set_page(UserTableState.last_page)),
            rx.button(
                "»",
                on_click=UserTableState.set_page(UserTableState.last_page),
                disabled=True,
            ),
        )

    @staticmethod
    def get_previous_page_button():
        return rx.cond(
            UserTableState.current_page != UserTableState.first_page,
            rx.button(
                "‹", on_click=UserTableState.set_page(UserTableState.current_page - 1)
            ),
            rx.button(
                "‹",
                on_click=UserTableState.set_page(UserTableState.current_page - 1),
                disabled=True,
            ),
        )

    @staticmethod
    def get_next_page_button():
        return rx.cond(
            UserTableState.current_page != UserTableState.last_page,
            rx.button(
                "›", on_click=UserTableState.set_page(UserTableState.current_page + 1)
            ),
            rx.button(
                "›",
                on_click=UserTableState.set_page(UserTableState.current_page + 1),
                disabled=True,
            ),
        )

    @staticmethod
    def get_pagination_bar():
        return rx.hstack(
            rx.cond(UserTableState.pages, UserDataTable.get_first_page_button()),
            rx.cond(UserTableState.pages, UserDataTable.get_previous_page_button()),
            rx.foreach(UserTableState.pages, UserDataTable.get_page_button),
            rx.cond(UserTableState.pages, UserDataTable.get_next_page_button()),
            rx.cond(UserTableState.pages, UserDataTable.get_last_page_button()),
            UserDataTable.get_row_per_page_drop_down(),
        )

    @staticmethod
    def get_table():
        return rx.box(
            rx.table.root(
                rx.table.header(
                    rx.foreach(
                        UserTableState.header,
                        UserDataTable.render_header,
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        UserTableState.data,
                        UserDataTable.render_row,
                    )
                ),
            ),
            overflow_y="auto",
        )

    @staticmethod
    def get_components():
        return rx.vstack(
            UserDataTable.get_table(),
            rx.divider(color_scheme="tomato", style={"borderBottomWidth": "4px"}),
            UserDataTable.get_pagination_bar(),
            align="center",
            justify="center",
            id="table",
            width="100%",
            height="80%",
        )
