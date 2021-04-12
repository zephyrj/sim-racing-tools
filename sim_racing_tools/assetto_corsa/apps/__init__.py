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
