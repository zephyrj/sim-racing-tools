import os
from typing import List
from sim_racing_tools.utils import IniObj, extract_ini_primitive_value


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
        self.version = extract_ini_primitive_value(drivetrain_ini_data["HEADER"]["VERSION"], int)
        self.drive_type = extract_ini_primitive_value(drivetrain_ini_data["TRACTION"]["TYPE"])
        self.clutch_max_torque = extract_ini_primitive_value(drivetrain_ini_data["CLUTCH"]["MAX_TORQUE"], int)
        self.gearbox.load_settings_from_ini(drivetrain_ini_data)
        self.differential.load_settings_from_ini(drivetrain_ini_data)
        self.auto_clutch.load_settings_from_ini(drivetrain_ini_data)
        self.autoblip.load_settings_from_ini(drivetrain_ini_data)
        self.auto_shifter.load_settings_from_ini(drivetrain_ini_data)
        self.downshift_protection.load_settings_from_ini(drivetrain_ini_data)

    def write(self, output_path=None):
        if output_path is None and self.ini_data is None:
            raise IOError("No output file specified")

        ini_data = IniObj(os.path.join(output_path, "drivetrain.ini")) if output_path else self.ini_data
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
        self.gearbox.write_gear_files(os.path.dirname(os.path.abspath(ini_data.filename)))
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
        self.count: int = 0
        self.reverse_gear: float = 0.0
        self.gears = dict()
        self.default_gears = dict()
        self.final_gears = list()
        self.default_final_gear: float = 0.0
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
        self.count = extract_ini_primitive_value(drivetrain_ini_data["GEARS"]["COUNT"], int)
        self.reverse_gear = extract_ini_primitive_value(drivetrain_ini_data["GEARS"]["GEAR_R"], float)
        self.default_final_gear = extract_ini_primitive_value(drivetrain_ini_data["GEARS"]["FINAL"], float)
        for gear_num in range(1, self.count+1):
            self.default_gears[gear_num] = \
                extract_ini_primitive_value(drivetrain_ini_data["GEARS"][f"GEAR_{gear_num}"], float)
        self._lookup_gear_data(drivetrain_ini_data)

        self.change_up_time = extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["CHANGE_UP_TIME"], int)
        self.change_dn_time = extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["CHANGE_DN_TIME"], int)
        self.auto_cutoff_time = extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["AUTO_CUTOFF_TIME"], int)
        self.supports_shifter = extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["SUPPORTS_SHIFTER"], int)
        self.valid_shift_rpm_window = extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["VALID_SHIFT_RPM_WINDOW"], int)
        self.controls_window_gain = extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["CONTROLS_WINDOW_GAIN"], float)
        if "INERTIA" in drivetrain_ini_data["GEARBOX"]:
            self.inertia = extract_ini_primitive_value(drivetrain_ini_data["GEARBOX"]["INERTIA"], float)

    def update_ini(self, ini_object):
        if "GEARS" not in ini_object:
            ini_object["GEARS"] = dict()
        ini_object["GEARS"]["COUNT"] = self.count
        ini_object["GEARS"]["GEAR_R"] = self.reverse_gear
        ini_object["GEARS"]["FINAL"] = self.default_final_gear
        for gear_num, gear_ratio in sorted(self.default_gears.items()):
            ini_object["GEARS"][f"GEAR_{gear_num}"] = gear_ratio
        self.write_gear_files(os.path.dirname(os.path.abspath(ini_object.filename)))
        if "GEARBOX" not in ini_object:
            ini_object["GEARBOX"] = dict()
        ini_object["GEARBOX"]["CHANGE_UP_TIME"] = self.change_up_time
        ini_object["GEARBOX"]["CHANGE_DN_TIME"] = self.change_dn_time
        ini_object["GEARBOX"]["AUTO_CUTOFF_TIME"] = self.auto_cutoff_time
        ini_object["GEARBOX"]["SUPPORTS_SHIFTER"] = self.supports_shifter
        ini_object["GEARBOX"]["VALID_SHIFT_RPM_WINDOW"] = self.valid_shift_rpm_window
        ini_object["GEARBOX"]["CONTROLS_WINDOW_GAIN"] = self.controls_window_gain
        ini_object["GEARBOX"]["INERTIA"] = self.inertia

    def write_gear_files(self, output_dir):
        setup_file = os.path.join(output_dir, "setup.ini")
        setup_ini = IniObj(setup_file)
        for gear_num, gear_list in sorted(self.gears.items()):
            gear_rto_filepath = os.path.join(output_dir, f"{GEAR_LOOKUP[gear_num]}.rto")
            with open(gear_rto_filepath, "w+") as f:
                for gear in gear_list:
                    f.write(f"{gear.name}|{gear.ratio}\n")
            gear_setup_section_name = f"GEAR_{gear_num}"
            if gear_setup_section_name not in setup_ini:
                setup_ini[gear_setup_section_name] = dict()
            setup_ini[gear_setup_section_name]["RATIOS"] = os.path.basename(gear_rto_filepath)
        if self.final_gears:
            with open(os.path.join(output_dir, "final.rto"), "w+") as f:
                for gear in self.final_gears:
                    f.write(f"{gear.name}|{gear.ratio}\n")
            if "FINAL_GEAR_RATIO" not in setup_ini:
                setup_ini["FINAL_GEAR_RATIO"] = dict()
            setup_ini["FINAL_GEAR_RATIO"]["RATIOS"] = "final.rto"
        setup_ini.write()

    def _lookup_gear_data(self, ini_object):
        lookup_path = os.path.dirname(os.path.abspath(ini_object.filename))
        setup_file = os.path.join(lookup_path, "setup.ini")
        if not os.path.exists(setup_file):
            return
        ratio_files_map = dict()
        setup_ini = IniObj(setup_file)
        for idx in range(1, self.count+1):
            if f"GEAR_{idx}" not in setup_ini:
                continue
            ratio_file = extract_ini_primitive_value(setup_ini[f"GEAR_{idx}"]["RATIOS"])
            if ratio_file not in ratio_files_map:
                ratio_files_map[ratio_file] = list()
            ratio_files_map[ratio_file].append(idx)

        if "FINAL_GEAR_RATIO" in setup_ini:
            ratio_file = extract_ini_primitive_value(setup_ini["FINAL_GEAR_RATIO"]["RATIOS"])
            self.final_gears.extend(Gear.load_gears_from_file(os.path.join(lookup_path, ratio_file)))

        dir_name, dirs, files = next(os.walk(lookup_path))
        for filename in files:
            if filename not in ratio_files_map:
                continue

            full_file_path = os.path.join(dir_name, filename)
            gear_list = Gear.load_gears_from_file(full_file_path)
            for gear_num in ratio_files_map[filename]:
                if gear_num not in self.gears:
                    self.gears[gear_num] = list()
                self.gears[gear_num].extend(gear_list)


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
GEAR_LOOKUP = {1: FIRST, 2: SECOND, 3: THIRD, 4: FOURTH, 5: FIFTH, 6: SIXTH, 7: SEVENTH, 8: EIGHTH}


