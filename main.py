from threading import Thread
from can_interface import deinit_bus, receive_can_messages, stop_event
from gui import AppGui

def main():
    apps_gui = AppGui()
    # initialize_can_bus()

    # Запуск потока для приема сообщений
    #receive_thread = Thread(target=receive_can_messages, daemon=True)
    #receive_thread.start()

    while apps_gui.app_is_running():
        apps_gui.update_gui()
        
    deinit_bus()
    stop_event.set()  # Убедитесь, что поток остановлен при выходе из программы
    #receive_thread.join()
    apps_gui.exit_gui()

if __name__ == "__main__":

    main()
