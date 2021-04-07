import os
import glob
import math

import automation.installation as installation
import automation.sandbox as sandbox
import sim_racing_tools.utils as utils
from automation.car_file_decoder import CarFile
from automation.jbeam import Parser as JBeamParser

from assetto_corsa.car.engine import Engine, TurboSection, FROM_COAST_REF, EngineSources, EngineUIData


def kw_to_bhp(kw):
    return kw / 0.745699872


def generate_assetto_corsa_engine_data(exported_car_name):
    car_export_path = os.path.join(installation.get_beamng_export_path(),
                                   exported_car_name)
    if not os.path.isdir(car_export_path):
        raise IOError(f"No such directory: {car_export_path}")

    data_dir = os.path.join(car_export_path,
                            os.sep.join(["vehicles", exported_car_name]))

    try:
        car_file = glob.glob(f"{data_dir}/*.car")[0]
    except IndexError:
        raise RuntimeError(f"No .car file present in {data_dir}")

    with open(car_file, "rb") as f:
        car = CarFile(os.path.basename(car_file), f.read())
        car.parse()
        car_data = car.get_data()

    var_uid = car_data['Car']['Variant']['UID']
    engine_data = sandbox.get_engine_data(var_uid)
    p = JBeamParser()
    jbeam_engine_data = p.naive_parse(os.path.join(data_dir, installation.ENGINE_JBEAM_NAME))

    engine = Engine()
    engine.metadata.source = EngineSources.AUTOMATION
    engine.metadata.mass_kg = round(engine_data["Weight"])
    engine.metadata.info_dict["automation-version"] = engine_data["GameVersion"]
    ui_data = EngineUIData()
    ui_data.torque_curve = [[str(round(rpm)), str(round(engine_data["torque-curve"][idx]))]
                            for idx, rpm in enumerate(engine_data["rpm-curve"])]
    ui_data.max_torque = f"{round(engine_data['PeakTorque'])}Nm"
    ui_data.power_curve = [[str(round(rpm)), str(round(kw_to_bhp(engine_data["power-curve"][idx])))]
                           for idx, rpm in enumerate(engine_data["rpm-curve"])]
    ui_data.max_power = f"{round(kw_to_bhp(engine_data['PeakPower']))}bhp"
    engine.metadata.ui_data = ui_data

    # engine.max_power = (round(engine_data["PeakPower"]), round(engine_data["PeakPowerRPM"]))
    # engine.max_torque = (round(engine_data["PeakTorque"]), round(engine_data["PeakTorqueRPM"]))
    engine.inertia = round(jbeam_engine_data["Camso_Engine"]["mainEngine"]["inertia"], 3)
    engine.minimum = round(engine_data["IdleSpeed"] if engine_data["IdleSpeed"] >= engine_data["rpm-curve"][0] else engine_data["rpm-curve"][0])
    engine.limiter = round(engine_data["MaxRPM"])
    # TODO work out how to use the min acceptable value from Automation based
    # TODO on the engine components and their quality
    engine.rpm_threshold = engine.limiter + 200
    # TODO work out some kind of translation from MTTF to this
    engine.rpm_damage_k = 1

    # fuel use in l/h = (Max Power * Max RPM) / fuel density
    fuel_use_per_hour = (engine_data["PeakPower"] * engine_data["Econ"]) / 750
    fuel_use_per_sec = fuel_use_per_hour / 3600

    # Assetto Corsa calculation:
    # In one second the consumption is (rpm*gas*CONSUMPTION)/1000
    # fuel_use_per_sec = (engine_data["PeakPowerRPM"] * 1 * C) / 1000
    # fuel_use_per_sec * 1000 =  engine_data["PeakPowerRPM"]*C
    # C = (fuel_use_per_sec * 1000) / engine_data["PeakPowerRPM"]
    # This is being generous for now as the Econ value doesn't apply for MaxPower
    # we can look up the econ value @ Max power later
    # TODO refine this to get an average over a wider range of engine usage
    engine.fuel_consumption = round((fuel_use_per_sec * 1000) / engine_data["PeakPowerRPM"], 3)

    if engine_data["AspirationType"].startswith("Aspiration_Natural"):
        write_na_torque_curve(engine, engine_data)
    else:
        write_turbo_torque_curve(engine, engine_data)
        create_turbo_sections(engine, engine_data)
        engine.metadata.boost_curve = {round(rpm): engine_data["boost-curve"][idx]
                                       for idx, rpm in enumerate(engine_data["rpm-curve"])}

    rpm_increments = engine_data["rpm-curve"][-1] - engine_data["rpm-curve"][-2]
    engine.power_info.rpm_curve.append(round(engine_data["rpm-curve"][-1]+rpm_increments))
    engine.power_info.torque_curve.append(round(engine.power_info.torque_curve[-1] / 2))
    engine.power_info.rpm_curve.append(round(engine_data["rpm-curve"][-1] + (rpm_increments*2)))
    engine.power_info.torque_curve.append(0)

    dynamic_friction = jbeam_engine_data["Camso_Engine"]["mainEngine"]["dynamicFriction"]
    angular_velocity_at_max_rpm = (engine_data["MaxRPM"] * 2 * math.pi) / 60
    friction_torque = (angular_velocity_at_max_rpm * dynamic_friction) + \
                      (2*jbeam_engine_data["Camso_Engine"]["mainEngine"]["friction"])

    engine.coast_curve.curve_data_source = FROM_COAST_REF
    engine.coast_curve.reference_rpm = round(engine_data["MaxRPM"])
    engine.coast_curve.torque = round(friction_torque)
    engine.coast_curve.non_linearity = 0
    return engine


def write_na_torque_curve(engine, engine_data):
    for idx in range(0, len(engine_data["rpm-curve"])):
        engine.power_info.rpm_curve.append(round(engine_data["rpm-curve"][idx]))
        engine.power_info.torque_curve.append(round(engine_data["torque-curve"][idx]))


def write_turbo_torque_curve(engine, engine_data):
    for idx in range(0, len(engine_data["rpm-curve"])):
        engine.power_info.rpm_curve.append(round(engine_data["rpm-curve"][idx]))
        boost_pressure = max(0, engine_data["boost-curve"][idx])
        engine.power_info.torque_curve.append(round(engine_data["torque-curve"][idx] / (1+boost_pressure)))


def create_turbo_sections(engine, engine_data):
    t = TurboSection()
    t.cockpit_adjustable = 0
    t.max_boost = round(engine_data["PeakBoost"], 2)
    t.display_max_boost = utils.round_up(engine_data["PeakBoost"], 1)
    t.wastegate = round(engine_data["PeakBoost"], 2)
    t.reference_rpm = round(engine_data["PeakBoostRPM"])
    # TODO work out how to better approximate these
    t.lag_dn = 0.99
    t.lag_up = 0.995
    t.gamma = 1
    engine.turbo.sections.append(t)
