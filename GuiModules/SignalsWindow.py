import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow

def end_point():return

class SignalLogic:

    def update(self): return


class SignalsWindow(BaseWindow):

    tag = "signals"
    title = "Сигналы"
    size = (0.3, 0.45)
    position = (0, 0.55)
    logic = SignalLogic()

    @classmethod
    def setup(cls, *args, **kwargs):
        cls.data = kwargs['data']
        with dpg.window(
            tag=cls.tag,
            label=cls.title,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            no_close=True,
        ):
            with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_innerH=True, 
                        borders_outerH=True, borders_innerV=True, borders_outerV=True, row_background=True, tag='SignalsTable'):
                dpg.add_table_column(label='График')
                dpg.add_table_column(label='ID сообщения')
                dpg.add_table_column(label='Имя сигнала')
                dpg.add_table_column(label='Значение')

    @classmethod
    def update(cls):
        pass

