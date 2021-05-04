# Transferring Automation engines into Assetto Corsa
There is support for taking an engine created within Automation and exported to a BeamNG mod and converting that into configuration files that can be placed into a cars' data directory in your Assetto Corsa installation. 

## Prerequisites
In order to put the generated files into an Assetto Corsa car you must first ensure that the car you wish to transfer the engine data to has its data.acd file extracted into a data directory. This can be done using the Content Manager launcher for Assetto Corsa or by using the QuickBMS tool with the .acd plugin.

The data used to generate the engine config data comes from 2 sources: 
- the Automation sandbox database file 
- a car exported as a BeamNG mod 
  
As we need a BeamNG mod to get the data we need the engine that you wish to transfer will need to be present in a car - the car used doesn't matter and will be ignored by the conversion process. In order to get the correct data you must also ensure that the most recent save of the engine within Automation matches up with the BeamNG mod that you have created - this is because the beamNG mod will reference the engine stored within the Automation sandbox db file. To ensure all data is correct when you perform the transfer, create your engine, place it in a car, export that car to BeamNG and then run the tool at this point. 
> Note: if you make changes to the engine you will need to re-export the car containing the engine again before re-running the tool.

## Running the command
The swap process can be done using the command:
```commandline
ac-tools swap-automation-engine <name-of-ac-car-folder> <name-of-beamng-mod-folder>
```
The tool assumes:
- the Assetto Corsa car you are transferring the engine data to resides within the standard Assetto Corsa installation directory 
- the AC car has its data.acd file unpacked into a data folder
- the BeamNG mod that you wish to export the engine from resides within the standard BeamNG mod folder - if you don't have BeamNG installed then you will need to create this folder `Documents/BeamNG.drive/mods`.
### Example
```commandline
ac-tools swap-automation-engine tatuusfa1 myBeamNGMod
```

## Additional options
There are a few options you can provide when performing the transfer. You can see the full list by running:
```commandline
ac-tools swap-automation-engine --help
```
At the time of writing the available options are:
### `-m` or `--update-mass`
This will ask the tool to also update the mass of the car you are transferring the engine into based on the mass of the engine. If the car has an Automation engine in it before performing the transfer then this option can be used on its own and it will calculate the new mass automatically. If you are swapping in a Automation engine into this car for the first time then you will also need to provide the `--mass-hint` option.

### `--mass-hint`
This allows you to specify what mass (in kg) that the tool should use for the existing engine when using the `-m/--update-mass` option. For example if your Automation engine weighs 110kg and you specify `--mass-hint 100` then the tool will increase the cars mass by 10kgs as the Automation engine will be 10kgs heavier.

### `-c` or `--use-csp-physics`
If this flag is provided then the data files created will use the extended-2 option to allow for CSP extended physics. If you provide this option then you will only be able to use the car when running AC with CSP - at the time of writing CSP version 0.1.73 worked correctly. More info can be found at [CSP GitHub](https://github.com/ac-custom-shaders-patch/acc-extension-config/wiki/Cars-%E2%80%93-Enabling-extended-physics) and [CSP Trello](https://trello.com/b/xq54vHsX/ac-patch)

## How the transfer works
You can find the nitty-gritty details of what conversions are made [here](sim_racing_tools/automation/fabricator/assetto_corsa/docs/ac_conversion_calculations.md)