import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow

def end_point():return


class MessagesWindow(BaseWindow):

    tag = "msg"
    title = "Входящие соообщения"
    size = (0.3, 0.45)
    position = (0, 0.1)

    @classmethod
    def setup(cls):
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
                            borders_innerV=True, borders_outerV=True, row_background=True, tag='ReceivedMessagesTable', sortable=True, callback=end_point,
                            freeze_rows=1, freeze_columns=1,scrollY=True, scrollX=True, height=-1):
                    
                    dpg.add_table_column(label='ID',width_fixed=True)
                    dpg.add_table_column(label='Count',width_fixed=True)
                    dpg.add_table_column(label='Rate',width_fixed=True)
                    dpg.add_table_column(label='DLC',width_fixed=True)
                    dpg.add_table_column(label='Data (Hex)',width_stretch=True, init_width_or_weight=0.0)

            with dpg.tab(label="Трассировка"):
                dpg.add_checkbox(label="auto scroll",callback=end_point)

                with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit, borders_innerH=True, borders_outerH=True, 
                            borders_innerV=True, borders_outerV=True, row_background=False, tag='ReceivedMessagesTrace',freeze_rows=1, freeze_columns=1,
                            scrollY=True, scrollX=True, height=-1):
                    dpg.add_table_column(label='Timestamp',width_fixed=True)
                    dpg.add_table_column(label='ID',width_fixed=True)
                    dpg.add_table_column(label='DLC',width_fixed=True)
                    dpg.add_table_column(label='Data (Hex)',width_stretch=True, init_width_or_weight=0.0)

    @classmethod
    def update(cls):
        pass

