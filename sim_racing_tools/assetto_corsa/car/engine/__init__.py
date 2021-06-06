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

import toml
import os
import csv
from collections import OrderedDict

from typing import List
from sim_racing_tools.assetto_corsa.utils import IniObj, extract_ini_primitive_value

NATURALLY_ASPIRATED = "n/a"
TURBO = "turbo"

FROM_COAST_REF = "FROM_COAST_REF"

ENGINE_INI_FILENAME = "engine.ini"
METADATA_FILENAME = "engine-metadata.toml"
BOOST_FILENAME = "boost.csv"
THERMAL_EFFICIENCY_RATIO_LUT_NAME = "therm_eff.lut"
FUEL_FLOW_LUT_NAME = "max_flow.lut"


class NoEngineIni(ValueError):
    def __init__(self, path):
        super(NoEngineIni, self).__init__(f"There is no {ENGINE_INI_FILENAME} file within {path}")


def load_engine(engine_path):
    e = Engine()
    ini_path = os.path.join(engine_path, ENGINE_INI_FILENAME)
    if not os.path.isfile(ini_path):
        raise NoEngineIni(engine_path)
    engine_ini_data = IniObj(ini_path)
    e.load_settings_from_ini(engine_ini_data)
    return e


class EngineSources(object):
    ASSETTO_CORSA = "ac"
    AUTOMATION = "automation"


class EngineUIData(object):
    @staticmethod
    def from_dict(data_dict):
        e = EngineUIData()
        if "TorqueCurve" in data_dict:
            e.torque_curve = data_dict["TorqueCurve"]
        if "PowerCurve" in data_dict:
            e.power_curve = data_dict["PowerCurve"]
        if "max-torque" in data_dict:
            e.max_torque = data_dict["max-torque"]
        if "max-power" in data_dict:
            e.max_power = data_dict["max-power"]
        return e

    def __init__(self):
        self.torque_curve: List[List[str]] = list()
        self.power_curve: List[List[str]] = list()
        self.max_torque = "---"
        self.max_power = "---"

    def to_dict(self):
        return {"TorqueCurve": self.torque_curve,
                "PowerCurve": self.power_curve,
                "max-torque": self.max_torque,
                "max-power": self.max_power}


class EngineMetadata(object):
    def __init__(self):
        self.source = None
        self.ui_data = None
        self.mass_kg: int or None = None
        self.boost_curve = dict()
        self.efficiency_dict = dict()
        self.info_dict = dict()

    def load(self, data_dir):
        metadata_path = os.path.join(data_dir, METADATA_FILENAME)
        if os.path.isfile(metadata_path):
            with open(metadata_path, "r") as f:
                data_dict = toml.load(f)
                for a in ["source", "mass_kg", "info_dict"]:
                    if a in data_dict:
                        setattr(self, a, data_dict[a])
                if "ui_data" in data_dict:
                    self.ui_data = EngineUIData.from_dict(data_dict["ui_data"])
        boost_filepath = os.path.join(data_dir, BOOST_FILENAME)
        if os.path.isfile(boost_filepath):
            with open(boost_filepath, "r") as f:
                self.boost_curve = {int(row["rpm"]): float(row["boost_bar"])
                                    for row in csv.DictReader(f, delimiter=',')}

    def write(self, output_dir):
        self._write_metadate_file(output_dir)
        self._write_boost_curve(output_dir)

    def _write_metadate_file(self, output_dir):
        with open(os.path.join(output_dir, METADATA_FILENAME), "w+") as f:
            ui_data = None if not self.ui_data else self.ui_data.to_dict()
            toml.dump({"source": self.source,
                       "mass_kg": self.mass_kg,
                       "ui_data": ui_data,
                       "info_dict": self.info_dict}, f)

    def _write_boost_curve(self, output_dir):
        if self.boost_curve:
            with open(os.path.join(output_dir, BOOST_FILENAME), "w+") as f:
                f.write("rpm,boost_bar\n")
                for rpm, boost_bar in self.boost_curve.items():
                    f.write(f'{round(rpm)},{boost_bar}\n')


