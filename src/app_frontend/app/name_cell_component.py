import reflex as rx


class EditableComponent(rx.ComponentState):
    text: str

    def start_editing(self):
        self.editing = True

    @rx.event
    async def stop_editing(self):
        self.editing = False

        print(f"Changing id {self.id} to {self.text}")

        # user_table_state = await self.get_state(UserTableState)
        #
        # yield type(user_table_state).patch_data({"name": self.text})

    def set_text(self, value: str):
        self.text = value

    editing: bool = False

    @classmethod
    def get_component(cls, *, id: str, value: str, **props) -> rx.Component:
        cls.id = id
        cls.text = value

        return rx.input(
            value=cls.text,
            on_blur=cls.stop_editing,
            on_change=cls.set_text,
            auto_focus=True,
            required=True,
            on_click=cls.start_editing,
        )

        # return rx.cond(
        #     cls.editing,
        #     rx.input(
        #         value=cls.text,
        #         on_blur=cls.stop_editing,
        #         on_change=cls.set_text,
        #         auto_focus=True,
        #         required=True,
        #         on_click=cls.start_editing
        #     ),
        #     rx.hstack(
        #         rx.text(cls.text),
        #         rx.icon_button(
        #             rx.icon("pencil"),
        #             on_click=cls.start_editing,
        #             background_color="transparent",
        #             color="blue"
        #         ),
        #         spacing="1",
        #     ),
        # )


editable_text = EditableComponent.create
