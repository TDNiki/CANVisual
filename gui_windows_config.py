import json
import os

from dataclasses import dataclass
from dataclasses import asdict



class WindowsConfigManager:

    __configs = []
    __updated: bool = False

    def __init__(self, path: str):
        self.__path = path
        
        if os.path.exists(self.__path):
            with open(self.__path, "r", encoding="utf-8") as file:
                if not os.path.getsize(self.__path) == 0: 
                    self.__configs = [WindowConfig(**obj) for obj in json.load(file)]
        else:
            with open(self.__path, "x"):
                ...
                

    def get_configs(self) -> dict[str, object]:
        config_dict = {}
        for config in self.__configs:
            config_dict[config.id] = config
        return config_dict
    

    def set_config(
        self,
        id: str,
        title: str,
        size: tuple[float, float],
        pos: tuple[float, float],
        ):

        wconfig = WindowConfig(
            id = id,
            title = title,
            size = size,
            pos = pos)
        
        for config in self.__configs:
            if config.id == id:
                config = wconfig
                self.__updated = True
                return;

        self.__configs.append(wconfig)
        self.__updated = True
        return;

    def del_config(self, id: str):
        for config in self.__configs:
            if config.id == id:
                self.__configs.remove(config)
                return;

        raise KeyError("No such config")

    def __del__(self):
        if self.__updated:
            with open(self.__path, 'w', encoding="utf-8") as file:
                json.dump([asdict(obj) for obj in self.__configs], file, ensure_ascii=False, indent=4)
            
        






@dataclass
class WindowConfig:
    """Settings for the window"""

    id: str
    title: str
    size: tuple[float, float]
    pos: tuple[float, float]


"""a = WindowsConfigManager("C:\\Users\\Никита\\Desktop\\camozzi\\CANVisual\\guiconfigs.json")

a.set_config(
    id = "signals",
    title = "Сигналы",
    size = (0.3, 0.4),
    pos = (0, 0.5)
)"""