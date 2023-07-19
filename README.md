# Bestest_Andrea

1. Project Description

This is an updated and improved work from the thesis work of the EPFL student Walter Emmanuel (github: https://github.com/ibpsa/project1-destest , 
                                                                                               zenodo: https://zenodo.org/record/3463414).
This repo contains all the necessary files used to accomplish the bestest benchmark with the latest version of CitySim tool (https://www.epfl.ch/labs/leso/transfer/software/citysim/).


2. Table of Contents

The repo contains:
- /Archives                 # there are csv files with the results of others software for the bestest
- BESTEST_#models.zip       # there are the models (.xml) for the bestest simulation with citysim
- /CitySimVersion           # there is the executable software for windows
- /Climatefile              # there is the climate file of the bestest
- bestest_updated.py        # is the main file. You can use the terminal to run it 
- /Images                   # images of the output results
- README.md                 # this text
- requirements.txt          # list of all the libraries used in 'bestest_updated.py'


3. How it Works

The python script:
- 
- 
- 
- 

4. How to Run

- Download the repo. You can move the repo anywhere but don't change the names or the folders inside the repo.
- Install the requirements
- Unzip the 'BESTEST_#models.zip'. Note that not all the folders and the xml models are used in the bestest. The unused ones are for debugging and in depth analisys.
- Run the Python file.The first time you run the file add the command-line argument '--run_citysim' or set 'run_citysim=True' to get the outputs in 
- You will get a folder output '/xlsx_outputs' where you can find the dataframes of the bestest with citysim


5. Current Results

In the dataframes you have the case model in the index and the other software as columns.
The grey column is the reference software. The distance_% is the comparison between the reference softare and the boundaries of min and max.

![My Image](../Images/coolin_with_citysim.png)
coolin_with_citysim

![My Image](../Images/heatin_with_citysim.png)
heatin_with_citysim

![My Image](../Images/peak_cooling_with_citysim.png)
peak_cooling_with_citysim

![My Image](../Images/peak_heating_with_citysim.png)
peak_heating_with_citysim
