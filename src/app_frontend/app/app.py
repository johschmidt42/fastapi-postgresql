import reflex as rx

from app.data_component import DataState, get_components


def index():
    return rx.vstack(
        get_components(name="Fetch Users", url="http://localhost:9000/users"),
        # custom_button(name='Fetch Documents', url='http://localhost:9000/documents'),
        # custom_button(name='Fetch Professions', url='http://localhost:9000/professions'),
        width="100%",
    )


app = rx.App()
app.add_page(index, on_load=DataState.set_page(page=1))
