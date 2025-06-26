from typing import List, Dict, Any, Optional

import httpx
import reflex as rx
from starlette import status


class DataState(rx.State):
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
                    self.header = (
                        list(json_data["items"][0].keys()) if json_data else []
                    )
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
            url=f"http://localhost:9000/users?{DataState.get_offset_and_limit(self.current_page, limit=8)}"
        )  # TODO translate the page to limit offset


def render_header(item: str):
    return rx.table.column_header_cell(item)


def render_value(v: List):
    return rx.table.cell(v[1])


def render_row(row: rx.Var[Dict[str, str]]):
    return rx.table.row(
        rx.foreach(
            row,
            render_value,
        )
    )


def get_page_button(num: int):
    return rx.cond(
        DataState.current_page == num,
        rx.button(num, on_click=DataState.set_page(num), color_scheme="red"),
        rx.button(num, on_click=DataState.set_page(num), color_scheme="blue"),
    )


def get_first_page_button():
    return rx.cond(
        DataState.current_page != DataState.first_page,
        rx.button("«", on_click=DataState.set_page(DataState.first_page)),
        rx.button(
            "«", on_click=DataState.set_page(DataState.first_page), disabled=True
        ),
    )


def get_last_page_button():
    return rx.cond(
        DataState.current_page != DataState.last_page,
        rx.button("»", on_click=DataState.set_page(DataState.last_page)),
        rx.button("»", on_click=DataState.set_page(DataState.last_page), disabled=True),
    )


def get_previous_page_button():
    return rx.cond(
        DataState.current_page != DataState.first_page,
        rx.button("‹", on_click=DataState.set_page(DataState.current_page - 1)),
        rx.button(
            "‹", on_click=DataState.set_page(DataState.current_page - 1), disabled=True
        ),
    )


def get_next_page_button():
    return rx.cond(
        DataState.current_page != DataState.last_page,
        rx.button("›", on_click=DataState.set_page(DataState.current_page + 1)),
        rx.button(
            "›", on_click=DataState.set_page(DataState.current_page + 1), disabled=True
        ),
    )


def get_pagination_bar():
    return rx.hstack(
        rx.cond(DataState.pages, get_first_page_button()),
        rx.cond(DataState.pages, get_previous_page_button()),
        rx.foreach(DataState.pages, get_page_button),
        rx.cond(DataState.pages, get_next_page_button()),
        rx.cond(DataState.pages, get_last_page_button()),
    )


def get_components(name: str, url: str, expected_status_code: int = status.HTTP_200_OK):
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.foreach(
                    DataState.header,
                    render_header,
                )
            ),
            rx.table.body(
                rx.foreach(
                    DataState.data,
                    render_row,
                )
            ),
        ),
        rx.hstack(
            # rx.button(name, on_click=DataState.fetch_data(url=url, expected_status_code=expected_status_code)),
            # rx.button("Clear", on_click=DataState.clear_data),
        ),
        get_pagination_bar(),
        width="100%",
        align="center",
        # on_mount=self.fetch_data(url=url, expected_status_code=expected_status_code)
    )
