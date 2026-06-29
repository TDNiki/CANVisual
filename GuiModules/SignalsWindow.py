import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow
from CanInterface import CANData
from settings import DEFAULT_PLOT_COLOR, MIN_PLOTS_COUNT

def end_point():return


class SignalLogic:



    __msg_header_tag = "msginsigtab"
    __signal_table_tag = "sigtab"
    __plot_count = MIN_PLOTS_COUNT

    def __init__(self, data : CANData, signal_window_tag : str, event_hander):
        self.data = data
        self.__signal_window_tag = signal_window_tag
        self.event_hander = event_hander
        self.__set_up_event()
    
    def __set_up_event(self):
        self.event_hander.sub("on_plot_size_change", self.__set_plot_count)
        self.event_hander.sub("on_signals_move", self.__on_signal_move)




    def __set_plot_count(self, count):
        self.__plot_count = count
    
    def __on_signal_move(self, signal_id, plot_id):

        msg_id, sig = signal_id
        dpg.set_value(f"{msg_id}_{sig}_combo", plot_id)

    def update(self): 

        msg_copy = self.data.get_messages_snapshot()

        if not len(msg_copy):
            dpg.delete_item(self.__signal_window_tag, children_only=True)

        for id, data in msg_copy.items():
            if not len(data['decoded']) or not data['is_dbc']: continue

            if not dpg.does_item_exist(f"{self.__msg_header_tag}_{id}"):
                self.__create_msg(id, data)

            self.__check_signals(id, data)

    def __create_msg(self, id: str | int, data: dict):

        with dpg.collapsing_header(parent=self.__signal_window_tag, label=data.get("dbc_name", f"{id:08X}") + f" ({id:08X})", tag=f"{self.__msg_header_tag}_{id}"):
            with dpg.table(resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_innerH=True, 
                        borders_outerH=False, borders_innerV=True, borders_outerV=False, row_background=False, no_keep_columns_visible=True, tag=f"{self.__signal_table_tag}_{id}"):
                    dpg.add_table_column(label='ID графика', init_width_or_weight=0.2)
                    dpg.add_table_column(label = 'Цвет', init_width_or_weight=0.1)
                    dpg.add_table_column(label='Имя сигнала', init_width_or_weight=0.5)
                    dpg.add_table_column(label='Значение', init_width_or_weight=0.2)
    
    def __check_signals(self, msg_id, data):

        if not dpg.get_value(f"{self.__msg_header_tag}_{msg_id}"): return #лишний раз не будет обновлять данные, если они закрыты
        
        for sig, value in data['decoded'].items():

            try:

                if dpg.does_item_exist(f"{msg_id}_{sig}"):
                    dpg.set_value(f"{msg_id}_{sig}", f"{value:.2f}")
                    if len(dpg.get_item_configuration(f"{msg_id}_{sig}_combo")['items']) - 1 != self.__plot_count: # -1 : offset bcs default value
                        dpg.configure_item(f"{msg_id}_{sig}_combo", items = [i for i in range(self.__plot_count)] + ["-"])
                else:
                    with dpg.table_row(parent = f"{self.__signal_table_tag}_{msg_id}"):
                        combo_init_items = ["-"] + [i for i in range(self.__plot_count)]
                        combo = dpg.add_combo(combo_init_items, width=-1, tag = f"{msg_id}_{sig}_combo", callback = lambda sender, plot_id, signal_name: self.event_hander.invoke("on_combo_plot_change", sender, plot_id, signal_name), user_data=(msg_id, sig))
                        dpg.set_value(combo, combo_init_items[0])
                        dpg.add_color_value(default_value=DEFAULT_PLOT_COLOR, parent = "shared_value_registr", tag = f"{msg_id}_{sig}_color")
                        dpg.add_color_edit(tag = f"{msg_id}_{sig}_colore",no_alpha=True, no_inputs=True, no_label=True, no_drag_drop=True, no_options=True, no_tooltip=True, alpha_bar=True, source=f"{msg_id}_{sig}_color", width=-1, callback = lambda sender, data, signal_id: self.event_hander.invoke("on_plot_color_change", sender, data, signal_id), user_data=(msg_id, sig))
                        dpg.add_text(sig)
                        dpg.add_text(f"{value:.2f}", tag = f"{msg_id}_{sig}", color=(150, 200, 255, 255))
                        #dpg.add_drag_payload(parent=ui_obj, drag_data=sig, payload_type="plotting")

            except Exception as error: 
                print(error)
                pass #eror log 


           



class SignalsWindow(BaseWindow):

    tag = "signals"
    title = "Сигналы"
    size = (0.3, 0.45)
    position = (0, 0.55)
    logic = None




    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = SignalLogic(kwargs['data'], cls.tag, kwargs['event_handler'])
        with dpg.window(
            tag=cls.tag,
            label=cls.title,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            no_close=True,
        ): 
            ...


