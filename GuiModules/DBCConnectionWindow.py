import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow
from GuiModules.BusConnectionWindow import BusConnectionWindow

from settings import FILE_EXT_COLOR


class DBCLogic:


    def __init__(self, status_dbc, window_tag):
        self.status_dbc = status_dbc
        self.window_tag = window_tag
        self.dbc_path = None
        self.dbc_name = None


    def update(self): return

    def on_file_load(self, sender_event, data):
        """Callbacck for file_dialog result"""

        BusConnectionWindow.logic.set_dbc(data['file_path_name'])
        dpg.configure_item(self.status_dbc, default_value = f"Подключенный dbc: {data['file_name'].split('.')[0]}")
        self.dbc_path = data['file_path_name']
        self.dbc_name = data['file_name']
    
    def save_info(self):

        if not self.dbc_path: return

        return self.window_tag, {
            "file_path_name": self.dbc_path,
            "file_name": self.dbc_name
        }
    
    def load_info(self, data):
        self.on_file_load("", data)


class DBCConnectionWindow(BaseWindow):

    tag = "dbc"
    title = "Окно подключения dbc"
    logic = None

    __dbc_connected_tag = "dbc_connected_status"

    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = DBCLogic(cls.__dbc_connected_tag, cls.tag)
        with dpg.child_window(
            tag=cls.tag,
            label=cls.title,
            height=kwargs['height'],
            width=kwargs['width']
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
                dpg.add_file_extension(".dbc", color=FILE_EXT_COLOR)


