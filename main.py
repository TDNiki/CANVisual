from threading import Thread
from can_interface import deinit_bus, receive_can_messages, stop_event
from gui import AppGui

def main():
    apps_gui = AppGui()

    while apps_gui.app_is_running():
        apps_gui.update_gui()
        
    deinit_bus()
    stop_event.set()  # Убедитесь, что поток остановлен при выходе из программы

    apps_gui.exit_gui()

if __name__ == "__main__":

    main()
