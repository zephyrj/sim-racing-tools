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
import logging
import shutil
import json

import sim_racing_tools.utils as utils
import sim_racing_tools.assetto_corsa.utils as ac_utils
from sim_racing_tools.assetto_corsa.utils import extract_ini_primitive_value
import sim_racing_tools.assetto_corsa.installation as installation
import sim_racing_tools.assetto_corsa.car.engine as engine
import assetto_corsa.car.drivetrain as drivetrain
import sim_racing_tools.quick_bms as quick_bms
from typing import List


class NoSuchCar(ValueError):
    def __init__(self, car_name):
        super(NoSuchCar, self).__init__(f"No car exists with the name {car_name}")


class CannotUpdateMass(ValueError):
    def __init__(self):
        super(CannotUpdateMass, self).__init__("Can't update car weight as no engine weight is available")


def load_car(car_folder_name):
    ac_install = installation.Installation()
    if car_folder_name not in ac_install.installed_cars:
        raise NoSuchCar(car_folder_name)
    c = Car()
    c.load_from_path(os.path.join(ac_install.get_installed_cars_path(), car_folder_name))
    return c


def create_new_car_from_existing(brand, model, existing_car_folder_name, folder_prefix=None, folder_name=None):
    ac_install = installation.Installation()

    if not folder_name:
        folder_name = _create_car_folder_name(brand, model, folder_prefix)
    folder_name = utils.create_filename_safe_name(folder_name)
    logging.basicConfig(filename=f'create_{folder_name}.log', level=logging.INFO)
    logging.getLogger()

    new_car_path = _create_copy_of_existing_car_directory(ac_install, existing_car_folder_name, folder_name)
    if not os.path.isdir(os.path.join(new_car_path, installation.DATA_FOLDER_NAME)):
        # todo find and run openBMS (on wine if linux)
        logging.error(f"The existing car does not have an extracted data folder. "
                      f"The {installation.ENCODED_DATA_FILENAME} needs to be extracted with "
                      f"{quick_bms.QUICKBMS_EXE_NAME}")
        raise NotImplementedError("TODO run openBMS on data.acd")
    acd_file_path = os.path.join(new_car_path, installation.ENCODED_DATA_FILENAME)
    if os.path.exists(acd_file_path):
        logging.info(f"Removing {acd_file_path}")
        os.remove(acd_file_path)

    _update_filenames_and_references(new_car_path, existing_car_folder_name, brand, model)
    _update_car_sfx_dir(ac_install, new_car_path, existing_car_folder_name)


def _create_car_folder_name(brand: str, model_name:str, folder_prefix=None):
    folder_name = "" if not folder_prefix else f'{folder_prefix}_'
    folder_name += f'{brand}_{model_name}'
    return folder_name.lower()


def _create_copy_of_existing_car_directory(ac_install: installation.Installation,
                                           existing_car_path: str,
                                           new_car_path: str):
    if existing_car_path not in ac_install.installed_cars:
        err_str = f"{existing_car_path} is not present in {ac_install.get_installed_cars_path()}"
        logging.error(err_str)
        raise ValueError(err_str)
    existing_car_full_path = os.path.join(ac_install.get_installed_cars_path(), existing_car_path)
    new_car_full_path = os.path.join(ac_install.get_installed_cars_path(), new_car_path)
    if os.path.exists(new_car_full_path):
        err_str = f"There is already a car of this name present at {new_car_full_path}"
        logging.error(err_str)
        raise ValueError(err_str)
    logging.info(f'Copying contents of {existing_car_full_path} to {new_car_full_path}')
    shutil.copytree(existing_car_full_path, new_car_full_path)
    return new_car_full_path


