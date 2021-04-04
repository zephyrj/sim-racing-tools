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
import math

appWindow = 0
active_label = None
boost_map = dict()
app_name = "Boost Tracker"
active = False


# This function gets called by AC when the Plugin is initialised
# The function has to return a string with the plugin name
def acMain(ac_version):
    global appWindow, app_name, active_label
    appWindow = ac.newApp(app_name)
    ac.setSize(appWindow, 100, 100)
    ac.addRenderCallback(appWindow, onFormRender)
    ac.addOnAppActivatedListener(appWindow, on_activate)
    ac.addOnAppDismissedListener(appWindow, on_deactivate)
    active_label = ac.addLabel(appWindow, "INACTIVE")
    ac.setPosition(active_label, 25, 25)
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


def on_activate(delta):
    global active, boost_map
    boost_map.clear()
    active = True


def on_deactivate(delta):
    global active, boost_map
    active = False
    with open("boost.csv", "w+") as f:
        for rpm, boost in boost_map.items():
            f.write("{},{}\n".format(rpm, boost))


def onFormRender(delta):
    pass
