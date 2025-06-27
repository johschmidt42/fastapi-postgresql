from typing import Dict, List

import reflex as rx


class RowTableState(rx.ComponentState):
    row_data = {}
    form_data = {}

    dialog_open: bool = False

    @rx.event
    def open_dialog(self):
        self.dialog_open = True

    @rx.event
    def submit_form(self, form_data):
        self.form_data = form_data
        self.dialog_open = False
        # Add any additional logic here

    @classmethod
    def get_component(cls, *, row: rx.Var[Dict[str, str]], **props):
        cls.row_data = row

        def edit_button():
            return rx.icon_button(
                rx.icon(
                    "pencil",
                    color="blue",
                    style={
                        "opacity": 0,
                        "transition": "opacity 0.2s",
                        "cursor": "pointer",
                    },
                    _hover={"opacity": 1},
                ),
                on_click=cls.open_dialog,
                background_color="transparent",
                _hover={"& svg": {"opacity": 1, "cursor": "pointer"}},
                # Ensure the button itself triggers hover on the icon
            )

        def id_cell(value):
            return rx.table.cell(
                rx.hstack(
                    rx.dialog.root(
                        rx.dialog.trigger(
                            edit_button(),
                        ),
                        rx.dialog.content(
                            rx.dialog.title("Enter Details"),
                            rx.dialog.description("Fill in the form fields below."),
                            # rx.form.root(
                            #     rx.form.field(
                            #         rx.form.label("ID"),
                            #         rx.form.control(rx.input(name="id")),
                            #         name="id"
                            #     ),
                            #     rx.form.field(
                            #         rx.form.label("Name"),
                            #         rx.form.control(rx.input(name="name")),
                            #         name="name"
                            #     ),
                            #     rx.form.field(
                            #         rx.form.label("Created At"),
                            #         rx.form.control(rx.input(name="created_at")),
                            #         name="created_at"
                            #     ),
                            #     rx.form.submit(
                            #         rx.button("Submit"),
                            #         as_child=True,
                            #     ),
                            #     on_submit=cls.submit_form,
                            # ),
                            rx.dialog.close(rx.button("Cancel")),
                        ),
                    ),
                    rx.text(
                        value,
                        font_weight="bold",
                        border_radius="8px",
                        background_color="#ECEAFD",
                        color="#163FAA",
                        align="center",
                    ),
                ),
                id="table_cell_id",
            )

        def name_cell(value: str):
            return rx.table.cell(rx.text(value))

        def default_cell(value):
            return rx.table.cell(
                rx.text(value, justify="center", align="center"),
                id="table_cell_default",
            )

        def profession_cell(value):
            return rx.code_block(
                code=value,
                language="json",
                wrap_long_lines=True,
            )

        def created_at_cell(value):
            return rx.table.cell(rx.moment(value, from_now=True))

        def render_value(v: List):
            key = v[0]
            value = v[1]
            return default_cell(value)

            # return rx.match(
            #     key,
            #     (
            #         "id",
            #         id_cell(value),
            #     ),
            #     (
            #         "name",
            #         name_cell(value),
            #     ),
            #     (
            #         "profession",
            #         profession_cell(value),
            #     ),
            #     (
            #         "created_at",
            #         created_at_cell(value)
            #     ),
            #     default_cell(value),
            # )

        return rx.table.row(
            rx.foreach(
                cls.row_data,
                render_value,
            ),
            # edit_button()
        )


row_table = RowTableState.create
