import dearpygui.dearpygui as dpg
import threading

from BaseWindow import BaseWindow
from CanInterface import CANManager, CanLogReader, CANData
from settings import FILE_EXT_COLOR
from datetime import datetime
from os import path


class BusLogic:

    dbc_path = None

    def __init__(self, data: CANData, con_button_tag, discon_buttun_tag, load_log_tag, clear_log_tag, window_tag, log_status_tag, log_path, interface_tag, bitrate_tag, clr_online_btn, event):
        self.can = CANManager(data)
        self.data = data
        self.con_button_tag = con_button_tag
        self.discon_button_tag = discon_buttun_tag
        self.load_log_tag = load_log_tag
        self.clear_log_tag = clear_log_tag
        self.window_tag = window_tag
        self.log_status_tag = log_status_tag
        self.interface_tag = interface_tag
        self.bitrate_tag = bitrate_tag
        self.clr_online_btn = clr_online_btn
        self.log_read = None
        self.log_thread_read = None
        self.log_path = log_path

        self.event_handler = event

    def update_available_interfaces(self, combo_tag: str):
        self.can.scan_available_configs()
        dpg.configure_item(combo_tag, items=self.get_available_interfaces())

    def get_available_interfaces(self) -> tuple[str]:
        interfaces = list()
        for config in self.can.get_configs():
            interfaces.append(f"{config['interface']} : {config['channel']}")
        return interfaces
    
    def enable_log(self):
        if self.can.log_mode: return   

        self.can.enable_log(path.join(self.log_path, "CANLOG_" + f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.blf"))

    def on_log_checkbox_call(self, sender, data):
        if data and not self.can.log_mode: self.enable_log()
        else: self.can.disable_log()


    
    def on_connect_click(self, combo_interface_tag: str, bitrate_combo_tag: str):
        if self.log_read: raise Exception("Can't connect while log open")
        try:
            interface, channel = dpg.get_value(combo_interface_tag).split(" : ") # format "vector : chnannel"
            bitrate = int(dpg.get_value(bitrate_combo_tag)) * 1000
            self.can.connect(interface, int(channel), dbc_path=self.dbc_path, bitrate=bitrate)
            dpg.configure_item(self.con_button_tag, label = 'Подключен', enabled = False)
            dpg.configure_item(self.discon_button_tag, label = 'Отключить', enabled = True)
            dpg.configure_item(self.load_log_tag, enabled = False)

            self.event_handler.invoke("resume")

        except ValueError:
            return # пока заглушка для ошибки
        except Exception as err:
            print(err)

    def on_disconnect_click(self):
        self.event_handler.invoke("pause")
        self.can.disconnect()
        dpg.configure_item(self.con_button_tag, label = 'Подключить', enabled = True)
        dpg.configure_item(self.discon_button_tag, label = 'Отключено', enabled = False)
        dpg.configure_item(self.load_log_tag, enabled = True)
    
    def on_clear_click(self):
        self.event_handler.invoke("resume")

    def open_log_dialog(self, sender, data):
        if self.can.get_connection_status(): return

        if self.dbc_path is None: raise ValueError("dbc file is required")

        dpg.show_item(f"{self.window_tag}_file_dialog_offline")

    def open_log(self, sender, data):
        if self.can.get_connection_status(): raise Exception("Can't read log while connect online")

        log = CanLogReader()
        self.log_read = log

        # self.log_read.

        self.log_thread_read = threading.Thread(target = log.read_log, args=(data['file_path_name'], self.dbc_path), daemon = True)

        self.log_thread_read.start()

        dpg.configure_item(self.load_log_tag, enabled = False)
        dpg.configure_item(self.clear_log_tag, enabled = True)
        dpg.configure_item(self.log_status_tag, default_value = f"Загрузка лога: {data['file_name'].split('.')[0]}")
        dpg.configure_item(self.con_button_tag, enabled = False)
        dpg.configure_item(self.clr_online_btn, enabled = False)





    
    def set_dbc(self, path_dbc):
        self.dbc_path = path_dbc

        if self.can.get_connection_status(): self.can.scanner.decoder.set_db(path_dbc)


    def update(self):
        if self.log_read and self.log_read.is_ready:
            self.data.static_mode = True
            self.data.messages = self.log_read.messages
            self.data.signal_plot = self.log_read.signal_plot
            self.log_thread_read = None
            self.log_read = None
            dpg.configure_item(self.log_status_tag, default_value = "Лог загружен")
    
    def clear_log(self):
        print('button is pressed')
        if self.log_read:
            self.log_read.event.set()

        if self.log_thread_read is not None and self.log_thread_read.is_alive():
            self.log_thread_read.join()
            self.log_thread_read = None
            
        self.data.reset()
        self.log_read = None
        dpg.configure_item(self.log_status_tag, default_value = "Лог не загружен")
        dpg.configure_item(self.load_log_tag, enabled = True)
        dpg.configure_item(self.clear_log_tag, enabled = False)
        dpg.configure_item(self.con_button_tag, enabled = True)
        dpg.configure_item(self.clr_online_btn, enabled = True)
    
    def clear(self):
        if self.log_read or self.can.get_connection_status():
            self.clear_log()
            self.on_disconnect_click()

    def save_info(self):

        params = {}
        if self.log_path:
            params['path'] = self.log_path
        if dpg.get_value(self.bitrate_tag):
            params['bitrate'] = dpg.get_value(self.bitrate_tag)
        if dpg.get_value(self.interface_tag):
            interface, channel = dpg.get_value(self.interface_tag).split(" : ")
            params['interface'] = interface
            params['channel'] = channel

        # if self.log_read:
        #     mode = 0
        #     params['path'] = self.log_path
        # elif self.can.get_connection_status():
        #     mode = 1
        #     params['bitrate'] = dpg.get_value("bitrate_combo")
        #     interface, channel = dpg.get_value(self.combo_interface_tag).split(" : ")
        #     params['interface'] = interface
        #     params['channel'] = channel
        # else:
        #     return
        

        
        return self.window_tag, params
        # return self.window_tag, {
        #     "mode": mode,
        #     **params
        # }

    def load_info(self, data: dict):
        self.clear()
        if data['mode'] > 0:
            self.open_log("", data['path'])
        elif data["mode"] == 0:
            dpg.set_value("bitrate_combo", data['bitrate'])
            dpg.set_value(self.combo_interface_tag, f"{data['interface']} : {data['channel']}")






        
        




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
    __is_logging_tag = "is_logging_check"
    __clear_button_tag = "clear_online_button"
    

    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = BusLogic(kwargs['data'], cls.__connect_button_tag, cls.__disconnect_button_tag, cls.__load_log_tag, cls.__clear_log_tag, cls.tag, cls.__log_status_tag, kwargs['log_path'], cls.__interface_combo_tag, cls.__bitrate_combo_tag, cls.__clear_button_tag, event = kwargs['event_handler'])
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
                        with dpg.table_row():
                            dpg.add_button(
                                label = "Очистить",
                                width = -1,
                                callback = cls.logic.on_clear_click,
                                tag = cls.__clear_button_tag
                            )
                            dpg.add_checkbox(label = "Запись", tag=cls.__is_logging_tag, callback=cls.logic.on_log_checkbox_call)
                            

                with dpg.tab(label="Оффлайн"):
                    with dpg.group(horizontal = True):
                        dpg.add_button(label = "Выбрать лог", callback= cls.logic.open_log_dialog, tag = cls.__load_log_tag)
                        dpg.add_text("Лог не загружен", tag = cls.__log_status_tag)
                        dpg.add_button(label = "Очитстить", tag = cls.__clear_log_tag, enabled = False, callback = cls.logic.clear_log)

                    with dpg.file_dialog(
                        label = "Выбрать BLF",
                        default_path = kwargs['log_path'],
                        directory_selector=False,
                        show=False,
                        tag=f"{cls.tag}_file_dialog_offline",
                        file_count=1,
                        callback=cls.logic.open_log,
                        width=700,
                        height=400
                    ):
                        dpg.add_file_extension(".blf", color=FILE_EXT_COLOR)

