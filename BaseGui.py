import dearpygui.dearpygui as dpg
import time
import ctypes
import os

from GuiModules.BusConnectionWindow import BusConnectionWindow
from GuiModules.DBCConnectionWindow import DBCConnectionWindow
from GuiModules.MessagesWindow import MessagesWindow
from GuiModules.SignalsWindow import SignalsWindow
from GuiModules.PlotWindow import PlotWindow
from GuiModules.ProjectWindow import ProjectWindow
from CanInterface import CANData
from EventHandler import EventHandler
from settings import MAX_DATA_IN_RAM, FILE_LOG_BASE_NAME, APP_NAME
from ProjectManager import ProjectManager



class AppGui:
    """"""
    
    windows = [BusConnectionWindow, DBCConnectionWindow, SignalsWindow, PlotWindow]
    additional_windows = [MessagesWindow, ProjectWindow]

    data = CANData(plot_data_max_sec=MAX_DATA_IN_RAM)
    event_handler = EventHandler()
    state_manager = ProjectManager()

    def __init__(self, update_interval = 0.1):
        log_path = os.path.join(os.getcwd(), FILE_LOG_BASE_NAME)
        if not os.path.exists(log_path): os.mkdir(log_path)
        self.log_path = log_path
        self.__setup_gui()
        self.__last_update_time = time.time()
        self.update_interval = update_interval

        

         #Для синхронизации данных

        
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

        


    def __setup_gui(self):     

        dpg.create_context()

        with dpg.value_registry(tag="shared_value_registr"): pass
        
        with dpg.window(tag = "main_window", on_close = self.exit_gui) as root:

            with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchSame):
                dpg.add_table_column(init_width_or_weight=0.3)
                dpg.add_table_column(init_width_or_weight=0.7)

                with dpg.table_row():
                    DBCConnectionWindow.setup(data = self.data, event_handler = self.event_handler, width=-1 ,height=80)
                    BusConnectionWindow.setup(data = self.data, event_handler = self.event_handler, width=-1 ,height=80, log_path = self.log_path)
                with dpg.table_row(height=-1):
                    SignalsWindow.setup(data = self.data, event_handler = self.event_handler, width=-1 ,height=-1)
                    PlotWindow.setup(data = self.data, event_handler = self.event_handler, width=-1 ,height=-1)

        
        
        with dpg.viewport_menu_bar():
            with dpg.menu(label = "Дополнителные инструменты"):
                for window in self.additional_windows:
                    window.setup_menu_bar_intro(data = self.data, event_handler = self.event_handler, state_manager = self.state_manager)
            with dpg.menu(label = "Проекты"):
                ProjectWindow.setup_project_menu()
                    

        
        dpg.create_viewport(title = APP_NAME, min_width=1200, min_height=800)
        dpg.setup_dearpygui()
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        dpg.show_viewport()
        dpg.set_primary_window(root, True)
        
        self.__set_up_font()
        self.__set_up_theme()



    @staticmethod
    def app_is_running():
        return dpg.is_dearpygui_running()


    def update_gui(self):
        
        current_time = time.time()
        if current_time - self.__last_update_time >= self.update_interval:  # Обновление интерфейса согласно частоте
            
            for window in self.windows + self.additional_windows:
                try:
                    window.logic.update()
                except Exception as err:
                    print(err)
            
            self.__last_update_time = current_time

        dpg.render_dearpygui_frame()



    def exit_gui(self):
        dpg.destroy_context()
        self.state_manager.export_meta_data()
