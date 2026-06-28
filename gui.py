import dearpygui.dearpygui as dpg
import time

from GuiModules.BusConnectionWindow import BusConnectionWindow
from GuiModules.DBCConnectionWindow import DBCConnectionWindow
from GuiModules.MessagesWindow import MessagesWindow
from GuiModules.SignalsWindow import SignalsWindow
from GuiModules.PlotWindow import PlotWindow
from CanInterface import CANData
from EventHandler import EventHandler

class AppLogic:

    data = CANData()
    event_handler = EventHandler()


class AppGui:
    """"""

    #windows = [bus_window, recieve_window, dbc_window, signal_window, plot_window]
    
    windows = [BusConnectionWindow, DBCConnectionWindow, MessagesWindow, SignalsWindow, PlotWindow]



    def __init__(self, update_interval = 0.1):
        self.logic = AppLogic()
        self.__setup_gui()
        self.__last_update_time = time.time()
        self.update_interval = update_interval

        
    @staticmethod
    def __set_up_font():
        with dpg.font_registry():
            with dpg.font("Fonts\\timesnewromanpsmt.ttf", 13, default_font=True, tag="Default font"):
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

            for uicomponent in self.windows:
                dpg.bind_item_theme(uicomponent.tag, flat_window_theme)
        
        with dpg.theme() as button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 100, 200))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 120, 220))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (30, 80, 180))

        dpg.bind_theme(button_theme)

        


    def __on_resize(self, sender, app_data):
        width = dpg.get_viewport_client_width()
        height = dpg.get_viewport_client_height()

        
        for window_obj in self.windows:

            w, h, x, y = window_obj.resize_window(width, height)
            dpg.configure_item(
                window_obj.tag,
                width=w,
                height=h,
                pos=(x, y)
            )


    def __setup_gui(self):     

        dpg.create_context()
        dpg.create_viewport(title="CAN GUI", width = 1600, height=900, min_width=1200, min_height=800)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        
        
        

        for sub_gui in self.windows:
           sub_gui.setup(data = self.logic.data, event_handler = self.logic.event_handler)
        
        
        self.__set_up_font()
        self.__set_up_theme()
        dpg.set_viewport_resize_callback(self.__on_resize)



    @staticmethod
    def app_is_running():
        return dpg.is_dearpygui_running()


    def update_gui(self):
        
        current_time = time.time()
        if current_time - self.__last_update_time >= self.update_interval:  # Обновление интерфейса согласно частоте
            
            for window in self.windows:
                window.logic.update()
            
            self.__last_update_time = current_time

        dpg.render_dearpygui_frame()


    @staticmethod
    def exit_gui():
        dpg.destroy_context()
