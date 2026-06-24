
import dearpygui.dearpygui as dpg

class gui_window:

    def __init__(self, name, menu_label, window_tag, update_callback="def", setup_callback="deff", open_callback="def"):

        self.label = menu_label
        self.tag = window_tag
        self.name = name
        self.no_move=True
        self.no_resize=True
        self.no_collapse=True
        self.no_close=True

        if update_callback == "def":
            self.update_callback = self.default_up_calback
        else:
            self.update_callback = update_callback

        if setup_callback == "deff":
            self.setup_callback = self.default_set_calback
        else:
            self.setup_callback = setup_callback
        
        if open_callback == "deff":
            self.open_callback = self.default_set_calback
        else:
            self.open_callback = open_callback
        
        
    def menu_bar(self):
        dpg.add_menu_item(label=self.label, callback=lambda: self.show_item())
    
    def show_item(self):
        dpg.show_item(self.tag)
        try:
            self.open_callback(sender=self)
        except:
            pass

    def setup(self):
        with dpg.window(label=self.name, tag=self.tag, no_move=self.no_move, no_resize=self.no_resize, no_collapse=self.no_collapse, no_close=self.no_close):
            self.setup_callback(sender = self)

    def default_up_calback(self,sender):
        # print("def_up")
        pass

    def default_set_calback(self,sender):
        # print("def_up")
        pass

    def update(self):
        self.update_callback(sender=self)
        pass

    

