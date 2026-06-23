import can
import cantools
import dearpygui.dearpygui as dpg
from threading import Thread, Event
import time
import queue
from collections import defaultdict
from math import sin

# creating data
sindatax = []
sindatay = []
for i in range(0, 500):
    sindatax.append(i / 1000)
    sindatay.append(0.5 + 0.5 * sin(50 * i / 1000))

# Загрузка DBC файла
dbc_file = 'C:\\Camozzi\\j1939(Camozzi)new251.dbc'
db = cantools.database.load_file(dbc_file)

# Настройка PCAN
# can_interface = 'pcan'
# channel='PCAN_USBBUS1'
from can.interfaces.vector import VectorBus

import can
from can.interfaces.vector import VectorBus

configs = can.detect_available_configs(interfaces=['vector'])
cfg = configs[0]
VectorBus.set_application_config(app_name='python-can', app_channel=0, **cfg)

can_interface = 'vector'
channel = 0

bus = can.interface.Bus(bustype='vector', channel=0, bitrate=500000, app_name='python-can')

# try:
#     bus = can.interface.Bus(bustype=can_interface, channel=channel, bitrate=250000)
# except Exception as e:
#     print(f"Failed to connect to CAN interface: {e}")
#     bus = None

# Очереди для передачи сообщений между потоками
message_queue = queue.Queue()
stop_event = Event()
update_interval = 0.1  # Интервал обновления по умолчанию в секундах
message_frequencies = defaultdict(lambda: {'count': 0, 'frequency': 0, 'dlc': 0, 'data': [], 'isDBS': False})  # Частоты сообщений
parsed_signals = {}
available_signals = defaultdict(list)  # Словарь для хранения доступных сигналов для графиков
plot_signals = []  # Список для хранения выбранных сигналов для графиков
signal_data = defaultdict(lambda: {'time': [], 'value': []})  # Данные сигналов для графиков

def receive_can_messages():
    global bus, message_frequencies, parsed_signals, available_signals
    last_timestamps = {}

    while not stop_event.is_set():
        try:
            message = bus.recv(timeout=1.0)  # Установите таймаут для предотвращения зависания
            if message:
                timestamp = time.time()
                if message.arbitration_id not in last_timestamps:
                    last_timestamps[message.arbitration_id] = timestamp

                # Обновление частоты получения сообщений
                time_diff = timestamp - last_timestamps[message.arbitration_id]
                last_timestamps[message.arbitration_id] = timestamp
                if message.arbitration_id not in message_frequencies:
                    message_frequencies[message.arbitration_id] = {'count': 1, 'frequency': 0, 'dlc': message.dlc, 'data': message.data}
                else:
                    message_frequencies[message.arbitration_id]['count'] += 1
                    try:
                        message_frequencies[message.arbitration_id]['frequency'] = 1 / time_diff
                    except Exception as e:
                        message_frequencies[message.arbitration_id]['frequency'] = 0
                    message_frequencies[message.arbitration_id]['data'] = message.data

                message_frequencies[message.arbitration_id]['isDBC'] = False
                # Распарсивание сигналов
                try:
                    
                    decoded_message = db.decode_message(message.arbitration_id, message.data)
                    message_frequencies[message.arbitration_id]['isDBC'] = True
                    parsed_signals[message.arbitration_id] = decoded_message
                    for signal_name, signal_value in decoded_message.items():
                        available_signals[signal_name].append((message.arbitration_id, signal_value))
                        if signal_name in plot_signals:
                            signal_data[signal_name]['time'].append(timestamp)
                            signal_data[signal_name]['value'].append(signal_value)
                    refresh_signal_list()
                except Exception as e:
                    print(f"Decoding error: {e}")
                    # message_frequencies[message.arbitration_id]['isDBC'] = False

                message_queue.put(message)
        except can.CanError:
            print("CAN interface error. Check if the adapter is connected.")
            stop_event.set()  # Останавливаем поток, если ошибка интерфейса
        except Exception as e:
            print(f"Unexpected error: {e}")
            stop_event.set()  # Останавливаем поток в случае неожиданной ошибки

def send_can_message(sender, app_data, user_data):
    if bus:
        try:
            arbitration_id = int(dpg.get_value('MessageID'), 16)
            data = bytearray.fromhex(dpg.get_value('MessageData'))
            message = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
            bus.send(message)
            print(f"Sent message: {message}")
        except Exception as e:
            print(f"Failed to send message: {e}")
    else:
        print("CAN interface is not available.")

