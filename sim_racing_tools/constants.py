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
