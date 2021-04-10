import sys
import math
import struct
import sqlite3
import toml
import logging

from collections import OrderedDict
import sim_racing_tools.automation.installation as installation

SAMPLE_VARIANT_UID = 'B70604DD4EF0BE1E016E1F9559D67659'
SANDBOX_DB_FILE_PATH = None

schema = dict()


class SQLiteColumn(object):
    def __init__(self):
        self.name = None
        self.sqlite_type = None

    def __str__(self):
        return f'{self.sqlite_type} called {self.name}'


def load_engine_results_schema():
    with sqlite3.connect(installation.get_sandbox_db_path()) as conn:
        cur = conn.cursor()
        for row in cur.execute('PRAGMA table_info("EngineResults")').fetchall():
            a = SQLiteColumn()
            a.name = row[1]
            a.sqlite_type = row[2]
            schema[a.name] = a


def get_resource_data(variant_uid):
    resource_stats_to_collect = ["EngineeringCost", "EngineeringTime", "ManHours",
                                 "MaterialCost", "ToolingCosts", "TotalCost"]
    data_dict = OrderedDict()
    with sqlite3.connect(installation.get_sandbox_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM EngineResults WHERE UID = ?', (variant_uid,)).fetchone()
        for stat in resource_stats_to_collect:
            data_dict[stat] = row[stat]
    return data_dict


def write_resource_summary(variant_uid, out_file):
    with open(out_file, "w+") as f:
        toml.dump(get_resource_data(variant_uid), f)


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


def get_engine_graph_data(variant_uid):
    with sqlite3.connect(installation.get_sandbox_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        conn.text_factory = bytes
        cur = conn.cursor()
        data = cur.execute('SELECT * from EngineCurves where uid = ?', (variant_uid,)).fetchone()
        collection_data = {"rpm": 'RPMCurve',
                           "power": 'PowerCurve',
                           "torque": 'TorqueCurve',
                           'econ': 'EconCurve',
                           'econ-eff': 'EconEffCurve',
                           'boost': 'BoostCurve'}
        data_dict = OrderedDict()
        for header, column_name in collection_data.items():
            logging.debug(f'{header} data')
            logging.debug(" ".join(f'{b:02X}' for b in data[column_name]))
            data_dict[header] = _decode_blob(data[column_name])
        return data_dict


def write_engine_performance_summary(variant_uid, out_file):
    engine_graph_data = get_engine_graph_data(variant_uid)
    with open(out_file, "w+") as f:
        toml.dump(engine_graph_data, f)
    with open("power.lut", "w+") as f:
        for idx in range(0, len(engine_graph_data["rpm"])):
            f.write(f'{engine_graph_data["rpm"][idx]}|{math.ceil(engine_graph_data["torque"][idx])}\n')


if __name__ == '__main__':
    write_resource_summary(sys.argv[1], "resource_summary.toml")
    write_engine_performance_summary(sys.argv[1], "performance_summary.toml")