class ExtendedFuelConsumptionData(object):
    def __init__(self):
        self.idle_throttle: float = 0.03
        self.idle_cutoff: int = 0
        self.mechanical_efficiency: float = 0.85

    def load_base_params_from_ini(self, ini_object):
        engine_data_params = ["MECHANICAL_EFFICIENCY", "IDLE_THROTTLE", "IDLE_CUTOFF"]
        for param in engine_data_params:
            if param in ini_object["ENGINE_DATA"]:
                setattr(self, param.lower(), ini_object["ENGINE_DATA"][param])

    def update_ini_with_base_params(self, ini_object):
        ini_object["ENGINE_DATA"]["MECHANICAL_EFFICIENCY"] = self.mechanical_efficiency
        ini_object["ENGINE_DATA"]["IDLE_THROTTLE"] = self.idle_throttle
        ini_object["ENGINE_DATA"]["IDLE_CUTOFF"] = self.idle_cutoff


class FuelConsumptionEfficiency(ExtendedFuelConsumptionData):
    def __init__(self):
        super(FuelConsumptionEfficiency, self).__init__()
        self.thermal_efficiency: float = 0.30
        self.thermal_efficiency_dict = None
        self.fuel_lhv: int = 43
        self.turbo_efficiency: float or None = None

    def load_from_ini(self, ini_object):
        self.load_base_params_from_ini(ini_object)
        if "FUEL_CONSUMPTION" in ini_object:
            fuel_consumption_params = ["THERMAL_EFFICIENCY", "FUEL_LHV", "TURBO_EFFICIENCY"]
            for param in fuel_consumption_params:
                if param in ini_object["FUEL_CONSUMPTION"]:
                    setattr(self, param.lower(), ini_object["FUEL_CONSUMPTION"][param])
            if "THERMAL_EFFICIENCY_LUT" in ini_object["FUEL_CONSUMPTION"]:
                self.thermal_efficiency_dict = OrderedDict()
                with open(os.path.join(ini_object.dirname(),
                                       ini_object["FUEL_CONSUMPTION"]["THERMAL_EFFICIENCY_LUT"])) as f:
                    for line in f.readlines():
                        data = line.strip().split("|")
                        self.thermal_efficiency_dict[data[0]] = data[1]

    def update_ini_object(self, ini_object):
        self.update_ini_with_base_params(ini_object)
        ini_object["FUEL_CONSUMPTION"]["THERMAL_EFFICIENCY"] = self.thermal_efficiency
        ini_object["FUEL_CONSUMPTION"]["FUEL_LHV"] = self.fuel_lhv
        if self.turbo_efficiency:
            ini_object["FUEL_CONSUMPTION"]["TURBO_EFFICIENCY"] = self.turbo_efficiency
        if self.thermal_efficiency_dict:
            ini_object["FUEL_CONSUMPTION"]["THERMAL_EFFICIENCY_LUT"] = THERMAL_EFFICIENCY_RATIO_LUT_NAME
            with open(os.path.join(ini_object.dirname(), THERMAL_EFFICIENCY_RATIO_LUT_NAME)) as f:
                for torque_ratio, thermal_efficiency in self.thermal_efficiency_dict.items():
                    f.write(f'{torque_ratio}|{thermal_efficiency}\n')


class FuelConsumptionFlowRate(ExtendedFuelConsumptionData):
    def __init__(self):
        super(FuelConsumptionFlowRate, self).__init__()
        self.max_fuel_flow_lut = None
        self.max_fuel_flow = 0

    def load_from_ini(self, ini_object):
        self.load_base_params_from_ini(ini_object)
        if "FUEL_CONSUMPTION" not in ini_object:
            return
        self.max_fuel_flow = ini_object["FUEL_CONSUMPTION"]["MAX_FUEL_FLOW"]
        if "MAX_FUEL_FLOW_LUT" in ini_object["FUEL_CONSUMPTION"]:
            self.max_fuel_flow_lut = dict()
            with open(os.path.join(ini_object.dirname(), ini_object["FUEL_CONSUMPTION"]["MAX_FUEL_FLOW_LUT"]), "r") as f:
                for line in f.readlines():
                    data = line.strip().split("|")
                    if len(data) > 1:
                        self.max_fuel_flow_lut[data[0]] = data[1]

    def update_ini_object(self, ini_object):
        self.update_ini_with_base_params(ini_object)
        ini_object["FUEL_CONSUMPTION"] = dict()
        ini_object["FUEL_CONSUMPTION"]["MAX_FUEL_FLOW"] = self.max_fuel_flow
        if self.max_fuel_flow_lut:
            ini_object["FUEL_CONSUMPTION"]["MAX_FUEL_FLOW_LUT"] = FUEL_FLOW_LUT_NAME
            with open(os.path.join(ini_object.dirname(), FUEL_FLOW_LUT_NAME), "w+") as f:
                for rpm, max_flow_rate in self.max_fuel_flow_lut.items():
                    f.write(f'{rpm}|{max_flow_rate}\n')


