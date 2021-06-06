"""
Copyright (c):
2021 zephyrj
zephyrj@protonmail.com

This file is part of sim-racing-tools.

sim-racing-tools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

sim-racing-tools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with sim-racing-tools. If not, see <https://www.gnu.org/licenses/>.
"""

import sys

if sys.platform == "win32":
    from win32com.shell import shell, shellcon

import sys
import os
import sim_racing_tools.constants as constants
import sim_racing_tools.utils as utils

GAME_NAME = "Automation"
GAME_ID = 293760

if sys.platform == "win32":
    WINDOWS_PERSONAL_DIRECTORY = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
else:
    pass

USER_GAME_DATA_PATH = os.sep.join(["My Games", GAME_NAME])
BEAMNG_MOD_PATH = os.sep.join(["BeamNG.drive", "mods"])
BEAMNG_LATEST_VERSION_SHORTCUT = os.sep.join(["BeamNG.drive", "latest.lnk"])
SANDBOX_DB_NAME = "Sandbox_openbeta.db"

ENGINE_JBEAM_NAME = "camso_engine.jbeam"


def get_install_dir():
    return os.path.join(constants.get_game_install_path(), GAME_NAME)


def get_user_documents_dir():
    if sys.platform == "linux" or sys.platform == "linux2":
        return os.path.join(constants.get_wine_prefix_path(GAME_ID),
                            os.sep.join(["drive_c", "users", "steamuser", "My Documents"]))
    else:
        return shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)


def get_user_appdata_local():
    return shell.SHGetFolderPath(0, shellcon.CSIDL_LOCAL_APPDATA, 0, 0)


def get_userdata_path():
    return os.path.join(get_user_documents_dir(), USER_GAME_DATA_PATH)


def get_sandbox_db_path():
    return os.path.join(get_userdata_path(), SANDBOX_DB_NAME)


def get_beamng_export_paths():
    locations = [os.path.join(get_user_documents_dir(), BEAMNG_MOD_PATH)]
    latest_shortcut_path = os.path.join(get_user_appdata_local(), BEAMNG_LATEST_VERSION_SHORTCUT)
    if os.path.exists(latest_shortcut_path):
        import sim_racing_tools.utils as utils
        locations.insert(0, os.path.join(utils.read_win_shortcut(latest_shortcut_path), 'mods'))
    return locations


def get_exported_car_data_dir(beamng_mod_folder_name):
    found_path = None
    for mod_location in get_beamng_export_paths():
        potential_path = os.path.join(mod_location, beamng_mod_folder_name)
        if os.path.isdir(potential_path):
            found_path = potential_path
            break
        zip_filename = os.path.join(os.path.dirname(potential_path), os.path.basename(potential_path) + ".zip")
        if os.path.exists(zip_filename):
            utils.unzip_file(zip_filename)
            found_path = potential_path
            break

    if not found_path:
        raise ValueError(f"Can't find {beamng_mod_folder_name} in {','.join(get_beamng_export_paths())}")
    return os.path.join(found_path, os.sep.join(["vehicles", beamng_mod_folder_name]))


class Installation(object):
    def __init__(self, custom_root=None):
        self.on_linux = sys.platform == "linux" or sys.platform == "linux2"
        self.installation_root = get_install_dir() if not custom_root else custom_root
