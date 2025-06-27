import reflex as rx


class ChevronUp(rx.ComponentState):
    opacity: float = 0.2  # Default to inactive

    @rx.event
    def toggle_opacity(self):
        # Toggle between 0.2 and 1.0
        self.opacity = 1.0 if self.opacity == 0.2 else 0.2

    @classmethod
    def get_component(cls, **props):
        return rx.icon_button(
            rx.icon(
                "chevron-up",
                color="blue",
                opacity=cls.opacity,
                style={"cursor": "pointer"},
                id="chevron_up_icon",
            ),
            on_click=cls.toggle_opacity,
            style={"margin": "0em", "padding": "0em"},
            background_color="transparent",
            disabled=False,
            id="chevron_up",
            **props,
        )


chevron_up = ChevronUp.create