def _update_filenames_and_references(new_car_path: str,
                                     old_name: str,
                                     brand: str,
                                     model: str):
    new_car_dir_name = os.path.basename(new_car_path)
    for dirname, dirs, files in os.walk(new_car_path):
        for filename in files:
            full_file_path = os.path.join(dirname, filename)
            if filename.startswith(old_name) and (filename.endswith(".kn5") or filename.endswith(".bank")):
                new_file_path = os.path.join(dirname, filename.replace(old_name, new_car_dir_name))
                logging.info(f"Renaming {full_file_path} to {new_file_path}")
                os.rename(full_file_path, new_file_path)
            elif filename == "car.ini":
                config = ac_utils.IniObj(full_file_path)
                new_screen_name = f'{brand} {model}'
                logging.info(f"Updating SCREEN_NAME in car.ini to {new_screen_name}")
                config["INFO"]["SCREEN_NAME"] = new_screen_name
                config.write()
            elif filename == "lods.ini":
                config = ac_utils.IniObj(full_file_path)
                idx = 0
                while True:
                    current_lod_name = f'LOD_{idx}'
                    if current_lod_name not in config:
                        break
                    lod_section = config[current_lod_name]
                    if "FILE" in lod_section:
                        tmp = lod_section["FILE"]
                        logging.info(f"Updating FILE in {current_lod_name} section of {full_file_path} from "
                                     f"{old_name} to {new_car_dir_name}")
                        lod_section["FILE"] = tmp.replace(old_name, new_car_dir_name)
                    idx += 1
                config.write()
            elif filename == "ui_car.json":
                with open(full_file_path, "r") as ui_car_file:
                    config = json.load(ui_car_file, strict=False)
                    logging.info("Updating ui_car.json")
                    new_name = f'{brand} {model}'
                    logging.info(f"Updating {config['name']} to {new_name}")
                    config["name"] = new_name
                    logging.info(f"Updating {config['brand']} to {brand}")
                    config["brand"] = brand
                with open(full_file_path, "w+") as ui_car_file:
                    ui_car_file.write(json.dumps(config, indent=4))


def _update_car_sfx_dir(ac_install: installation.Installation,
                        new_car_path: str,
                        existing_car_folder_name: str):
    new_car_dirname = os.path.basename(new_car_path)
    guids_file_path = os.path.join(new_car_path, os.sep.join(["sfx", installation.SFX_GUID_FILENAME]))
    if os.path.isfile(guids_file_path):
        logging.info(f"Existing {installation.SFX_GUID_FILENAME} file present")
        with open(guids_file_path, "r") as f:
            existing_guid_lines = f.readlines()

        def _update_guid_line(guid_line):
            updated_line = guid_line.replace(existing_car_folder_name, new_car_dirname)
            logging.info(f"Updating {guid_line} to {updated_line}")
            return updated_line

        with open(guids_file_path, "w+") as f:
            f.writelines([_update_guid_line(line) for line in existing_guid_lines])
    else:
        logging.info(f"No {installation.SFX_GUID_FILENAME} file present. A new one will be created")
        with open(guids_file_path, "w+") as guid_file:
            try:
                guid_file.writelines(_generate_guids_content(ac_install, new_car_dirname, existing_car_folder_name))
            except IndexError:
                logging.warning(f"Can't find any existing sfx data for {existing_car_folder_name} - new car won't "
                                f"have any sfx")


def _generate_guids_content(ac_install: installation.Installation,
                            new_car_dir_name: str,
                            old_car_dir_name: str):
    sfx_list = list()
    sfx_list.append(f'{ac_install.sfx_bank_dict[old_car_dir_name]} bank:/{new_car_dir_name}\n')
    for sfx_entry in ac_install.sfx_dict_by_folder_name[old_car_dir_name]:
        sfx_list.append(sfx_entry.replace(old_car_dir_name, new_car_dir_name))
    return sfx_list


