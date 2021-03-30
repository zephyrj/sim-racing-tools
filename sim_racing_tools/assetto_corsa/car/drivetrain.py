from typing import List
from sim_racing_tools.utils import IniObj


def load_drivetrain(drivetrain_ini_path):
    d = Drivetrain()
    drivetrain_ini_data = IniObj(drivetrain_ini_path)
    d.load_settings_from_ini(drivetrain_ini_data)
    return d


class Drivetrain(object):
    def __init__(self):
        self.ini_data = None
        self.version: int = 3
        self.drive_type: str = DriveType.RWD
        self.gearbox: Gearbox = Gearbox()
        self.differential: Differential = Differential()
        self.clutch_max_torque: int = 0
        self.auto_clutch: AutoClutch = AutoClutch()
        self.autoblip: AutoBlip = AutoBlip()
        self.auto_shifter: AutoShifter = AutoShifter()
        self.downshift_protection: DownshiftProtection = DownshiftProtection()

    def load_settings_from_ini(self, drivetrain_ini_data):
        self.ini_data = drivetrain_ini_data
        self.version = int(_extract_ini_primitive_value(drivetrain_ini_data["HEADER"]["VERSION"]))
        self.drive_type = _extract_ini_primitive_value(drivetrain_ini_data["TRACTION"]["TYPE"])
        self.clutch_max_torque = int(_extract_ini_primitive_value(drivetrain_ini_data["CLUTCH"]["MAX_TORQUE"]))
        self.gearbox.load_settings_from_ini(drivetrain_ini_data)
        self.differential.load_settings_from_ini(drivetrain_ini_data)
        self.auto_clutch.load_settings_from_ini(drivetrain_ini_data)
        self.autoblip.load_settings_from_ini(drivetrain_ini_data)
        self.auto_shifter.load_settings_from_ini(drivetrain_ini_data)
        self.downshift_protection.load_settings_from_ini(drivetrain_ini_data)

    def write(self, output_path=None):
        if output_path is None and self.ini_data is None:
            raise IOError("No output file specified")

        ini_data = IniObj(output_path) if output_path else self.ini_data
        if "HEADER" not in ini_data:
            ini_data["HEADER"] = dict()
        ini_data["HEADER"]["VERSION"] = self.version
        if "TRACTION" not in ini_data:
            ini_data["TRACTION"] = dict()
        ini_data["TRACTION"]["TYPE"] = self.drive_type
        if "CLUTCH" not in ini_data:
            ini_data["CLUTCH"] = dict()
        ini_data["CLUTCH"]["MAX_TORQUE"] = self.clutch_max_torque
        self.gearbox.update_ini(ini_data)
        self.gearbox.write_gear_files()
        self.differential.update_ini(ini_data)
        self.auto_clutch.update_ini(ini_data)
        self.autoblip.update_ini(ini_data)
        self.auto_shifter.update_ini(ini_data)
        self.downshift_protection.update_ini(ini_data)
        ini_data.write()


class DriveType(object):
    RWD = "RWD"
    FWD = "FWD"


class Gearbox(object):
    def __init__(self):
        self.gears = dict()
        ''' change up time in milliseconds '''
        self.change_up_time: int = 0
        ''' change down time in milliseconds '''
        self.change_dn_time: int = 0
        ''' Auto cutoff time for upshifts in milliseconds, 0 to disable '''
        self.auto_cutoff_time: int = 0
        ''' 1=Car supports shifter, 0=car supports only paddles '''
        self.supports_shifter: int = 0
        ''' range window additional to the precise rev matching rpm that permits gear engage. '''
        self.valid_shift_rpm_window: int = 0
        ''' 
        multiplayer for gas,brake,clutch pedals that permits gear engage on different rev matching rpm. 
        the lower the more difficult.
        '''
        self.controls_window_gain: float = 0.0
        ''' gearbox inertia. default values to 0.02 if not set '''
        self.inertia: float = 0.02

    def load_settings_from_ini(self, drivetrain_ini_data):
        self._lookup_gear_data()
        self.change_up_time = int(_extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["CHANGE_UP_TIME"]))
        self.change_dn_time = int(_extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["CHANGE_DN_TIME"]))
        self.auto_cutoff_time = int(_extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["AUTO_CUTOFF_TIME"]))
        self.supports_shifter = int(_extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["SUPPORTS_SHIFTER"]))
        self.valid_shift_rpm_window = int(_extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["VALID_SHIFT_RPM_WINDOW"]))
        self.controls_window_gain = float(_extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["CONTROLS_WINDOW_GAIN"]))
        if "INERTIA" in drivetrain_ini_data["GEARBOX"]:
            self.inertia = float(_extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["INERTIA"]))

    def update_ini(self, ini_object):
        if "GEARBOX" not in ini_object:
            ini_object["GEARBOX"] = dict()
        ini_object["GEARBOX"]["CHANGE_UP_TIME"] = self.change_up_time
        ini_object["GEARBOX"]["CHANGE_DN_TIME"] = self.change_dn_time
        ini_object["GEARBOX"]["AUTO_CUTOFF_TIME"] = self.auto_cutoff_time
        ini_object["GEARBOX"]["SUPPORTS_SHIFTER"] = self.supports_shifter
        ini_object["GEARBOX"]["VALID_SHIFT_RPM_WINDOW"] = self.valid_shift_rpm_window
        ini_object["GEARBOX"]["CONTROLS_WINDOW_GAIN"] = self.controls_window_gain

    def write_gear_files(self):
        pass

    def _lookup_gear_data(self):
        pass


