import dearpygui.dearpygui as dpg
import threading

from BaseWindow import BaseWindow
from CanInterface import CANManager, CanLog, CANData
from settings import FILE_EXT_COLOR

class BusLogic:

    dbc_path = None

    def __init__(self, data: CANData, con_button_tag, discon_buttun_tag, load_log_tag, clear_log_tag, window_tag, log_status_tag):
        self.can = CANManager(data)
        self.data = data
        self.con_button_tag = con_button_tag
        self.discon_button_tag = discon_buttun_tag
        self.load_log_tag = load_log_tag
        self.clear_log_tag = clear_log_tag
        self.window_tag = window_tag
        self.log_status_tag = log_status_tag
        self.log = None
        self.log_thread = None

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
            dpg.configure_item(self.load_log_tag, enabled = False)

        except ValueError:
            return # пока заглушка для ошибки
        except Exception as err:
            print(err)

    def on_disconnect_click(self):
        self.can.disconnect()
        dpg.configure_item(self.con_button_tag, label = 'Подключить', enabled = True)
        dpg.configure_item(self.discon_button_tag, label = 'Отключено', enabled = False)
        dpg.configure_item(self.load_log_tag, enabled = True)

    def open_log_dialog(self, sender, data):
        if self.can.get_connection_status(): return

        if self.dbc_path is None: raise ValueError("dbc file is required")

        dpg.show_item(f"{self.window_tag}_file_dialog_offline")

    def open_log(self, sender, data):

        log = CanLog()
        self.log = log

        self.log_thread = threading.Thread(target = log.read_log, args=(data['file_path_name'], self.dbc_path), daemon = True)

        self.log_thread.start()

        dpg.configure_item(self.load_log_tag, enabled = False)
        dpg.configure_item(self.clear_log_tag, enabled = True)
        dpg.configure_item(self.log_status_tag, default_value = f"Загрузка лога: {data['file_name'].split('.')[0]}")
        dpg.configure_item(self.con_button_tag, enabled = False)





    
    def set_dbc(self, path_dbc):
        self.dbc_path = path_dbc

        if self.can.get_connection_status(): self.can.scanner.decoder.set_db(path_dbc)


    def update(self):
        if self.log and self.log.is_ready:
            self.data.static_mode = True
            self.data.messages = self.log.messages
            self.data.signal_plot = self.log.signal_plot
            self.log_thread = None
            self.log = None
            dpg.configure_item(self.log_status_tag, default_value = "Лог загружен")
    
    def clear_log(self, sender, data):
        print('button is pressed')
        if self.log:
            print("log")
            self.log.event.set()

        if self.log_thread is not None and self.log_thread.is_alive():
            print("alive")
            self.log_thread.join()
            self.log_thread = None
            
        self.data.reset()
        self.log = None
        dpg.configure_item(self.log_status_tag, default_value = "Лог не загружен")
        dpg.configure_item(self.load_log_tag, enabled = True)
        dpg.configure_item(self.clear_log_tag, enabled = False)
        dpg.configure_item(self.con_button_tag, enabled = True)



        
        




class BusConnectionWindow(BaseWindow):

    tag = "bus"
    title = "Окно подключения интерфейса"
    logic = None

    __connect_button_tag = 'connect_bus'
    __disconnect_button_tag = 'disconnect_bus'
    __interface_combo_tag = 'device_combo'
    __bitrate_combo_tag = "bitrate_combo"
    __log_status_tag = "log_status_text"
    __load_log_tag = "load_log_button"
    __clear_log_tag = "clear_log_button"
    

    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = BusLogic(kwargs['data'], cls.__connect_button_tag, cls.__disconnect_button_tag, cls.__load_log_tag, cls.__clear_log_tag, cls.tag, cls.__log_status_tag)
        with dpg.child_window(
            tag=cls.tag,
            label=cls.title,
            height=kwargs['height'],
            width=kwargs['width']
        ):
            with dpg.tab_bar():
                with dpg.tab(label="Онлайн"):
                    with dpg.table(
                        header_row=False,
                        borders_innerV=False,
                        borders_innerH=False,
                        resizable=False
                    ):
                        dpg.add_table_column(init_width_or_weight=0.2)
                        dpg.add_table_column(init_width_or_weight=0.2)
                        dpg.add_table_column(init_width_or_weight=0.2)
                        dpg.add_table_column(init_width_or_weight=0.2)
                        dpg.add_table_column(init_width_or_weight=0.2)
                        
                        with dpg.table_row():
                            
                            dpg.add_button(label="Найти", width=-1, callback = lambda: cls.logic.update_available_interfaces(cls.__interface_combo_tag))

                            dpg.add_combo(cls.logic.get_available_interfaces(), tag=cls.__interface_combo_tag, width=-1)

                            dpg.add_combo(
                                ["250", "500"],
                                default_value="500",
                                tag=cls.__bitrate_combo_tag,
                                width=-1
                            )

                            dpg.add_button(
                                label = "Подключить",
                                width = -1,
                                callback = lambda: cls.logic.on_connect_click(cls.__interface_combo_tag, cls.__bitrate_combo_tag),
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
                    with dpg.group(horizontal = True):
                        dpg.add_button(label = "Выбрать лог", callback= cls.logic.open_log_dialog, tag = cls.__load_log_tag)
                        dpg.add_text("Лог не загружен", tag = cls.__log_status_tag)
                        dpg.add_button(label = "Очитстить", tag = cls.__clear_log_tag, enabled = False, callback = cls.logic.clear_log)

                    with dpg.file_dialog(
                        label = "Выбрать BLF",
                        directory_selector=False,
                        show=False,
                        tag=f"{cls.tag}_file_dialog_offline",
                        file_count=1,
                        callback=cls.logic.open_log,
                        width=700,
                        height=400
                    ):
                        dpg.add_file_extension(".blf", color=FILE_EXT_COLOR)

