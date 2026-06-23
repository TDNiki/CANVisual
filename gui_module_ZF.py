import dearpygui.dearpygui as dpg
from window_class import gui_window
from can_interface import message_frequencies,message_queue
from datetime import datetime

def setup_window(sender):
    # dpg.set_item
    with dpg.child_window(width=-1,height=300):
        with dpg.tab_bar():

            with dpg.tab(label="Valves"):
                pass

            with dpg.tab(label="Actuators"):
                pass

            with dpg.tab(label="Gears"):
                pass

    with dpg.group(horizontal=True):
        with dpg.subplots(2, 1, label="", width=-100, height=-1, link_all_x=True, tag="ZF_subplot") as subplot_id:
        # dpg.add_plot_legend(outside=True,horizontal=False, location=5)
        # dpg.add_plot_legend()
            for i in range(2):
                with dpg.plot(no_title=True):
                    dpg.add_plot_legend()
                    if i == 0:
                        dpg.add_plot_axis(dpg.mvXAxis,label='',tag ="ZFpX")
                    else:
                        dpg.add_plot_axis(dpg.mvXAxis, label='')
                    dpg.add_plot_axis(dpg.mvYAxis, label="")

def update_window(sender):
    pass

ZF_window = gui_window(name = 'ZF test interface',menu_label='ZF test', window_tag = 'ZFWindow', 
                            setup_callback=setup_window, update_callback=update_window,width=600,height=700)