class Engine(object):
    def __init__(self):
        self.metadata: EngineMetadata = EngineMetadata()
        self.ini_data = None
        self.version = 1  # The version of the assetto corsa ini file to output
        self.basic_fuel_consumption: None or int = None
        self.power_info: Power = Power()
        self.coast_curve: CoastCurve = CoastCurve()
        self.altitude_sensitivity = 0.1
        self.inertia: float = 0.0  # engine.jbeam mainEngine.inertia
        self.limiter: int = 0  # sql Variants.MaxRPM
        self.limiter_hz: int = 30
        self.minimum: int = 0  # sql Variants.IdleSpeed
        self.extended_fuel_consumption: FuelConsumptionEfficiency or FuelConsumptionFlowRate or None = None

        # We generate this from generate_resource_summary as power.lut
        self.torque_curve = None
        self.turbo: Turbo = Turbo()

        self.rpm_threshold = 0  # RPM at which the engine starts to take damage
        self.rpm_damage_k = 1  # amount of damage per second per (max - threshold)

    def load_from_dir(self, dir_name):
        self.load_settings_from_ini(IniObj(os.path.join(dir_name, "engine.ini")))

    def load_settings_from_ini(self, ini_data):
        self.metadata.load(ini_data.dirname())
        self.ini_data = ini_data
        self.version = ini_data["HEADER"]["VERSION"]
        self.altitude_sensitivity = extract_ini_primitive_value(ini_data["ENGINE_DATA"]["ALTITUDE_SENSITIVITY"], float)
        self.inertia = extract_ini_primitive_value(ini_data["ENGINE_DATA"]["INERTIA"], float)
        self.limiter = extract_ini_primitive_value(ini_data["ENGINE_DATA"]["LIMITER"], int)
        self.limiter_hz = extract_ini_primitive_value(ini_data["ENGINE_DATA"]["LIMITER_HZ"], int)
        self.minimum = extract_ini_primitive_value(ini_data["ENGINE_DATA"]["MINIMUM"], int)
        self.rpm_threshold = extract_ini_primitive_value(ini_data["DAMAGE"]["RPM_THRESHOLD"], int)
        self.rpm_damage_k = extract_ini_primitive_value(ini_data["DAMAGE"]["RPM_DAMAGE_K"], int)
        self.power_info.load_from_lut(os.path.join(self.ini_data.dirname(),
                                      extract_ini_primitive_value(self.ini_data["HEADER"]["POWER_CURVE"])))
        self.coast_curve.load_from_ini(ini_data)
        self.turbo.load_from_ini(ini_data)
        if "FUEL_CONSUMPTION" in ini_data:
            if "MAX_FUEL_FLOW" in ini_data["FUEL_CONSUMPTION"]:
                self.extended_fuel_consumption = FuelConsumptionFlowRate()
            else:
                self.extended_fuel_consumption = FuelConsumptionEfficiency()
            self.extended_fuel_consumption.load_from_ini(ini_data)

    def write(self, output_path=None, use_csp_extended_physics=False):
        if output_path is None and self.ini_data is None:
            raise IOError("No output file specified")
        ini_data = IniObj(os.path.join(output_path, "engine.ini")) if output_path else self.ini_data
        self.metadata.write(ini_data.dirname())
        if "HEADER" not in ini_data:
            ini_data["HEADER"] = dict()
        ini_data["HEADER"]["VERSION"] = self.version
        if "ENGINE_DATA" not in ini_data:
            ini_data["ENGINE_DATA"] = dict()
        ini_data["ENGINE_DATA"]["ALTITUDE_SENSITIVITY"] = self.altitude_sensitivity
        ini_data["ENGINE_DATA"]["INERTIA"] = self.inertia
        ini_data["ENGINE_DATA"]["LIMITER"] = self.limiter
        ini_data["ENGINE_DATA"]["LIMITER_HZ"] = self.limiter_hz
        ini_data["ENGINE_DATA"]["MINIMUM"] = self.minimum
        self.power_info.write_power_files(ini_data)
        self.coast_curve.update_ini(ini_data)
        if "DAMAGE" not in ini_data:
            ini_data["DAMAGE"] = dict()
        ini_data["DAMAGE"]["RPM_THRESHOLD"] = self.rpm_threshold
        ini_data["DAMAGE"]["RPM_DAMAGE_K"] = self.rpm_damage_k
        self.turbo.update_ini(ini_data)
        if use_csp_extended_physics:
            if self.extended_fuel_consumption:
                self.extended_fuel_consumption.update_ini_object(ini_data)
        else:
            for param in ["MECHANICAL_EFFICIENCY", "IDLE_THROTTLE", "IDLE_CUTOFF"]:
                if param in ini_data["ENGINE_DATA"]:
                    ini_data["ENGINE_DATA"].pop(param)
            if "FUEL_CONSUMPTION" in ini_data:
                ini_data.pop("FUEL_CONSUMPTION")
        ini_data.write()

    def aspiration(self):
        if self.turbo.is_present():
            return TURBO
        return NATURALLY_ASPIRATED


