# Where Assetto Corsa engine parameters come from
## Altitude sensitivity
```ini
[ENGINE_DATA]
ALTITUDE_SENSITIVITY = <value>
```
I don't know much about how this is used; presumably its how much power an engine loses as you get higher from sea-level. A higher value would suggest that more power is lost when running at higher altitudes.  

This is currently always set to 0.1
## Inertia
```ini
[ENGINE_DATA]
INERTIA = <value>
```
Roughly approximates to how "free revving" the engine is. The lower the value the faster the engine can reach its max rpm.
### v1
Take the inertia value from a BeamNG mods' engine.jbeam file

## Minimum
```ini
[ENGINE_DATA]
MINIMUM = <value>
```
The rpm that the engine idles at
### v1
Take the IdleSpeed stored in the sandbox.db for the engine, or the lowest value stored within the rpm-curve for the engine - whichever is higher.

## Limiter
```ini
[ENGINE_DATA]
LIMITER = <value>
```
The rpm where the engine hits the rev limiter; stopping it going any faster.
### v1
Take the MaxRPM stored in the sandbox.db for the engine

## Limiter Hz
```ini
[ENGINE_DATA]
LIMITER_HZ = <value>
```
I'm not sure how this is used.  

This is always set to 30

## RPM Threshold
```ini
[ENGINE_DATA]
RPM_THRESHOLD = <value>
```
The max RPM the engine can run at before engine damage occurs
### v1
Take the value of limiter and add 200 rpm

### Future work
Ideally we would be able to work out the value from the stress metrics that Automation provides.

## RPM Damage K
```ini
[ENGINE_DATA]
RPM_DAMAGE_K = <value>
```
How much damage the engine takes for every second its rpm is over the value defined in RPM_THRESHOLD
### v1
This is currently always set to 1

### Future work
We could potentially set this value based upon the Quality slider for engine components. Or use the mean time to fail (MTTF) metric.

## Power Curve
```ini
[HEADER]
POWER_CURVE="power.lut"
```
Points to a file within the cars' data directory that provides a mapping between engine rpm and torque generated at the wheels at that rpm when the engine is naturally aspirated. `rpm|torque(Nm)`
### v1
For naturally aspirated engines this is a simple mapping from the torque curve stored within the sandbox.db file with the assumption that drivetrain is 85% efficient i.e.
`rpm|torque@rpm * drive-type-efficiency`
For turbocharged engines the mapping takes into account that the torque curve in the sandbox.db will include torque made with turbo pressure so this will be adjusted based upon the BoostCurve that is also stored within the sandbox.db. The values used will be
`rpm|(torque@rpm / (1+boost@rpm)) * drive-type-efficiency`
where:
```
AWD efficiency = 0.75
RWD efficiency = 0.85 
FWD efficiency = 0.9
```
## Future work
Allow this to be a variable that could be set through some config 

## Turbo sections
### v1
In order to map turbo parameters from Automation to Assetto Corsa we use a combination of a turbo section and a turbo controller file.:
```ini
[TURBO_0]
LAG_DN = <value>
LAG_UP = <value>
MAX_BOOST = <value>
WASTEGATE = <value>
DISPLAY_MAX_BOOST = <value>
REFERENCE_RPM = <value>
GAMMA = <value>
COCKPIT_ADJUSTABLE = <value>
```
LAG_DN is always set to 0.99
LAG_UP is always set to 0.965
GAMMA is always set to 2.5
MAX_BOOST is set using the value of PeakBoost in the sandbox.db
WASTEGATE is set to MAX_BOOST
DISPLAY_MAX_BOOST is set to MAX_BOOST and rounded up to 1 decimal place
REFERENCE_RPM is set using the value of PeakBoostRPM in the sandbox.db and 600rpm is subtracted
COCKPIT_ADJUSTABLE is always set to 0

A ctrl_turbo0.ini file is then created to match the BoostCurve generated in the sandbox.db file.
```ini
[CONTROLLER_0]
INPUT=RPMS
COMBINATOR=ADD
LUT=<value-mappings>
FILTER=0.95
UP_LIMIT=10000
DOWN_LIMIT=0.0
```
The lut values are set to `rpm|boost@rpm`

The premise behind this approach is that the turbo behaviour will be "about right" without much tweaking. The TURBO_0 section sets it up in such a way that the boost is available in the lower rpms and then the CONTROLLER_0 throttles the boost with the wastegate parameter to simulate the correct boost levels at a given RPM

## Future work
The current mechanism should approximate turbo threshold pretty well but doesn't account for different amounts of turbo lag - the scenario where the rpm is above the threshold needed to generate max boost whilst we are off throttle and then re-apply the throttle will not be very accurate and wont vary (I don't think) from engine to engine. To address this in future it would be good if we could find a "best fit" - potentially the largest LAG_UP (maybe including GAMMA) value that can be applied whilst still allowing the values in the turbo controller to be hit. This will require more looking into


## Fuel Consumption
This is defined in the car.ini when using the base Assetto Corsa physics
```ini
[FUEL]
CONSUMPTION = <value>
```
According to comments in the data files fuel consumption is calculated in the following manner every second:
(rpm*gas*CONSUMPTION) / 1000

It can also be defined in a more accurate manner by using the extended physics that are available when using Custom Shader Patch (CSP); this can be enabled/disabled when creating the engine data. With the extended physics enabled we can use fuel flow rates for modelling fuel consumption. This is enabled by using a FUEL_CONSUMPTION section in the engine.ini file.
```ini
[FUEL_CONSUMPTION]
MAX_FUEL_FLOW_LUT=max_flow.lut
```
each value in max_flow.lut is `rpm|litres_per_hour`

### v1
To calculate a value for the AC base physics fuel consumption constant we start with the following equation:
`Fuel Use (l/h) = (Engine Power (kW) * BSFC@Power) / Fuel density kg/m3`and substitute in `fuel_use_per_sec = (("PeakPower" * "Econ") / 750) / 36000`. We then substitute this value into the equation AC uses for fuel consumption `fuel_use_per_sec = ("PeakPowerRPM"*1*C) / 1000` - giving us the equation:
`CONSUMPTION = (fuel_use_per_sec * 1000) / "PeakPowerRPM"`

If the tool is allowed to use CSP extended physics then max_flow.lut is populated by starting with the equation `Fuel consumption (g/s) = BSFC (g/j) * Power (watts)` and plugging in the values `consumption (g/s) = (EconCurve@rpm/3600000) * (PowerCurve@rpm*1000)"` then taking that value and converting it to litres per hour by multiplying by 3.6

## Coast Curve
```ini
[COAST_REF]
RPM=6500
TORQUE=38
NON_LINEARITY=0
```
A way of simulating the torque used to slow the car down through engine braking. The TORQUE value applies at the
provided RPM and then the value drops linearly as the RPM goes down unless NON_LINEARITY is set.

### v1
The Friction and dynamic friction data is available from the engine.jbeam exported file. 
The dynamic friction torque on the engine in Nm/s - this is a friction torque which increases proportional to 
engine AV (rad/s).  
`angular_velocity_at_max_rpm = ("MaxRPM" * 2 * math.pi) / 60`  
`friction_torque = (angular_velocity_at_max_rpm * dynamic_friction) + (2 * friction)`

### Future work
The values that come out for this seem much lower than the values used on Kunos cars so I suspect something is
missing - this needs more investigation. Potentially pumping losses need adding somehow?
https://mechanics.stackexchange.com/questions/33271/engine-braking-force
