import can
import cantools
import time
from threading import Event
from queue import Queue
from collections import defaultdict
import logging
# Настройка CAN интерфейса
# dbc_file = 'C:\\Camozzi\\j1939(Camozzi)new251.dbc'
log = logging.getLogger("db")
# db = cantools.database.load_file(dbc_file)

db = None
bus = None
# Очереди и переменные для работы с CAN
message_queue = Queue()
stop_event = Event()
message_frequencies = defaultdict(lambda: {'count': 0, 'frequency': 0, 'dlc': 0, 'data': [], 'isDBC': 0, 'ParsedSignals' : [], "DBC_name":""})
parsed_signals = defaultdict(list)
available_signals = defaultdict(list)
plot_signals = []
signal_data = defaultdict(lambda: {'time': [], 'value': []})

configs = None

deinit_event = False

# init_time = time.time()
init_time = 0

def initialize_can_bus(interface,channel,bitrate = 500):
    global bus
    
    if not bus:
        if interface == 'vector':
            try:
                from can.interfaces.vector import VectorBus

                configs = can.detect_available_configs(interfaces=['vector'])
                cfg = configs[0]
                VectorBus.set_application_config(app_name='python-can', app_channel=0, **cfg)
                cfg = configs[1]
                VectorBus.set_application_config(app_name='python-can', app_channel=1, **cfg)

                # can_interface = 'vector'
                # channel = 0

                bus = can.interface.Bus(bustype=interface, channel=channel, bitrate=bitrate, app_name='python-can')
                print(f"connected")
            except Exception as e:
                print(f"Failed to connect to CAN interface: {e}")
                raise  ValueError(e)

        elif interface == 'pcan':
            try:
                bus = can.interface.Bus(bustype=interface, channel=channel, bitrate=bitrate)
            except Exception as e:
                print(f"Failed to connect to CAN interface: {e}")
                raise  ValueError(e)
        else:
                print(f"Failed to connect to CAN interface: {e}")
                raise  ValueError(e)

def deinit_bus():
    global deinit_event
    deinit_event = True

def detect_avalible_config():
    # global configs
    configs = can.detect_available_configs(("vector","pcan"))
    return configs
    
def connect_db(filepath):
    global db

    dbc_file = filepath

    try:
        db = cantools.database.load_file(dbc_file)
    except Exception as e:
        print(f"err {e}")
        raise  ValueError(e)

def receive_can_messages():
    global bus, message_frequencies, parsed_signals, available_signals, deinit_event,init_time
    last_timestamps = {}

    while not stop_event.is_set():
        if bus:
            try:
                message = bus.recv(timeout=1.0)  # Установите таймаут для предотвращения зависания
            
                if message:
                    # timestamp = time.time()
                    timestamp = message.timestamp
                    if init_time == 0:
                        init_time = timestamp
                    if message.arbitration_id not in last_timestamps:
                        last_timestamps[message.arbitration_id] = timestamp

                    # Обновление частоты получения сообщений
                    time_diff = timestamp - last_timestamps[message.arbitration_id]
                    last_timestamps[message.arbitration_id] = timestamp
                    if message.arbitration_id not in message_frequencies:
                        message_frequencies[message.arbitration_id] = {'count': 1, 'frequency': 0, 'dlc': message.dlc, 'data': message.data,'ParsedSignals' : [],"DBC_name":""}
                    else:
                        message_frequencies[message.arbitration_id]['count'] += 1
                        try:
                            message_frequencies[message.arbitration_id]['frequency'] = time_diff*1000
                        except Exception as e:
                            message_frequencies[message.arbitration_id]['frequency'] = 0
                        message_frequencies[message.arbitration_id]['data'] = message.data

                    # Распарсивание сигналов
                    try:
                        decoded_message = db.decode_message(message.arbitration_id, message.data)
                        message_frequencies[message.arbitration_id]['isDBC'] = True
                        ms = db.get_message_by_frame_id(message.arbitration_id)
                        message_frequencies[message.arbitration_id]['DBC_name'] = ms.name
                        message_frequencies[message.arbitration_id]['ParsedSignals'] = decoded_message

                        for signal_name, signal_value in decoded_message.items():
                            # available_signals[signal_name].append((message.arbitration_id, signal_value))
                            if signal_name in plot_signals:
                                signal_data[signal_name]['time'].append(timestamp-init_time)
                                signal_data[signal_name]['value'].append(signal_value)

                    except Exception as e:
                        message_frequencies[message.arbitration_id]['isDBC'] = False
                        # print(f"Decoding error: {e}")

                    message_queue.put(message)
            except can.CanError:
                print("CAN interface error. Check if the adapter is connected.")
                stop_event.set()  # Останавливаем поток, если ошибка интерфейса
            except Exception as e:
                print(f"Unexpected error: {e}")
                stop_event.set()  # Останавливаем поток в случае неожиданной ошибки
                
            if deinit_event:
                deinit_event = False
                bus.shutdown()
                bus = None
                # message_frequencies = defaultdict(lambda: {'count': 0, 'frequency': 0, 'dlc': 0, 'data': [], 'isDBC': 0})
                # parsed_signals = {}

def send_can_message(sender, app_data, user_data):
    print(sender,app_data,user_data)
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