def update_received_messages_window():
    # Удаляем старые строки, чтобы избежать дублирования
    rows = dpg.get_item_children('ReceivedMessagesTable', 1)
    for row in rows:
        dpg.delete_item(row)

    # Добавляем уникальные сообщения и их частоты
    for msg_id, data in message_frequencies.items():
        if data['isDBC']:
            color=[255, 255, 200, 255]
        else:
            color=[255, 255, 255, 255]

        with dpg.table_row(parent='ReceivedMessagesTable'):
            dpg.add_text(hex(msg_id),color=color)
            dpg.add_text(str(data['count']))
            dpg.add_text(f"{data['frequency']:.2f}")
            dpg.add_text(str(data['dlc']))
            dpg.add_text(' '.join(f"{byte:02x}" for byte in data['data']))

def update_signals_window():
    # Удаляем старые строки, чтобы избежать дублирования
    rows = dpg.get_item_children('SignalsTable', 1)
    for row in rows:
        dpg.delete_item(row)

    # Добавляем распарсенные сигналы
    for msg_id, signals in parsed_signals.items():
        for signal_name, signal_value in signals.items():
            with dpg.table_row(parent='SignalsTable'):
                dpg.add_text(hex(msg_id))
                d=dpg.add_text(signal_name)
                dpg.add_text(f"{signal_value:.2f}")  # Значение сигнала
                with dpg.drag_payload(parent=d, drag_data=signal_name, payload_type="plotting"):
                    dpg.add_text(signal_name)
                    dpg.add_simple_plot(label="", default_value=sindatay)

def refresh_signal_list():
    # Обновляем выпадающий список доступных сигналов
    dpg.configure_item('SignalCombo', items=list(available_signals.keys()))

def add_signal_to_plot_drop(sender, app_data, user_data):
    signal_name = str(app_data)
    if signal_name and signal_name not in plot_signals:
        plot_signals.append(signal_name)
        dpg.add_line_series(signal_data[signal_name]['time'], signal_data[signal_name]['value'], label=signal_name, parent="y_axis",tag=signal_name)
        dpg.add_button(label="Delete", parent=dpg.last_item(), callback=lambda: remove_signal_from_plot_d(signal_name))

        if signal_name not in signal_data:
            signal_data[signal_name] = {'time': [], 'value': []}
        dpg.add_text(f"Signal '{signal_name}' added to plot.", parent='PlotSignalsStatus')
        refresh_signal_list()

def add_signal_to_plot(sender, app_data, user_data):
    signal_name = dpg.get_value('SignalCombo')
    if signal_name and signal_name not in plot_signals:
        plot_signals.append(signal_name)
        dpg.add_line_series(signal_data[signal_name]['time'], signal_data[signal_name]['value'], label=signal_name, parent="y_axis",tag=signal_name)
        dpg.add_button(label="Delete", parent=dpg.last_item(), callback=lambda: remove_signal_from_plot_d(signal_name))

        if signal_name not in signal_data:
            signal_data[signal_name] = {'time': [], 'value': []}
        dpg.add_text(f"Signal '{signal_name}' added to plot.", parent='PlotSignalsStatus')
        refresh_signal_list()

def remove_signal_from_plot(sender, app_data, user_data):
    signal_name = dpg.get_value('SignalCombo')
    if signal_name and signal_name in plot_signals:
        plot_signals.remove(signal_name)
        dpg.delete_item(signal_name)
        dpg.add_text(f"Signal '{signal_name}' removed from plot.", parent='PlotSignalsStatus')
        refresh_signal_list()

def remove_signal_from_plot_d(sender):
    signal_name = sender
    if signal_name and signal_name in plot_signals:
        plot_signals.remove(signal_name)
        dpg.delete_item(signal_name)
        dpg.add_text(f"Signal '{signal_name}' removed from plot.", parent='PlotSignalsStatus')
        refresh_signal_list()

def update_plot():
    x_wight = 500
    dpg.delete_item('SignalPlot', children_only=True)
    for signal_name in plot_signals:
        if signal_data[signal_name]['time']:
            try:
                # print('')
                lend = len(signal_data[signal_name]['time'])
                if lend > x_wight:
                    start=lend-x_wight
                else:
                    start=0
                data_t = signal_data[signal_name]['time'][start:lend]
                data_v = signal_data[signal_name]['value'][start:lend]
                # data_t = signal_data[signal_name]['time']
                # data_v = signal_data[signal_name]['value']
                
                dpg.set_value(signal_name, [data_t, data_v])
                # dpg.fit_axis_data("time")

            except Exception as e:
                print(f"Error adding line series for {signal_name}: {e}")


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