class Gear(object):
    @staticmethod
    def load_gears_from_file(file_path):
        with open(file_path, "r") as f:
            gear_list = list()
            for line in f.readlines():
                gear_info = line.strip().split("|")
                if len(gear_info) > 1:
                    gear_list.append(Gear(gear_info[0], float(gear_info[1])))
        return gear_list

    def __init__(self, name, ratio):
        self.name: str = name
        self.ratio: float = ratio


class Differential(object):
    def __init__(self):
        self.power: float = 0.0
        self.coast: float = 0.0
        self.preload: int = 13

    def load_settings_from_ini(self, drivetrain_ini_data):
        self.power = extract_ini_primitive_value(drivetrain_ini_data["DIFFERENTIAL"]["POWER"], float)
        self.coast = extract_ini_primitive_value(drivetrain_ini_data["DIFFERENTIAL"]["COAST"], float)
        self.preload = extract_ini_primitive_value(drivetrain_ini_data["DIFFERENTIAL"]["PRELOAD"], int)

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
        up_profile = extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["UPSHIFT_PROFILE"])
        if up_profile.lower() != "none":
            self.upshift_profile = ShiftProfile.create_from_section(drivetrain_ini_data, up_profile)
        down_profile = extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["DOWNSHIFT_PROFILE"])
        if down_profile.lower() != "none":
            self.downshift_profile = ShiftProfile.create_from_section(drivetrain_ini_data, down_profile)
        self.use_on_changes = extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["USE_ON_CHANGES"], int)
        self.min_rpm = extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["MIN_RPM"], int)
        self.max_rpm = extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["MAX_RPM"], int)
        self.forced_on = extract_ini_primitive_value(drivetrain_ini_data["AUTOCLUTCH"]["FORCED_ON"], int)

    def update_ini(self, ini_object):
        if "AUTOCLUTCH" not in ini_object:
            ini_object["AUTOCLUTCH"] = dict()
        if self.upshift_profile:
            ini_object["AUTOCLUTCH"]["UPSHIFT_PROFILE"] = self.upshift_profile.name
            self.upshift_profile.update_ini(ini_object)
        if self.downshift_profile:
            ini_object["AUTOCLUTCH"]["DOWNSHIFT_PROFILE"] = self.downshift_profile.name
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
            profile.points.append(extract_ini_primitive_value(ini_data[section_name][f"POINT_{idx}"], int))
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
        self.electronic = extract_ini_primitive_value(drivetrain_ini_data["AUTOBLIP"]["ELECTRONIC"], int)
        for idx in range(3):
            self.points.append(extract_ini_primitive_value(drivetrain_ini_data["AUTOBLIP"][f"POINT_{idx}"], int))
        self.level = extract_ini_primitive_value(drivetrain_ini_data["AUTOBLIP"]["LEVEL"], float)

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
        self.up = extract_ini_primitive_value(drivetrain_ini_data["AUTO_SHIFTER"]["UP"], int)
        self.down = extract_ini_primitive_value(drivetrain_ini_data["AUTO_SHIFTER"]["DOWN"], int)
        self.slip_threshold = extract_ini_primitive_value(drivetrain_ini_data["AUTO_SHIFTER"]["SLIP_THRESHOLD"], float)
        self.gas_cutoff_time = extract_ini_primitive_value(drivetrain_ini_data["AUTO_SHIFTER"]["GAS_CUTOFF_TIME"], float)

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
        self.active = extract_ini_primitive_value(drivetrain_ini_data["DOWNSHIFT_PROTECTION"]["ACTIVE"], int)
        self.debug = extract_ini_primitive_value(drivetrain_ini_data["DOWNSHIFT_PROTECTION"]["DEBUG"], int)
        self.overrev = extract_ini_primitive_value(drivetrain_ini_data["DOWNSHIFT_PROTECTION"]["OVERREV"], int)
        self.lock_n = extract_ini_primitive_value(drivetrain_ini_data["DOWNSHIFT_PROTECTION"]["LOCK_N"], int)

    def update_ini(self, ini_object):
        if "DOWNSHIFT_PROTECTION" not in ini_object:
            ini_object["DOWNSHIFT_PROTECTION"] = dict()
        ini_object["DOWNSHIFT_PROTECTION"]["ACTIVE"] = self.active
        ini_object["DOWNSHIFT_PROTECTION"]["DEBUG"] = self.debug
        ini_object["DOWNSHIFT_PROTECTION"]["OVERREV"] = self.overrev
        ini_object["DOWNSHIFT_PROTECTION"]["LOCK_N"] = self.lock_n