class Car(object):
    def __init__(self):
        self.car_path = None
        self.data_path = None
        self.car_ini_data = None
        self.ui_info = UIInfo()
        self.version: str = '1'
        self.screen_name: str = ""
        self.total_mass: int = 0  # total vehicle weight in kg with driver and no fuel
        '''
        sql EngineResults.Econ = BSFC (g/(kWh))
        EconEff = 1 / (BSFC * "LHV of fuel")
        LHC of gasoline from wikipedia -> 0.0122222
        bsfc = (fuel consumption rate) / (Power output) = M.f / Pwrb kg/kWh
        1680.8221 = r / 167236.78
        Q = N * q / R, where
        Q – (in l / h) maximum theoretical fuel consumption in grams per 1 hour of engine operation at maximum power;
        q – (in g / kWh) specific fuel consumption for power N;
        N – (in kW) engine power;
        R – (kg / m3) fuel density
        Gasoline (petrol) fuel density: 710 – 760 kg / m3
        fuel consumption. In one second the consumption is (rpm*gas*CONSUMPTION)/1000 litres
        is gas 0 - 1 or 0 - 100?
        0.175698056 = (8600 * 100 * C) / 100
        632.513 l/h
        '''
        self.fuel_consumption: float = 0.0
        self.default_fuel: int = 0  # default starting fuel in litres
        self.max_fuel: int = 0  # max fuel in litres
        self.ai_shift_up: int = 0
        self.ai_shift_down: int = 0
        self.engine: engine.Engine or None = None
        self.drivetrain: drivetrain.Drivetrain or None = None
        self.shift_lights: ShiftLights = ShiftLights()

    def load_from_path(self, car_path):
        self.car_path = car_path
        self.data_path = os.path.join(car_path, "data")
        ini_data = ac_utils.IniObj(os.path.join(self.data_path, "car.ini"))
        self.version = ini_data["HEADER"]["VERSION"]
        self.screen_name = ini_data["INFO"]["SCREEN_NAME"]
        self.total_mass = extract_ini_primitive_value(ini_data["BASIC"]["TOTALMASS"], int)
        self.fuel_consumption = extract_ini_primitive_value(ini_data["FUEL"]["CONSUMPTION"], float)
        self.default_fuel = extract_ini_primitive_value(ini_data["FUEL"]["FUEL"], int)
        self.max_fuel = extract_ini_primitive_value(ini_data["FUEL"]["MAX_FUEL"], int)
        self._load_ai_data()
        self.engine = engine.load_engine(self.data_path)
        self.drivetrain = drivetrain.load_drivetrain(os.path.join(self.data_path, "drivetrain.ini"))
        self.shift_lights.load_from_ini(self.data_path)
        self.car_ini_data = ini_data
        self.ui_info.load(self.car_path)

    def swap_engine(self, new_engine, update_mass=False, old_engine_mass=None):
        """
        ai.ini:
        [GEARS]
        UP - What RPM AI should shift up
        DOWN - What RPM AI should shift down

        car.ini
        [BASIC] TOTALMASS (Take a value for the chassis and existing engine and adjust accordingly)
        [FUEL] CONSUMPTION
        [INERTIA] If the engine weight changes does this affect this?

        digital_instruments.ini
        [LED_0] - [LED_4] - used for showing shift lights

        drivetrain.ini
        [AUTOCLUTCH]
        [AUTO_SHIFTER]
        [DOWNSHIFT_PROTECTION] (dependant on quality?)

        TODO
        ctrl_turbo0.ini
        [CONTROLLER_0]
        INPUT=RPMS
        COMBINATOR=ADD
        LUT=(0=2.0|3500=2.0|6400=1.95|6600=1.91|6800=1.85|7000=1.82|7200=1.8|7400=1.76|7600=1.73|7800=1.69|8000=1.64|8200=1.59|8400=1.53|8600=1.48|8800=1.42|9000=1.37)
        FILTER=0.99     ; new value each physics step = filter*last_step_value+(1-filter)*lut_value
        UP_LIMIT=10000
        DOWN_LIMIT=0.0


        :param new_engine:
        :param update_mass:
        :param old_engine_mass:
        :return:
        """
        if new_engine.metadata.mass_kg and update_mass:
            old_mass = self.engine.metadata.mass_kg if self.engine.metadata.mass_kg else old_engine_mass
            if not old_mass:
                raise CannotUpdateMass()
            self.total_mass -= old_mass
            self.total_mass += new_engine.metadata.mass_kg
        self.engine = new_engine

        if new_engine.fuel_consumption:
            self.fuel_consumption = new_engine.fuel_consumption
        if not self.data_path:
            return
        self.shift_lights.update(self.engine.limiter)
        if self.engine.metadata.ui_data:
            self.ui_info.torqueCurve = new_engine.metadata.ui_data.torque_curve
            self.ui_info.powerCurve = new_engine.metadata.ui_data.power_curve
            self.ui_info.specs["bhp"] = new_engine.metadata.ui_data.max_power
            self.ui_info.specs["torque"] = new_engine.metadata.ui_data.max_torque
            self.ui_info.specs["weight"] = self.total_mass

    def write(self, output_path=None):
        if output_path is None and self.car_ini_data is None:
            raise IOError("No output file specified")
        ini_data = ac_utils.IniObj(output_path) if output_path else self.car_ini_data
        ini_data.update_attribute("VERSION", self.version, section_name="HEADER")
        ini_data.update_attribute("SCREEN_NAME", self.screen_name, section_name="INFO")
        ini_data.update_attribute("TOTALMASS", self.total_mass, section_name="BASIC")
        ini_data.update_attribute("CONSUMPTION", self.fuel_consumption, section_name="FUEL")
        ini_data.update_attribute("FUEL", self.default_fuel, section_name="FUEL")
        ini_data.update_attribute("MAX_FUEL", self.max_fuel, section_name="FUEL")
        ini_data.write()
        self._write_ai_data(ini_data.dirname())
        self.engine.write(ini_data.dirname())
        self.drivetrain.write(ini_data.dirname())
        self.shift_lights.write(ini_data.dirname())
        self.ui_info.write(self.car_path if not output_path else output_path)

    def _load_ai_data(self):
        ai_file_path = os.path.join(self.data_path, "ai.ini")
        ai_ini = ac_utils.IniObj(ai_file_path)
        self.ai_shift_up = extract_ini_primitive_value(ai_ini["GEARS"]["UP"], int)
        self.ai_shift_down = extract_ini_primitive_value(ai_ini["GEARS"]["DOWN"], int)

    def _write_ai_data(self, output_dir):
        ai_ini = ac_utils.IniObj(os.path.join(output_dir, "ai.ini"))
        ai_ini.update_attribute("UP", self.ai_shift_up, section_name="GEARS")
        ai_ini.update_attribute("DOWN", self.ai_shift_down, section_name="GEARS")
        ai_ini.write()


