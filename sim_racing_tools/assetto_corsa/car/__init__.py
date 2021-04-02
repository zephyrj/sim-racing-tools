import os
import logging
import shutil
import json

import sim_racing_tools.utils as utils
from sim_racing_tools.utils import extract_ini_primitive_value
import sim_racing_tools.assetto_corsa.installation as installation
import sim_racing_tools.assetto_corsa.car.engine as engine
import sim_racing_tools.assetto_corsa.car.drivetrain as drivetrain
import sim_racing_tools.quick_bms as quick_bms
from typing import List


def load_car(car_path):
    c = Car()
    c.load_from_path(car_path)
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
                config = utils.IniObj(full_file_path)
                new_screen_name = f'{brand} {model}'
                logging.info(f"Updating SCREEN_NAME in car.ini to {new_screen_name}")
                config["INFO"]["SCREEN_NAME"] = new_screen_name
                config.write()
            elif filename == "lods.ini":
                config = utils.IniObj(full_file_path)
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
        self.version: int = 1
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
        self.shift_lights_rpms: List[int] = list()
        self.engine = None
        self.drivetrain = None

    def load_from_path(self, car_path):
        self.car_path = car_path
        self.data_path = os.path.join(car_path, "data")
        ini_data = utils.IniObj(os.path.join(self.data_path, "car.ini"))
        self.version = extract_ini_primitive_value(ini_data["HEADER"]["VERSION"], int)
        self.screen_name = ini_data["INFO"]["SCREEN_NAME"]
        self.total_mass = extract_ini_primitive_value(ini_data["BASIC"]["TOTALMASS"], int)
        self.fuel_consumption = extract_ini_primitive_value(ini_data["FUEL"]["CONSUMPTION"], float)
        self.default_fuel = extract_ini_primitive_value(ini_data["FUEL"]["FUEL"], int)
        self.max_fuel = extract_ini_primitive_value(ini_data["FUEL"]["MAX_FUEL"], int)
        self._load_ai_data()
        self.engine = engine.load_engine(os.path.join(self.data_path, "engine.ini"))
        self.drivetrain = drivetrain.load_drivetrain(os.path.join(self.data_path, "drivetrain.ini"))
        self.car_ini_data = ini_data

    def swap_engine(self, new_engine):
        pass

    def write(self, output_path=None):
        if output_path is None and self.car_ini_data is None:
            raise IOError("No output file specified")
        ini_data = utils.IniObj(output_path) if output_path else self.car_ini_data
        ini_data.update_attribute("VERSION", self.version, section_name="HEADER")
        ini_data.update_attribute("SCREEN_NAME", self.screen_name, section_name="INFO")
        ini_data.update_attribute("TOTALMASS", self.total_mass, section_name="BASIC")
        ini_data.update_attribute("CONSUMPTION", self.fuel_consumption, section_name="FUEL")
        ini_data.update_attribute("FUEL", self.default_fuel, section_name="FUEL")
        ini_data.update_attribute("MAX_FUEL", self.max_fuel, section_name="FUEL")
        ini_data.write()
        self._write_ai_data(ini_data.dirname())
        self.engine.write(os.path.join(ini_data.dirname(), "engine.ini"))
        self.drivetrain.write(os.path.join(ini_data.dirname(), "drivetrain.ini"))

    def _load_ai_data(self):
        ai_file_path = os.path.join(self.data_path, "ai.ini")
        ai_ini = utils.IniObj(ai_file_path)
        self.ai_shift_up = extract_ini_primitive_value(ai_ini["GEARS"]["UP"], int)
        self.ai_shift_down = extract_ini_primitive_value(ai_ini["GEARS"]["DOWN"], int)

    def _write_ai_data(self, output_dir):
        ai_ini = utils.IniObj(os.path.join(output_dir, "ai.ini"))
        ai_ini.update_attribute("UP", self.ai_shift_up, section_name="GEARS")
        ai_ini.update_attribute("DOWN", self.ai_shift_down, section_name="GEARS")
        ai_ini.write()


class UIInfo(object):
    def __init__(self):
        self.ui_ini_json = None
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

        self.torque_curve: List[List[str]] = list()
        self.power_curve: List[List[str]] = list()
