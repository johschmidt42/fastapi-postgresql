import asyncio

import reflex as rx


class ClipboardButtonState(rx.ComponentState):
    copied: bool = False

    @rx.event
    async def copy_to_clipboard(self, text: str):
        self.copied = True
        yield rx.set_clipboard(text)
        # yield rx.toast.info("Copied to clipboard!")
        await asyncio.sleep(0.75)
        self.copied = False

    @classmethod
    def get_component(cls, text: str, **kwargs):
        return rx.button(
            rx.box(
                rx.icon(
                    "copy",
                    opacity=rx.cond(~cls.copied, 1, 0),
                    transition="opacity 0.3s ease",
                    position="absolute",
                    top="50%",
                    left="50%",
                    transform="translate(-50%, -50%)",
                ),
                rx.icon(
                    "check",
                    opacity=rx.cond(cls.copied, 1, 0),
                    transition="opacity 0.3s ease",
                    position="absolute",
                    top="50%",
                    left="50%",
                    transform="translate(-50%, -50%)",
                    color="green",
                ),
                position="relative",
                width="24px",
                height="24px",
            ),
            on_click=cls.copy_to_clipboard(text),
            # style=clipboard_button_style
            **kwargs,
        )


clipboard_button = ClipboardButtonState.create
