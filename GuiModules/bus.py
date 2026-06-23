import dearpygui.dearpygui as dpg
from can_interface import message_frequencies,initialize_can_bus,detect_avalible_config,deinit_bus
from collections import defaultdict

class BusGui:
    avalible_devices = defaultdict(lambda:{'name': [], 'interface': [], 'channel': 0})