class ShiftLights(object):
    def __init__(self):
        self.leds: List[ShiftLED] = list()

    def load_from_ini(self, ini_dir):
        instruments_path = os.path.join(ini_dir, "digital_instruments.ini")
        if not os.path.isfile(instruments_path):
            return
        instruments_ini = ac_utils.IniObj(instruments_path)
        led_idx = 0
        while True:
            led_section_name = f"LED_{led_idx}"
            if led_section_name not in instruments_ini:
                break
            self.leds.append(ShiftLED.create_from_led_section(instruments_ini[led_section_name]))
            led_idx += 1

    def update(self, limiter_rpm):
        # TODO allow spacing of the lights to be provided rather than just 100RPM
        rpm_switch_val = limiter_rpm - 100
        for led in reversed(self.leds):
            led.rpm_switch = rpm_switch_val
            led.blink_switch = limiter_rpm
            rpm_switch_val -= 100

    def write(self, output_path):
        ini_file = ac_utils.IniObj(os.path.join(output_path, "digital_instruments.ini"))
        for led_idx, led in enumerate(self.leds):
            led_section_name = f"LED_{led_idx}"
            if led_section_name not in ini_file:
                ini_file[led_section_name] = dict()
            led.write_to_section(ini_file[led_section_name])
        ini_file.write()


class ShiftLED(object):
    @staticmethod
    def create_from_led_section(section):
        l = ShiftLED()
        l.object_name = section["OBJECT_NAME"]
        l.rpm_switch = section["RPM_SWITCH"]
        l.emissive = section["EMISSIVE"]
        l.diffuse = section["DIFFUSE"]
        l.blink_switch = section["BLINK_SWITCH"]
        l.blink_hz = section["BLINK_HZ"]
        return l

    def __init__(self):
        self.object_name: str = ""
        self.rpm_switch: int = 0
        self.emissive: List[float] = list()
        self.diffuse: float = 0.0
        self.blink_switch: int = 0
        self.blink_hz: int = 0

    def write_to_section(self, section):
        section["OBJECT_NAME"] = self.object_name
        section["RPM_SWITCH"] = self.rpm_switch
        section["EMISSIVE"] = self.emissive
        section["DIFFUSE"] = self.diffuse
        section["BLINK_SWITCH"] = self.blink_switch
        section["BLINK_HZ"] = self.blink_hz


