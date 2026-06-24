import dearpygui.dearpygui as dpg
from window_class import gui_window
#from can_interface import message_frequencies,initialize_can_bus,detect_avalible_config,deinit_bus
#from collections import defaultdict


def end_point(): return

class GuiConnections:

    def __set_up_widow(self):
        dpg.add_text("Интерфейсы")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh",callback=end_point)
            dpg.add_combo(tag="deviceCombo",width=200,callback=end_point)
            dpg.add_combo((500, 250), default_value= 500, tag="bitrateCombo", width=80)

    def __init__(self):

       self.__set_up_widow()

gui_coonnection_menu = GuiConnections()


bus_window = gui_window(name = 'Bus Connection', menu_label='BusConnection', window_tag='BusCon', 
                        setup_callback=gui_coonnection_menu, update_callback=end_point,open_callback=end_point)
