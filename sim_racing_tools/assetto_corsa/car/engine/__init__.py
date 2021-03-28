import toml


class Engine(object):
    def __init__(self):
        # sql Variants.Weight
        self.mass_kg: int = 0

        # sql Variants.PeakPower - needs converting from KW
        # sql Variants.PeakPowerRPM
        self.max_power: dict[int, int] = {}  # hp at rpm

        # sql Variants.PeakTorque
        # sql Variants.PeakTorqueRPM
        self.max_torque: dict[int, int] = {}  # Nm at rpm

        # engine.jbeam mainEngine.inertia
        self.inertia: float = 0.0

        # sql Variants.IdleSpeed
        self.min_rpm: int = 0

        # sql Variants.MaxRPM
        self.max_rpm: int = 0

        # sql EngineResults.Econ = BSFC (g/(kWh))
        # EconEff = 1 / (BSFC * "LHV of fuel")
        # LHC of gasoline from wikipedia -> 0.0122222
        # bsfc = (fuel consumption rate) / (Power output) = M.f / Pwrb kg/kWh
        # 1680.8221 = r / 167236.78
        # Q = N * q / R, where
        # Q – (in l / h) maximum theoretical fuel consumption in grams per 1 hour of engine operation at maximum power;
        # q – (in g / kWh) specific fuel consumption for power N;
        # N – (in kW) engine power;
        # R – (kg / m3) fuel density
        # Gasoline (petrol) fuel density: 710 – 760 kg / m3
        # fuel consumption. In one second the consumption is (rpm*gas*CONSUMPTION)/1000 litres
        # is gas 0 - 1 or 0 - 100?
        # 0.175698056 = (8600 * 100 * C) / 100
        # 632.513 l/h
        self.fuel_consumption: float = 0.0

        # We generate this from generate_resource_summary as power.lut
        self.torque_curve = None

        # Engine braking will come from 2 things:
        #  1 - Friction from the engine
        #      The follow data is available from the engine.jbeam exported file
        #      The dynamic friction torque on the engine in Nm/s.
        #      This is a friction torque which increases proportional to engine AV (rad/s).
        #      AV = (2pi * RPM) / 60
        #      friction torque = (AV * dynamicFriction) + 2*staticFriction
        #      dynamicFriction = brakingcoefRPS/2pi from pre 0.7.2.
        #      So dynamicFriction*2pi = braking_coefficientRPS
        #      friction torque = (ref_rpm * (brakingCoefficientRPS / 60)) + staticFriction
        #
        #  2 - the engines attempt to suck in air when the butterfly valve is closed where a near vacuum occurs.
        #      This is a very rough approximation based on the stackoverflow answer:
        #
        #      the "I have no idea what I'm doing" dog meme has never been more appropriate
        #      W (j) = difference in pressure (pa) x volume displaced (m3)
        #      Vacuum pressure (https://www.engineeringtoolbox.com/vacuum-converter-d_460.html)
        #      Atmospheric pressure = 101325pa
        #      95% vacuum = 5000pa
        #      work_done_by_one_intake_stroke = (Atmospheric pressure - Vacuum pressure) x engine_cc

        #      1000 rpm = 16.6 rps = 8.3 intake strokes per second
        #      work_done@1000RPM = 8.3 x work_done_by_one_intake_stroke (Watts)
        #      torque = (9.554140127 * watts) / RPM
        self.coast_curve_info = None

        # This is going to need some work. We can get a boost curve
        # from the engine curves table. We've then somehow got to
        # create a curve close to it using [TURBO_N] sections
        # in the engine.ini file.
        self.turbos = list()

    def to_toml(self):
        return toml.dumps({"mass_kg": self.mass_kg,
                           "max_power": f"{self.max_power[0]}@{self.max_power[1]}",
                           "max_torque": f"{self.max_torque[0]}@{self.max_torque[1]}",
                           "inertia": self.inertia,
                           "idle_rpm": self.min_rpm,
                           "max_rpm": self.max_rpm,
                           "fuel_consumption_constant": self.fuel_consumption,
                           "coast_curve_info": f"Ref RPM: {self.coast_curve_info[0]} "
                                               f"Torque: {self.coast_curve_info[1]}"})
