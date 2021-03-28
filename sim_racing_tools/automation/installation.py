import sys

if sys.platform == "win32":
    from win32com.shell import shell, shellcon

import automation.constants as constants

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


def get_beamng_export_path():
    return os.path.join(get_user_documents_dir(), BEAMNG_EXPORT_PATH)


class Installation(object):
    def __init__(self, custom_root=None):
        self.on_linux = sys.platform == "linux" or sys.platform == "linux2"
        self.installation_root = get_install_dir() if not custom_root else custom_root

