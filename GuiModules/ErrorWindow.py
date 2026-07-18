import dearpygui.dearpygui as dpg
import time

from BaseWindow import BaseWindow
from queue import Queue
from settings import ERROR_TIMELIFE



class ErrorLogic:

    

    def __init__(self, window_tag: str):
        self.__error_to_show = Queue()
        self.cur_errors = list()
        self.max_show_errors = 4
        self.window_tag = window_tag
        self.error_time_life = ERROR_TIMELIFE

    def add_error(self, from_module: str, error_title: str, error_desc: str):
        self.__error_to_show.put((from_module, error_title, error_desc))

    
    def update(self): 
        
        x = 0
        y = (dpg.get_viewport_client_height() - dpg.get_item_height(self.window_tag))
        dpg.configure_item(
            self.window_tag,
            pos = (x, y)
        )

        expired = []

        for error in self.cur_errors:
            timestamp, error_id = error
            if time.time()  - timestamp > self.error_time_life:
                expired.append(error_id)
        
        for error in expired:
            self.__delete_error(error)
            self.cur_errors.remove(error)
        
        if len(self.cur_errors) >= self.max_show_errors: return
        
        while len(self.cur_errors) < self.max_show_errors and not self.__error_to_show.empty(): 
            module, title, desc = self.__error_to_show.get()
            self.cur_errors.append((time.time(), self.__create_error(f"[{module}] {title}", desc)))

        
        

    

    def __create_error(self, title, desc): 
        with dpg.child_window(
        parent=self.window_tag,
        border=True,
        autosize_x=True,
        height=60
        ) as error_id:
            
            dpg.add_text(title)
            dpg.add_text(desc, wrap=250) 

        return error_id
        

    def __delete_error(self, tag: str):
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
            









class ErrorWindow(BaseWindow):

    tag = "err"
    title = "Монитор ошибок"

    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = ErrorLogic(cls.tag)
        with dpg.window(
            tag=cls.tag,
            show=True,
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            no_close=True,
            autosize=True,
            no_background=True,
            ):
            ...
