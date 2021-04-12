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

import pandas as pd
import plotly.graph_objects as go

import sim_racing_tools.assetto_corsa.installation as installation


def main():
    car_name = sys.argv[1]
    ac_install = installation.Installation()
    car_path = os.path.join(ac_install.get_installed_cars_path(), car_name)
    if not os.path.isdir(car_path):
        print("No such car")
        return 1

    expected_boost_df = pd.read_csv(os.path.join(car_path, "data", "boost.csv"))
    actual_boost_df = pd.read_csv(os.path.join(car_path, "data", "boost_tracker.csv"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=expected_boost_df['rpm'], y=expected_boost_df['boost_bar'],
                             mode='lines+markers',
                             name='Expected boost'))
    fig.add_trace(go.Scatter(x=actual_boost_df['rpm'], y=actual_boost_df['boost_bar'],
                             mode='lines+markers',
                             name='Actual boost'))
    fig.show()


if __name__ == '__main__':
    main()
