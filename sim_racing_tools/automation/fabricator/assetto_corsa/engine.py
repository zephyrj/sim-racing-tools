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
import glob
import math

import automation.installation as installation
import automation.sandbox as sandbox
import sim_racing_tools.utils as utils
from automation.car_file_decoder import CarFile
from automation.jbeam import Parser as JBeamParser

from assetto_corsa.car.engine import Engine, TurboSection, FROM_COAST_REF, EngineSources, EngineUIData

LATEST_VERSION = 1


class EngineParameterCalculatorV1(object):
    def __init__(self, car_file_data, engine_db_data, jbeam_engine_data):
        self.car_file_data = car_file_data
        self.engine_db_data = engine_db_data
        self.jbeam_engine_data = jbeam_engine_data

    @property
    def inertia(self):
        return get_inertia_v1(self.jbeam_engine_data)

    @property
    def idle_speed(self):
        return get_idle_speed_v1(self.engine_db_data)

    @property
    def limiter(self):
        return get_limiter_v1(self.engine_db_data)

    @property
    def max_rpm_without_damage(self):
        # TODO work out how to use the min acceptable value from Automation based
        # TODO on the engine components and their quality
        return self.limiter + 200

    @property
    def engine_damage_rate_over_max_rpm(self):
        # TODO work out some kind of translation from Quality/MTTF to this
        return 1

    @property
    def fuel_consumption(self):
        return get_fuel_consumption_v1(self.engine_db_data)

    def set_engine_power_info(self, engine):
        set_power_info_v1(engine, self.engine_db_data)

    def set_engine_coast_info(self, engine):
        set_coast_info_v1(engine, self.engine_db_data, self.jbeam_engine_data)


version_to_parameter_selector = {1: EngineParameterCalculatorV1}


class DefaultEngineFabricator(object):
    def __init__(self, version=None):
        self.version = LATEST_VERSION if not version else version

    def create_from_beamng_mod(self, beamng_mod_folder_name):
        data_dir = get_mod_data_dir(beamng_mod_folder_name)
        car_data = load_car_file_data(data_dir)
        engine_db_data = sandbox.get_engine_data(car_data['Car']['Variant']['UID'])
        jbeam_engine_data = JBeamParser().naive_parse(os.path.join(data_dir, installation.ENGINE_JBEAM_NAME))
        params = version_to_parameter_selector[self.version](car_data, engine_db_data, jbeam_engine_data)

        engine = Engine()
        set_metadata(engine, engine_db_data)
        set_ui_data(engine, engine_db_data)
        engine.inertia = params.inertia
        engine.minimum = params.idle_speed
        engine.limiter = params.limiter
        engine.rpm_threshold = params.max_rpm_without_damage
        engine.rpm_damage_k = params.engine_damage_rate_over_max_rpm
        engine.fuel_consumption = params.fuel_consumption
        params.set_engine_power_info(engine)
        params.set_engine_coast_info(engine)
        return engine


def set_metadata(ac_engine, engine_db_data):
    ac_engine.metadata.source = EngineSources.AUTOMATION
    ac_engine.metadata.mass_kg = round(engine_db_data["Weight"])
    ac_engine.metadata.info_dict["automation-version"] = engine_db_data["GameVersion"]
    ac_engine.metadata.info_dict["automation-data"] = engine_db_data


def set_ui_data(ac_engine, engine_db_data):
    ui_data = EngineUIData()
    ui_data.torque_curve = [[str(round(rpm)), str(round(engine_db_data["torque-curve"][idx]))]
                            for idx, rpm in enumerate(engine_db_data["rpm-curve"])]
    ui_data.max_torque = f"{round(engine_db_data['PeakTorque'])}Nm"
    ui_data.power_curve = [[str(round(rpm)), str(round(utils.kw_to_bhp(engine_db_data["power-curve"][idx])))]
                           for idx, rpm in enumerate(engine_db_data["rpm-curve"])]
    ui_data.max_power = f"{round(utils.kw_to_bhp(engine_db_data['PeakPower']))}bhp"
    ac_engine.metadata.ui_data = ui_data


def get_inertia_v1(jbeam_engine_data):
    return round(jbeam_engine_data["Camso_Engine"]["mainEngine"]["inertia"], 3)


def get_idle_speed_v1(engine_db_data):
    return round(engine_db_data["IdleSpeed"] if engine_db_data["IdleSpeed"] >= engine_db_data["rpm-curve"][0] else
                 engine_db_data["rpm-curve"][0])


def get_limiter_v1(engine_db_data):
    return round(engine_db_data["MaxRPM"])


def get_fuel_consumption_v1(engine_db_data):
    # From https://buildingclub.info/calculator/g-kwh-to-l-h-online-from-gram-kwh-to-liters-per-hour/
    # Fuel Use (l/h) = (Engine Power (kW) * BSFC@Power) / Fuel density kg/m3
    fuel_use_per_hour = (engine_db_data["PeakPower"] * engine_db_data["Econ"]) / 750
    fuel_use_per_sec = fuel_use_per_hour / 3600

    # Assetto Corsa calculation:
    # In one second the consumption is (rpm*gas*CONSUMPTION)/1000
    # fuel_use_per_sec = (engine_data["PeakPowerRPM"] * 1 * C) / 1000
    # fuel_use_per_sec * 1000 =  engine_data["PeakPowerRPM"]*C
    # C = (fuel_use_per_sec * 1000) / engine_data["PeakPowerRPM"]
    # In theory this is being generous as the Econ value is an average over all engine RPMs
    # rather than the consumption at max power but the values still seem to be higher than
    # the values of other AC engines
    # TODO refine this
    return round((fuel_use_per_sec * 1000) / engine_db_data["PeakPowerRPM"], 4)


