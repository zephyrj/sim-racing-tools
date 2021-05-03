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


def get_engine_bill_of_materials(variant_uid):
    resource_stats_to_collect = ["EngineeringCost", "EngineeringTime", "ManHours",
                                 "MaterialCost", "ToolingCosts", "TotalCost", "ServiceCost"]
    data_dict = OrderedDict()
    with sqlite3.connect(os.path.join(installation.get_userdata_path(),
                                      installation.SANDBOX_DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM EngineResults WHERE UID = ?', (variant_uid,)).fetchone()
        for stat in resource_stats_to_collect:
            data_dict[stat] = row[stat]
    return data_dict


def get_engine_graph_data(variant_uid):
    with sqlite3.connect(os.path.join(installation.get_userdata_path(),
                                      installation.SANDBOX_DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        conn.text_factory = bytes
        cur = conn.cursor()
        data = cur.execute('SELECT * from EngineCurves where uid = ?', (variant_uid,)).fetchone()
        collection_data = {"rpm-curve": 'RPMCurve',
                           "power-curve": 'PowerCurve',
                           "torque-curve": 'TorqueCurve',
                           'econ-curve': 'EconCurve',
                           'econ-eff-curve': 'EconEffCurve',
                           'boost-curve': 'BoostCurve'}
        data_dict = OrderedDict()
        for header, column_name in collection_data.items():
            # logging.debug(f'{header} data')
            # logging.debug(" ".join(f'{b:02X}' for b in data[column_name]))
            data_dict[header] = _decode_blob(data[column_name])
        return data_dict


def get_engine_performance_data(variant_uid):
    with sqlite3.connect(os.path.join(installation.get_userdata_path(),
                                      installation.SANDBOX_DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        engine_result_columns = ["AverageCruiseEcon", "Econ", "MinEcon", "WorstEcon", "EconEff", "IdleSpeed", "MaxRPM",
                                 "MTTF", "Weight", "PeakTorque", "PeakTorqueRPM", "PeakPower", "PeakPowerRPM",
                                 "PeakBoost", "PeakBoostRPM"]
        query = f"SELECT {', '.join(engine_result_columns)} FROM EngineResults WHERE uid = ?"
        return cur.execute(query, (variant_uid,)).fetchone()


def get_engine_data(variant_uid):
    with sqlite3.connect(os.path.join(installation.get_userdata_path(),
                                      installation.SANDBOX_DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        variant_columns = ["UID", "FUID", "Name", "GameVersion", "Crank", "Conrods", "Pistons", "VVT", "Aspiration",
                           "AspirationType", "AspirationOption", "IntercoolerSetting", "FuelSystemType", "FuelSystem",
                           "IntakeManifold", "Intake", "FuelType", "Headers", "ExhaustCount", "ExhaustBypassValves",
                           "Cat", "Muffler1", "Muffler2", "Bore", "Stroke", "Capacity", "Compression",
                           "CamProfileSetting", "VVLCamProfileSetting", "AFR", "AFRLean", "RPMLimit",
                           "IgnitionTimingSetting", "ARRatio", "BoostCutOff", "CompressorFraction", "TurbineFraction",
                           "ExhaustDiameter", "QualityBottomEnd", "QualityTopEnd", "QualityAspiration",
                           "QualityFuelSystem", "QualityExhaust", "Tags"]
        query = f"SELECT {', '.join(variant_columns)} from Variants where uid = ?"
        row = cur.execute(query, (variant_uid,)).fetchone()
        data_dict = {k: row[k] for k in row.keys()}
        data_dict["FamilyName"] = cur.execute('SELECT Name from Families where uid = ?',
                                              (data_dict['FUID'],)).fetchone()["Name"]
        data_dict.update(get_engine_performance_data(variant_uid))
        data_dict.update(get_engine_bill_of_materials(variant_uid))
        data_dict.update(get_engine_graph_data(variant_uid))
    return data_dict


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
