# Bestest_Andrea

# Project Description

This is an updated and improved work from the thesis work of the EPFL student Walter Emmanuel (EPFL: https://infoscience.epfl.ch/record/214754 , 
                                                                                               zenodo: https://zenodo.org/record/3463414).
This repo contains all the necessary files used to accomplish the BESTEST benchmark with the latest version of CitySim tool (https://www.epfl.ch/labs/leso/transfer/software/citysim/).


# Contents
```
The repo contains:
- /Archives                 # there are csv files with the results of others software for the bestest
- BESTEST_#models.zip       # there are the models (.xml) for the bestest simulation with citysim
- /CitySimVersions          # all versions of CitySim are here
- /Climatefile              # there is the climate file of the bestest
- /csv_outputs              # there are the output results saved in CSV format
- bestest_updated.py        # is the main file
- /Images                   # images of the output results
- README.md                 # this text
- requirements.txt          # list of all the libraries used in 'bestest_updated.py'
```

# How to install and run
```
Before using this script, you need to ensure the following:

CitySim Software: You must have CitySim installed on your system. This script is intended to work with multiple versions of CitySim, and you should have the executable files (.exe) for each version.

Python Environment: The script requires a Python environment. Ensure you have Python installed, along with the necessary libraries such as pandas, seaborn, matplotlib, argparse, and PIL.
```
### How to Run
```
- Download the repo. You can move the repo anywhere but don't change the names or the folders inside the repo.
- Install the requirements
- Unzip the 'BESTEST_#models.zip'. Note that not all the folders and the xml models are used in the bestest. The unused ones are for debugging and in depth analisys.
- Run the Python file.The first time you run the file add the command-line argument '--run_citysim' or set 'run_citysim=True' to get the outputs in 
- You will get a folder output '/csv_outputs' where you can find the dataframes of the bestest with citysim. In the folder Images there are all the images saved as output.
```

# How to use the file

- Prepare Your CitySim Versions:
  Place the executable files for different CitySim versions in a folder named "CitySimVersion" within the script's directory. Keep the correct nomenclature. To see the version of CitySim just run it on the terminal and watch the version.
- Run CitySim Simulations:
  If you want to run CitySim simulations, set the run_citysim flag to True in the script. This will execute CitySim with various XML files found in your working
  directory.
- Data analysis:
  The script performs data analysis on the simulation results. It extracts annual heating and cooling data, peak loads, and more from the CitySim output files.
- Generate heatmaps:
  Heatmaps are generated to visualize the data. The script creates heatmaps for annual heating, peak heating, annual cooling, and peak cooling data. On the x-axis, all the cases of the BESTEST are listed, while on the y-axis, values in red correspond to the percentage distance between the value obtained with CitySim and the maximum/minimum identified in the BESTEST, where the CitySim value goes outside that boundary. Values in green indicate that the values fall within the ranges, so only the absolute value in kWh is shown. The cells in green without a number correspond to values within the range but when rounded are 0, so they are not shown. In the event that another folder is added with a new version of CitySim, a row will be added to each heatmap to observe the differences.
- Results:
  The processed data, including distance percentages from min and max values, is saved as CSV files: "dist_AH.csv", "dist_APH.csv", "dist_AC.csv", and "dist_APC.csv.   

# Current Results



<img src="/Images/vconcat_resize.png"/>

