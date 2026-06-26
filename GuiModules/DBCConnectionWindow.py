import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow
from GuiModules.BusConnectionWindow import BusConnectionWindow

def end_point():return

class DBCLogic:


    def __init__(self, status_dbc):
        self.status_dbc = status_dbc
        pass

    def update(self): return

    def on_file_load(self, sender_event, data):
        """Callbacck for file_dialog result"""

        BusConnectionWindow.logic.set_dbc(data['file_path_name'])
        dpg.configure_item(self.status_dbc, default_value = f"Подключенный dbc: {data['file_name'].split('.')[0]}")
        


class DBCConnectionWindow(BaseWindow):

    tag = "dbc"
    title = "Окно подключения dbc"
    size = (0.5, 0.1)
    position = (0.5, 0)
    logic = None

    __dbc_connected_tag = "dbc_connected_status"

    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = DBCLogic(cls.__dbc_connected_tag)
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
                dpg.add_table_column(init_width_or_weight=0.4)
                dpg.add_table_column(init_width_or_weight=0.6)

                with dpg.table_row():

                    dpg.add_button(
                            label="Найти DBC",
                            callback=lambda: dpg.show_item(f"{cls.tag}_file_dialog"),
                            
                    )

                    dpg.add_text(default_value = "Подключенный dbc: отстутсвует", tag = cls.__dbc_connected_tag)
            

            with dpg.file_dialog(
                directory_selector=False,
                show=False,
                tag=f"{cls.tag}_file_dialog",
                callback=cls.logic.on_file_load,
                file_count=1,
                width=700,
                height=400
            ):
                dpg.add_file_extension(".dbc", color=[150, 200, 255, 255])

    @classmethod
    def update(cls):
        pass

