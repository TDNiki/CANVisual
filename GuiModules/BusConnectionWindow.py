import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow


class BusConnectionWindow(BaseWindow):

    tag = "bus"
    title = "Bus Connection"

    @classmethod
    def setup(cls):

        with dpg.window(
            tag=cls.tag,
            label=cls.title,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            no_close=True
        ):

            dpg.add_text("Devices")

            dpg.add_combo(
                [],
                tag="device_combo"
            )

            dpg.add_same_line()

            dpg.add_combo(
                ["125", "250", "500", "1000"],
                default_value="500",
                tag="bitrate_combo"
            )

            dpg.add_same_line()

            dpg.add_button(
                label="Connect"
            )

    @classmethod
    def update(cls):
        pass