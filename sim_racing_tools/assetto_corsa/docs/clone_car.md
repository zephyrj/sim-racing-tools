# Cloning a car
> I try to assume people are decent until proven otherwise but just a gentle reminder; please don't use this to rip off anyone else's hard work. Play around with it all you like on your computer but don't upload something based off someone else's work without getting the original authors permission. Most people are very happy to share their work if you ask politely and credit them for it.  
- If you have set one up, enter your virtual environment in a command prompt window (see [README.md](/README.md))

- First we need to find where all our cars are installed. If the game is installed through Steam then this will be:
  ```
  C:\Program Files (x86)\Steam\steamapps\common\assettocorsa\content\cars
  ```
  this can be opened in an explorer window;
  you will be able to see a folder for each installed car.
- Open the folder of the car you would like to clone. Create a new directory inside this called `data`  

- We now need to extract the data.acd file inside the car directory. This can be done using QuickBMS or Content Manager
  ### QuickBMS
  - Go to the directory that you downloaded QuickBMS into and double-click on quickbms.exe
  - You will first be asked to select the plugin to use; choose the AC extractor plugin (assetto_corsa_acd.bms)
    that you downloaded
  - Next it will ask you for the file to extract; choose the data.acd file in the folder of the car you wish to clone
  - Finally, it will ask you to select the folder to extract into; choose the data folder we created in the previous step 
  ### Content Manager
  - Go to the "About" tab and then into the "About" subtab within it
  - Repeatedly click on the Version value near the top of the page; this will allow you to enable dev mode
  - Go to the "Content" tab and select the "cars" subtab
  - Select the car you wish to clone and then at the bottom of the window click the button "Unpack data"
- We can now clone the car. To create a clone of, say, the Tatuus you would run the 
  following command inside your command prompt:
  ```commandline
  ac-tools clone-car tatuusfa1 newBrand newCarName
  ```
  Replace the "newBrand" with the name of the brand you want your clone to have, "newCarName" with the name 
  of the car model and "tatuusfa1" with the name of the folder of the car you are cloning.  

You should now find a new folder in the assetto corsa car directory of the form `<car-brand>_<car-name>`  
