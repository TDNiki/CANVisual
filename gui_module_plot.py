import dearpygui.dearpygui as dpg
from window_class import gui_window
from can_interface import available_signals, plot_signals, signal_data

time_auto_fit = False
x_wight = 10
subplot_x_set = 0
subplot_y_set = 0

sublots_axis_item = []
signal_plot_items = []

subplot_signals = {}

drag_lines_1 = []

drag_anotation_1 = []

def set_auto_fit_time():
    if dpg.get_value("auto_x"):
        lim = dpg.get_axis_limits("time")
        plot_time = (lim[1]-lim[0])
        if plot_time < 0.1: plot_time = 0.1
        if plot_time > 100: plot_time = 100
        dpg.set_value("time_slider",plot_time)
        dpg.enable_item("time_slider")
        dpg.show_item("time_slider")
    else:
        dpg.disable_item("time_slider")
        dpg.hide_item("time_slider")

def cal(sender):
    print(sender)


def setup_plot_window(sender):
    global subplot_x_set, subplot_y_set
    dpg.add_menu_bar()
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Save"),
            dpg.add_menu_item(label="Save as"),
            dpg.add_menu_item(label="Import"),
        with dpg.menu(label="Settings"):
                with dpg.menu(label="Subplot settings"):
                    dpg.add_text("WARNING: All plot signal will be clear!",color=(255,255,0,100))
                    subplot_x_set = dpg.add_input_int(label="subplot x",width=80,default_value=1, min_value=1,min_clamped=True,max_value=5,max_clamped=True,callback=config_subplot)
                    subplot_y_set = dpg.add_input_int(label="subplot y",width=80,default_value=1, min_value=1,min_clamped=True,max_value=5,max_clamped=True,callback=config_subplot)

    with dpg.group(horizontal=True):
        dpg.add_button(label="fit x", callback=lambda: dpg.fit_axis_data("time"))
        dpg.add_button(label="fit y", callback=lambda: dpg.fit_axis_data("y_axis"))
        dpg.add_checkbox(label="auto x",tag="auto_x",callback=set_auto_fit_time)
        dpg.add_slider_float(tag="time_slider",format="history = %.1fsec",default_value=10, max_value=100, min_value=0.1, width=200, show=False)
        dpg.add_button(label="|<", callback=add_drag_1)
        # dpg.add_checkbox(label="axis_mode",callback=set_axis_multi_mode)


    with dpg.subplots(1, 1, label="", width=-1, height=-1, link_all_x=True, tag="main_subplot") as subplot_id:
        # dpg.add_plot_legend(outside=True,horizontal=False, location=5)
        # dpg.add_plot_legend()
        for i in range(1):
            with dpg.plot(no_title=True):
                dpg.add_plot_legend()
                if i == 0:
                    dpg.add_plot_axis(dpg.mvXAxis,label='',tag ="time")
                else:
                    dpg.add_plot_axis(dpg.mvXAxis, label='')
                dpg.add_plot_axis(dpg.mvYAxis, label="val", drop_callback=add_signal_to_plot_drop_new, payload_type="plotting")

    # with dpg.plot(label="Signal Plot", height=-1, width=-1,no_title=True, crosshairs=True, 
    #             drop_callback=lambda s, a, u :add_signal_to_plot_drop("y_axis",a), payload_type="plotting", callback=cal, tag="main_plot",show=False):
    #     # optionally create legend
    #     dpg.add_plot_legend(outside=True)

    #     # REQUIRED: create x and y axes
    #     # dpg.add_plot_axis(dpg.mvXAxis, label="time",tag="time")
    #     dpg.add_plot_axis(dpg.mvXAxis, label="")
    #     dpg.add_plot_axis(dpg.mvYAxis, label="val", tag="y_axis", drop_callback=add_signal_to_plot_drop, payload_type="plotting")
    #     dpg.add_plot_axis(dpg.mvYAxis, label="val", tag="y1_axis", drop_callback=add_signal_to_plot_drop, payload_type="plotting",show=False)
    #     dpg.add_plot_axis(dpg.mvYAxis, label="val", tag="y2_axis", drop_callback=add_signal_to_plot_drop, payload_type="plotting",show=False)

    #     dpg.add_drag_line(label="dline2", color=[255, 255, 0, 255], vertical=False, default_value=-2)
    #     # series belong to a y axis
   
def update_plot_window(sender):
    update_plot_new()
    # update_plot_table()
    pass

plot_window = gui_window(name='Plot',menu_label='Plot',window_tag='PlotWindow',setup_callback=setup_plot_window,update_callback=update_plot_window)

def add_signal_to_plot_drop(sender, app_data):
    signal_name = str(app_data[1])
    if signal_name and signal_name not in plot_signals:
        plot_signals.append(signal_name)
        dpg.add_line_series(signal_data[signal_name]['time'], signal_data[signal_name]['value'], label=signal_name, parent=sender,tag=signal_name)
        dpg.add_button(label="Delete", parent=dpg.last_item(), callback=lambda: remove_signal_from_plot_d(signal_name))
        # dpg.fit_axis_data("time")

        if signal_name not in signal_data:
            signal_data[signal_name] = {'time': [], 'value': []}

