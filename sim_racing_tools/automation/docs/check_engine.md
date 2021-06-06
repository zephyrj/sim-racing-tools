# check-engine tool
You can validate that the specifications of an engine created within automation match a set of given parameters using the `check-engine` script.

## Choose an engine to check
You can choose the engine you wish to check in one of three ways:
1. You can provide the name of the engine by using `-n`:
   ```commandline
   check-engine -n "family name" "variant name" engine_checks.toml
   ```
2. You can provide the UID of the variant in the sandbox.db file with `-u`:
   ```commandline
   check-engine -u 1C9B25A04DB1E814879CC8BDA0B1DCF0 engine_checks.toml
   ```
3. You can provide the name of a mod folder exported to BeamNG with `-c`:
   ```commandline
   check-engine -c "zephyr_piccolo_a_spec" engine_checks.toml
   ```
> Note that the final parameter `engine_checks.toml` represents the file containing the checks you want to perform. This contents of this file is described in the next section. This file can be named whatever you want

## Choose what to check for
You can then specify the parameters you wish to check for through a [.toml](https://toml.io/en/v1.0.0) file. Specify each parameter you wish to validate as a table in the file and then provide some checks you want to perform.   
e.g. You could check that an engine:
- is either an inline or V6 
- has maximum capacity of 3 litres
- has some form of catalytic convertor 
- doesn't have either no or a straight through muffler 
- has a minimum bottom-end quality of 0 and a max of 5
- runs on super (100 octane) fuel  

with the following file

```toml
[BlockConfig]
one_of = ["EngBlock_Inl6_Name", "EngBlock_V6_v90_Name"]

[Capacity]
max = 3.001

[Cat]
not = "CatConvert_None_Name"

[Muffler1]
not = ["Muffler_None_Name", "Muffler_Straight_Name"]

[QualityBottomEnd]
min = 0
max = 5

[FuelType]
equals = "FuelType_Super100_Name"
```
Another example file can be found [here](sim_racing_tools/automation/docs/check_engine.md)

### Parameters you can check
This list will need updating with more information as I work it out but here is the full list of parameters you can check:
```
'FUID', 'Cat', 'BlockType', 'CompressorFraction', 'UID', 'FuelSystemType', 'ExhaustBypassValves', 'BoostCurve', 'HeadMaterial', 'MaxRPM', 'Muffler1', 'GameVersion', 'QualityBottomEnd', 'Econ', 'Headers', 'QualityTopEnd', 'IntakeManifold', 'TorqueCurve', 'PeakPowerRPM', 'QualityFuelSystem', 'MaterialCost', 'Stroke', 'Intake', 'BoostCutOff', 'Bore', 'Tags', 'EconEff', 'TotalCost', 'VVLCamProfileSetting', 'ServiceCost', 'Valves', 'Pistons', 'AspirationOption', 'Compression', 'PeakTorqueRPM', 'EngineeringTime', 'MinEcon', 'AverageCruiseEcon', 'PeakPower', 'EconEffCurve', 'AFRLean', 'QualityExhaust', 'FuelType', 'BlockConfig', 'CamProfileSetting', 'Muffler2', 'TurbineFraction', 'ARRatio', 'QualityAspiration', 'IntercoolerSetting', 'ToolingCosts', 'Name', 'Conrods', 'VVL', 'AFR', 'PeakTorque', 'Aspiration', 'AspirationType', 'Crank', 'FuelSystem', 'Capacity', 'Weight', 'ExhaustDiameter', 'VVT', 'MTTF', 'IdleSpeed', 'EconCurve', 'RPMCurve', 'ExhaustCount', 'ManHours', 'PeakBoost', 'RPMLimit', 'PeakBoostRPM', 'EngineeringCost', 'Head', 'PowerCurve', 'IgnitionTimingSetting', 'BlockMaterial', 'WorstEcon', 'FamilyName'}
```

### Ways to check the engine
You can combine multiple check on a parameter but you can only use each type of check once for each parameter. The full list of checks you can make are:  
`min` -> value must be larger than this  
`max` -> value must be smaller than this  
`equals` -> value must equal this  
`not = "item"` -> value can't be equal to this  
`not = ["item1", "item2"]` -> value can't be equal to anything in this list  
`one_of = ["itemA", "itemB"]` -> value must be one of these items