class Power(object):
    def __init__(self):
        self.rpm_curve: List[int] = list()
        self.torque_curve: List[int] = list()

    def load_from_lut(self, lut_path):
        with open(lut_path, "r") as f:
            for line in f.readlines():
                if "|" not in line:
                    continue
                rpm, torque = tuple(line.strip().split("|"))
                self.rpm_curve.append(int(rpm))
                self.torque_curve.append(int(torque))

    def write_power_files(self, ini_data):
        with open(os.path.join(ini_data.dirname(), "power.lut"), "w+") as f:
            for idx, rpm in enumerate(self.rpm_curve):
                f.write(f"{rpm}|{self.torque_curve[idx]}\n")
        ini_data["HEADER"]["POWER_CURVE"] = "power.lut"


class CoastCurve(object):
    """
    From https://en.wikipedia.org/wiki/Engine_efficiency
    An engine has many moving parts that produce friction. Some of these friction forces remain constant
    (as long as applied load is constant); some of these friction losses increase as engine speed increases,
    such as piston side forces and connecting bearing forces (due to increased inertia forces from the oscillating piston).
    A few friction forces decrease at higher speed, such as the friction force on the cam's lobes used to operate
    the inlet and outlet valves (the valves' inertia at high speed tends to pull the cam follower away from the cam lobe).
    Along with friction forces, an operating engine has pumping losses, which is the work required to move air into
    and out of the cylinders. This pumping loss is minimal at low speed, but increases approximately as the square of the
    speed, until at rated power an engine is using about 20% of total power production to overcome
    friction and pumping losses.
    """
    def __init__(self):
        # TODO this assumes coast is defined by COAST_REF
        self.curve_data_source: str = ""
        self.reference_rpm: int = 0
        self.torque: int = 0
        self.non_linearity = 0

    def curve_type(self):
        return self.curve_data_source

    def load_from_ini(self, ini_data):
        self.curve_data_source = extract_ini_primitive_value(ini_data["HEADER"]["COAST_CURVE"])
        if self.curve_data_source != FROM_COAST_REF:
            raise NotImplementedError("Can only handle coast data from COAST_REF section")
        self.reference_rpm = extract_ini_primitive_value(ini_data["COAST_REF"]["RPM"], int)
        self.torque = extract_ini_primitive_value(ini_data["COAST_REF"]["TORQUE"], int)
        self.non_linearity = extract_ini_primitive_value(ini_data["COAST_REF"]["NON_LINEARITY"], int)

    def update_ini(self, ini_data):
        ini_data["HEADER"]["COAST_CURVE"] = self.curve_data_source
        if "COAST_REF" not in ini_data:
            ini_data["COAST_REF"] = dict()
        ini_data["COAST_REF"]["RPM"] = self.reference_rpm
        ini_data["COAST_REF"]["TORQUE"] = self.torque
        ini_data["COAST_REF"]["NON_LINEARITY"] = self.non_linearity


