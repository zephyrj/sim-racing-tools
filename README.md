# sim-racing-tools
A collection of tools to make sim-racing more fun

### Pre-requisites
- A Windows computer (I plan to support Linux in future)
- The [Git](https://git-scm.com/downloads) version control system needs to be installed
- [python3](https://www.python.org/downloads/) needs to be installed
- [QuickBMS](http://aluigi.altervista.org/quickbms.htm) needs to be downloaded and you will need to know the folder it is in.
- The [.acd extractor plugin](http://aluigi.org/papers/bms/others/assetto_corsa_acd.bms) for QuickBMS needs to be downloaded and placed inside the folder containing `quickbms.exe`
- A willingness to hack around with a bit python programming

### Installation
Run the following command from a command prompt window:
```
py -m pip install git+https://github.com/zephyrj/sim-racing-tools@main
```
The tools should now be available from a python console

### Creating a new car clone from an existing car installed in assetto corsa
> I try to assume people are decent until proven otherwise but just a gentle reminder; please don't use this to rip off anyone else's hard work. Play around with it all you like on your computer but don't upload something based off someone else's work without getting the original authors permission. Most people are very happy to share their work if you ask politely and credit them for it.  
- Open up a python command prompt. You can get to this by searching for "python" in windows search - the result will be Python 3.9 (64 bit) (the version number may differ slightly)
- First we need to find where all our cars are installed. We can find this directory by running the following commands at the python prompt:
  ```
  
  ```