def set_power_info_v1(ac_engine, engine_db_data):
    if engine_db_data["AspirationType"].startswith("Aspiration_Natural"):
        write_na_torque_curve(ac_engine, engine_db_data)
    else:
        write_turbo_torque_curve(ac_engine, engine_db_data)
        create_turbo_sections_v1(ac_engine, engine_db_data)
        ac_engine.metadata.boost_curve = {round(rpm): engine_db_data["boost-curve"][idx]
                                          for idx, rpm in enumerate(engine_db_data["rpm-curve"])}

    rpm_increments = engine_db_data["rpm-curve"][-1] - engine_db_data["rpm-curve"][-2]
    ac_engine.power_info.rpm_curve.append(round(engine_db_data["rpm-curve"][-1] + rpm_increments))
    ac_engine.power_info.torque_curve.append(round(ac_engine.power_info.torque_curve[-1] / 2))
    ac_engine.power_info.rpm_curve.append(round(engine_db_data["rpm-curve"][-1] + (rpm_increments * 2)))
    ac_engine.power_info.torque_curve.append(0)


def set_coast_info_v1(engine, engine_db_data, jbeam_engine_data):
    """
    The following data is available from the engine.jbeam exported file
    The dynamic friction torque on the engine in Nm/s.
    This is a friction torque which increases proportional to engine AV (rad/s).
    AV = (2pi * RPM) / 60
    friction torque = (AV * dynamicFriction) + 2*staticFriction
    dynamicFriction = brakingcoefRPS/2pi from pre 0.7.2.
    So dynamicFriction*2pi = braking_coefficientRPS
    friction torque = (ref_rpm * (brakingCoefficientRPS / 60)) + staticFriction

    #### NOTE ####
    I'm assuming that all of the sources of friction are being taken into account in the BeamNG parameters used above
    this may not be correct.
    """
    dynamic_friction = jbeam_engine_data["Camso_Engine"]["mainEngine"]["dynamicFriction"]
    angular_velocity_at_max_rpm = (engine_db_data["MaxRPM"] * 2 * math.pi) / 60
    friction_torque = (angular_velocity_at_max_rpm * dynamic_friction) + \
                      (2 * jbeam_engine_data["Camso_Engine"]["mainEngine"]["friction"])

    engine.coast_curve.curve_data_source = FROM_COAST_REF
    engine.coast_curve.reference_rpm = round(engine_db_data["MaxRPM"])
    engine.coast_curve.torque = round(friction_torque)
    engine.coast_curve.non_linearity = 0


def write_na_torque_curve(engine, engine_data):
    for idx in range(0, len(engine_data["rpm-curve"])):
        engine.power_info.rpm_curve.append(round(engine_data["rpm-curve"][idx]))
        engine.power_info.torque_curve.append(round(engine_data["torque-curve"][idx]))


def write_turbo_torque_curve(engine, engine_data):
    for idx in range(0, len(engine_data["rpm-curve"])):
        engine.power_info.rpm_curve.append(round(engine_data["rpm-curve"][idx]))
        boost_pressure = max(0, engine_data["boost-curve"][idx])
        engine.power_info.torque_curve.append(round(engine_data["torque-curve"][idx] / (1+boost_pressure)))


def create_turbo_sections_v1(engine, engine_data):
    t = TurboSection()
    t.cockpit_adjustable = 0
    t.max_boost = round(engine_data["PeakBoost"], 2)
    t.display_max_boost = utils.round_up(engine_data["PeakBoost"], 1)
    t.wastegate = round(engine_data["PeakBoost"], 2)
    t.reference_rpm = round(engine_data["PeakBoostRPM"])
    # TODO work out how to better approximate these
    t.lag_dn = 0.99
    t.lag_up = 0.965
    t.gamma = 2.5
    engine.turbo.sections.append(t)


def get_mod_data_dir(beamng_mod_folder_name):
    car_export_path = os.path.join(installation.get_beamng_export_path(),
                                   beamng_mod_folder_name)
    if not os.path.isdir(car_export_path):
        utils.unzip_file(os.path.join(os.path.dirname(car_export_path),
                                      os.path.basename(car_export_path) + ".zip"))
    return os.path.join(car_export_path, os.sep.join(["vehicles", beamng_mod_folder_name]))


def load_car_file_data(directory):
    try:
        car_file = glob.glob(f"{directory}/*.car")[0]
    except IndexError:
        raise RuntimeError(f"No .car file present in {directory}")

    with open(car_file, "rb") as f:
        car = CarFile(os.path.basename(car_file), f.read())
        car.parse()
        return car.get_data()