class Gear(object):
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"
    FOURTH = "4th"
    FIFTH = "5th"
    SIXTH = "6th"
    SEVENTH = "7th"
    EIGHTH = "8th"
    FINAL = "final"
    REVERSE = "reverse"

    def __init__(self):
        self.name: str = ""
        self.ratio: float = 0.0


class Differential(object):
    def __init__(self):
        self.power: float = 0.0
        self.coast: float = 0.0
        self.preload: int = 13

    def load_settings_from_ini(self, drivetrain_ini_data):
        self.power = float(_extract_ini_primitive_value(drivetrain_ini_data["DIFFERENTIAL"]["POWER"]))
        self.coast = float(_extract_ini_primitive_value(drivetrain_ini_data["DIFFERENTIAL"]["COAST"]))
        self.preload = int(_extract_ini_primitive_value(drivetrain_ini_data["DIFFERENTIAL"]["PRELOAD"]))

    def update_ini(self, ini_object):
        if "DIFFERENTIAL" not in ini_object:
            ini_object["DIFFERENTIAL"] = dict()
        ini_object["DIFFERENTIAL"]["POWER"] = self.power
        ini_object["DIFFERENTIAL"]["COAST"] = self.coast
        ini_object["DIFFERENTIAL"]["PRELOAD"] = self.preload


class AutoClutch(object):
    def __init__(self):
        self.upshift_profile = None
        self.downshift_profile = None
        '''
        Use the autoclutch on gear shifts even when autoclutch is set to off. 
        Needed for cars with semiautomatic gearboxes. values 1,0
        '''
        self.use_on_changes: int = 0
        self.min_rpm: int = 0
        self.max_rpm: int = 0
        self.forced_on: int = 0

    def load_settings_from_ini(self, drivetrain_ini_data):
        up_profile = _extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["UPSHIFT_PROFILE"])
        if up_profile.lower() != "none":
            self.upshift_profile = ShiftProfile.create_from_section(drivetrain_ini_data, up_profile)
        down_profile = _extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["DOWNSHIFT_PROFILE"])
        if down_profile.lower() != "none":
            self.downshift_profile = ShiftProfile.create_from_section(drivetrain_ini_data, down_profile)
        self.use_on_changes = int(_extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["USE_ON_CHANGES"]))
        self.min_rpm = int(_extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["MIN_RPM"]))
        self.max_rpm = int(_extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["MAX_RPM"]))
        self.forced_on = int(_extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["FORCED_ON"]))

    def update_ini(self, ini_object):
        if "AUTOCLUTCH" not in ini_object:
            ini_object["AUTOCLUTCH"] = dict()
        if self.upshift_profile:
            self.upshift_profile.update_ini(ini_object)
        if self.downshift_profile:
            self.downshift_profile.update_ini(ini_object)
        ini_object["AUTOCLUTCH"]["USE_ON_CHANGES"] = self.use_on_changes
        ini_object["AUTOCLUTCH"]["MIN_RPM"] = self.min_rpm
        ini_object["AUTOCLUTCH"]["MAX_RPM"] = self.max_rpm
        ini_object["AUTOCLUTCH"]["FORCED_ON"] = self.forced_on


class ShiftProfile(object):
    @staticmethod
    def create_from_section(ini_data, section_name):
        profile = ShiftProfile()
        profile.name = section_name
        for idx in range(3):
            profile.points.append(int(_extract_ini_primitive_value(ini_data[section_name][f"POINT_{idx}"])))
        return profile

    def __init__(self):
        self.name = ""
        self.points: List[int] = list()

    def update_ini(self, ini_object):
        if self.name not in ini_object:
            ini_object[self.name] = dict()
        for idx, point in enumerate(self.points):
            ini_object[self.name][f"POINT_{idx}"] = point


