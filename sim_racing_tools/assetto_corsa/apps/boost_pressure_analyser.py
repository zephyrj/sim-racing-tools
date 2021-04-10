# ##############################################################
# # Kunos Simulazioni
# # AC Python tutorial 04 : Get data from AC
# #
# # To activate create a folder with the same name as this file
# # in apps/python. Ex apps/python/tutorial01
# # Then copy this file inside it and launch AC
# #############################################################
#
import ac
import acsys
import sys
import os
import platform
from collections import OrderedDict


if platform.architecture()[0] == "64bit":
    sysdir = "stdlib64"
else:
    sysdir = "stdlib"

ac.console(os.getcwd())
add_path = os.path.join(os.path.dirname(__file__), sysdir)
ac.console("Path to add {}".format(add_path))
sys.path.insert(0, add_path)
os.environ['PATH'] = os.environ['PATH'] + ";."

from third_party.sim_info import info

appWindow = 0
active_label = None
car_label = None
boost_map = OrderedDict()
app_name = "Boost Tracker"
active = False


# This function gets called by AC when the Plugin is initialised
# The function has to return a string with the plugin name
def acMain(ac_version):
    global appWindow, app_name, active_label, car_label
    appWindow = ac.newApp(app_name)
    ac.setSize(appWindow, 100, 100)
    ac.addRenderCallback(appWindow, onFormRender)
    ac.addOnAppActivatedListener(appWindow, on_activate)
    ac.addOnAppDismissedListener(appWindow, on_deactivate)
    car_label = ac.addLabel(appWindow, info.static.carModel)
    ac.setPosition(car_label, 25, 25)
    active_label = ac.addLabel(appWindow, "INACTIVE")
    ac.setPosition(active_label, 25, 50)
    return app_name


def acUpdate(delta):
    """
    This is where you update your app window ( != OpenGL graphics )
    such as : labels , listener , ect ...
    """
    global active, boost_map, active_label
    if not active or ac.getCarState(0, acsys.CS.Gas) < 1:
        ac.setText(active_label, "INACTIVE")
        return
    ac.setText(active_label, "ACTIVE")
    rpm = ac.getCarState(0, acsys.CS.RPM)
    boost = ac.getCarState(0, acsys.CS.TurboBoost)
    boost_map[rpm] = boost


def acShutdown():
    global active
    if active:
        active = False
        _write_results_file()


def on_activate(delta):
    global active, boost_map, car_label
    boost_map.clear()
    ac.setText(car_label, info.static.carModel)
    active = True


def on_deactivate(delta):
    global active, boost_map
    active = False
    _write_results_file()


def _write_results_file():
    output_dir = _get_car_directory(info.static.carModel)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, "boost_tracker.csv"), "w+") as f:
        f.write("rpm,boost_bar\n")
        for rpm, boost in boost_map.items():
            f.write("{},{}\n".format(rpm, boost))


def _get_car_directory(car_name):
    return os.path.join(get_game_install_path(), "assettocorsa", "content", "cars", car_name, "data")


USER_HOME_DIR = os.path.expanduser("~")
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


def onFormRender(delta):
    pass
