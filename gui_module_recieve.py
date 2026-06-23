import dearpygui.dearpygui as dpg
from window_class import gui_window
from can_interface import message_frequencies,message_queue
from datetime import datetime

trace_list = []
trace_auto_scroll = False

def setup_received_message_window(sender):
    # dpg.set_item
    with dpg.tab_bar():

        with dpg.tab(label="Rates"):

            with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit, borders_innerH=True, borders_outerH=True, 
                        borders_innerV=True, borders_outerV=True, row_background=True, tag='ReceivedMessagesTable', sortable=True, callback=sort_callback,
                        freeze_rows=1, freeze_columns=1,scrollY=True, scrollX=True, height=-1):
                
                dpg.add_table_column(label='ID',width_fixed=True)
                dpg.add_table_column(label='Count',width_fixed=True)
                dpg.add_table_column(label='Rate',width_fixed=True)
                dpg.add_table_column(label='DLC',width_fixed=True)
                dpg.add_table_column(label='Data (Hex)',width_stretch=True, init_width_or_weight=0.0)

        with dpg.tab(label="Trace"):
            dpg.add_checkbox(label="auto scroll",callback=set_auto_scroll)

            with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit, borders_innerH=True, borders_outerH=True, 
                        borders_innerV=True, borders_outerV=True, row_background=False, tag='ReceivedMessagesTrace',freeze_rows=1, freeze_columns=1,
                        scrollY=True, scrollX=True, height=-1):
                dpg.add_table_column(label='Timestamp',width_fixed=True)
                dpg.add_table_column(label='ID',width_fixed=True)
                dpg.add_table_column(label='DLC',width_fixed=True)
                dpg.add_table_column(label='Data (Hex)',width_stretch=True, init_width_or_weight=0.0)

def update_received_messages_window(sender):
    global trace_list, trace_auto_scroll

    # Удаляем старые строки, чтобы избежать дублирования
    rows = dpg.get_item_children('ReceivedMessagesTable', 1)
    for row in rows:
        dpg.delete_item(row)

    # Добавляем уникальные сообщения и их частоты
    for msg_id, data in message_frequencies.items():
        if data['isDBC']:
            color=[150, 200, 255, 255]
        else:
            color=[255, 255, 255, 255]

        with dpg.table_row(parent='ReceivedMessagesTable'):
            # dpg.add_text(hex(msg_id))
            dpg.add_text(f"{msg_id:08X}", color=color)
            dpg.add_text(str(data['count']))
            dpg.add_text(f"{data['frequency']:.2f}")
            dpg.add_text(str(data['dlc']))
            dpg.add_text(' '.join(f"{byte:02X}" for byte in data['data']))

    rows = dpg.get_item_children('ReceivedMessagesTrace', 1)
    for row in rows:
        dpg.delete_item(row)
    # Добавляем новые строки из очереди
    refresh_trace_list()
    for msg in trace_list:

        with dpg.table_row(parent='ReceivedMessagesTrace'):
            # dpg.add_text(str(msg.timestamp))
            dpg.add_text(datetime.fromtimestamp(msg.timestamp).strftime('%H:%M:%S.%f')[:-3])
            dpg.add_text(f"{msg.arbitration_id:08X}")
            dpg.add_text(str(msg.dlc))
            dpg.add_text(' '.join(f"{byte:02x}" for byte in msg.data))
    if trace_auto_scroll:
        dpg.set_y_scroll('ReceivedMessagesTrace', -1)

 

recieve_window = gui_window(name = 'RecievedMessages',menu_label='RecievedMessages', window_tag = 'SignalsWindow', 
                            setup_callback=setup_received_message_window, update_callback=update_received_messages_window)

def refresh_trace_list():
    global trace_list

    while not message_queue.empty():
        msg = message_queue.get()

        trace_list.append(msg)

        if len(trace_list) > 100:
            trace_list.pop(0)

        pass

def set_auto_scroll(sender):
    global trace_auto_scroll
    if dpg.get_value(sender):
        trace_auto_scroll = True
    else:
        trace_auto_scroll = False

def sort_callback(sender, sort_specs):

    # sort_specs scenarios:
    #   1. no sorting -> sort_specs == None
    #   2. single sorting -> sort_specs == [[column_id, direction]]
    #   3. multi sorting -> sort_specs == [[column_id, direction], [column_id, direction], ...]
    #
    # notes:
    #   1. direction is ascending if == 1
    #   2. direction is ascending if == -1

    # no sorting case
    if sort_specs is None: return

    rows = dpg.get_item_children(sender, 1)

    # create a list that can be sorted based on first cell
    # value, keeping track of row and value used to sort
    sortable_list = []
    for row in rows:
        first_cell = dpg.get_item_children(row, 1)[0]
        sortable_list.append([row, dpg.get_value(first_cell)])

    def _sorter(e):
        return e[1]

    sortable_list.sort(key=_sorter, reverse=sort_specs[0][1] < 0)

    # create list of just sorted row ids
    new_order = []
    for pair in sortable_list:
        new_order.append(pair[0])

    dpg.reorder_items(sender, 1, new_order)