def add_signal_to_plot_drop_new(sender, app_data):
    global drag_anotation_1
    signal_name = str(app_data[1])
    if signal_name and signal_name not in plot_signals:
        plot_signals.append(signal_name)
    if signal_name not in signal_data:
        signal_data[signal_name] = {'time': [], 'value': []}

    try:   
        
        d = (dpg.add_line_series(signal_data[signal_name]['time'], signal_data[signal_name]['value'], label=signal_name, parent=sender))
        subplot_signals[d] = (signal_name,sender)
        dpg.add_button(label="Delete", parent=dpg.last_item(), callback=lambda: remove_signal_from_plot_d(signal_name,d))
        a=dpg.add_plot_annotation( parent=sender, label=signal_name, default_value=(0.25, 0.25), offset=(0, 0), color=[255, 255, 0, 100],show=False)
        drag_anotation_1.append(a)
    except:
        print("Сос")
    # dpg.fit_axis_data("time")
    print(subplot_signals)

def remove_signal_from_plot_d(sender,parent):
    signal_name = sender
    if signal_name and signal_name in plot_signals:
        # plot_signals.remove(signal_name)
        dpg.delete_item(parent)
        del subplot_signals[parent]
        plot_signals.pop(signal_name)

def config_subplot(sender,app_data):
    global sublots_axis_item,drag_lines_1,drag_anotation_1
    dpg.delete_item("main_subplot")
    plot_signals.clear()
    sublots_axis_item.clear()
    subplot_signals.clear()
    drag_lines_1.clear()
    with dpg.subplots(parent='PlotWindow', rows=dpg.get_value(subplot_x_set),columns=dpg.get_value(subplot_y_set) , label="", 
                      width=-1, height=-1, link_all_x=True, tag="main_subplot") as subplot_id:
        # dpg.add_plot_legend(outside=True,horizontal=False, location=5)
        for i in range(dpg.get_value(subplot_x_set)*dpg.get_value(subplot_y_set)):
            with dpg.plot(no_title=True):
                dpg.add_plot_legend()
                if i == 0:
                    dpg.add_plot_axis(dpg.mvXAxis,label='',tag ="time")
                else:
                    dpg.add_plot_axis(dpg.mvXAxis, label='')
                d = dpg.add_plot_axis(dpg.mvYAxis, label="", drop_callback=add_signal_to_plot_drop_new, payload_type="plotting")
                sublots_axis_item.append(d)
                d=dpg.add_drag_line(label="dline1", color=[255, 255, 0, 100],callback=dragLineCall,show=False,thickness=0.01)
                # a=dpg.add_plot_annotation(label="BL", default_value=(0.25, 0.25), offset=(0, 0), color=[255, 255, 0, 100],show=False)
                drag_lines_1.append((d,[]))
                # subplot_signals[d] = []
    # print(subplot_signals)
    # 

def add_drag_1(sender):
    global drag_anotation_1,drag_lines_1
    for drag in drag_lines_1:
        if dpg.is_item_shown(drag[0]):
            dpg.hide_item(drag[0])
        else:
            lim = dpg.get_axis_limits("time")
            print(lim)
            dpg.set_value(drag[0],(lim[1]-lim[0])/2+lim[0])

            dpg.show_item(drag[0])
        i=0
        for an in drag_anotation_1:
            dpg.set_value(an,((lim[1]-lim[0])/2+lim[0],0.25*i))
            dpg.show_item(an)
            i=i+1
            

def dragLineCall(sender,app_data,user):
    global drag_lines_1
    print( drag_lines_1)
    for drag in drag_lines_1:
        dpg.set_value(drag[0],dpg.get_value(sender))
    for an in drag_anotation_1:
            dpg.set_value(an,(dpg.get_value(sender),0.25))


def set_axis_multi_mode(sender):
        if dpg.get_value(sender):
            # dpg.add_plot_axis(parent="main_plot", axis=dpg.mvXAxis, label="val", tag="y1_axis", drop_callback=add_signal_to_plot_drop, payload_type="plotting")
            # dpg.add_plot_axis(parent="main_plot",axis=dpg.mvXAxis, label="val", tag="y2_axis", drop_callback=add_signal_to_plot_drop, payload_type="plotting")
            dpg.show_item("y1_axis")
            dpg.show_item("y2_axis")
        else:
            # dpg.delete_item("y1_axis")
            # dpg.delete_item("y2_axis")
            dpg.hide_item("y1_axis")
            dpg.hide_item("y2_axis")
# def update_plot_table():
#         # Удаляем старые строки, чтобы избежать дублирования
#     rows = dpg.get_item_children('PlotTable', 1)
#     for row in rows:
#         dpg.delete_item(row)

#     # Добавляем распарсенные сигналы
    
