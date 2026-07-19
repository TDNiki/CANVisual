import dearpygui.dearpygui as dpg
import numpy as np

from BaseWindow import BaseWindow
from math import ceil


from settings import (
    MAX_PLOTS_COUNT,
    MIN_PLOTS_COUNT,
    DEFAULT_DISPLAY_RANGE,
    MIN_DISPLAY_RANGE,
    MAX_DISPLAY_RANGE,
    POINTS_PER_PIXEL,
    MIN_DISTANCE_PLOT_TOOL_SHOW,
    DEFAULT_PLOT_COLOR
)

class Subplot:

    def __init__(self, index):

        self.index = index
        self.x_axis = None
        self.y_axis = None
        self.plot_id = None
        self.signals = []

class CursorX:

    def __init__(self, general_tag: str):
        self.__tag = general_tag
        self.__cursors = {} # plot_id : cursor_id
        self.annot = []
        self.x = 0
        # self.__init_share_registr(float(x)) почему то source не работает в adddrag
        self.mode = -1 # -1: hide, 0 static mode, 1 real time (checking mouse pos)

        
    def get_cursor_id(self): return self.__tag
    
    def __init_share_registr(self, x):
        if not dpg.does_item_exist(f"{self.__tag}_x_pos"):
            dpg.add_float_value(tag = f"{self.__tag}_x_pos", default_value = x, parent = "shared_value_registr")
        
    def clear_cursors(self):
        for cursor in self.__cursors.values():
            if dpg.does_item_exist(cursor):
                dpg.delete_item(cursor)
        
        for ann in self.annot:
            if dpg.does_item_exist(ann):
                dpg.delete_item(ann)
        
        self.annot.clear()
        self.__cursors.clear()

    def __on_x_change(self, sender):
        x = dpg.get_value(sender)
        if self.mode == 0 and x != self.x:
            self.update_cursors(x)

    def edit_lines(self, plots: tuple[Subplot]):
        self.clear_cursors()
        
        for plot in plots:
            self.__cursors[plot.plot_id] = dpg.add_drag_line(
            label = self.__tag,
            show = False if self.mode < 0 else True,
            parent = plot.plot_id,
            callback = self.__on_x_change
            )
    
    def show(self):
        if self.mode >= 0: return
        for cursor in self.__cursors.values():
            dpg.show_item(cursor)
        for ann in self.annot:
            dpg.show_item(ann)
        
        self.mode = 1

    def set_static(self):
        self.mode = 0
        

    def hide(self): 
        if self.mode < 0: return
        for cursor in self.__cursors.values():
            dpg.hide_item(cursor)

        for ann in self.annot:
            dpg.hide_item(ann)
        
        self.mode = -1

    def update_cursors(self, x):
        for cursor in self.__cursors.values():
                dpg.set_value(cursor, x)
            
        self.x = x
    
    def update_info(self, x: float, y: float = None, plot_id: str | int = None, signal_name: str = None, offset_annotation: tuple = (15, 15), color: tuple = DEFAULT_PLOT_COLOR):
        if self.mode < 0: return
        if self.x != x:
            self.update_cursors(x)

        if y != None:
            if not dpg.does_item_exist(f"{signal_name}_ann{self.__tag}"):
                self.annot.append(dpg.add_plot_annotation(label = f"{signal_name}: {y:.2f}", color = color, tag = f"{signal_name}_ann{self.__tag}", parent = plot_id, default_value = (x, y), offset = offset_annotation))
            else:
                dpg.configure_item(f"{signal_name}_ann{self.__tag}", label = f"{signal_name}: {y:.2f}", color = color, parent = plot_id, default_value = (x, y))

            

    
    def get_distance_between_cursors(self, cursor):
        if self.mode < 0 and cursor.mode < 0: return
        cursor_x = dpg.get_value(f"{cursor.get_cursor_id()}_x_pos")
        self_cursor_x = dpg.get_value(f"{self.get_cursor_id()}_x_pos")

        if cursor_x > self_cursor_x: return cursor_x - self_cursor_x
        elif self_cursor_x > cursor_x: return self_cursor_x - cursor_x
        else: return 0

