import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow

def end_point():return

class PlotLogic:

    def update(self): return

class PlotWindow(BaseWindow):

    tag = "plot"
    title = "Визуализация данных"
    size = (0.7, 0.9)
    position = (0.3, 0.1)
    logic = PlotLogic()

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
            with dpg.group(horizontal=True):
                dpg.add_button(label="Fit X", callback=lambda: dpg.fit_axis_data("x_axis"))
                dpg.add_button(label="Fit Y", callback=lambda: dpg.fit_axis_data("y_axis"))
                dpg.add_checkbox(tag="auto_x", label="Auto X")

            with dpg.subplots(rows=1, columns=1, tag="main_subplots", no_title=True, width=-1, height=-1):

                with dpg.plot(label="", height=-1, width=-1):

                    dpg.add_plot_legend()

                    dpg.add_plot_axis(dpg.mvXAxis, tag="x_axis")
                    dpg.add_plot_axis(dpg.mvYAxis, tag="y_axis")

    @classmethod
    def update(cls):
        pass

