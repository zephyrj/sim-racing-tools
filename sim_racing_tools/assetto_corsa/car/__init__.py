from typing import List


class Car(object):
    def __init__(self):
        self.ini_data = None
        self.ui_info = UIInfo()
        self.version: int = 1
        self.screen_name: str = ""
        self.total_mass: int = 0  # total vehicle weight in kg with driver and no fuel
        '''
        sql EngineResults.Econ = BSFC (g/(kWh))
        EconEff = 1 / (BSFC * "LHV of fuel")
        LHC of gasoline from wikipedia -> 0.0122222
        bsfc = (fuel consumption rate) / (Power output) = M.f / Pwrb kg/kWh
        1680.8221 = r / 167236.78
        Q = N * q / R, where
        Q – (in l / h) maximum theoretical fuel consumption in grams per 1 hour of engine operation at maximum power;
        q – (in g / kWh) specific fuel consumption for power N;
        N – (in kW) engine power;
        R – (kg / m3) fuel density
        Gasoline (petrol) fuel density: 710 – 760 kg / m3
        fuel consumption. In one second the consumption is (rpm*gas*CONSUMPTION)/1000 litres
        is gas 0 - 1 or 0 - 100?
        0.175698056 = (8600 * 100 * C) / 100
        632.513 l/h
        '''
        self.fuel_consumption: float = 0.0
        self.default_fuel: int = 0  # default starting fuel in litres
        self.max_fuel: int = 0  # max fuel in litres
        self.ai_shift_up: int = 0
        self.ai_shift_down: int = 0


class UIInfo(object):
    def __init__(self):
        self.ui_ini_json = None
        self.name: str = ""
        self.brand: str = ""
        self.description: str = ""
        self.tags: List[str] = list()
        self.car_class: str = ""

        '''
        "specs":
        {
            "bhp": "198bhp",
            "torque": "230Nm",
            "weight": "455kg",
            "topspeed": "230+km/h",
            "acceleration": "--s 0-100",
            "pwratio": "2.30kg/hp",
            "range": 85
        },
        '''
        self.specs = dict()

        self.torque_curve: List[List[str]] = list()
        self.power_curve: List[List[str]] = list()
