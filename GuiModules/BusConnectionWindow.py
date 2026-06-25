import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow
from CanInterface import CANManager

class BusLogic:

    def __init__(self):
        self.can = CANManager()
        pass


class BusConnectionWindow(BaseWindow):

    tag = "bus"
    title = "Окно подключения интерфейса"
    size = (0.5, 0.1)
    position = (0, 0)
    logic = BusLogic()

    @classmethod
    def setup(cls):
        with dpg.window(
            tag=cls.tag,
            label=cls.title,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            no_close=True,
        ):

            with dpg.table(
                header_row=False,
                borders_innerV=False,
                borders_innerH=False,
                resizable=False
            ):
                dpg.add_table_column(init_width_or_weight=0.1)
                dpg.add_table_column(init_width_or_weight=0.1)
                dpg.add_table_column(init_width_or_weight=0.3)
                dpg.add_table_column(init_width_or_weight=0.2)
                dpg.add_table_column(init_width_or_weight=0.3)
                
                with dpg.table_row():
                    
                    dpg.add_button(label="Найти", width=-1)
                    dpg.add_loading_indicator(tag = f"{cls.tag}_loading", show = False, height=-1, radius=1)

                    dpg.add_combo(cls.logic.can.get_configs(), tag="device_combo", width=-1)

                    dpg.add_combo(
                        ["250", "500"],
                        default_value="500",
                        tag="bitrate_combo",
                        width=-1
                    )

                    dpg.add_button(
                        label="Подключить",
                        width=-1
                    )

    @classmethod
    def update(cls):
        pass