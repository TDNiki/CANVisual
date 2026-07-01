import dearpygui.dearpygui as dpg

from BaseWindow import BaseWindow
from bisect import bisect_left, bisect_right
from math import ceil

from settings import (
    MAX_PLOTS_COUNT,
    MIN_PLOTS_COUNT,
    DEFAULT_DISPLAY_RANGE,
    MIN_DISPLAY_RANGE,
    MAX_DISPLAY_RANGE,
    POINTS_PER_PIXEL
)

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

    def __init__(self, data, event_hander, plot_window_tag):
        self.data = data
        self.subplots = list()
        self.signal_locations = {} #signal id: subplot index
        self.signal_theme = {} # signal id: theme
        self.__plot_window_tag = plot_window_tag
        self.event_hander = event_hander
        self.__set_up_event()

    def on_display_range_change(self, sender, sec_str: str):
        self.window_seconds = int (sec_str)
    
    def __set_up_event(self):
        self.event_hander.sub("on_combo_plot_change", self.on_signal_change)
        self.event_hander.sub("on_plot_color_change", self.on_color_change)

    def on_color_change(self, sender: str | None, color, signal_id):
        if sender and not dpg.is_item_activated(sender): #обработка от спама вызовов
            return
        if signal_id not in self.signal_theme: return

        print(sender, color, signal_id )

        color = [int(color[i] * 255) for i in range(len(color) - 1)]

        dpg.delete_item(self.signal_theme[signal_id], children_only=True)

        with dpg.theme_component(parent=self.signal_theme[signal_id]):
            dpg.add_theme_color(dpg.mvPlotCol_Line, color, category=dpg.mvThemeCat_Plots)

        #dpg.bind_item_theme(f"plot_{msg_id}_{signal_name}", self.signal_theme[signal_id])



    def update(self):

        max_time = 0
        xmin, xmax = dpg.get_axis_limits(self.subplots[0].x_axis)
        width, _ = dpg.get_item_rect_size(self.__plot_window_tag) # у subplot нету такого аттрибута
        data = self.data.get_signal_plot()
        for signal, _ in self.signal_locations.items():
            try:
                
                x = data[signal]["time"]
                y = data[signal]["value"]
                i_left = bisect_left(x, xmin) # на базе бинарного поиска
                i_right = bisect_right(x, xmax)
                x_view = x[i_left:i_right]
                y_view = y[i_left:i_right]
                view_points_count = int(width * POINTS_PER_PIXEL)
                count_points = int(width * POINTS_PER_PIXEL)
                x_view, y_view = self.__min_max_decimate(x_view, y_view, count_points)
                msg_id, signal_name = signal
                dpg.set_value(f"plot_{msg_id}_{signal_name}", [x_view, y_view])

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

                with dpg.plot(label = f"График №{i}"):

                    dpg.add_plot_legend()

                    subplot.x_axis = dpg.add_plot_axis(
                        dpg.mvXAxis,
                        tag=f"x_axis_{i}"
                    )

                    subplot.y_axis = dpg.add_plot_axis(
                        dpg.mvYAxis,
                        tag=f"y_axis_{i}",
                        # drop_callback=self.drop_signal,
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

        msg_id, signal_name = signal

        dpg.delete_item(f"plot_{msg_id}_{signal_name}")
        self.__delete_plot_theme(signal)
        self.event_hander.invoke("on_signals_move", signal, "-")

    def add_signal(self, signal: tuple[str, str], subplot_index):

        if signal in self.signal_locations:
            return

        subplot = self.subplots[subplot_index]

        subplot.signals.append(signal)
        self.signal_locations[signal] = subplot_index

        msg_id, signal_name = signal

        line = dpg.add_line_series(
            [],
            [],
            label= f"{signal_name} ({msg_id:08X})",
            parent=subplot.y_axis,
            tag=f"plot_{msg_id}_{signal_name}",
        )

        self.__add_modals_settings(signal, line)

        self.__create_plot_theme(signal)

        self.event_hander.invoke("on_signals_move", signal, subplot_index)
        
    def __add_modals_settings(self, signal, parent):

        msg_id, signal_name = signal

        dpg.add_button(label="Удалить", parent=parent, callback=lambda : self.remove_signal(signal)) # можно было отдельный ивент создать, но раз уж есть похожий зачем память тратить

        with dpg.group(parent=parent, horizontal=False):
            dpg.add_text("Цвет: ")
            dpg.add_color_edit(label = "Цвет линии", source=f"{msg_id}_{signal_name}_color", parent=parent, no_alpha=True, no_inputs=True, no_label=True, no_drag_drop=True, no_options=True, no_tooltip=True, alpha_bar=True, width=-1, callback = lambda sender, data, signal_id: self.on_color_change(sender, data, signal_id), user_data = (signal))


    def __create_plot_theme(self, signal_id):
        msg_id, signal_name = signal_id

        with dpg.theme() as theme:
            with dpg.theme_component(parent=theme):
                dpg.add_theme_color(dpg.mvPlotCol_Line, dpg.get_value(f"{msg_id}_{signal_name}_colore"), category=dpg.mvThemeCat_Plots)
        
        dpg.bind_item_theme(f"plot_{msg_id}_{signal_name}", theme)
        self.signal_theme[signal_id] = theme
    
    def __delete_plot_theme(self, signal_id):
        dpg.delete_item(self.signal_theme[signal_id])
        self.signal_theme.pop(signal_id)

        
    def move_signal(self, signal: tuple[str, str], new_subplot_index):

        self.remove_signal(signal)
        self.add_signal(signal, new_subplot_index)

    # def drop_signal(self, sender, app_data):
    #     signal = app_data
    #     subplot_index = next( i for i, subplot in enumerate(self.subplots) if subplot.y_axis == sender)

    #     self.add_signal(signal, subplot_index)

    def set_rows(self, rows):
        self.rows = rows
        self.rebuild()
        self.event_hander.invoke("on_plot_size_change", self.cols  * self.rows)


    def set_columns(self, columns):
        self.cols = columns
        self.rebuild()
        self.event_hander.invoke("on_plot_size_change", self.cols  * self.rows)
    
    def fit_x(self):

        for subplot in self.subplots:
            dpg.fit_axis_data(subplot.x_axis)


    def fit_y(self):

        for subplot in self.subplots:
            dpg.fit_axis_data(subplot.y_axis)

    def set_auto_scroll_x(self, sender, is_checked):
        self.auto_scroll = is_checked

        if not is_checked: dpg.set_axis_limits_auto(self.subplots[0].x_axis)
    
    def __reset_data(self):
        self.signal_locations.clear()

    def on_signal_change(self, sender, plot_index:str, signal_name: tuple[str, str]):
        if not plot_index.isdigit(): 
            self.remove_signal(signal_name)
            return
        if signal_name not in self.signal_locations: self.add_signal(signal_name, int(plot_index))
        else: self.move_signal(signal_name, int(plot_index))

    def __min_max_decimate(self, x, y, exits_count: int):
        """
        Implementation of the MinMax algorithm to reduce the size of the displayed points.
        https://www.pvsm.ru/datchiki/453719
        """
        if len(x) <= exits_count:
            return x, y
        
        step = ceil(len(x) / (exits_count // 2))

        dx = []
        dy = []

        for i in range(0, len(x), step):
            chunk_x = x[i:i+step]
            chunk_y = y[i:i+step]

            if not chunk_x:
                continue

            min_i = min(range(len(chunk_y)), key=lambda k: chunk_y[k])
            max_i = max(range(len(chunk_y)), key=lambda k: chunk_y[k])

            if min_i == max_i:
                dx.append(chunk_x[min_i])
                dy.append(chunk_y[min_i])
            elif min_i < max_i:
                dx.append(chunk_x[min_i])
                dy.append(chunk_y[min_i])

                dx.append(chunk_x[max_i])
                dy.append(chunk_y[max_i])
            else:
                dx.append(chunk_x[max_i])
                dy.append(chunk_y[max_i])

                dx.append(chunk_x[min_i])
                dy.append(chunk_y[min_i])

        return list(dx), list(dy)

    

    

class PlotWindow(BaseWindow):

    tag = "plot"
    title = "Визуализация данных"
    size = (0.7, 0.9)
    position = (0.3, 0.1)

    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = PlotLogic(kwargs['data'], kwargs['event_handler'], cls.tag);
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
                dpg.add_button(label="Подгон X", callback=lambda: cls.logic.fit_x())
                dpg.add_button(label="Подгон Y", callback=lambda: cls.logic.fit_y())
                dpg.add_checkbox(tag="auto_x", label="Отслеживание по времени", callback=cls.logic.set_auto_scroll_x)
                dpg.add_drag_int(label="Диапазон отображения", default_value=DEFAULT_DISPLAY_RANGE, min_value=MIN_DISPLAY_RANGE, max_value=MAX_DISPLAY_RANGE, callback = cls.logic.on_display_range_change)

            cls.logic.rebuild()


