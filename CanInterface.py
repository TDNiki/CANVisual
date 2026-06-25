import can
import threading
import cantools

from collections import defaultdict

class CANDriver:
    def __init__(self, interface, channel, bitrate=500000):
        self.bus = can.interface.Bus(
            bustype=interface,
            channel=channel,
            bitrate=bitrate
        )

    def recv(self, timeout=0.1):
        return self.bus.recv(timeout)

    def close(self):
        self.bus.shutdown()

class DBCDecoder:

    def __init__(self, db):
        self.db = db

    def decode(self, msg):
        try:
            decoded = self.db.decode_message(msg.arbitration_id, msg.data)
            name = self.db.get_message_by_frame_id(msg.arbitration_id).name
            return name, decoded
        except:
            return None, None
        



class CANData:

    def __init__(self):
        self.lock = threading.Lock()

        self.messages = {}
        self.signals = defaultdict(list)
        self.signal_plot = defaultdict(lambda: {"time": [], "value": []})

    def update_message(self, msg_id, data, dlc, frequency=0, dbc_name=None, decoded=None):

        with self.lock:

            if msg_id not in self.messages:
                self.messages[msg_id] = {
                    "count": 0,
                    "frequency": 0,
                    "dlc": 0,
                    "data": None,
                    "dbc_name": "",
                    "decoded": {}
                }

            msg = self.messages[msg_id]

            msg["count"] += 1
            msg["frequency"] = frequency
            msg["dlc"] = dlc
            msg["data"] = data
            msg["dbc_name"] = dbc_name or ""
            msg["decoded"] = decoded or {}

    def update_signal(self, name, t, value):
        with self.lock:
            self.signal_plot[name]["time"].append(t)
            self.signal_plot[name]["value"].append(value)




class CANScanner:

    def __init__(self, driver, decoder, data_store):

        self.driver = driver
        self.decoder = decoder
        self.data_store = data_store
        self.running = False
        self.init_time = None

    def start(self):
        self.running = True
        while self.running:
            msg = self.driver.recv(timeout=1.0)
            if not msg:
                continue

            t = msg.timestamp
            if self.init_time is None:
                self.init_time = t

            

            name, decoded = self.decoder.decode(msg)
            self.data_store.update_message(msg.arbitration_id, msg.data, msg.dlc, name, decoded)

            if decoded:
                for sig, val in decoded.items():
                    self.data_store.update_signal(sig, t - self.init_time, val)

    def stop(self):
        self.running = False




class CANManager:

    

    def __init__(self, dbc_path = None):
        if dbc_path is not None:
            try:
                self.db = cantools.database.load_file(dbc_path)
            except Exception as error:
                raise  ValueError(f"Can't load dbc file correctly: {error}")
        
        self.scan_available_configs()
        self.thread = None
        

    def scan_available_configs(self, interfaces=("vector", "pcan")):
        self.configs = can.detect_available_configs(interfaces=interfaces)
    
    def get_configs(self):
        if self.configs is None: self.scan_available_configs()

        return self.configs
    
    def connect(self, interface: str, channel, bitrate: int = 500000):

        if self.thread and self.thread.is_alive():
            raise RuntimeError("CAN connection already active")

        self.driver = CANDriver(interface = interface, channel = channel, bitrate = bitrate)

        decoder = DBCDecoder(self.db)
        datastore = CANData()
        
        self.scanner = CANScanner(self.driver, decoder, datastore)

        self.thread = threading.Thread(
            target = self.scanner.start,
            daemon=True
        )

        self.thread.start()

    def disconnect(self):

        self.scanner.stop()

        if self.thread:
            self.thread.join(timeout=2)
        
        self.driver.close()


        

        
    
