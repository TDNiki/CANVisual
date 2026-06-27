import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow

MIN_PLOTS_COUNT = 1
MAX_PLOTS_COUNT = 5

class Subplot:

    def __init__(self, index):

        self.index = index
        self.x_axis = None
        self.y_axis = None
        self.signals = []

class PlotLogic:

    rows = MIN_PLOTS_COUNT
    cols = MIN_PLOTS_COUNT
    window_seconds = 10
    auto_scroll = False

    def __init__(self, data):
        self.data = data
        self.subplots = list()
        self.signal_locations = {}

    def count_subplots(self): return len(self.subplots)


    def update(self):

        max_time = 0

        data = self.data.get_signal_plot()
        for signal, _ in self.signal_locations.items():
            try:
                x = data[signal]["time"]
                y = data[signal]["value"]
                dpg.set_value(f"plot_{signal}", [x, y])

                if len(x) > 0:
                    max_time = max(max_time, x[-1])
            except KeyError:
                self.__reset_data()
                self.rebuild()
                break
                #warning set

        if self.auto_scroll and max_time > 0:
            self.__scroll_x(max_time)
    
    def __scroll_x(self, max_time):
        start = max(0, max_time - self.window_seconds)


        dpg.set_axis_limits(self.subplots[0].x_axis, start, max_time)

    def rebuild(self):

        saved_locations = self.signal_locations.copy()

        if dpg.does_item_exist("subplots"):
            dpg.delete_item("subplots")

        self.subplots.clear()

        with dpg.subplots(
            parent=PlotWindow.tag,
            tag="subplots",
            rows=self.rows,
            columns=self.cols,
            width=-1,
            height=-1,
            link_all_x=True,
        ):

            for i in range(self.rows * self.cols):

                subplot = Subplot(i)

                with dpg.plot(label = f"№{i}"):

                    dpg.add_plot_legend()

                    subplot.x_axis = dpg.add_plot_axis(
                        dpg.mvXAxis,
                        tag=f"x_axis_{i}"
                    )

                    subplot.y_axis = dpg.add_plot_axis(
                        dpg.mvYAxis,
                        tag=f"y_axis_{i}",
                        drop_callback=self.drop_signal,
                        payload_type="plotting"
                    )

                self.subplots.append(subplot)

        self.signal_locations.clear()

        for signal, subplot_index in saved_locations.items():

            subplot_index = min(subplot_index, len(self.subplots) - 1)

            self.add_signal(signal, subplot_index)

    def remove_signal(self, signal):

        if signal not in self.signal_locations:
            return
        subplot_index = self.signal_locations.pop(signal)
        self.subplots[subplot_index].signals.remove(signal)

        dpg.delete_item(f"plot_{signal}")

    def add_signal(self, signal, subplot_index):

        if signal in self.signal_locations:
            return

        subplot = self.subplots[subplot_index]

        subplot.signals.append(signal)
        self.signal_locations[signal] = subplot_index

        dpg.add_line_series(
            [],
            [],
            label=signal,
            parent=subplot.y_axis,
            tag=f"plot_{signal}"
        )

    def move_signal(self, signal, new_subplot_index):

        self.remove_signal(signal)
        self.add_signal(signal, new_subplot_index)

    def drop_signal(self, sender, app_data):
        signal = app_data
        subplot_index = next( i for i, subplot in enumerate(self.subplots) if subplot.y_axis == sender)

        self.add_signal(signal, subplot_index)

    def set_rows(self, rows):
        self.rows = rows
        self.rebuild()


    def set_columns(self, columns):
        self.cols = columns
        self.rebuild()
    
    def fit_x(self):

        for subplot in self.subplots:
            dpg.fit_axis_data(subplot.x_axis)


    def fit_y(self):

        for subplot in self.subplots:
            dpg.fit_axis_data(subplot.y_axis)

    def set_auto_scroll_x(self, sender, is_checked):
        self.auto_scroll = is_checked
    
    def __reset_data(self):
        self.signal_locations.clear()

    def on_signal_change(self, sender, plot_index:str, signal_name):
        if not plot_index.isdigit(): self.remove_signal(signal_name)
        if signal_name not in self.signal_locations: self.add_signal(signal_name, int(plot_index))
        else: self.move_signal(signal_name, int(plot_index))



    

    

class PlotWindow(BaseWindow):

    tag = "plot"
    title = "Визуализация данных"
    size = (0.7, 0.9)
    position = (0.3, 0.1)

    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = PlotLogic(kwargs['data']);
        with dpg.window(
            tag=cls.tag,
            label=cls.title,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            no_close=True,
        ):
            with dpg.menu_bar():
                with dpg.menu(label="Настройки"):

                    with dpg.menu(label="Настройка сетки"):

                        dpg.add_text(
                            "При удалении сетки, графики удалятся",
                            color=(255, 255, 0, 255)
                        )

                        dpg.add_input_int(
                            label="Строки",
                            default_value=MIN_PLOTS_COUNT,
                            min_value=MIN_PLOTS_COUNT,
                            max_value=MAX_PLOTS_COUNT,
                            min_clamped=True,
                            max_clamped=True,
                            callback=lambda _, a: cls.logic.set_rows(a)
                        )

                        dpg.add_input_int(
                            label="Столбцы",
                            default_value=MIN_PLOTS_COUNT,
                            min_value=MIN_PLOTS_COUNT,
                            max_value=MAX_PLOTS_COUNT,
                            min_clamped=True,
                            max_clamped=True,
                            callback=lambda _, a: cls.logic.set_columns(a)
                        )
            with dpg.group(horizontal=True):
                dpg.add_button(label="Fit X", callback=lambda: cls.logic.fit_x())
                dpg.add_button(label="Fit Y", callback=lambda: cls.logic.fit_y())
                dpg.add_checkbox(tag="auto_x", label="Отслеживание по времени", callback=cls.logic.set_auto_scroll_x)

            cls.logic.rebuild()


