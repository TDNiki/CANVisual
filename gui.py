import dearpygui.dearpygui as dpg
from can_interface import send_can_message, available_signals, plot_signals, signal_data
from utils import set_update_interval
from math import sin
import time

from gui_module_recieve import recieve_window
from gui_module_signals import signal_window
from gui_module_plot import plot_window
from gui_modul_connect import bus_window
from gui_modul_dbc import dbc_window
from gui_module_ZF import ZF_window

windows = [bus_window, recieve_window, dbc_window, signal_window, plot_window,ZF_window]


# creating data
sindatax = []
sindatay = []
for i in range(0, 500):
    sindatax.append(i / 1000)
    sindatay.append(0.5 + 0.5 * sin(50 * i / 1000))

#########################################
last_update_time = time.time()

def setup_gui():
    global update_interval
    global last_update_time
    
    dpg.create_context()
    dpg.create_viewport(title='CAN Analyzer', width=1600, height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()


    # with dpg.theme(tag="background"):
    #     with dpg.theme_component(dpg.mvButton):
    #         dpg.add_theme_color(dpg.mvThemeCol_NavWindowingDimBg,(0,255,255,100))

    # with dpg.window(tag="backg",label='v',width=1000, height=100, pos=(0, 0)):
    #     pass
    # dpg.bind_item_theme("backg", "background")
    # dpg.set_primary_window("backg",True)
    # Верхний бар для открытия окон
    with dpg.viewport_menu_bar():
        with dpg.menu(label="Windows"):

            for window in windows:
                window.menu_bar()

        with dpg.menu(label="Tools"):

            dpg.add_menu_item(label="Show About", callback=lambda:dpg.show_tool(dpg.mvTool_About))
            dpg.add_menu_item(label="Show Metrics", callback=lambda:dpg.show_tool(dpg.mvTool_Metrics))
            dpg.add_menu_item(label="Show Documentation", callback=lambda:dpg.show_tool(dpg.mvTool_Doc))
            dpg.add_menu_item(label="Show Debug", callback=lambda:dpg.show_tool(dpg.mvTool_Debug))
            dpg.add_menu_item(label="Show Style Editor", callback=lambda:dpg.show_tool(dpg.mvTool_Style))
            dpg.add_menu_item(label="Show Font Manager", callback=lambda:dpg.show_tool(dpg.mvTool_Font))
            dpg.add_menu_item(label="Show Item Registry", callback=lambda:dpg.show_tool(dpg.mvTool_ItemRegistry))

    for window in windows:
        window.setup()

    # Окно для отправки сообщений
    with dpg.window(label='Send Message', width=1000, height=100, tag='SendMessageWindow', pos=(0, 0), show=False):
        dpg.add_text('Send Message')
        dpg.add_input_text(label='ID', tag='MessageID')
        dpg.add_input_text(label='Data', tag='MessageData')
        dpg.add_button(label='Send', callback=send_can_message)
        dpg.add_input_float(label='Update Interval (s)', default_value=1.0, tag='UpdateInterval', callback=lambda sender, app_data, user_data: set_update_interval(dpg.get_value(sender)))

    last_update_time = time.time()

    dpg.set_viewport_vsync(True)

def app_is_running():
    return dpg.is_dearpygui_running()

def update_gui():
    global last_update_time

    current_time = time.time()
    if current_time - last_update_time >= set_update_interval():  # Обновление интерфейса согласно частоте
        recieve_window.update()
        signal_window.update()
        bus_window.update()
        ZF_window.update()
        last_update_time = current_time
    # update_plot()
    plot_window.update()
    dpg.render_dearpygui_frame()

def exit_gui():
    dpg.destroy_context()
