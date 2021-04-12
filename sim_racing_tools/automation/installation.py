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
import constants

GAME_NAME = "Automation"
GAME_ID = 293760

if sys.platform == "win32":
    WINDOWS_PERSONAL_DIRECTORY = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
else:
    pass

USER_GAME_DATA_PATH = os.sep.join(["My Games", GAME_NAME])
BEAMNG_EXPORT_PATH = os.sep.join(["BeamNG.drive", "mods"])
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


def get_userdata_path():
    return os.path.join(get_user_documents_dir(), USER_GAME_DATA_PATH)


def get_sandbox_db_path():
    return os.path.join(get_userdata_path(), SANDBOX_DB_NAME)


def get_beamng_export_path():
    return os.path.join(get_user_documents_dir(), BEAMNG_EXPORT_PATH)


class Installation(object):
    def __init__(self, custom_root=None):
        self.on_linux = sys.platform == "linux" or sys.platform == "linux2"
        self.installation_root = get_install_dir() if not custom_root else custom_root

