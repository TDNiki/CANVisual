import can
import threading
import cantools
import numpy as np

from collections import defaultdict
from can.interfaces.vector import VectorBus
from collections import deque# bufer, max = auto deletion first
from queue import Queue


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
    
    def send_msg(self, msg):
        self.bus.send(msg)

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


    def __init__(self, msg_log_max_size = 100, plot_data_max_sec = 60):
        """
        Динамически формируем количество точек в зависимости от времени. То есть в оперативке будем хранить 60 секунд информации
        """
        self.lock = threading.Lock()
        self.__plot_data_max_sec = plot_data_max_sec
        self.messages = {}
        self.msg_log = deque(maxlen=msg_log_max_size)
        self.signal_plot = {}
        self.__static_mode = False # using this mode for log static data
        self.static_log_path = None

    def is_static_mode(self): return self.__static_mode
    
    def enable_static_mode(self, log_path: str):
        self.__static_mode = True
        self.static_log_path = log_path
    
    def disable_static_mode(self):
        self.__static_mode = False
        self.static_log_path = None

    def update_message(self, msg_id, data, dlc, receive_msg_timestamp, dbc_name:str = None, is_dbc=False, decoded=None):
        if self.__static_mode: raise Exception("Func is not allowed to use in static mode")
        with self.lock:

            if msg_id not in self.messages:
                self.messages[msg_id] = {
                    "count": 0,
                    "receive_time": receive_msg_timestamp,
                    "frequency": 0,
                    "dlc": 0,
                    "data": None,
                    "is_dbc": False,
                    "dbc_name": dbc_name or "",
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
                msg["dbc_name"] = dbc_name or ""
                msg["decoded"] = decoded or {}
            

    def update_signal(self, msg_id, name, time, value):
        if self.__static_mode: raise Exception("Func is not allowed to use in static mode")
        key = (msg_id, name)
        with self.lock:
            if key not in self.signal_plot:
                self.signal_plot[key] = {"time": deque(), "value": deque()}

            time_data = self.signal_plot[key]["time"]
            value_data = self.signal_plot[key]["value"]
            time_data.append(time)
            value_data.append(value)

            while time_data and (time - time_data[0]) > self.__plot_data_max_sec:
                time_data.popleft()
                value_data.popleft()

    def get_messages_snapshot(self):
        if self.__static_mode: self.__get_static_msg()
        with self.lock:
            return dict(self.messages)
    
    def __get_static_msg(self):
        return self.messages
    
    def get_trace_snapshot(self):
        if self.__static_mode: raise Exception("Func is not allowed to use in static mode")
        with self.lock:
            return list(self.msg_log)
    
    def get_signal_plot(self, signal_ids: tuple[tuple]):
        if self.__static_mode: self.__get_signal_plot_static(signal_ids)
        with self.lock:
            return {
                sig: (
                    np.array(self.signal_plot[sig]["time"], dtype=np.float64),
                    np.array(self.signal_plot[sig]["value"], dtype=np.float64)
                )
                for sig in signal_ids if self.signal_plot.get(sig)
            }
    def __get_signal_plot_static(self, signal_ids):
        return {
                sig: (
                    self.signal_plot[sig]["time"],
                    self.signal_plot[sig]["value"]
                )
                for sig in signal_ids if self.signal_plot.get(sig)
            }
    
    def reset(self):
        with self.lock:
            self.messages.clear()
            self.msg_log.clear()
            self.signal_plot.clear()
            self.disable_static_mode()





class CANScanner:

    def __init__(self, driver, decoder, data_store):

        self.driver = driver
        self.decoder = decoder
        self.data_store = data_store
        self.running = False
        self.init_time = None
        self.stop_event = threading.Event()

    def start(self, log_obj = None):

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
            self.data_store.update_message(msg.arbitration_id, msg.data, msg.dlc, t, name, is_dbc, decoded)

            if decoded:
                for sig, val in decoded.items():
                    self.data_store.update_signal(msg.arbitration_id, sig, t - self.init_time, val)
                if log_obj:
                    log_obj.add_log(msg)

    def stop(self):
        self.stop_event.set()




class CANManager:

    

    def __init__(self, data: CANData):
        self.can_data = data
        self.scan_available_configs()
        self.thread = None
        self.log_mode = False
        self.log_file_name = None
        self.log_thread = None

    def enable_log(self, log_file_name: str | None = None):
        if self.log_mode: return
        self.log_file_name = log_file_name
        self.log_mode = True
    
    def disable_log(self):
        if not self.log_mode: return
        
        self.log_mode = False
    

    def scan_available_configs(self, interfaces=("vector", "pcan")):
        self.configs = can.detect_available_configs(interfaces=interfaces)
    
    def get_configs(self):
        if self.configs is None: self.scan_available_configs()

        return self.configs
    
    def connect(self, interface: str, channel: int, dbc_path = None, bitrate: int = 500000):
        self.can_data.reset()

        if self.thread and self.thread.is_alive():
            raise RuntimeError("CAN connection already active")

        if interface == "vector":
            for config in self.get_configs():
                if config['interface'] == "vector" and config['channel'] == channel:
                    VectorBus.set_application_config(app_name='python-can', app_channel=channel, **config)
                    break

            self.driver = CANDriver(interface = interface, channel = channel, bitrate = bitrate, app_name='python-can')
        
        else:
            self.driver = CANDriver(interface = interface, channel = channel, bitrate = bitrate)

        decoder = DBCDecoder(dbc_path)
        
        self.scanner = CANScanner(self.driver, decoder, self.can_data)

        if self.log_mode:
            self.log = CanLogWriter(self.log_file_name)
            self.log_thread = threading.Thread(
                target = self.log.log_init,
                daemon=True
            )
            self.log_thread.start()

        args = (self.log,) if self.log_mode else (None, )

        self.thread = threading.Thread(
            target = self.scanner.start,
            daemon=True,
            args=args
        )

        

        

        self.thread.start()

    def get_connection_status(self):

        return True if self.thread else False

    def disconnect(self, reset_data: bool = False):

        if not self.thread: return

        self.scanner.stop()
        

        if self.thread:
            self.thread.join()
        if self.log_thread:
            self.log.stop_log()
            self.log_thread.join()
            self.log = None
            self.log_thread = None
        
        self.driver.close()
        self.thread = None
        self.driver = None
        self.scanner = None

        if reset_data:
            self.can_data.reset()


class CanLogWriter:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data_to_log = Queue()
        self.event = threading.Event()
        self.lock = threading.Lock()

    def log_init(self):

        with can.BLFWriter(self.file_path) as writter:
            while not self.event.is_set():
                try:
                    msg = self.data_to_log.get(timeout=0.1)
                except Exception: #empty except
                    continue

                writter.on_message_received(msg)

    def add_log(self, msg: can.Message):
        if not isinstance(msg, can.Message): raise TypeError("msg must be can.Message class")


        self.data_to_log.put(msg) # Queue already has safe treathing 

    
    def stop_log(self):
        self.event.set()

class CanLogReader:

    __allowed_ext = ['blf']

    def __init__(self):
        self.signal_plot = {}
        self.messages = {}
        self.__init_time = None
        self.is_ready = False
        self.event = threading.Event()
        self.path = None

    def read_log(self, log_path: str, dbc_path):
        
        if not any(log_path.endswith(ext) for ext in self.__allowed_ext): raise ValueError(f"{self.__name__} doesn't allow this ext. Allowed ext: {self.__allowed_ext}")

        decoder = DBCDecoder(dbc_path)
        self.path = log_path

        with can.BLFReader(log_path) as reader:
            
            for msg in reader:
                if self.event.is_set():
                    return

                if self.__init_time is None:
                    self.__init_time = msg.timestamp

                name, signals_info = decoder.decode(msg)
                if signals_info is None: continue

                if not msg.arbitration_id in self.messages:
                    self.messages[msg.arbitration_id] = {
                        "dbc_name": name or "",
                        "is_dbc": True,
                        "decoded": {}
                    }
                
                

                for sname, value in signals_info.items():
                    if sname not in self.messages[msg.arbitration_id]['decoded']: self.messages[msg.arbitration_id]['decoded'][sname] = 0
                    if (msg.arbitration_id, sname) not in self.signal_plot:
                        self.signal_plot[(msg.arbitration_id, sname)] = {
                            "time": [],
                            "value": []
                        }
                    self.signal_plot[(msg.arbitration_id, sname)]['time'].append(msg.timestamp - self.__init_time)
                    self.signal_plot[(msg.arbitration_id, sname)]['value'].append(value)
                
        for _, data in self.signal_plot.items():
            for axis, value  in data.items():
                data[axis] = np.array(value, dtype=np.float64)

        self.is_ready = True



    


 
