import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow
from CanInterface import CANManager

class BusLogic:

    dbc_path = None

    def __init__(self, data, con_button_tag, discon_buttun_tag):
        self.can = CANManager(data)
        self.con_button_tag = con_button_tag
        self.discon_button_tag = discon_buttun_tag

    def update_available_interfaces(self, combo_tag: str):
        self.can.scan_available_configs()
        dpg.configure_item(combo_tag, items=self.get_available_interfaces())

    def get_available_interfaces(self) -> tuple[str]:
        interfaces = list()
        for config in self.can.get_configs():
            interfaces.append(f"{config['interface']} : {config['channel']}")
        return interfaces
    
    def on_connect_click(self, combo_interface_tag: str, bitrate_combo_tag: str):

        try:
            interface, channel = dpg.get_value(combo_interface_tag).split(" : ") # format "vector : chnannel"
            bitrate = int(dpg.get_value(bitrate_combo_tag)) * 1000
            self.can.connect(interface, int(channel), dbc_path=self.dbc_path, bitrate=bitrate)
            dpg.configure_item(self.con_button_tag, label = 'Подключен', enabled = False)
            dpg.configure_item(self.discon_button_tag, label = 'Отключить', enabled = True)

        except ValueError:
            return # пока заглушка для ошибки
        except Exception as err:
            print(err)

    def on_disconnect_click(self):
        self.can.disconnect()
        dpg.configure_item(self.con_button_tag, label = 'Подключить', enabled = True)
        dpg.configure_item(self.discon_button_tag, label = 'Отключено', enabled = False)
    
    def set_dbc(self, path_dbc):
        self.dbc_path = path_dbc

        if self.can.get_connection_status(): self.can.scanner.decoder.set_db(path_dbc)


    def update(self): return
        
        




class BusConnectionWindow(BaseWindow):

    tag = "bus"
    title = "Окно подключения интерфейса"
    size = (0.5, 0.1)
    position = (0, 0)
    logic = None

    __connect_button_tag = 'connect_bus'
    __disconnect_button_tag = 'disconnect_bus'
    __interface_combo_tag = 'device_combo'

    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = BusLogic(kwargs['data'], cls.__connect_button_tag, cls.__disconnect_button_tag)
        with dpg.window(
            tag=cls.tag,
            label=cls.title,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            no_close=True,
        ):
            with dpg.tab_bar():
                with dpg.tab(label="Онлайн"):
                    with dpg.table(
                        header_row=False,
                        borders_innerV=False,
                        borders_innerH=False,
                        resizable=False
                    ):
                        dpg.add_table_column(init_width_or_weight=0.1)
                        dpg.add_table_column(init_width_or_weight=0.3)
                        dpg.add_table_column(init_width_or_weight=0.2)
                        dpg.add_table_column(init_width_or_weight=0.2)
                        dpg.add_table_column(init_width_or_weight=0.2)
                        
                        with dpg.table_row():
                            
                            dpg.add_button(label="Найти", width=-1, callback = lambda: cls.logic.update_available_interfaces(cls.__interface_combo_tag))

                            dpg.add_combo(cls.logic.get_available_interfaces(), tag=cls.__interface_combo_tag, width=-1)

                            dpg.add_combo(
                                ["250", "500"],
                                default_value="500",
                                tag="bitrate_combo",
                                width=-1
                            )

                            dpg.add_button(
                                label = "Подключить",
                                width = -1,
                                callback = lambda: cls.logic.on_connect_click(cls.__interface_combo_tag, сды),
                                tag= cls.__connect_button_tag
                            )
                            dpg.add_button(
                                label = "Отключено",
                                width = -1,
                                callback = lambda: cls.logic.on_disconnect_click(),
                                tag = cls.__disconnect_button_tag,
                                enabled = False
                            )
                with dpg.tab(label="Оффлайн"):
                    ...

    @classmethod
    def update(cls):
        pass