import can
import threading
import cantools

from collections import defaultdict
from can.interfaces.vector import VectorBus
from collections import deque # bufer, max = auto deletion first 

class CANDriver:
    def __init__(self, interface, channel, bitrate=500000, app_name = None):

       if app_name is None:
            self.bus = can.Bus(
                interface=interface, #DeprecationWarning: The 'bustype' argument is deprecated since python-can v4.2.0
                channel=channel,
                bitrate=bitrate
            )
       else:
           self.bus = can.Bus(
                interface=interface, #DeprecationWarning: The 'bustype' argument is deprecated since python-can v4.2.0
                channel=channel,
                bitrate=bitrate,
                app_name = app_name
            )

    def recv(self, timeout=1):
        return self.bus.recv(timeout)

    def close(self):
        self.bus.shutdown()

class DBCDecoder:

    def __init__(self, dbc_path = None):
        self.__db = None
        if dbc_path:
            self.set_db(dbc_path)



    def decode(self, msg):
        try:
            decoded = self.__db.decode_message(msg.arbitration_id, msg.data)
            name = self.__db.get_message_by_frame_id(msg.arbitration_id).name
            return name, decoded
        except:
            return None, None
    
    def set_db(self, path):
        try:
            self.__db = cantools.database.load_file(path)

        except Exception as error:
            raise  ValueError(f"Can't load dbc file correctly: {error}")
        



class CANData:


    def __init__(self, msg_log_max_size = 100, plot_data_max_size = 1000):
        self.lock = threading.Lock()

        self.messages = {}
        self.msg_log = deque(maxlen=msg_log_max_size)
        self.signals = defaultdict(list)
        self.signal_plot = defaultdict(lambda: {"time": deque(maxlen=plot_data_max_size), "value": deque(maxlen=plot_data_max_size)})

    def update_message(self, msg_id, data, dlc, receive_msg_timestamp, is_dbc=False, decoded=None):

        with self.lock:

            if msg_id not in self.messages:
                self.messages[msg_id] = {
                    "count": 0,
                    "receive_time": receive_msg_timestamp,
                    "frequency": 0,
                    "dlc": 0,
                    "data": None,
                    "is_dbc": False,
                    "decoded": {}
                }

            else:

                msg = self.messages[msg_id]

                msg["count"] += 1
                msg["frequency"] = receive_msg_timestamp - msg["receive_time"]
                msg['receive_time'] = receive_msg_timestamp
                msg["dlc"] = dlc
                msg["data"] = data
                msg["is_dbc"] = is_dbc
                msg["decoded"] = decoded or {}
            

    def update_signal(self, name, t, value):
        with self.lock:
            self.signal_plot[name]["time"].append(t)
            self.signal_plot[name]["value"].append(value)

    def get_messages_snapshot(self):
        with self.lock:
            return dict(self.messages)
    
    def get_trace_snapshot(self):
        with self.lock:
            return list(self.msg_log)




class CANScanner:

    def __init__(self, driver, decoder, data_store):

        self.driver = driver
        self.decoder = decoder
        self.data_store = data_store
        self.running = False
        self.init_time = None
        self.stop_event = threading.Event()

    def start(self):

        while not self.stop_event.is_set():
            msg = self.driver.recv(1)
            
            if not msg:
                continue

            t = msg.timestamp
            if self.init_time is None:
                self.init_time = t

            self.data_store.msg_log.append(msg)
            
            
            name, decoded = self.decoder.decode(msg)



            is_dbc = False if name is None else True
            self.data_store.update_message(msg.arbitration_id, msg.data, msg.dlc, t, is_dbc, decoded)

            if decoded:
                for sig, val in decoded.items():
                    self.data_store.update_signal(sig, t - self.init_time, val)

    def stop(self):
        self.stop_event.set()




class CANManager:

    

    def __init__(self, data: CANData):
        self.can_data = data
        self.scan_available_configs()
        self.thread = None

    
        

    def scan_available_configs(self, interfaces=("vector", "pcan")):
        self.configs = can.detect_available_configs(interfaces=interfaces)
    
    def get_configs(self):
        if self.configs is None: self.scan_available_configs()

        return self.configs
    
    def connect(self, interface: str, channel: int, dbc_path = None, bitrate: int = 500000):

        if self.thread and self.thread.is_alive():
            raise RuntimeError("CAN connection already active")

        if interface == "vector":
            for config in self.get_configs():
                if config['interface'] == "vector":
                    VectorBus.set_application_config(app_name='python-can', app_channel=int(config["channel"]), **config)

            self.driver = CANDriver(interface = interface, channel = channel, bitrate = bitrate, app_name='python-can')
        
        else:
            self.driver = CANDriver(interface = interface, channel = channel, bitrate = bitrate)

        decoder = DBCDecoder(dbc_path)
        
        self.scanner = CANScanner(self.driver, decoder, self.can_data)

        self.thread = threading.Thread(
            target = self.scanner.start,
            daemon=True
        )

        self.thread.start()

    def get_connection_status(self):

        return True if self.thread else False

    def disconnect(self):

        if not self.thread: return

        self.scanner.stop()
        

        if self.thread:
            self.thread.join()
        
        self.driver.close()
        self.thread = None
        self.driver = None
        self.scanner = None


        

        
    
