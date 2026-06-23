
import dearpygui.dearpygui as dpg

class gui_window:

    def __init__(self,name,menu_label,window_tag,update_callback="def",setup_callback="deff",width=-1,height=-1,pos=(0,0), no_resize=False, show=False, open_callback="def"):
        self.label = menu_label
        self.tag = window_tag
        self.name = name
        self.width = width
        self.height = height
        self.pos = pos
        self.show = show
        self.no_resize = no_resize

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
        with dpg.window(label=self.name, width=self.width, min_size=(400,100), max_size= (1960,1000), height=self.height, tag=self.tag, pos=self.pos, no_resize=self.no_resize, show=self.show):
            self.setup_callback(sender = self)
            pass

    def default_up_calback(self,sender):
        # print("def_up")
        pass

    def default_set_calback(self,sender):
        # print("def_up")
        pass

    def update(self):
        self.update_callback(sender=self)
        pass

