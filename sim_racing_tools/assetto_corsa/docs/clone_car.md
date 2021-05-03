> I try to assume people are decent until proven otherwise but just a gentle reminder; please don't use this to rip off anyone else's hard work. Play around with it all you like on your computer but don't upload something based off someone else's work without getting the original authors permission. Most people are very happy to share their work if you ask politely and credit them for it.  
- If you have set one up, enter your virtual environment (see [README.md](README.md)) and type:
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
