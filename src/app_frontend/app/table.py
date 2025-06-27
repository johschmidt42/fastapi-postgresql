from typing import List, Dict, Any, Optional

import httpx
import reflex as rx
from starlette import status

from app.chevron_up import chevron_up
from app.row import row_table


class TableState(rx.ComponentState):
    URL: str = ""

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

    @classmethod
    def get_component(cls, *, url: str, **props) -> rx.Component:
        cls.__fields__["URL"].default = url

        def get_table():
            return rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.foreach(
                            cls.header,
                            render_header,
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            cls.data,
                            render_row,
                        )
                    ),
                ),
                overflow_y="auto",
            )

        def get_pagination_bar():
            return rx.hstack(
                rx.cond(cls.pages, get_first_page_button()),
                rx.cond(cls.pages, get_previous_page_button()),
                rx.foreach(cls.pages, get_page_button),
                rx.cond(cls.pages, get_next_page_button()),
                rx.cond(cls.pages, get_last_page_button()),
                get_row_per_page_drop_down(),
            )

        def get_row_per_page_drop_down():
            return rx.menu.root(
                rx.menu.trigger(
                    rx.button(
                        "Rows per page: ",
                        rx.text(
                            cls.limit,
                            font_weight="bold",
                            color="#163FAA",
                            align="center",
                        ),
                        variant="soft",
                    ),
                ),
                rx.menu.content(
                    rx.menu.item("10", on_click=cls.set_rows_per_page(10)),
                    rx.menu.item("20", on_click=cls.set_rows_per_page(20)),
                    rx.menu.item("30", on_click=cls.set_rows_per_page(30)),
                    rx.menu.item("40", on_click=cls.set_rows_per_page(40)),
                    rx.menu.item("50", on_click=cls.set_rows_per_page(50)),
                ),
            )

        def chevron_down(item):
            return rx.icon_button(
                rx.icon(
                    "chevron-down",
                    color="blue",
                    style={"cursor": "pointer", "margin": "0em", "padding": "0em"},
                    id=f"chevron_down_icon_{item}",
                ),
                # on_click="TODO",
                style={"margin": "0em", "padding": "0em"},
                background_color="transparent",
                disabled=True,
                id=f"chevron_down_{item}",
            )

        def render_header(item: str):
            return rx.table.column_header_cell(
                rx.hstack(
                    item,
                    chevron_up(),
                    # chevron_down(item),
                    justify="start",
                    align="center",
                    spacing="0",
                    id="header_cell_hstack",
                )
            )

        def render_row(row: rx.Var[Dict[str, str]]):
            return row_table(row=row)

        def get_page_button(num: int):
            return rx.cond(
                cls.current_page == num,
                rx.button(num, on_click=cls.set_page(num), color_scheme="red"),
                rx.button(num, on_click=cls.set_page(num), color_scheme="blue"),
            )

        def get_first_page_button():
            return rx.cond(
                cls.current_page != cls.first_page,
                rx.button("«", on_click=cls.set_page(cls.first_page)),
                rx.button(
                    "«",
                    on_click=cls.set_page(cls.first_page),
                    disabled=True,
                ),
            )

        def get_last_page_button():
            return rx.cond(
                cls.current_page != cls.last_page,
                rx.button("»", on_click=cls.set_page(cls.last_page)),
                rx.button(
                    "»",
                    on_click=cls.set_page(cls.last_page),
                    disabled=True,
                ),
            )

        def get_previous_page_button():
            return rx.cond(
                cls.current_page != cls.first_page,
                rx.button("‹", on_click=cls.set_page(cls.current_page - 1)),
                rx.button(
                    "‹",
                    on_click=cls.set_page(cls.current_page - 1),
                    disabled=True,
                ),
            )

        def get_next_page_button():
            return rx.cond(
                cls.current_page != cls.last_page,
                rx.button("›", on_click=cls.set_page(cls.current_page + 1)),
                rx.button(
                    "›",
                    on_click=cls.set_page(cls.current_page + 1),
                    disabled=True,
                ),
            )

        return rx.vstack(
            get_table(),
            rx.divider(color_scheme="tomato", style={"borderBottomWidth": "4px"}),
            get_pagination_bar(),
            align="center",
            justify="center",
            id="table",
            width="100%",
            height="80%",
        )


custom_table = TableState.create
