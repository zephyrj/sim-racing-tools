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
