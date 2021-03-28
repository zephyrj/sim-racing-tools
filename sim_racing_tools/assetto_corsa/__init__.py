import os
import logging
import shutil
import json

import utils

import sim_racing_tools.assetto_corsa.installation as installation
import sim_racing_tools.quick_bms as quick_bms


def create_new_car(brand, model, existing_car_folder_name, folder_prefix=None, folder_name=None):
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
