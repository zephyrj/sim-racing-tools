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
import os
from pathlib import Path

USER_HOME_DIR = str(Path.home())
WINDOWS_STEAM_LOCAL_FILE_PATH = 'C:\Program Files (x86)\Steam'
LINUX_STEAM_LOCAL_FILE_PATH = os.path.join(USER_HOME_DIR, ".steam/debian-installation")
LINUX_WINE_PREFIX_PATH = os.path.join(LINUX_STEAM_LOCAL_FILE_PATH, os.sep.join(["steamapps", "compatdata"]))

STEAM_GAME_INSTALL_PATH = os.sep.join(["steamapps", "common"])


def get_game_install_path():
    if sys.platform == "linux" or sys.platform == "linux2":
        return os.path.join(LINUX_STEAM_LOCAL_FILE_PATH, STEAM_GAME_INSTALL_PATH)
    else:
        return os.path.join(WINDOWS_STEAM_LOCAL_FILE_PATH, STEAM_GAME_INSTALL_PATH)


def get_wine_prefix_path(game_id):
    return os.path.join(LINUX_WINE_PREFIX_PATH, os.sep.join([str(game_id), "pfx"]))
