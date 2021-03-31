import toml
import os

from typing import List
from collections import namedtuple
from sim_racing_tools.utils import IniObj, extract_ini_primitive_value

NATURALLY_ASPIRATED = "n/a"
TURBO = "turbo"

FROM_COAST_REF = "FROM_COAST_REF"


def load_engine(engine_ini_path):
    e = Engine()
    engine_ini_data = IniObj(engine_ini_path)
    e.load_settings_from_ini(engine_ini_data)
    return e


class Engine(object):
    def load_settings_from_ini(self, ini_data):
        self.ini_data = ini_data
        self.version = extract_ini_primitive_value(ini_data["HEADER"]["VERSION"], int)
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

    def __init__(self):
        self.ini_data = None
        self.version = 1  # The version of the assetto corsa ini file to output
        self.mass_kg: int = 0  # sql Variants.Weight

        self.power_info: Power = Power()
        self.coast_curve: CoastCurve = CoastCurve()
        self.altitude_sensitivity = 0.1
        self.inertia: float = 0.0  # engine.jbeam mainEngine.inertia
        self.limiter: int = 0  # sql Variants.MaxRPM
        self.limiter_hz: int = 30
        self.minimum: int = 0  # sql Variants.IdleSpeed

        # We generate this from generate_resource_summary as power.lut
        self.torque_curve = None
        self.turbo: Turbo = Turbo()

        self.rpm_threshold = 0  # RPM at which the engine starts to take damage
        self.rpm_damage_k = 1  # amount of damage per second per (max - threshold)

    def aspiration(self):
        if self.turbo.is_present():
            return TURBO
        return NATURALLY_ASPIRATED

    def max_power_stats(self):
        # sql Variants.PeakPower - needs converting from KW
        # sql Variants.PeakPowerRPM
        self.max_power: dict[int, int] = {}  # hp at rpm

    def max_torque_stats(self):
        # sql Variants.PeakTorque
        # sql Variants.PeakTorqueRPM
        self.max_torque: dict[int, int] = {}  # Nm at rpm

    def to_toml(self):
        return toml.dumps({"mass_kg": self.mass_kg,
                           "max_power": f"{self.max_power[0]}@{self.max_power[1]}",
                           "max_torque": f"{self.max_torque[0]}@{self.max_torque[1]}",
                           "inertia": self.inertia,
                           "idle_rpm": self.minimum,
                           "max_rpm": self.limiter,
                           "fuel_consumption_constant": self.fuel_consumption,
                           "coast_curve_info": f"Ref RPM: {self.coast_curve.reference_rpm} "
                                               f"Torque: {self.coast_curve.torque}"})


class Power(object):
    def __init__(self):
        self.rpm_curve: List[int] = list()
        self.torque_curve: List[int] = list()

    def load_from_lut(self, lut_path):
        with open(lut_path, "r") as f:
            rpm, torque = tuple(f.readline().strip().split("|"))
            self.rpm_curve.append(int(rpm))
            self.torque_curve.append(int(torque))


class CoastCurve(object):
    """
     Engine braking (coast) will come from 2 things:
      1 - Friction from the engine
          The following data is available from the engine.jbeam exported file
          The dynamic friction torque on the engine in Nm/s.
          This is a friction torque which increases proportional to engine AV (rad/s).
          AV = (2pi * RPM) / 60
          friction torque = (AV * dynamicFriction) + 2*staticFriction
          dynamicFriction = brakingcoefRPS/2pi from pre 0.7.2.
          So dynamicFriction*2pi = braking_coefficientRPS
          friction torque = (ref_rpm * (brakingCoefficientRPS / 60)) + staticFriction

      #### NOTE ####
      For now we are only going to consider the friction as this is easier to derive from the
      BeamNG data we have

      2 - the engines attempt to suck in air when the butterfly valve is closed where a near vacuum occurs.
          This is a very rough approximation based on the stackoverflow answer:

          the "I have no idea what I'm doing" dog meme has never been more appropriate
          W (j) = difference in pressure (pa) x volume displaced (m3)
          Vacuum pressure (https://www.engineeringtoolbox.com/vacuum-converter-d_460.html)
          Atmospheric pressure = 101325pa
          95% vacuum = 5000pa
          work_done_by_one_intake_stroke = (Atmospheric pressure - Vacuum pressure) x engine_cc

          1000 rpm = 16.6 rps = 8.3 intake strokes per second
          work_done@1000RPM = 8.3 x work_done_by_one_intake_stroke (Watts)
          torque = (9.554140127 * watts) / RPM
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
TurboSection = namedtuple('TurboSection',
                          ['lag_dn', 'lag_up', 'max_boost', 'wastegate', 'display_max_boost',
                           'reference_rpm', 'gamma', 'cockpit_adjustable'])
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
        self.turbo_boost_threshold: float = 0  # level of TOTAL boost before the engine starts to take damage
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
            section = TurboSection(extract_ini_primitive_value(ini_data[turbo_section_name]["LAG_DN"], float),
                                   extract_ini_primitive_value(ini_data[turbo_section_name]["LAG_UP"], float),
                                   extract_ini_primitive_value(ini_data[turbo_section_name]["MAX_BOOST"], float),
                                   extract_ini_primitive_value(ini_data[turbo_section_name]["WASTEGATE"], float),
                                   extract_ini_primitive_value(ini_data[turbo_section_name]["DISPLAY_MAX_BOOST"], float),
                                   extract_ini_primitive_value(ini_data[turbo_section_name]["REFERENCE_RPM"], int),
                                   extract_ini_primitive_value(ini_data[turbo_section_name]["GAMMA"], float),
                                   extract_ini_primitive_value(ini_data[turbo_section_name]["COCKPIT_ADJUSTABLE"], float))
            self.sections.append(section)
            turbo_idx += 1

    def is_present(self):
        return len(self.sections) > 0
