import dearpygui.dearpygui as dpg
from window_class import gui_window
from can_interface import message_frequencies,initialize_can_bus,detect_avalible_config,deinit_bus
from collections import defaultdict

avalible_devices = defaultdict(lambda:{'name': [], 'interface': [], 'channel': 0})
# avalible_devices = {'name': [], 'interface': [], 'channel': 0}
# avalible_devices = {}



def setup_bus_window(sender):
    dpg.add_text("Devices")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Refresh",callback=refresh_HW_list)
        dpg.add_combo(tag="deviceCombo",width=200,callback=choose_device)
        dpg.add_combo((500, 250), default_value= 500, tag="bitrateCombo", width=80)
    with dpg.group(horizontal=True):
        dpg.add_text("Connection")
        dpg.add_text(tag="conn_status",color=(255,255,0,100))
    with dpg.group(horizontal=True):
        with dpg.theme(tag="green"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button,(25,255,25,50))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,(25,255,25,40))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,(25,255,25,60))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 21, 21)
        with dpg.theme(tag="red"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button,(255,25,25,50))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,(255,25,25,40))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,(255,25,25,60))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 21, 21)
        with dpg.theme(tag="gray"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Text,(255,255,255,100))
                dpg.add_theme_color(dpg.mvThemeCol_Button,(255,255,255,50))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,(255,255,255,50))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,(255,255,255,50))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 21, 21)

        dpg.add_button(tag="conBut",label="Connect",width=200,callback=lambda: connect_calback())
        dpg.bind_item_theme(dpg.last_item(), "green")
        dpg.add_button(tag="disconBut",label="Disconnect",width=200,callback=lambda: disconnect_calback())
        dpg.bind_item_theme("disconBut", "gray")

def open_bus_window(sender):
    refresh_HW_list()
    pass

def update_bus_window(sender):

    pass

bus_window = gui_window(name = 'Bus Connection', menu_label='BusConnection', window_tag='BusCon', 
                        setup_callback=setup_bus_window, update_callback=update_bus_window,open_callback=open_bus_window)


def choose_device(sender,app_data):
    print(app_data)

def refresh_HW_list():
    global avalible_devices
    
    config = detect_avalible_config()
    
    dpg.delete_item('deviceCombo', children_only=True)  # Очистка существующих элементов
    conf_name = []
    i = 0
    for d in config:
        # print(d["interface"],d["channel"])
        avalible_devices[i]["interface"] = d["interface"]
        avalible_devices[i]["channel"] = d["channel"]
        name = d["interface"] + ' ' + f"{d['channel']}"
        conf_name.append(name)
        avalible_devices[i]["name"] = name
        i = i+1
        # conf_name.append(d["interface"])
    dpg.configure_item('deviceCombo',items=conf_name)
    print(avalible_devices)
    dpg.set_value('deviceCombo',conf_name[0])
    
    pass

def connect_calback():
    
    for device in avalible_devices:
        print(avalible_devices[device])
        if dpg.get_value("deviceCombo") == avalible_devices[device]["name"]:
            try:
                # bitrate= re.findall(r'\b\d+\b', dpg.get_value("bitrateCombo"))
                bitrate = int(dpg.get_value("bitrateCombo")) *1000
                print(bitrate)
                initialize_can_bus(interface=avalible_devices[device]["interface"],channel=avalible_devices[device]["channel"], bitrate=bitrate)
                dpg.bind_item_theme("disconBut", "red")
                dpg.bind_item_theme("conBut", "gray")
                dpg.set_value("conn_status", "Connected.")
                return
            except Exception as E:
                print(f"ConnectionErr {E}")
                dpg.set_value("conn_status", f"error: {E}.")
                return
    print("No device!")


def disconnect_calback():
    deinit_bus()
    dpg.bind_item_theme("disconBut", "gray")
    dpg.bind_item_theme("conBut", "green")
    dpg.set_value("conn_status", "Disconnected.")
    pass