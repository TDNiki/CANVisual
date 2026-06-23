from threading import Thread
from can_interface import deinit_bus, receive_can_messages, stop_event
from gui import setup_gui, update_gui,app_is_running,exit_gui

def main():
    setup_gui()
    # initialize_can_bus()

    # Запуск потока для приема сообщений
    receive_thread = Thread(target=receive_can_messages, daemon=True)
    receive_thread.start()

    while app_is_running():
        update_gui()
        
    deinit_bus()
    stop_event.set()  # Убедитесь, что поток остановлен при выходе из программы
    receive_thread.join()
    exit_gui()

if __name__ == "__main__":

    main()
