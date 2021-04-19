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
### Clone an existing car installed in Assetto Corsa
> I try to assume people are decent until proven otherwise but just a gentle reminder; please don't use this to rip off anyone else's hard work. Play around with it all you like on your computer but don't upload something based off someone else's work without getting the original authors permission. Most people are very happy to share their work if you ask politely and credit them for it.  
- Enter your virtual environment (see above) and type:
  ```
  py
  ```
  this will open up a python console that you can type python commands into. You can tell you are in a python
  console if you see a `>>>` at the start of every line. If you need to exit the 
  python console you can do so by typing `exit()`
- First we need to find where all our cars are installed. We can find this directory by running the following commands at the python prompt:
  ```python
  import sim_racing_tools.assetto_corsa as ac
  ac.get_cars_dir()
  ```
  This will output the path of all the cars installed - this can be opened in an explorer window and
  you will be able to see a folder for each installed car.
- Open the folder of the car you would like to clone. Create a new directory inside this called `data`
- We now need to extract the data.acd file inside the car directory using QuickBMS
  - Go to the directory that you downloaded QuickBMS into and double-click on quickbms.exe
  - You will first be asked to select the plugin to use; choose the AC extractor plugin (assetto_corsa_acd.bms)
    that you downloaded
  - Next it will ask you for the file to extract; choose the data.acd file in the folder of the car you wish to clone
  - Finally, it will ask you to select the folder to extract into; choose the data folder we created in the previous step 
- We can now clone the car. To create a clone of, say, the Tatuus you would run the 
  following commands:
  ```python
  import sim_racing_tools.assetto_corsa.car as ac_car
  ac_car.create_new_car_from_existing("newBrand", "newCarName", "tatuusfa1")  
  ```
  Replace the "newBrand" with the name of the brand you want your clone to have, "newCarName" with the name 
  of the car model and "tatuusfa1" with the name of the folder of the car you are cloning
- Assuming that worked you can now exit the python console by typing:
  ```python
  exit()
  ```
  You should now find a new folder in the assetto corsa car directory of the form `<car-brand>_<car-name>`  