class AutoBlip(object):
    def __init__(self):
        """ If =1 then it is a feature of the car and cannot be disabled """
        self.electronic: int = 0
        """
        In tatuus:
          - 0 = Time to reach full level
          - 1 = Time to start releasing gas
          - 2 = Time to reach 0 gas
        """
        self.points: List[int] = list()
        """ Gas level to be reached """
        self.level: float = 0.0

    def load_settings_from_ini(self, drivetrain_ini_data):
        self.electronic = int(_extract_ini_primitive_value(drivetrain_ini_data["AUTOBLIP"]["ELECTRONIC"]))
        for idx in range(3):
            self.points.append((int(_extract_ini_primitive_value(drivetrain_ini_data["AUTOBLIP"][f"POINT_{idx}"]))))
        self.level = float(_extract_ini_primitive_value(drivetrain_ini_data["AUTOBLIP"]["LEVEL"]))

    def update_ini(self, ini_object):
        if "AUTOBLIP" not in ini_object:
            ini_object["AUTOBLIP"] = dict()
        ini_object["AUTOBLIP"]["ELECTRONIC"] = self.electronic
        for idx, point in enumerate(self.points):
            ini_object["AUTOBLIP"][f"POINT_{idx}"] = point
        ini_object["AUTOBLIP"]["LEVEL"] = self.level


class AutoShifter(object):
    def __init__(self):
        self.up: int = 0
        self.down: int = 0
        self.slip_threshold: float = 0.0
        self.gas_cutoff_time: float = 0.0

    def load_settings_from_ini(self, drivetrain_ini_data):
        self.up = int(_extract_ini_primitive_value(drivetrain_ini_data["AUTO_SHIFTER"]["UP"]))
        self.down = int(_extract_ini_primitive_value(drivetrain_ini_data["AUTO_SHIFTER"]["DOWN"]))
        self.slip_threshold = float(_extract_ini_primitive_value(drivetrain_ini_data["AUTO_SHIFTER"]["SLIP_THRESHOLD"]))
        self.gas_cutoff_time = float(_extract_ini_primitive_value(drivetrain_ini_data["AUTO_SHIFTER"]["GAS_CUTOFF_TIME"]))

    def update_ini(self, ini_object):
        if "AUTO_SHIFTER" not in ini_object:
            ini_object["AUTO_SHIFTER"] = dict()
        ini_object["AUTO_SHIFTER"]["UP"] = self.up
        ini_object["AUTO_SHIFTER"]["DOWN"] = self.down
        ini_object["AUTO_SHIFTER"]["SLIP_THRESHOLD"] = self.slip_threshold
        ini_object["AUTO_SHIFTER"]["GAS_CUTOFF_TIME"] = self.gas_cutoff_time


class DownshiftProtection(object):
    def __init__(self):
        self.active = 1
        ''' adds a line in the log for every missed downshift '''
        self.debug = 0
        ''' How many RPM over the limiter the car is allowed to go '''
        self.overrev = 200
        self.lock_n = 1

    def load_settings_from_ini(self, drivetrain_ini_data):
        self.active = int(_extract_ini_primitive_value(drivetrain_ini_data["DOWNSHIFT_PROTECTION"]["ACTIVE"]))
        self.debug = int(_extract_ini_primitive_value(drivetrain_ini_data["DOWNSHIFT_PROTECTION"]["DEBUG"]))
        self.overrev = int(_extract_ini_primitive_value(drivetrain_ini_data["DOWNSHIFT_PROTECTION"]["OVERREV"]))
        self.lock_n = int(_extract_ini_primitive_value(drivetrain_ini_data["DOWNSHIFT_PROTECTION"]["LOCK_N"]))

    def update_ini(self, ini_object):
        if "DOWNSHIFT_PROTECTION" not in ini_object:
            ini_object["DOWNSHIFT_PROTECTION"] = dict()
        ini_object["DOWNSHIFT_PROTECTION"]["ACTIVE"] = self.active
        ini_object["DOWNSHIFT_PROTECTION"]["DEBUG"] = self.debug
        ini_object["DOWNSHIFT_PROTECTION"]["OVERREV"] = self.overrev
        ini_object["DOWNSHIFT_PROTECTION"]["LOCK_N"] = self.lock_n


def _extract_ini_primitive_value(returned_val):
    if isinstance(returned_val, list):
        returned_val = returned_val[0]
    return returned_val.split()[0]
