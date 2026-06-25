import dearpygui.dearpygui as dpg
from window_class import gui_window
from can_interface import parsed_signals,message_frequencies
from math import sin

# creating data
sindatax = []
sindatay = []
for i in range(0, 500):
    sindatax.append(i / 1000)
    sindatay.append(0.5 + 0.5 * sin(50 * i / 1000))

msg_list = []
colase_list = []

def setup_dbc_signals_window(sender):

    with dpg.group(horizontal=True):
        dpg.add_button(label="Collapse")
        dpg.add_button(label="Clear")

    

def update_dbc_signals_window(sender):
    # Удаляем старые строки, чтобы избежать дублирования
    rows = dpg.get_item_children('SignalsTable', 1)
    for row in rows:
        dpg.delete_item(row)

    # Добавляем распарсенные сигналы
    for msg_name, signals in parsed_signals.items():
        for signal_name, signal_value in signals.items():
            with dpg.table_row(parent='SignalsTable'):
                # dpg.add_text(hex(msg_id))
                dpg.add_text(msg_name)
                d=dpg.add_text(signal_name)
                dpg.add_text(f"{signal_value:.2f}")  # Значение сигнала
                with dpg.drag_payload(parent=d, drag_data=signal_name, payload_type="plotting"):
                    dpg.add_text(signal_name)
                    dpg.add_simple_plot(label="", default_value=sindatay)

def update_dbc_signals_window2(sender):
    global msg_list
    
    refresh_msgs_list()

    if len(msg_list) > len(colase_list):
        for msg in msg_list[len(colase_list)-len(msg_list):]:
            # colase_list.append(dpg.add_collapsing_header(label=msg))
            with dpg.collapsing_header(parent='RecievedWindow',label=message_frequencies[msg]["DBC_name"]):              
                colase_list.append(dpg.last_container())

                with dpg.table(pos=(100,-1),header_row=False, resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_innerH=True, 
                        borders_outerH=False, borders_innerV=True, borders_outerV=False, row_background=False, no_keep_columns_visible=True, tag=f'tab{msg}'):
                    # dpg.add_table_column(label='Message ID')
                    dpg.add_table_column(label='Signal Name')
                    dpg.add_table_column(label='Value')

    # Удаляем старые строки, чтобы избежать дублирования
    for msg in msg_list:
        rows = dpg.get_item_children(f'tab{msg}', 1)
        for row in rows:
            dpg.delete_item(row)

    # Добавляем распарсенные сигналы
    for msg_id, data in message_frequencies.items():
        if data['isDBC']:
            for signal_name, signal_value in data['ParsedSignals'].items():
                try:
                    with dpg.table_row(parent=f'tab{msg_id}'):
                        # dpg.add_text(f"{msg_id:08X}")
                        # dpg.add_text(data['DBC_name'])
                        d=dpg.add_text("   "+signal_name)
                        color=[150, 200, 255, 255]
                        dpg.add_text(f"{signal_value:.2f}",color=color)  # Значение сигнала
                        with dpg.drag_payload(parent=d, drag_data=(msg_id,signal_name), payload_type="plotting"):
                            dpg.add_text(signal_name)
                            dpg.add_simple_plot(label="", default_value=sindatay)
                except:
                    pass
       

def refresh_msgs_list():
    global msg_list
    is_incl = 0

    #     # Добавляем распарсенные сигналы
    # for msg_name,signals in parsed_signals.items():
    #     if msg_list.count == 0:
    #         msg_list.append(msg_name)
    #         continue

    #     for msg in msg_list:
    #         if msg == msg_name:
    #             is_incl = 1
    #             break
    #     if not is_incl:
    #         msg_list.append(msg_name)

        # Добавляем уникальные сообщения и их частоты
    for msg_id, data in message_frequencies.items():
        if data['isDBC']:
            if msg_list.count == 0:
                msg_list.append(msg_id)
                continue

            for msg in msg_list:
                if msg == msg_id:
                    is_incl = 1
                    break
            if not is_incl:
                msg_list.append(msg_id)
            is_incl = 0

signal_window = gui_window(name = 'RecievedSignals',menu_label='RecievedSignals', window_tag = 'RecievedWindow', 
                           setup_callback=setup_dbc_signals_window,update_callback=update_dbc_signals_window2)