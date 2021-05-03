# Transferring Automation engines into Assetto Corsa
There is support for taking an engine created within Automation and exported to a BeamNG mod and converting that into configuration files that can be placed into a cars' data directory in your Assetto Corsa installation. 

## Prerequisites
In order to put the generated files into an Assetto Corsa car you must first ensure that the car you wish to transfer the engine data to has its data.acd file extracted into a data directory. This can be done using the Content Manager launcher for Assetto Corsa or by using the QuickBMS tool with the .acd plugin.

The data used to generate the engine config data comes from 2 sources: 
- the Automation sandbox database file 
- a car exported as a BeamNG mod 
  
As we need a BeamNG mod to get the data we need the engine that you wish to transfer will need to be present in a car - the car used doesn't matter and will be ignored by the conversion process. In order to get the correct data you must also ensure that the most recent save of the engine within Automation matches up with the BeamNG mod that you have created - this is because the beamNG mod will reference the engine stored within the Automation sandbox db file. To ensure all data is correct when you perform the transfer, create your engine, place it in a car, export that car to BeamNG and then run the tool at this point. Note: if you make changes to the engine you will need to re-export the car containing the engine again before re-running the tool.

## Running the command
The swap process can be done using the command:
```commandline
ac-tools swap-automation-engine <name-of-ac-car-folder> <name-of-beamng-mod-folder>
```
The tool assumes:
- the Assetto Corsa car you are transferring the engine data to resides within the standard Assetto Corsa installation directory 
- the AC car has its data.acd file unpacked into a data folder
- the BeamNG mod that you wish to export the engine from resides within the standard BeamNG mod folder - if you don't have BeamNG installed then you will need to create this folder.
### Example
```commandline
ac-tools swap-automation-engine tatuusfa1 myBeamNGMod
```