#     for signal_name in plot_signals:
#         with dpg.table_row(parent='PlotTable'):
#             # dpg.add_text(signal_name)
#             dpg.add_button(label=signal_name, parent=dpg.last_item(), callback=lambda: remove_signal_from_plot_d(signal_name))
#             last_val = signal_data[signal_name]['value'][-1]
#             dpg.add_text(f"{last_val:.2f}")  # Значение сигнала

def update_plot():
    global x_wight,sublots_axis_item
    lim = dpg.get_axis_limits("time")
    plot_time = round((lim[1]-lim[0])*10)/10
    x_wight = plot_time
    dpg.delete_item('SignalPlot', children_only=True)

    for signal_name in plot_signals:
        if signal_data[signal_name]['time']:
            try:
                # data_t = signal_data[signal_name]['time'][-x_wight:]
                # data_v = signal_data[signal_name]['value'][-x_wight:]
                data_t = signal_data[signal_name]['time']
                data_v = signal_data[signal_name]['value']
                last_val = data_v[-1]
                # Добвить обновление как в симулинке
                if dpg.get_value("auto_x"):
                    
                    x_wight = dpg.get_value('time_slider')
                    last_t = signal_data[signal_name]['time'][-1]
                    # print(x_wight)
                    dpg.set_axis_limits("time",last_t-x_wight,last_t)
                    
                    # dpg.fit_axis_data("time")
                else:
                    dpg.set_axis_limits_auto("time")
                # dpg.set_item_label(signal_name, signal_name +"="+f"{last_val:.1f}")

                dpg.set_value(signal_name, [data_t, data_v])

         

            except Exception as e:
                # print(f"Error adding line series for {signal_name}: {e}")
                pass

def update_plot_new():
    global x_wight, sublots_axis_item
    lim = dpg.get_axis_limits("time")
    plot_time = round((lim[1]-lim[0])*10)/10
    x_wight = plot_time
    dpg.delete_item('SignalPlot', children_only=True)
    indx0 = 1
    indx1 = 1
    for signal_name in plot_signals:
        if signal_data[signal_name]['time']:
            try:
                # data_t = signal_data[signal_name]['time'][-plot_time-10:] #вывод окна оптимизированней, чем все данные с ограниченной видимостью - стэк гуи не пеерполянется ненужной инфой, если она не нужна на грфике
                # data_v = signal_data[signal_name]['value'][-plot_time-10:]
                



                # while signal_data[signal_name]['time'][indx1] < lim[1]:
                #     if indx1 < len(signal_data[signal_name]['time'])-1:
                #         indx1 = indx1+1
                #     else:
                #         indx1 = len(signal_data[signal_name]['time'])-1
                #         break

                # while signal_data[signal_name]['time'][indx1-1] > lim[1]:
                #     if indx1 > 0:
                #         indx1 = indx1-1
                #     else:
                #         break

                # while signal_data[signal_name]['time'][indx0] < lim[0]:
                #     if indx0 < indx1:
                #         indx0 = indx0+1
                #     else:
                #         indx0 = indx1-1
                #         break

                # while signal_data[signal_name]['time'][indx0-1] > lim[0]:
                #     if indx0 > 0:
                #         indx0 = indx0-1
                #     else:
                #         break

                
                # for time_data in signal_data[signal_name]['time']:
                #     indx1 = signal_data[signal_name]['time'].index(time_data)
                #     if time_data > lim[1]:
                #         break

                # indx0 = indx1
                # while indx0 != 0:
                #     if signal_data[signal_name]['time'][indx0] < lim[0]:
                #         break
                #     indx0 = indx0-1
                # for time_data in signal_data[signal_name]['time'][:indx1].reverse():
                #     indx0 = signal_data[signal_name]['time'].index(time_data)
                #     if time_data < lim[0]:
                #         break

                # print(lim[0],"->",signal_data[signal_name]['time'][indx0], lim[1],"->",signal_data[signal_name]['time'][indx1])


                # data_t = signal_data[signal_name]['time'][indx0:indx1]
                # data_v = signal_data[signal_name]['value'][indx0:indx1]

                data_t = signal_data[signal_name]['time']
                data_v = signal_data[signal_name]['value']
        
                last_val = data_v[-1] #TODO: Добавить оптимизацию точек при большом количестве выводимых данных (каждая втора/третья/10я)
                # Добвить обновление как в симулинке
                if dpg.get_value("auto_x"):
                    
                    x_wight = dpg.get_value('time_slider')
                    last_t = signal_data[signal_name]['time'][-1]
                    # print(x_wight)
                    dpg.set_axis_limits("time",last_t-x_wight,last_t) #ОШИБКА!
                    
                    # dpg.fit_axis_data("time") 
                else:
                    dpg.set_axis_limits_auto("time")
                # dpg.set_item_label(signal_name, signal_name +"="+f"{last_val:.1f}")
                for obj, sig in subplot_signals.items():
                        if sig[0] == signal_name:
                            dpg.set_value(obj, [data_t, data_v])

            except Exception as e:
                # print(f"Error adding line series for {signal_name}: {e}")
                pass