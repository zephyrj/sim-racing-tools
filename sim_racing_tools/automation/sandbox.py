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
import struct
import sqlite3
import logging
from collections import OrderedDict
import sim_racing_tools.automation.installation as installation


def get_engine_bill_of_material_params():
    return {"EngineeringCost", "EngineeringTime", "ManHours",
            "MaterialCost", "ToolingCosts", "TotalCost", "ServiceCost"}


def get_engine_bill_of_materials(variant_uid):
    resource_stats_to_collect = get_engine_bill_of_material_params()
    data_dict = OrderedDict()
    with sqlite3.connect(os.path.join(installation.get_userdata_path(),
                                      installation.SANDBOX_DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM EngineResults WHERE UID = ?', (variant_uid,)).fetchone()
        for stat in resource_stats_to_collect:
            data_dict[stat] = row[stat]
    return data_dict


def get_engine_graph_data_params():
    return {'RPMCurve', 'PowerCurve', 'TorqueCurve', 'EconCurve', 'EconEffCurve', 'BoostCurve'}


def get_engine_graph_data(variant_uid):
    with sqlite3.connect(os.path.join(installation.get_userdata_path(),
                                      installation.SANDBOX_DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        conn.text_factory = bytes
        cur = conn.cursor()
        data = cur.execute('SELECT * from EngineCurves where uid = ?', (variant_uid,)).fetchone()
        data_dict = OrderedDict()
        for header in get_engine_graph_data_params():
            # logging.debug(f'{header} data')
            # logging.debug(" ".join(f'{b:02X}' for b in data[column_name]))
            data_dict[header] = _decode_blob(data[header])
        return data_dict


def get_engine_performance_data_params():
    return {"AverageCruiseEcon", "Econ", "MinEcon", "WorstEcon", "EconEff", "IdleSpeed", "MaxRPM",
            "MTTF", "Weight", "PeakTorque", "PeakTorqueRPM", "PeakPower", "PeakPowerRPM",
            "PeakBoost", "PeakBoostRPM"}


def get_engine_performance_data(variant_uid):
    with sqlite3.connect(os.path.join(installation.get_userdata_path(),
                                      installation.SANDBOX_DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        engine_result_columns = get_engine_performance_data_params()
        query = f"SELECT {', '.join(engine_result_columns)} FROM EngineResults WHERE uid = ?"
        return cur.execute(query, (variant_uid,)).fetchone()


def get_variant_data_params():
    return {"UID", "FUID", "Name", "GameVersion", "Crank", "Conrods", "Pistons", "VVT", "Aspiration",
            "AspirationType", "AspirationOption", "IntercoolerSetting", "FuelSystemType", "FuelSystem",
            "IntakeManifold", "Intake", "FuelType", "Headers", "ExhaustCount", "ExhaustBypassValves",
            "Cat", "Muffler1", "Muffler2", "Bore", "Stroke", "Capacity", "Compression",
            "CamProfileSetting", "VVLCamProfileSetting", "AFR", "AFRLean", "RPMLimit",
            "IgnitionTimingSetting", "ARRatio", "BoostCutOff", "CompressorFraction", "TurbineFraction",
            "ExhaustDiameter", "QualityBottomEnd", "QualityTopEnd", "QualityAspiration",
            "QualityFuelSystem", "QualityExhaust", "Tags"}


def get_family_mapping():
    return {"Name": "FamilyName", "BlockConfig": "BlockConfig", "BlockMaterial": "BlockMaterial",
            "BlockType": "BlockType", "Head": "Head", "HeadMaterial": "HeadMaterial", "Valves": "Valves",
            "VVL": "VVL"}


def get_family_data_params():
    return set(get_family_mapping().values())


def get_engine_data_params():
    params = get_variant_data_params()
    params.update(get_engine_performance_data_params())
    params.update(get_engine_bill_of_material_params())
    params.update(get_engine_graph_data_params())
    params.update(get_family_data_params())
    return params


def get_engine_data(variant_uid):
    with sqlite3.connect(os.path.join(installation.get_userdata_path(),
                                      installation.SANDBOX_DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        variant_columns = get_variant_data_params()
        query = f"SELECT {', '.join(variant_columns)} from Variants where uid = ?"
        row = cur.execute(query, (variant_uid,)).fetchone()
        data_dict = {k: row[k] for k in row.keys()}
        family_row = cur.execute('SELECT * from Families where uid = ?',
                                 (data_dict['FUID'],)).fetchone()
        for family_key, data_key in get_family_mapping().items():
            data_dict[data_key] = family_row[family_key]
        data_dict.update(get_engine_performance_data(variant_uid))
        data_dict.update(get_engine_bill_of_materials(variant_uid))
        data_dict.update(get_engine_graph_data(variant_uid))
    return data_dict


def get_engine_uid_from_name(family_name, variant_name):
    with sqlite3.connect(os.path.join(installation.get_userdata_path(),
                                      installation.SANDBOX_DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        family_row = cur.execute('SELECT * from Families where Name = ?',
                                 (family_name,)).fetchone()
        query = f"SELECT UID from Variants where FUID = ? and Name = ?"
        return cur.execute(query, (family_row['UID'], variant_name)).fetchone()["UID"]


def get_engine_by_name(family_name, variant_name):
    return get_engine_data(get_engine_uid_from_name(family_name, variant_name))


def _decode_double(blob_bytes):
    logging.debug(" ".join(f'{b:02X}' for b in blob_bytes))
    return struct.unpack("d", bytearray(blob_bytes))[0]


def _decode_blob(blob_bytes):
    # skip blob header
    logging.debug(f'Blob length: {len(blob_bytes)}')
    data = blob_bytes[2:]
    num_data_points = struct.unpack("<LL", bytearray(data[0:8]))[0]
    logging.debug(f'Num data points: {num_data_points}')
    data = data[8:]
    current_pos = 0
    collected_points = 0
    out_list = list()
    while collected_points < num_data_points:
        logging.debug(f'{data[current_pos]:02X}')
        current_pos += 1
        logging.debug(f'{_decode_double(data[current_pos:current_pos+8])}')
        current_pos += 9
        out_list.append(_decode_double(data[current_pos:current_pos+8]))
        current_pos += 8
        collected_points += 1
    return out_list
