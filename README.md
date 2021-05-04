# sim-racing-tools
A collection of python tools to make sim-racing more fun. All a work in-progress based on things I've 
been playing around with. Feel free to contribute with any ideas or suggestions and let me know if you find any
bugs.

## Installation
### Pre-requisites
- A Windows computer (I plan to support Linux in future)
- The [Git](https://git-scm.com/downloads) version control system needs to be installed
- [python3](https://www.python.org/downloads/) needs to be installed
- [QuickBMS](http://aluigi.altervista.org/quickbms.htm) needs to be downloaded and you will need to know the folder it is in.
- The [.acd extractor plugin](http://aluigi.org/papers/bms/others/assetto_corsa_acd.bms) for QuickBMS needs to be downloaded and placed inside the folder containing `quickbms.exe`
- A willingness to hack around with a bit of python programming

### Optional first step:
I would recommend creating a [python virtual environment](https://docs.python.org/3/library/venv.html) 
to install the tools into. This will allow you to use the tools in an isolated environment without installing
anything system-wide.  

### Creating a virtual environment
To setup a virtual environment first decide where you would like this to live, change into that directory and
open a command-prompt within it. Inside the command prompt run the command:
```commandline
py -m venv sim-racing-tool-venv
```
That will have created a folder called `sim-racing-tool-venv` inside the directory you are in.

### Entering the virtual environment
This newly created folder contains a self-contained python environment that you can enter at anytime
by opening a command prompt inside the `sim-racing-tool-venv` folder and running:
```
.\Scripts\activate.bat
```
this command prompt window will now be running in the virtual environment and anything you install will only
be installed into it - rather than on the whole system

### Exiting the virtual environment
You can exit a virtual environment at any time by typing `deactivate` into the console

### Downloading and installing sim-racing-tools
To download and install first make sure that you have entered the virtual environment (if you set one up) and 
run the following command inside it:
```
py -m pip install git+https://github.com/zephyrj/sim-racing-tools@main
```
The tools will now be installed and available from a python console within your environment

## Things you can do
[Clone existing AC car](sim_racing_tools/assetto_corsa/docs/clone_car.md)  
[Transfer an engine made in Automation into a car in AC](sim_racing_tools/assetto_corsa/docs/swap_automation_engine.md)
