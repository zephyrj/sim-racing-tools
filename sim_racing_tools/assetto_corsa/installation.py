import os
import sys

import sim_racing_tools.constants as constants


GAME_NAME = "assettocorsa"
GAME_ID = 244210

CARS_PATH = os.sep.join(["content", "cars"])
SFX_PATH = os.sep.join(["content", "sfx"])

DATA_FOLDER_NAME = "data"
ENCODED_DATA_FILENAME = "data.acd"
SFX_GUID_FILENAME = "GUIDs.txt"


def get_install_dir():
    return os.path.join(constants.get_game_install_path(), GAME_NAME)


class Installation(object):
    def __init__(self, custom_root=None):
        self.on_linux = sys.platform == "linux" or sys.platform == "linux2"
        self.installation_root = get_install_dir() if not custom_root else custom_root
        self._build_installed_car_map()
        self._build_sfx_guid_map()

    def get_installed_cars_path(self):
        return os.path.join(self.installation_root, CARS_PATH)

    def _build_installed_car_map(self):
        self.installed_cars = set()
        _, dirnames, _ = next(os.walk(self.get_installed_cars_path()))
        self.installed_cars = {name for name in dirnames}

    def _build_sfx_guid_map(self):
        self.sfx_dict_by_folder_name = dict()
        self.sfx_bank_dict = dict()
        root_gui_file_path = os.path.join(self.installation_root,
                                          os.sep.join([SFX_PATH, SFX_GUID_FILENAME]))
        with open(root_gui_file_path, "r") as main_sfx_guid_file:
            for line in main_sfx_guid_file:
                line_data = line.split()
                guid = line_data[0]
                sfx_line = line_data[1]
                if sfx_line.startswith("event"):
                    folder_name = sfx_line.split(":")[1].split("/")[2]
                    if folder_name not in self.sfx_dict_by_folder_name:
                        self.sfx_dict_by_folder_name[folder_name] = list()
                    self.sfx_dict_by_folder_name[folder_name].append(line)
                elif sfx_line.startswith("bank"):
                    self.sfx_bank_dict[sfx_line.split("/")[1]] = guid

    def _generate_data_dir(self, new_car_path, existing_car_acd_path):
        # todo
        pass