class PlotLogic:

    rows = MIN_PLOTS_COUNT
    cols = MIN_PLOTS_COUNT
    window_seconds = 10
    auto_scroll = False
    __subplot_tag = "subplots"

    def __init__(self, data, event_hander, plot_window_tag):
        self.data = data
        self.subplots = list()
        self.signal_locations = {} #signal id: subplot index
        self.signal_theme = {} # signal id: theme
        self.__plot_window_tag = plot_window_tag
        self.event_hander = event_hander
        self.__set_up_event()
        self.first_cursor = CursorX("first_c")
        self.second_cursor = CursorX("second_c")
        self.selected_cursor = None
    

    def on_display_range_change(self, sender, sec_str: str):
        self.window_seconds = int (sec_str)
    
    def __set_up_event(self):
        self.event_hander.sub("on_combo_plot_change", self.on_signal_change)
        self.event_hander.sub("on_plot_color_change", self.on_color_change)
        self.event_hander.sub("clear_plots_request", self.__reset_data)

    def on_color_change(self, sender: str | None, color, signal_id, force_change: bool = True):
        if sender and not dpg.is_item_activated(sender): #обработка от спама вызовов
            return
        if signal_id not in self.signal_theme: return

        if color[0] < 1:
            color = [int(color[i] * 255) for i in range(len(color) - 1)]

        dpg.delete_item(self.signal_theme[signal_id], children_only=True)

        with dpg.theme_component(parent=self.signal_theme[signal_id]):
            dpg.add_theme_color(dpg.mvPlotCol_Line, color, category=dpg.mvThemeCat_Plots)
        
        if force_change:
            if not dpg.does_item_exist(f"{signal_id[0]}_{signal_id[1]}_color"):
                dpg.add_color_value(default_value = color, tag =  f"{signal_id[0]}_{signal_id[1]}_color", parent = "shared_value_registr")
            else:
                dpg.set_value(f"{signal_id[0]}_{signal_id[1]}_color", color)

        #dpg.bind_item_theme(f"plot_{msg_id}_{signal_name}", self.signal_theme[signal_id])



    def update(self):

        max_time = 0
        xmin, xmax = dpg.get_axis_limits(self.subplots[0].x_axis)
        width, _ = dpg.get_item_rect_size(self.__plot_window_tag) # у subplot нету такого аттрибута
        dpg.set_value(f"{self.__plot_window_tag}_tooltip", "")
        
        data = self.data.get_signal_plot(self.signal_locations.keys())

        
        for signal, _ in self.signal_locations.items():
            try:    
                x, y = data[signal]
                i_left = np.searchsorted(x, xmin) # на базе бинарного поиска
                i_right = np.searchsorted(x, xmax, "right")
                x_view = x[i_left:i_right]
                y_view = y[i_left:i_right]
                count_points = max(int(width * POINTS_PER_PIXEL / ((xmax - xmin) / MIN_DISPLAY_RANGE )), width / 2)
                x_view, y_view = self.__min_max_decimate(x_view, y_view, count_points)
                msg_id, signal_name = signal
                dpg.set_value(f"plot_{msg_id}_{signal_name}", [x_view, y_view])

                # print(len(x_view), xmax-xmin)

                if len(x) > 0:
                    max_time = max(max_time, x[-1])

                if not len(x_view): continue

                x, y = dpg.get_plot_mouse_pos()
                idx = np.abs(x_view - x).argmin()
                # distance = np.sqrt((x - x_view[idx])**2 + (y - y_view[idx])**2)
                # if distance < MIN_DISTANCE_PLOT_TOOL_SHOW * ((xmax - xmin) / MIN_DISPLAY_RANGE * 0.8): 
                #     dpg.set_value(f"{self.__plot_window_tag}_tooltip", f"{signal_name}: {x_view[idx]:.2f}; {y_view[idx]:.2f}")
                if self.first_cursor.mode == 1: #mouse real time
                    self.first_cursor.update_info(x_view[idx], y_view[idx], f"plot_{self.signal_locations[signal]}", signal_name, (-15, 15), dpg.get_value(f"{msg_id}_{signal_name}_color"))
                elif self.first_cursor.mode == 0:
                    idx_static = np.abs(x_view - self.first_cursor.x).argmin()
                    self.first_cursor.update_info(self.first_cursor.x, y_view[idx_static], f"plot_{self.signal_locations[signal]}", signal_name, (-15, 15), dpg.get_value(f"{msg_id}_{signal_name}_color"))

                if self.second_cursor.mode == 1: #mouse real time
                    self.second_cursor.update_info(x_view[idx], y_view[idx], f"plot_{self.signal_locations[signal]}", signal_name, (-15, 15), dpg.get_value(f"{msg_id}_{signal_name}_color"))
                elif self.second_cursor.mode == 0:
                    idx_static = np.abs(x_view - self.second_cursor.x).argmin()
                    self.second_cursor.update_info(self.second_cursor.x, y_view[idx_static], f"plot_{self.signal_locations[signal]}", signal_name, (-15, 15), dpg.get_value(f"{msg_id}_{signal_name}_color"))
                



            except KeyError:
                pass
            except Exception as err:
                self.event_hander("error", self.__name__, "Ошибка обработки графиков", str(err))
                self.__reset_data()
                self.rebuild()

        if self.auto_scroll and max_time > 0:
            self.__scroll_x(max_time)

        
    
    def __scroll_x(self, max_time):
        start = max(0, max_time - self.window_seconds)


        dpg.set_axis_limits(self.subplots[0].x_axis, start, max_time)

    def rebuild(self):

        saved_locations = self.signal_locations.copy()

        if dpg.does_item_exist(self.__subplot_tag):
            dpg.delete_item(self.__subplot_tag)
            

        self.subplots.clear()

        with dpg.subplots(
            parent=PlotWindow.tag,
            tag=self.__subplot_tag,
            rows=self.rows,
            columns=self.cols,
            width=-1,
            height=-1,
            link_all_x=True,
        ):

            for i in range(self.rows * self.cols):

                subplot = Subplot(i)

                with dpg.plot(label = f"График №{i}", tag = f"plot_{i}") as plot_id:

                    dpg.add_plot_legend()
                    subplot.plot_id = plot_id

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
        
        self.first_cursor.edit_lines(self.subplots)
        self.second_cursor.edit_lines(self.subplots)
        

    def remove_signal(self, signal):

        if signal not in self.signal_locations:
            return
        subplot_index = self.signal_locations.pop(signal)
        self.subplots[subplot_index].signals.remove(signal)

        msg_id, signal_name = signal

        dpg.delete_item(f"plot_{msg_id}_{signal_name}")
        self.__delete_plot_theme(signal)
        self.event_hander.invoke("on_signals_move", signal, "-")

    def add_signal(self, signal: tuple[int, str], subplot_index):
        
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
            if not dpg.does_item_exist(f"{msg_id}_{signal_name}_color"):
                dpg.add_color_value(tag =  f"{msg_id}_{signal_name}_color", parent = "shared_value_registr")
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

        
    def move_signal(self, signal: tuple[int, str], new_subplot_index):

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
        to_remove =  tuple(self.signal_locations.keys())
        for sig in to_remove:
            self.remove_signal(sig)
        self.signal_locations.clear()
        self.first_cursor.hide()
        self.second_cursor.hide()

    def on_signal_change(self, sender, plot_index:str, signal_name: tuple[int, str]):
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

        c_values_in_chunk = (len(x) // step) * step

        chunks_x = x[:c_values_in_chunk].reshape(-1, step)
        chunks_y = y[:c_values_in_chunk].reshape(-1, step)

        min_i = np.argmin(chunks_y, axis = 1)
        max_i = np.argmax(chunks_y, axis = 1)

        rows = np.arange(chunks_y.shape[0])

        first = np.minimum(min_i, max_i)
        second = np.maximum(min_i, max_i)

        xmin = chunks_x[rows, first]
        ymin = chunks_y[rows, first]

        xmax = chunks_x[rows, second]
        ymax = chunks_y[rows, second]

        
        dx = np.column_stack((xmin, xmax)).ravel()
        dy = np.column_stack((ymin, ymax)).ravel()

        tail_x = x[c_values_in_chunk:]
        tail_y  = y[c_values_in_chunk:]

        if len(tail_y):
            tx, ty = self.__min_max_decimate(tail_x, tail_y, 2)
            dx = np.concatenate((dx, tx))
            dy = np.concatenate((dy, ty))
        

        

        return dx, dy

    def save_info(self):
        
        settings = {
            "plot_count": (self.rows, self.cols),
        }

        if self.signal_locations:
            formatted_sig = dict()
            colors = []
            for signal_id, plot_index in self.signal_locations.items():
                formatted_sig['_'.join(str(i) for i in signal_id)] = plot_index
                colors.append(dpg.get_value(f"{signal_id[0]}_{signal_id[1]}_color"))
            
            settings['signals_locations'] = formatted_sig
            settings['signals_color'] = colors
        
        return self.__plot_window_tag, settings

    def load_info(self, data):

        if data['plot_count']:
            r, c = data['plot_count']
            self.set_columns(c)
            self.set_rows(r)
        
        if data['signals_locations']:
            for index, (key, plot_index) in enumerate(data['signals_locations'].items()):
                key = key.split("_")
                key[0] = int(key[0])
                key = tuple(key)
                self.add_signal(key, plot_index)
                self.on_color_change("", data['signals_color'][index], key) 

    def on_cursor_change(self, sender, _, cur_number):
        
        
        if self.selected_cursor == cur_number: 
            self.selected_cursor = None
            if cur_number == 1: self.first_cursor.hide()
            else: self.second_cursor.hide()
        elif not self.selected_cursor:
            if cur_number == 1 and self.first_cursor.mode >= 0: 
                self.first_cursor.hide()
            elif cur_number == 2 and self.second_cursor.mode >= 0: 
                self.second_cursor.hide()
            elif cur_number == 1:
                self.selected_cursor = cur_number
                self.first_cursor.show()
            else: 
                self.selected_cursor = cur_number
                self.second_cursor.show()
        else:
            if cur_number == 1:
                self.selected_cursor = cur_number
                self.first_cursor.hide()
                self.second_cursor.show()
            else:
                self.selected_cursor = cur_number
                self.first_cursor.show()
                self.second_cursor.hide()

        

    
    def on_mouse_click(self):
        """Handeler for cursor set"""
        if not self.selected_cursor and not any(dpg.is_item_hovered(subplot.plot_id) for subplot in self.subplots): return
        if self.selected_cursor == None: return
        elif self.selected_cursor == 1: self.first_cursor.set_static()
        else: self.second_cursor.set_static()
        self.selected_cursor = None
    

    

class PlotWindow(BaseWindow):

    tag = "plot"
    title = "Визуализация данных"


    @classmethod
    def setup(cls, *args, **kwargs):
        cls.logic = PlotLogic(kwargs['data'], kwargs['event_handler'], cls.tag);
        with dpg.child_window(
            tag=cls.tag,
            label=cls.title,
            height=kwargs['height'],
            width=kwargs['width'],
            menubar=True
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
                dpg.add_slider_int(label="Диапазон отображения", default_value=DEFAULT_DISPLAY_RANGE, min_value=MIN_DISPLAY_RANGE, max_value=MAX_DISPLAY_RANGE, callback = cls.logic.on_display_range_change)

            with dpg.group(horizontal = True):
                dpg.add_button(label = "Курсор 1", user_data = 1, callback = cls.logic.on_cursor_change)
                dpg.add_button(label = "Курсор 2", user_data = 2, callback = cls.logic.on_cursor_change)

            with dpg.tooltip(cls.tag, hide_on_activity = True) as tooltip:
                dpg.add_text("", tag = f"{cls.tag}_tooltip", color = (255, 255, 255))
            
            with dpg.theme() as tooltip_theme:
                with dpg.theme_component(dpg.mvTooltip):
                    dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (0, 0, 0, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_Border,(0, 0, 0, 0))
                    dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)

            
            dpg.bind_item_theme(tooltip, tooltip_theme)

            with dpg.handler_registry():
                dpg.add_mouse_click_handler(callback = cls.logic.on_mouse_click)

            cls.logic.rebuild()