def setup_gui():
    global update_interval

    # Верхний бар для открытия окон
    with dpg.viewport_menu_bar():
        with dpg.menu(label="Windows"):
            dpg.add_menu_item(label="Received Messages", callback=lambda: dpg.show_item('ReceivedMessagesWindow'))
            dpg.add_menu_item(label="Signals", callback=lambda: dpg.show_item('SignalsWindow'))
            dpg.add_menu_item(label="Send Message", callback=lambda: dpg.show_item('SendMessageWindow'))
            dpg.add_menu_item(label="Plot Signals", callback=lambda: dpg.show_item('PlotSignalsWindow'))

    # Окно для полученных сообщений
    with dpg.window(label='Received Messages', width=1000, height=300, tag='ReceivedMessagesWindow', pos=(0, 0),  show=True):
        dpg.add_text('Received Messages')
        with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True, row_background=True, tag='ReceivedMessagesTable', sortable=True, callback=sort_callback):
            dpg.add_table_column(label='ID')
            dpg.add_table_column(label='Count')
            dpg.add_table_column(label='Frequency (Hz)')
            dpg.add_table_column(label='DLC')
            dpg.add_table_column(label='Data (Hex)')

    # Окно для сигналов
    with dpg.window(label='Signals', width=1000, height=300, tag='SignalsWindow', pos=(0, 0), show=False):
        dpg.add_text('Signals')
        with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True, row_background=True, tag='SignalsTable'):
            dpg.add_table_column(label='Message ID')
            dpg.add_table_column(label='Signal Name')
            dpg.add_table_column(label='Value')

    # Окно для отправки сообщений
    with dpg.window(label='Send Message', width=1000, height=100, tag='SendMessageWindow', pos=(0, 0), show=False):
        dpg.add_text('Send Message')
        dpg.add_input_text(label='ID', tag='MessageID')
        dpg.add_input_text(label='Data', tag='MessageData')
        dpg.add_button(label='Send', callback=send_can_message)
        dpg.add_input_float(label='Update Interval (s)', default_value=1.0, tag='UpdateInterval', callback=lambda sender, app_data, user_data: set_update_interval(dpg.get_value(sender)))

    # Окно для графиков сигналов
    with dpg.window(label='Plot Signals', width=1000, height=600, tag='PlotSignalsWindow', pos=(0, 0), show=False):
        # dpg.add_text('Plot Signals')
        # dpg.add_combo(label='Available Signals', items=[], tag='SignalCombo')
        # dpg.add_button(label='Add Signal', callback=add_signal_to_plot)
        # dpg.add_button(label='Remove Signal', callback=remove_signal_from_plot)
        
        # dpg.add_text('Plot Status:', tag='PlotSignalsStatus')
        # dpg.add_plot(label='Signal Plot', height=-1, width=-1, tag='SignalPlot')
        with dpg.group(horizontal=True):
            dpg.add_button(label="fit x", callback=lambda: dpg.fit_axis_data("time"))
            dpg.add_button(label="fit y", callback=lambda: dpg.fit_axis_data("y_axis"))

        with dpg.plot(label="Signal Plot", height=-1, width=-1,no_title=True, crosshairs=True, drop_callback=add_signal_to_plot_drop, payload_type="plotting"):
            # optionally create legend
            dpg.add_plot_legend(outside=True)

            # REQUIRED: create x and y axes
            dpg.add_plot_axis(dpg.mvXAxis, label="time",tag="time")
            dpg.add_plot_axis(dpg.mvYAxis, label="val", tag="y_axis")

            dpg.add_drag_line(label="dline2", color=[255, 255, 0, 255], vertical=False, default_value=-2)
            # series belong to a y axis
          

def set_update_interval(value):
    global update_interval
    update_interval = float(value)

def main():
    setup_gui()

    # Запуск потока для приема сообщений
    receive_thread = Thread(target=receive_can_messages, daemon=True)
    receive_thread.start()

    last_update_time = time.time()
    while dpg.is_dearpygui_running():
        current_time = time.time()
        if current_time - last_update_time >= update_interval:  # Обновление интерфейса согласно частоте
            update_received_messages_window()
            update_signals_window()
            # update_plot()
            last_update_time = current_time
        update_plot()
        dpg.render_dearpygui_frame()

    stop_event.set()  # Убедитесь, что поток остановлен при выходе из программы
    receive_thread.join()
    dpg.destroy_context()

if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title='CAN Analyzer', width=1200, height=800, clear_color=(0, 1, 1, 1))
    dpg.setup_dearpygui()
    dpg.show_viewport()
    main()
