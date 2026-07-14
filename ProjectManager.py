import json
import os

from settings import FILE_META_NAME
from datetime import datetime



class ProjectData:
    
    def __init__(self, data: dict = None):
        if data is not None and type(data) is not dict: raise TypeError("Incorrect type given")
        self.__settings = data or {}
    
    def add_settings(self, id: str, data):
        if type(id) is str and len(data) > 0:

            if not id in self.__settings:
                self.__settings[id] = data
            else:
                for key, value in data.items():
                    if key not in self.__settings[id]: self.__settings[id][key] = value
        else: raise TypeError("id must be str type and not empty kwargs params")
    
    def edit_settings(self, id: str, data: dict,  add_new = True):
        if id not in self.__settings and add_new: self.add_settings(id, data)
        for key, value in data.items():
            self.__settings[id][key] = value
    
    def remove_settings(self, id: str, filter: tuple = None):
        """filter: kwargs keys to remove, if none - remove all settings with following id"""
        if id not in self.__settings: raise KeyError(f"{id} doesn't exists")
        if filter is not None:
            for key in filter:
                self.__settings[id].pop(key)
        else:
            self.__settings.pop(state_id)
    
    def export_settings(self): return self.__settings

    def get_settings(self, id: str): return self.__settings.get(id)



class ProjectManager:


    __data_ext = ".json"

    def __init__(self, base_path_meta: str = FILE_META_NAME, max_size: int = 10):

        self.full_path_meta = os.path.join(os.getcwd(), base_path_meta + self.__data_ext)
        self.max_size = max_size
        self.__import_meta()

    def __import_meta(self):

        try:
            with open(self.full_path_meta, mode = 'r', encoding="utf-8") as data:
                self.meta = json.load(data)
        except (FileNotFoundError, json.JSONDecodeError):
            self.meta = {}

            with open(self.full_path_meta, "w", encoding="utf-8") as data:
                json.dump({}, data)
                

    def get_meta_data(self) -> dict | None:
        return self.meta
    
    def set_meta_data(self, project_name: str, project_path: str, time_last: float = None):
        if not time_last: time_last = datetime.now().timestamp()
        
        self.meta[project_name] = {
            'file_path_name': project_path,
            'time_last': time_last
        }
    
    def save_project(self, path: str, project: ProjectData):
        
        with open(path, 'w', encoding = 'utf-8') as data:
            json.dump(project.export_settings(), data, indent = 4)
        
        self.set_meta_data(os.path.basename(path), path)

        
      
    
    def export_meta_data(self):
        if self.meta:
            while len(self.meta) > self.max_size:
                oldest_key = min(self.meta, key=lambda k: self.meta[k]["time_last"])
                self.meta.pop(oldest_key)

            with open(self.full_path_meta, "w", encoding="utf-8") as data:
                json.dump(self.meta, data, indent=4)

    def open_project(self, path: str):
        try:
            with open(path, mode = 'r', encoding="utf-8") as data:
                    return ProjectData(json.load(data))
            
            self.set_meta_data(os.path.basename(path), path)
        except Exception as err:
            raise Exception(f"Can't read this format of file, be sure of correct ext or pattern of save file: {err}")
        
    
    def init_project(self):
        return ProjectData()