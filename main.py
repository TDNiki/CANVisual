from BaseGui import AppGui

def main():
    apps_gui = AppGui()

    while apps_gui.app_is_running():
        apps_gui.update_gui()
        
    apps_gui.exit_gui()

if __name__ == "__main__":

    main()
