import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow
from EventHandler import EventHandler
from ProjectManager import ProjectManager, ProjectData
from datetime import datetime

from settings import FILE_EXT_COLOR

from GuiModules.BusConnectionWindow import BusConnectionWindow
from GuiModules.DBCConnectionWindow import DBCConnectionWindow
from GuiModules.PlotWindow import PlotWindow

from os import path



class ProjectLogic:
    
    def __init__(self, state_manager: ProjectManager, event_handler: EventHandler, window_tag):
        self.state_manager = state_manager
        self.event_handler = event_handler
        self.cur_project: ProjectData = None
        self.save_path = None
        self.window_tag = window_tag
        self.setup_events()
    
    def setup_events(self):
        ...

    def show_save_dialog(self):
        if dpg.is_item_shown(f"{self.window_tag}_file_dialog_wprj"): return
        if dpg.is_item_shown(f"{self.window_tag}_confirm_action"): dpg.hide_item(f"{self.window_tag}_confirm_action")
        dpg.show_item(f"{self.window_tag}_file_dialog_wprj")

    def request_close(self):
        x = (dpg.get_viewport_client_width() - dpg.get_item_width(f"{self.window_tag}_confirm_action")) // 2
        y = (dpg.get_viewport_client_height() - dpg.get_item_height(f"{self.window_tag}_confirm_action")) // 2
        dpg.configure_item(
            f"{self.window_tag}_confirm_action",
            show = True,
            pos = (x, y)
        )

    
    def close_project(self):
        self.cur_project = None
        self.save_path = None
        

    def save_project(self, sender):
        if not self.save_path: self.show_save_dialog()
        else:
            self.save()




    def save_as_project(self, sender, info): 
        print(f"saveas {info['file_path_name']}")
        if not self.cur_project: self.cur_project = self.state_manager.init_project()
        self.save_path = info['file_path_name']
        self.save()

    def save(self, save_project: bool = True):
        # DBC
        dbc = DBCConnectionWindow.logic.save_info()

        if dbc:
            self.cur_project.edit_settings(*dbc)
        # BUS
        bus = BusConnectionWindow.logic.save_info()
        if bus:
            self.cur_project.edit_settings(*bus)
        #PLOT and Signals
        plot = PlotWindow.logic.save_info()
        if plot:
            self.cur_project.edit_settings(*plot)

        if save_project:
            self.state_manager.save_project(self.save_path, self.cur_project)



        

    def on_open_project_btn_click(self, sender):
        if self.cur_project: self.request_close()

        dpg.show_item(f"{self.window_tag}_file_dialog_oprj")
        

        
    
    def open_project(self, sender, info):
        if self.cur_project: self.request_close()

        self.cur_project = self.state_manager.open_project(info['file_path_name'])
        self.save_path = info['file_path_name']

        dbc = self.cur_project.get_settings(DBCConnectionWindow.tag)
        if dbc:
            DBCConnectionWindow.logic.load_info(dbc)

        bus = self.cur_project.get_settings(BusConnectionWindow.tag)
        if bus:
             BusConnectionWindow.logic.load_info(bus)
    
        plot = self.cur_project.get_settings(PlotWindow.tag)
        if plot:
             PlotWindow.logic.load_info(plot)


    def update(self): ...
    
   
            









class ProjectWindow(BaseWindow):

    tag = "prj"
    title = "Управление проектами"


    @classmethod
    def setup_menu_bar_intro(cls, *args, **kwargs):
        """Class for additional class pre-setup"""
        cls.setup(*args, **kwargs)
        # dpg.add_menu_item(label=cls.title, callback = cls.show_window)


    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = ProjectLogic(kwargs['state_manager'], kwargs['event_handler'], cls.tag)

        with dpg.file_dialog(
                        label = "Выбрать Проект",
                        directory_selector=False,
                        show=False,
                        tag=f"{cls.tag}_file_dialog_oprj",
                        file_count=1,
                        callback = cls.logic.open_project,
                        width=700,
                        height=400
                    ):
                        dpg.add_file_extension(".json", color=FILE_EXT_COLOR)
        
        with dpg.file_dialog(
                        label = "Выбрать место для сохранения Проекта",
                        show=False,
                        tag=f"{cls.tag}_file_dialog_wprj",
                        default_filename="",
                        file_count=1,
                        callback = cls.logic.save_as_project,
                        width=700,
                        height=400
                    ):
                        dpg.add_file_extension(".json", color=FILE_EXT_COLOR)
        
        with dpg.window(
            label = "Подтвердите действие",
            modal = True,
            width = 350,
            height = 100,
            no_resize = True,
            no_move = True,
            no_close = True,
            show = False,
            tag = f"{cls.tag}_confirm_action"
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Вы уверены, что хотите закрыть проект, не сохраняя его?")
            with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchSame):
                dpg.add_table_column()
                dpg.add_table_column()
            
                with dpg.table_row():
                    dpg.add_button(label = "Сохранить", callback = cls.logic.show_save_dialog)
                    dpg.add_button(label = "Не сохранять")

    @classmethod
    def setup_project_menu(cls):
        dpg.add_menu_item(label = "Открыть", callback = cls.logic.on_open_project_btn_click)
        dpg.add_menu_item(label = "Сохранить", callback = cls.logic.save_project)
        dpg.add_menu_item(label = "Сохранить как", callback = cls.logic.save_as_project)

        with dpg.menu(label = "Последние"):
            projects = cls.logic.state_manager.get_meta_data()
            if projects:
                for project_name, values in projects.items():
                    dpg.add_menu_item(label = path.basename(project_name).split(".")[0], callback =  lambda: cls.logic.open_project("", values))
            else:
                dpg.add_text("Не найдены")
        
    