class Turbo(object):
    """
    # This is going to need some work. We can get a boost curve
    # from the engine curves table. We've then somehow got to
    # create a curve close to it using [TURBO_N] sections
    # in the engine.ini file.
    """
    def __init__(self):
        self.rpm_curve: List[int] = list()
        self.boost_curve: List[float] = list()
        self.sections = list()
        """ 
        the pressure on the air intake that the valve can take before opening, 
        the pressure on the intake depends on throttle, this is mostly used for fmod audio
        """
        self.pressure_threshold: None or float = None
        self.turbo_boost_threshold: float = 1.0  # level of TOTAL boost before the engine starts to take damage
        self.turbo_damage_k: int = 0  # amount of damage per second per (boost - threshold)

    def load_from_ini(self, ini_data):
        self.turbo_boost_threshold = extract_ini_primitive_value(ini_data["DAMAGE"]["TURBO_BOOST_THRESHOLD"], float)
        self.turbo_damage_k = extract_ini_primitive_value(ini_data["DAMAGE"]["TURBO_DAMAGE_K"], int)
        if "BOV" in ini_data:
            self.pressure_threshold = extract_ini_primitive_value(ini_data["BOV"]["PRESSURE_THRESHOLD"], float)
        turbo_idx = 0
        while True:
            turbo_section_name = f"TURBO_{turbo_idx}"
            if turbo_section_name not in ini_data:
                break
            section = TurboSection()
            section.load_from_ini(turbo_idx, ini_data)
            self.sections.append(section)
            turbo_idx += 1

    def is_present(self):
        return len(self.sections) > 0

    def update_ini(self, ini_data):
        ini_data["DAMAGE"]["TURBO_BOOST_THRESHOLD"] = self.turbo_boost_threshold
        ini_data["DAMAGE"]["TURBO_DAMAGE_K"] = self.turbo_damage_k
        if self.is_present():
            for turbo_idx, section in enumerate(self.sections):
                section.update_ini_with_section(turbo_idx, ini_data)
            if self.pressure_threshold:
                if "BOV" not in ini_data:
                    ini_data["BOV"] = dict()
                ini_data["BOV"]["PRESSURE_THRESHOLD"] = self.pressure_threshold
        else:
            turbo_idx = 0
            while True:
                turbo_section_name = f"TURBO_{turbo_idx}"
                if turbo_section_name not in ini_data:
                    break
                ini_data.pop(turbo_section_name)
                turbo_idx += 1
            if "BOV" in ini_data:
                ini_data.pop("BOV")


