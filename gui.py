import dearpygui.dearpygui as dpg
from can_interface import send_can_message, available_signals, plot_signals, signal_data
from utils import set_update_interval
from math import sin
import time
from gui_windows_config import WindowsConfigManager

from gui_module_recieve import recieve_window
from gui_module_signals import signal_window
from gui_module_plot import plot_window
from gui_modul_connect import bus_window
from gui_modul_dbc import dbc_window
from gui_module_ZF import ZF_window

CONFIG_WINDOWS_PATH = "guiconfigs.json"



class AppGui:
    """"""

    #windows = [bus_window, recieve_window, dbc_window, signal_window, plot_window]
    
    windows = {
        "bus": bus_window,
        "plot": plot_window,
        "msgs": recieve_window,
        "signals": signal_window
    }



    def __init__(self):
        cm = WindowsConfigManager(CONFIG_WINDOWS_PATH)
        self.__configs = cm.get_configs()
        self.__setup_gui()
        self.__last_update_time = time.time()

        
    @staticmethod
    def __set_up_font():
        with dpg.font_registry():
            with dpg.font("Fonts\\timesnewromanpsmt.ttf", 13, default_font=True, tag="Default font") as f:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    
        dpg.bind_font("Default font")

    

    def __set_up_theme(self):
        with dpg.theme() as flat_window_theme:
            with dpg.theme_component(dpg.mvWindowAppItem):

                color = (40, 40, 40)

                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, color)
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, color)
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, color)

                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 25))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 220, 220))

                dpg.add_theme_color(dpg.mvThemeCol_Border,(100, 100, 100, 255))
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)

            for uicomponent in self.windows.keys():
                dpg.bind_item_theme(uicomponent, flat_window_theme)

        


    def __on_resize(self, sender, app_data):
        width = dpg.get_viewport_client_width()
        height = dpg.get_viewport_client_height()

        
        for win_id, cfg in self.__configs.items():
            dpg.set_item_width(win_id, int(width * cfg.size[0]))
            dpg.set_item_height(win_id, int(height * cfg.size[1]))

            dpg.set_item_pos(win_id, (int(width *cfg.pos[0]), int(height * cfg.pos[1])))


    def __setup_gui(self):     

        dpg.create_context()
        dpg.create_viewport(title="CAN GUI", width=1200, height=800, min_width=1200, min_height=800)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        
        
        
        width = dpg.get_viewport_client_width()
        height = dpg.get_viewport_client_height()

        for id, sub_gui in self.windows.items():
           sub_gui.tag = id
           sub_gui.setup()

           """ with dpg.window(
                tag=id,
                label=self.__configs[id].title,
                no_move=True,
                no_resize=True,
                no_collapse=True,
                no_close=True):
                dpg.add_text(f"тут будет содержание модуля {id}")"""
        
        self.__set_up_font()
        self.__set_up_theme()
        dpg.set_viewport_resize_callback(self.__on_resize)



    @staticmethod
    def app_is_running():
        return dpg.is_dearpygui_running()


    def update_gui(self):

        current_time = time.time()
        if current_time - self.__last_update_time >= set_update_interval():  # Обновление интерфейса согласно частоте
            #recieve_window.update()
            #signal_window.update()
            #bus_window.update()
            #ZF_window.update()
            #plot_window.update()
            self.__last_update_time = current_time
        dpg.render_dearpygui_frame()


    @staticmethod
    def exit_gui():
        dpg.destroy_context()
