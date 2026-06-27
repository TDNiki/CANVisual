import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow
from CanInterface import CANData

def end_point():return


class SignalLogic:



    __msg_header_tag = "msginsigtab"
    __signal_table_tag = "sigtab"
    plot_logic = None

    def __init__(self, data : CANData, signal_window_tag : str):
        self.data = data
        self.__signal_window_tag = signal_window_tag



    def update(self): 

        msg_copy = self.data.get_messages_snapshot()

        if not len(msg_copy):
            dpg.delete_item(self.__signal_window_tag, children_only=True)

        for id, data in msg_copy.items():
            if not len(data['decoded']) or not data['is_dbc']: continue

            if not dpg.does_item_exist(f"{self.__msg_header_tag}_{id}"):
                self.__create_msg(id, data)

            self.__check_signals(id, data)

    def __create_msg(self, id: str, data: dict):

        with dpg.collapsing_header(parent=self.__signal_window_tag, label=data.get("dbc_name", str(id)), tag=f"{self.__msg_header_tag}_{id}"):
            with dpg.table(resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_innerH=True, 
                        borders_outerH=False, borders_innerV=True, borders_outerV=False, row_background=False, no_keep_columns_visible=True, tag=f"{self.__signal_table_tag}_{id}"):
                    dpg.add_table_column(label='ID графика', init_width_or_weight=0.2)
                    dpg.add_table_column(label = 'Цвет', init_width_or_weight=0.1)
                    dpg.add_table_column(label='Имя сигнала', init_width_or_weight=0.5)
                    dpg.add_table_column(label='Значение', init_width_or_weight=0.2)
    
    def __check_signals(self, msg_id, data):

        for sig, value in data['decoded'].items():

            try:

                if dpg.does_item_exist(f"{msg_id}_{sig}"):
                    dpg.set_value(f"{msg_id}_{sig}", f"{value:.2f}")
                    plots_count = self.plot_logic.count_subplots()
                    if len(dpg.get_item_configuration(f"{msg_id}_{sig}_combo")) != plots_count: 
                        dpg.configure_item(f"{msg_id}_{sig}_combo", items = [i for i in range(plots_count)] + ["-"], default = "-")
                else:
                    with dpg.table_row(parent = f"{self.__signal_table_tag}_{msg_id}"):
                        combo_init_items = ["-"]
                        combo = dpg.add_combo(combo_init_items, width=-1, tag = f"{msg_id}_{sig}_combo", callback = self.plot_logic.on_signal_change, user_data=sig)
                        dpg.set_value(combo, combo_init_items[0])
                        dpg.add_color_edit(no_alpha=True, no_inputs=True, no_label=True, no_drag_drop=True, no_options=True, no_tooltip=True, alpha_bar=True, default_value = (24, 81, 232), width=-1)
                        ui_obj = dpg.add_text(sig)
                        dpg.add_text(f"{value:.2f}", tag = f"{msg_id}_{sig}", color=(150, 200, 255, 255))
                        dpg.add_drag_payload(parent=ui_obj, drag_data=sig, payload_type="plotting")

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
        cls.logic = SignalLogic(kwargs['data'], cls.tag)
        with dpg.window(
            tag=cls.tag,
            label=cls.title,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            no_close=True,
        ): pass


