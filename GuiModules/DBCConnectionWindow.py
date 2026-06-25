import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow

def end_point():return


class DBCConnectionWindow(BaseWindow):

    tag = "dbc"
    title = "Окно подключения dbc"
    size = (0.5, 0.1)
    position = (0.5, 0)

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
                dpg.add_table_column(init_width_or_weight=0.2)
                dpg.add_table_column(init_width_or_weight=0.2)
                dpg.add_table_column(init_width_or_weight=0.6)

                with dpg.table_row():

                    dpg.add_button(
                            label="Найти DBC",
                            callback=lambda: dpg.show_item(f"{cls.tag}_file_dialog"),
                            
                    )

                    dpg.add_text("История DBC:")
                    dpg.add_combo([], tag=f"{cls.tag}_history_combo", width=-1)
            

            with dpg.file_dialog(
                directory_selector=False,
                show=False,
                tag=f"{cls.tag}_file_dialog",
                callback=end_point,
                width=700,
                height=400
            ):
                dpg.add_file_extension("*.dbc")

    @classmethod
    def update(cls):
        pass

