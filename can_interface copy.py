import can
import cantools
from threading import Event
from queue import Queue
from collections import defaultdict
from can.interfaces.vector import VectorBus

class CanInterface:


    db = None
    bus = None

    message_queue = Queue()

    stop_event = Event()

    message_frequencies = defaultdict(lambda: {'count': 0, 'frequency': 0, 'dlc': 0, 'data': [], 'isDBC': 0, 'ParsedSignals' : [], "DBC_name":""})
    parsed_signals = defaultdict(list)
    available_signals = defaultdict(list)
    plot_signals = []
    signal_data = defaultdict(lambda: {'time': [], 'value': []})

    configs = None

    init_time = 0

    def __parse_signals(self, message: can.Message):
        try:
            decoded_message = self.db.decode_message(message.arbitration_id, message.data)
            self.message_frequencies[message.arbitration_id]['isDBC'] = True
            ms = self.db.get_message_by_frame_id(message.arbitration_id)
            self.message_frequencies[message.arbitration_id]['DBC_name'] = ms.name
            self.message_frequencies[message.arbitration_id]['ParsedSignals'] = decoded_message

            return decoded_message

        except Exception as e:
            self.message_frequencies[message.arbitration_id]['isDBC'] = False


    def __update_plot_data(self, dec_msg, timestamp: float):

        for signal_name in self.plot_signals: # из расчета, что сигналов на графике намного меньше чем сигналы в сообщении
            if signal_name in dec_msg:
                self.signal_data[signal_name]['time'].append(timestamp- self.init_time)
                self.signal_data[signal_name]['value'].append(dec_msg[signal_name])


    def __get_msg(self, bus: can.interface, last_timestamps: dict, timeout = 1.0):
        """Checking for msgs from bus interface"""

        message = bus.recv(timeout = timeout)  # Установите таймаут для предотвращения зависания
        if message:
            timestamp = message.timestamp
            if self.init_time == 0:
                self.init_time = timestamp

            if message.arbitration_id not in self.last_timestamps:
                self.last_timestamps[message.arbitration_id] = timestamp

            # Обновление частоты получения сообщений
            time_diff = timestamp - self.last_timestamps[message.arbitration_id]
            self.last_timestamps[message.arbitration_id] = timestamp
            if message.arbitration_id not in self.message_frequencies:
                self.message_frequencies[message.arbitration_id] = {'count': 1, 'frequency': 0, 'dlc': message.dlc, 'data': message.data,'ParsedSignals' : [],"DBC_name":""}
            else:
                self.message_frequencies[message.arbitration_id]['count'] += 1
                try:
                    self.message_frequencies[message.arbitration_id]['frequency'] = time_diff*1000 # почему тыс?
                except Exception as e:
                    self.message_frequencies[message.arbitration_id]['frequency'] = 0

                self.message_frequencies[message.arbitration_id]['data'] = message.data

            return message, timestamp



            


    def receive_can_messages(self):

        last_timestamps = {}

        while not self.stop_event.is_set(): # специально ли прослушка без подключения интерфейса?
            if self.bus:
                try:
                    message, timestamp = self.__get_msg(self.bus, last_timestamps)
                    # Распарсивание сигналов
                    decoded_message = self.__parse_signals(message)
                    self.__update_plot_data(decoded_message, timestamp)
                    self.message_queue.put(message)

                except can.CanError:
                    print("CAN interface error. Check if the adapter is connected.")
                    self.stop_event.set()  # Останавливаем поток, если ошибка интерфейса
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    self.stop_event.set()  # Останавливаем поток в случае неожиданной ошибки
                    
                """if deinit_event:
                    deinit_event = False
                    bus.shutdown()
                    bus = None
                    # message_frequencies = defaultdict(lambda: {'count': 0, 'frequency': 0, 'dlc': 0, 'data': [], 'isDBC': 0})
                    # parsed_signals = {}"""
            
            else: self.stop_event.set()
        
        self.bus.shutdown()
        self.bus = None



    def initialize_can_bus(self, interface, channel, bitrate = 500000):
        
        if not self.bus:
            if interface == 'vector':
                try:
                    
                    configs = can.detect_available_configs('vector')
                    cfg = configs[0]
                    VectorBus.set_application_config(app_name='python-can', app_channel=0, **cfg)
                    cfg = configs[1]
                    VectorBus.set_application_config(app_name='python-can', app_channel=1, **cfg)

                    self.bus = can.interface.Bus(bustype=interface, channel=channel, bitrate=bitrate, app_name='python-can')
                   
                except Exception as e:
                    raise  ValueError(e)

            elif interface == 'pcan':
                try:
                    self.bus = can.interface.Bus(bustype=interface, channel=channel, bitrate=bitrate)
                except Exception as e:
                    raise  ValueError(f"Failed to connect to CAN interface: {e}")
            else:
                    raise  ValueError(f"Failed to connect to CAN interface: {e}")

    def deinit_bus():
        global deinit_event
        deinit_event = True

    def detect_avalible_config(filterconfig: tuple[str] = ("vector","pcan")):

        configs = can.detect_available_configs(filterconfig)

        return configs
    
    def connect_db(self, filepath):

        dbc_file = filepath

        try:
            self.db = cantools.database.load_file(dbc_file)
        except Exception as e:
            raise  ValueError(f"err {e}")


"""
    def send_can_message(self, sender, app_data, user_data):
        print(sender,app_data,user_data)
        if self.bus:
            try:
                arbitration_id = int(dpg.get_value('MessageID'), 16)
                data = bytearray.fromhex(dpg.get_value('MessageData'))
                message = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
                self.bus.send(message)
                print(f"Sent message: {message}")
            except Exception as e:
                print(f"Failed to send message: {e}")
        else:
            print("CAN interface is not available.")
"""