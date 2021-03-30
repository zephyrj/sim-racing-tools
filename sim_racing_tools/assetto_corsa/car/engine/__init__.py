import toml

from typing import List
from collections import namedtuple
import sim_racing_tools.utils as utils


class Engine(object):
    NATURALLY_ASPIRATED = "n/a"
    TURBO = "turbo"

    @staticmethod
    def load_from_ini(filename):
        ini_data = utils.IniObj(filename)
        engine = Engine()
        engine.version = ini_data["HEADER"]["VERSION"]
        engine.altitude_sensitivity = ini_data["ENGINE_DATA"]["ALTITUDE_SENSITIVITY"]
        engine.inertia = ini_data["ENGINE_DATA"]["INERTIA"]
        engine.limiter = ini_data["ENGINE_DATA"]["LIMITER"]
        engine.limiter_hz = ini_data["ENGINE_DATA"]["LIMITER_HZ"]
        engine.minimum = ini_data["ENGINE_DATA"]["MINIMUM"]

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
        self.turbo = None

        self.rpm_threshold = 6700  # RPM at which the engine starts to take damage
        self.rpm_damage_k = 1  # amount of damage per second per (max - threshold)

    def aspiration(self):
        if self.turbo:
            return Engine.TURBO
        return Engine.NATURALLY_ASPIRATED

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
    FROM_COAST_REF = "FROM_COAST_REF"

    def __init__(self):
        # TODO this assumes coast is defined by COAST_REF
        self.reference_rpm: int = 0
        self.torque: int = 0
        self.non_linearity = 0

    def curve_type(self):
        return CoastCurve.FROM_COAST_REF


class Turbo(object):
    TurboSection = namedtuple('TurboSection',
                              ['lag_dn', 'lag_up', 'max_boost', 'wastegate',
                               'reference_rpm', 'gamma', 'cockpit_adjustable'])
    """
    # This is going to need some work. We can get a boost curve
    # from the engine curves table. We've then somehow got to
    # create a curve close to it using [TURBO_N] sections
    # in the engine.ini file.
    """
    def __init__(self):
        self.rpm_curve: List[int] = list()
        self.boost_curve: List[float] = list()
        self.pressure_threshold: float = 0.5
        self.turbo_boost_threshold = 0  # level of TOTAL boost before the engine starts to take damage
        self.turbo_damage_k = 0  # amount of damage per second per (boost - threshold)


class Power(object):
    def __init__(self):
        self.rpm_curve: List[int] = list()
        self.torque_curve: List[int] = list()
