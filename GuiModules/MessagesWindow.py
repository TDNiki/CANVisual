import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow
from CanInterface import CANData
from datetime import datetime

def end_point(): ...

class MessagesLogic:

    __is_follow_trace = False

    def __init__(self, data: CANData, msg_table_tag, msg_trace_tag):
        self.data = data
        self.msg_table_tag = msg_table_tag
        self.msg_trace_tag = msg_trace_tag

    
    
    def _update_rates(self):

        rows = dpg.get_item_children(self.msg_table_tag, 1)
        for row in rows:
            dpg.delete_item(row)

        for msg_id, msg in self.data.get_messages_snapshot().items():

            color = (
                (150, 200, 255, 255)
                if msg["is_dbc"]
                else (255, 255, 255, 255)
            )

            with dpg.table_row(parent=self.msg_table_tag):

                dpg.add_text(f"{msg_id:08X}", color=color)
                dpg.add_text(str(msg["count"]))
                dpg.add_text(f"{msg['frequency']*1000:.2f}") #sec to ms
                dpg.add_text(str(msg["dlc"]))

                if msg["data"]:
                    dpg.add_text(
                        " ".join(f"{b:02X}" for b in msg["data"])
                    )
                else:
                    dpg.add_text("-")

    def _update_track(self):
        
        rows = dpg.get_item_children(self.msg_trace_tag, 1)

        for row in rows:
            dpg.delete_item(row)

        for msg in self.data.get_trace_snapshot():

            with dpg.table_row(parent=self.msg_trace_tag):
                # dpg.add_text(str(msg.timestamp))
                dpg.add_text(datetime.fromtimestamp(msg.timestamp).strftime('%H:%M:%S.%f')[:-3])
                dpg.add_text(f"{msg.arbitration_id:08X}")
                dpg.add_text(str(msg.dlc))
                dpg.add_text(' '.join(f"{byte:02x}" for byte in msg.data))
        
        if self.__is_follow_trace: dpg.set_y_scroll(self.msg_trace_tag, -1)
    
    def update(self): 
        self._update_rates()
        self._update_track()

    def follow_trace(self, event_sender):
        """Callbck for trace auto scroll"""

        self.__is_follow_trace = dpg.get_value(event_sender)
            









class MessagesWindow(BaseWindow):

    tag = "msg"
    title = "Входящие соообщения"
    size = (0.3, 0.45)
    position = (0, 0.1)

    __msg_table_tag = 'ReceivedMessagesTable'
    __msg_trace_tag = 'ReceivedMessagesTrace'


    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = MessagesLogic(kwargs['data'], cls.__msg_table_tag, cls.__msg_trace_tag)
        with dpg.window(
            tag=cls.tag,
            label=cls.title,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            no_close=True,
        ):
           with dpg.tab_bar():

            with dpg.tab(label="Сообщения"):

                with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit, borders_innerH=True, borders_outerH=True, 
                            borders_innerV=True, borders_outerV=True, row_background=True, tag=cls.__msg_table_tag, sortable=True, callback=end_point,
                            freeze_rows=1, freeze_columns=1,scrollY=True, scrollX=True, height=-1):
                    
                    dpg.add_table_column(label='ID',width_fixed=True)
                    dpg.add_table_column(label='Count',width_fixed=True)
                    dpg.add_table_column(label='Rate',width_fixed=True)
                    dpg.add_table_column(label='DLC',width_fixed=True)
                    dpg.add_table_column(label='Data (Hex)',width_stretch=True, init_width_or_weight=0.0)

            with dpg.tab(label="Трассировка"):
                dpg.add_checkbox(label="Отслеживание",callback=cls.logic.follow_trace)

                with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit, borders_innerH=True, borders_outerH=True, 
                            borders_innerV=True, borders_outerV=True, row_background=False, tag=cls.__msg_trace_tag,freeze_rows=1, freeze_columns=1,
                            scrollY=True, scrollX=True, height=-1):
                    dpg.add_table_column(label='Timestamp',width_fixed=True)
                    dpg.add_table_column(label='ID',width_fixed=True)
                    dpg.add_table_column(label='DLC',width_fixed=True)
                    dpg.add_table_column(label='Data (Hex)',width_stretch=True, init_width_or_weight=0.0)

    @classmethod
    def update(cls):
        pass

