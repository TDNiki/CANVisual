import dearpygui.dearpygui as dpg
from window_class import gui_window
from can_interface import connect_db,db
from collections import defaultdict
import re

def setup_window(sender):
    dpg.add_text("Devices")
    with dpg.file_dialog(label="DBC File Dialog", width=600, height=400, show=False, callback=lambda s, a, u : select_file(a), tag="filedialog"):
        dpg.add_file_extension(".dbc", color=[150, 200, 255, 255])
    # dpg.add_button(label="Path",user_data=dpg.last_container(), callback=lambda s, a, u: dpg.configure_item(u, show=True))
    with dpg.group(horizontal=True):
        dpg.add_button(label="Path",user_data="filedialog", callback=lambda s, a, u: dpg.configure_item(u, show=True))
        dpg.add_input_text(tag="dbc_file", width=-101)
        dpg.add_button(label="Open", width=100,callback=connect_calback)

    dpg.add_text(tag="dbc_status",color=[150, 200, 255, 255])

    # with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_innerH=True, borders_outerH=True, 
    #                borders_innerV=True, borders_outerV=True, row_background=True, tag='ReceivedMessagesTable'):
        
def open_window(sender):
    
    pass

def update_window(sender):

    pass

dbc_window = gui_window(name = 'DBC Config', menu_label='DBC', window_tag='dbc', 
                        setup_callback=setup_window, update_callback=update_window, open_callback=open_window)


def select_file(app_data):
    # print(app_data["file_path_name"])
    dpg.set_value("dbc_file",app_data["file_path_name"])

def connect_calback(sender,app_data):
    # if app_data == None:
    #     dpg.set_value("dbc_status", "error: No File.")
    #     return
    
    try:
        connect_db(dpg.get_value("dbc_file"))
        dpg.set_value("dbc_status", "DBC opened succes.")
        # dpg.set_colormap("dbc_status",(0,255,0,50))
    except Exception as e:
        dpg.set_value("dbc_status", f"error: {e}.")
        # dpg.set_colormap("dbc_status",(255,0,0,50))

    

    


# def disconnect_calback():
#     deinit_bus()
#     dpg.bind_item_theme("disconBut", "gray")
#     dpg.bind_item_theme("conBut", "green")
#     pass