class TurboSection(object):
    """
    Example:
        [TURBO_0]
        LAG_DN=0.99				; Interpolation lag used slowing down the turbo
        LAG_UP=0.992				; Interpolation lag used to spin up the turbo
        MAX_BOOST=1.38 				; Maximum boost generated. This value is never exceeded and multiply the torque
                                    ; like T=T*(1.0 + boost), so a boost of 2 will give you 3 times the torque
                                    ; at a given rpm.
        WASTEGATE=1.10				; Max level of boost before the wastegate does its things. 0 = no wastegate
        DISPLAY_MAX_BOOST=1.10		; Value used by display apps
        REFERENCE_RPM=2000			; The reference rpm where the turbo reaches maximum boost (at max gas pedal).
        GAMMA=2.5
        COCKPIT_ADJUSTABLE=0
    """
    def __init__(self):
        self.lag_dn: float = 0.0
        self.lag_up: float = 0.0
        self.max_boost: float = 0.0
        self.wastegate: float = 0.0
        self.display_max_boost: float = 0.0
        self.reference_rpm: int = 0
        self.gamma: float = 1.0
        self.cockpit_adjustable: int = 0
        self.controllers: TurboControllers = TurboControllers()

    def load_from_ini(self, section_idx, ini_data):
        turbo_section_name = f"TURBO_{section_idx}"
        self.lag_dn = extract_ini_primitive_value(ini_data[turbo_section_name]["LAG_DN"], float)
        self.lag_up = extract_ini_primitive_value(ini_data[turbo_section_name]["LAG_UP"], float)
        self.max_boost = extract_ini_primitive_value(ini_data[turbo_section_name]["MAX_BOOST"], float)
        self.wastegate = extract_ini_primitive_value(ini_data[turbo_section_name]["WASTEGATE"], float)
        self.display_max_boost = extract_ini_primitive_value(ini_data[turbo_section_name]["DISPLAY_MAX_BOOST"], float)
        self.reference_rpm = extract_ini_primitive_value(ini_data[turbo_section_name]["REFERENCE_RPM"], int)
        self.gamma = extract_ini_primitive_value(ini_data[turbo_section_name]["GAMMA"], float)
        self.cockpit_adjustable = extract_ini_primitive_value(ini_data[turbo_section_name]["COCKPIT_ADJUSTABLE"], float)
        self.controllers.load_from_dir(ini_data.dirname(), section_idx)

    def update_ini_with_section(self, section_idx, ini_data):
        turbo_section_name = f"TURBO_{section_idx}"
        if turbo_section_name not in ini_data:
            ini_data[turbo_section_name] = dict()
        ini_data[turbo_section_name]["LAG_DN"] = self.lag_dn
        ini_data[turbo_section_name]["LAG_UP"] = self.lag_up
        ini_data[turbo_section_name]["MAX_BOOST"] = self.max_boost
        ini_data[turbo_section_name]["WASTEGATE"] = self.wastegate
        ini_data[turbo_section_name]["DISPLAY_MAX_BOOST"] = self.display_max_boost
        ini_data[turbo_section_name]["REFERENCE_RPM"] = self.reference_rpm
        ini_data[turbo_section_name]["GAMMA"] = self.gamma
        ini_data[turbo_section_name]["COCKPIT_ADJUSTABLE"] = self.cockpit_adjustable
        self.controllers.write(ini_data.dirname())


class TurboControllers(object):
    def __init__(self):
        self.index = 0
        self.ini_data = None
        self.controllers = list()

    def load_from_dir(self, dirname, index):
        ctrl_filename = os.path.join(dirname, f"ctrl_turbo{index}.ini")
        if not os.path.isfile(ctrl_filename):
            return None

        self.ini_data = IniObj(ctrl_filename)
        controller_index = 0
        while True:
            if f"CONTROLLER_{controller_index}" not in self.ini_data:
                break
            c = TurboController(controller_index)
            c.load_from_ini(self.ini_data)
            self.controllers.append(c)
            controller_index += 1

    def get_filename(self):
        return f"ctrl_turbo{self.index}.ini"

    def write(self, output_dir):
        out_file = os.path.join(output_dir, self.get_filename())

        if not len(self.controllers):
            if os.path.isfile(self.get_filename()):
                os.remove(os.path.join(output_dir, self.get_filename()))
            return

        with open(out_file, "wb+") as f:
            if not self.ini_data:
                self.ini_data = IniObj(out_file)
            for controller in self.controllers:
                controller.update_ini(self.ini_data)
            self.ini_data.write(outfile=f)