class UIInfo(object):
    def __init__(self):
        self.loaded_ui_json_data = None
        self.ui_json_path = None
        self.name: str = ""
        self.brand: str = ""
        self.description: str = ""
        self.tags: List[str] = list()
        self.car_class: str = ""

        '''
        "specs":
        {
            "bhp": "198bhp",
            "torque": "230Nm",
            "weight": "455kg",
            "topspeed": "230+km/h",
            "acceleration": "--s 0-100",
            "pwratio": "2.30kg/hp",
            "range": 85
        },
        '''
        self.specs = dict()

        self.torqueCurve: List[List[str]] = list()
        self.powerCurve: List[List[str]] = list()

    def load(self, car_path):
        ui_json_path = os.path.join(car_path, os.path.sep.join(["ui", "ui_car.json"]))
        if not os.path.isfile(ui_json_path):
            return
        self.ui_json_path = ui_json_path
        with open(self.ui_json_path, "r") as f:
            self.loaded_ui_json_data = json.load(f)
        for a in ["name", "brand", "description", "tags", "specs", "torqueCurve", "powerCurve"]:
            if a in self.loaded_ui_json_data:
                setattr(self, a, self.loaded_ui_json_data[a])
        if "class" in self.loaded_ui_json_data:
            self.car_class = self.loaded_ui_json_data["class"]

    def write(self, output_dir):
        for a in ["name", "brand", "description", "tags", "specs", "torqueCurve", "powerCurve"]:
            self.loaded_ui_json_data[a] = getattr(self, a)
        self.loaded_ui_json_data["class"] = self.car_class
        with open(os.path.join(output_dir, os.path.sep.join(["ui", "ui_car.json"])), "w+") as f:
            json.dump(self.loaded_ui_json_data, f, indent=4)


"""
    ai.ini:
      [GEARS]
        UP - What RPM AI should shift up
        DOWN - What RPM AI should shift down

    car.ini
      [BASIC] TOTALMASS (Take a value for the chassis and existing engine and adjust accordingly)
      [FUEL] CONSUMPTION
      [INERTIA] If the engine weight changes does this affect this?

    digital_instruments.ini
      [LED_0] - [LED_4] - used for showing shift lights

    drivetrain.ini
      [AUTOCLUTCH]
      [AUTO_SHIFTER]
      [DOWNSHIFT_PROTECTION] (dependant on quality?)

    engine.ini
      [HEADER]
        COAST_CURVE - coast curve. can define 3 different options (coast reference, coast values for mathematical curve, coast curve file)
      [ENGINE_DATA]
        INERTIA
        LIMITER
        MINIMUM (idle rpm)
      [COAST_REF]
        RPM - rev number reference
        TORQUE - engine braking torque value in Nm at rev number reference
        NON_LINEARITY - coast engine brake from ZERO to TORQUE value at rpm with linear (0) to fully exponential (1)
      [TURBO_N]
        LAG_DN - Interpolation lag used slowing down the turbo (0.96 - 0.99)
        LAG_UP - Interpolation lag used to spin up the turbo (0.96 - 0.999)
        MAX_BOOST - Maximum boost generated. This value is never exceeded and multiply the torque
                        like T=T*(1.0 + boost), a boost of 2 will give you 3 times the torque at a given rpm.
        WASTEGATE - Max level of boost before the wastegate does its things. 0 = no wastegate
        DISPLAY_MAX_BOOST - Value used by display apps
        REFERENCE_RPM= - The reference rpm where the turbo reaches maximum boost (at max gas pedal)
        GAMMA=5 - A value used to make the boost curve more exponential. 1 = linear
        COCKPIT_ADJUSTABLE=0

      fuel_cons.ini
        [FUEL_EVAL]
          KM_PER_LITER

      power.lut
        A lookup table for torque values after applying drivetrain losses. Each line is <RPM>|<TORQUE_NM>

      sounds.ini
      No idea how to update these yet. An example from tatuusfa01
      [BACKFIRE]
      MAXGAS=0.4
      MINRPM=3500
      MAXRPM=15000
      TRIGGERGAS=0.8
      VOLUME_IN=1.0
      VOLUME_OUT=0.5
      VOLUME_SCALE_OUT=6

    Warnings:
      if engine torque is greater than [CLUTCH].MAX_TORQUE in drivetrain.ini
      
    Update pretty much everything in drivetrain.ini

    Create ratios.rto files for the gears available for the gearbox
    The files are of the form <ratio-name>|<ratio-value> e.g: F3B-12:38-INT|3.17

    Reference these ratio files in setup.ini
    [GEAR_N] where N is the gear number
      RATIOS=<ratios-file>
    [FINAL_GEAR_RATIO]
      RATIOS=<final.rto>

    In drivetrain.ini
    [GEARS]
     COUNT, GEAR_R, FINAL, GEAR_N (must be a gear for 1-N where N is COUNT)
     these should match up with a ratio lookup table file
"""
