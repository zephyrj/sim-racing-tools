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
import toml
import glob
import sim_racing_tools.automation.installation as auto_install
import sim_racing_tools.automation.sandbox as sandbox
from sim_racing_tools.automation.car_file_decoder import CarFile

SUCCESS = 0
FAILURE = 1
ARGUMENT_ERROR = 2


def validate_engine(args):
    if not os.path.isfile(args.spec_file):
        print(f"The file {args.spec_file} doesn't exist or is inaccessible")
        return ARGUMENT_ERROR

    if args.exported_car_path:
        if os.path.isabs(args.exported_car_path):
            data_dir = os.path.join(args.exported_car_path,
                                    os.sep.join(["vehicles", os.path.basename(args.exported_car_path)]))
        else:
            data_dir = auto_install.get_exported_car_data_dir(args.exported_car_path)
        try:
            car_file = glob.glob(f"{data_dir}/*.car")[0]
        except IndexError:
            print(f"No .car file present in {data_dir}")
            return ARGUMENT_ERROR

        with open(car_file, "rb") as f:
            car = CarFile(os.path.basename(car_file), f.read())
            car.parse()
            uid = car.get_data()['Car']['Variant']['UID']
    elif args.variant_uid:
        uid = args.variant_uid
    elif args.name:
        uid = sandbox.get_engine_uid_from_name(args.name[0], args.name[1])
    else:
        print("No method for getting Variant UID provided")
        return ARGUMENT_ERROR

    engine_db_data = sandbox.get_engine_data(uid)
    try:
        spec_data = toml.load(args.spec_file)
    except TypeError as e:
        print(f"Couldn't parse spec file: {str(e)}")
        return ARGUMENT_ERROR

    for key in spec_data.keys():
        if key not in engine_db_data:
            print(f"Ignoring {key} in {args.spec_file}")
            continue
        if "min" in spec_data[key]:
            if engine_db_data[key] < spec_data[key]["min"]:
                print(f"Engine doesn't meet specifications: {key} ({engine_db_data[key]}) "
                      f"is less than configured min of {spec_data[key]['min']}")
                return FAILURE
        if "max" in spec_data[key]:
            if engine_db_data[key] > spec_data[key]["max"]:
                print(f"Engine doesn't meet specifications: {key} ({engine_db_data[key]}) "
                      f"is more than configured max of {spec_data[key]['max']}")
                return FAILURE
        if "not" in spec_data[key]:
            try:
                iterator = iter(spec_data[key]["not"])
            except TypeError:
                if engine_db_data[key] == spec_data[key]["not"]:
                    print(f"Engine doesn't meet specifications: {key} ({engine_db_data[key]}) "
                          f"is equal to {spec_data[key]['not']}")
                    return FAILURE
            else:
                if engine_db_data[key] in spec_data[key]["not"]:
                    print(f"Engine doesn't meet specifications: {key} ({engine_db_data[key]}) "
                          f"is equal to {spec_data[key]['not']}")
                    return FAILURE
        if "equals" in spec_data[key]:
            if engine_db_data[key] != spec_data[key]["equals"]:
                print(f"Engine doesn't meet specifications: {key} ({engine_db_data[key]}) "
                      f"is not equal to {spec_data[key]['equals']}")
                return FAILURE
        if "one_of" in spec_data[key]:
            if engine_db_data[key] not in spec_data[key]["one_of"]:
                print(f"Engine doesn't meet specifications: {key} ({engine_db_data[key]}) "
                      f"is not one of {', '.join(spec_data[key]['one_of'])}")
                return FAILURE
    print(f"Engine meets specifications")
    return SUCCESS
