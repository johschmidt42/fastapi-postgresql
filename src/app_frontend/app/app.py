"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from typing import List, Dict, Any, Optional

import httpx
import reflex as rx


class State(rx.State):
    """The app state."""

    success: bool = False

    # Store the list of users
    users: List[Dict[str, Any]] = []

    # Flag to indicate if data is loading
    is_loading: bool = False

    # Error message if fetch fails
    error: Optional[str] = None

    @rx.event
    async def fetch_users(self):
        """Fetch users from the API."""
        self.is_loading = True
        self.error = None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:9000/users")
                if response.status_code == 200:
                    self.success: bool = True
                    self.users = response.json()["items"]
                else:
                    self.error = f"Error fetching users: {response.status_code}"
        except Exception as e:
            self.error = f"Error: {str(e)}"
        finally:
            self.is_loading = False


def index():
    return rx.vstack(
        rx.button("Toggle", on_click=State.fetch_users),
        rx.cond(
            State.success,
            rx.vstack(
                rx.heading("Users", size="6"),
                rx.data_table(
                    data=State.users,
                    columns=[
                        "id",
                        "name",
                        "created_at",
                        "last_updated_at",
                        {"id": "profession.name", "header": "Profession"},
                    ],
                    pagination=False,
                    search=True,
                    sort=True,
                ),
                width="100%",
                spacing="4",
            ),
            rx.text("Text 2", color="red"),
        ),
    )


app = rx.App()
app.add_page(index)
