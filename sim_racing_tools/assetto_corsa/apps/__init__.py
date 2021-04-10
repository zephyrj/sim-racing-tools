import os
import shutil
import sim_racing_tools.assetto_corsa.installation as installation

BOOST_TRACKER_APP_NAME = "boost_pressure_analyser"


def install_boost_tracker():
    install_dir = os.path.join(installation.get_install_dir(), "apps", "python", BOOST_TRACKER_APP_NAME)
    if os.path.isdir(install_dir):
        shutil.rmtree(install_dir)
    os.mkdir(install_dir)
    shutil.copytree(os.path.join(os.path.dirname(__file__), "stdlib"), os.path.join(install_dir, "stdlib"))
    shutil.copytree(os.path.join(os.path.dirname(__file__), "stdlib64"), os.path.join(install_dir, "stdlib64"))
    shutil.copytree(os.path.join(os.path.dirname(__file__), "third_party"), os.path.join(install_dir, "third_party"))
    shutil.copy(os.path.join(os.path.dirname(__file__), BOOST_TRACKER_APP_NAME + ".py"),
                os.path.join(install_dir, BOOST_TRACKER_APP_NAME + ".py"))