TURBO_CONTROLLER_PARAMS = ["INPUT", "COMBINATOR", "FILTER", "UP_LIMIT", "DOWN_LIMIT"]
class TurboController(object):
    """
    Details taken from:
    https://www.racedepartment.com/threads/engine-ini-turbo-configuration.174373/

    Example:
        ctrl_turbo0.ini
        [CONTROLLER_0]
        INPUT=RPMS
        COMBINATOR=ADD
        ; LUT parameters are rpm|wastegate
        LUT=(0=2.0|3500=2.0|6400=1.95|6600=1.91|6800=1.85|7000=1.82|7200=1.8|7400=1.76|7600=1.73|7800=1.69|8000=1.64|8200=1.59|8400=1.53|8600=1.48|8800=1.42|9000=1.37)
        FILTER=0.99     ; new value each physics step = filter*last_step_value+(1-filter)*lut_value
        UP_LIMIT=10000  ; Set the upper limit if multiple controllers used in combination
        DOWN_LIMIT=0.0  ; Set the lower limit if multiple controllers used in combination
    """
    def __init__(self, index):
        self.index = index
        self.input = "RPMS"
        self.combinator = "ADD"
        # TODO it might be valid for this to be a filename, if so, handle the case where this is a filename
        self.lut = OrderedDict()
        self.filter: float = 0.95
        self.up_limit = 10000
        self.down_limit = 0

    def load_from_ini(self, ini_object):
        for param in TURBO_CONTROLLER_PARAMS:
            if param in ini_object:
                setattr(self, param.lower(), ini_object[f"CONTROLLER_{self.index}"][param])
        if "LUT" in ini_object[f"CONTROLLER_{self.index}"]:
            lut_value = ini_object[f"CONTROLLER_{self.index}"]["LUT"].strip()
            if lut_value.startswith("("):
                self._load_lut_from_string(lut_value)
            else:
                self._load_lut_from_file(os.path.join(ini_object.dirname, lut_value))

    def _load_lut_from_string(self, lut_string):
        lut_string = lut_string[1:-1]  # Get rid of enclosing brackets '(' ')'
        for data in lut_string.split("|"):
            self._add_lut_entry(data)

    def _load_lut_from_file(self, lut_file_path):
        with open(lut_file_path, "r") as f:
            for line in f.readlines():
                self._add_lut_entry(line)

    def _add_lut_entry(self, lut_line):
        lut_data = lut_line.strip().split("=")
        self.lut[lut_data[0]] = lut_data[1]

    def update_ini(self, ini_object):
        section_name = f"CONTROLLER_{self.index}"
        if section_name not in ini_object:
            ini_object[section_name] = dict()
        for param in TURBO_CONTROLLER_PARAMS:
            ini_object[section_name][param] = getattr(self, param.lower())
        ini_object[section_name]["LUT"] = self.get_lut_string()

    def get_lut_string(self):
        out_string = "("
        out_string += "|".join([f"{rpm}={wastegate}" for rpm, wastegate in self.lut.items()])
        out_string += ")"
        return out_string


"""
Other formulas found on the web:

Friction calculations from:
https://www.eng-tips.com/viewthread.cfm?qid=83632

Input:
RPM = 8500
CID = 355
Stroke = 3.480

FHP = ((RPM ^ 2) * Stroke * CID) / ((13.7 / ((Stroke ^ .3333) * (RPM ^ .25))) * 350000000)
Should give you 270.8 FHP

pspeed = rpm * stroke * .16666667#
factor = 1.4105813# + 1.3602189# * COS(.0001257675# * pspeed + 3.2909413#)
ftq = factor * cid
fhp = (ftq * rpm) / 5252
should give you 249.1 FHP

FMEP calculations found online
I.P = (Pmep * L * A * N * k) / 60
I.P = Indicated Power (kW)
L and A = Stroke length and Area of cross section
N = RPM
k = 1/2 for 2 stroke and 1/4 for 4 stroke

Chen-Flynn friction correlation model
FMEP = (2pi*nr*T) / Vd

the engines attempt to suck in air when the butterfly valve is closed where a near vacuum occurs.
This is a very rough approximation based on the stackoverflow answer:

the "I have no idea what I'm doing" dog meme has never been more appropriate
W (j) = difference in pressure (pa) x volume displaced (m3)
Vacuum pressure (https://www.engineeringtoolbox.com/vacuum-converter-d_460.html)
Atmospheric pressure = 101325pa
90% vacuum = 10000pa
work_done_by_one_intake_stroke = (Atmospheric pressure - Vacuum pressure) x engine_cc

1000 rpm = 16.6 rps = 8.3 intake strokes per second
work_done@1000RPM = 8.3 x work_done_by_one_intake_stroke (Watts)
torque = (9.554140127 * watts) / RPM
"""
