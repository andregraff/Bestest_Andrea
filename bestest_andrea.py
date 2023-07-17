# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:56:58 2023

@author: andre
"""
import os
import pandas as pd
import fnmatch
import subprocess
import csv
import numpy as np


###############################################################################
###                           search_extensions                             ###
###############################################################################

def search_extensions(current_dir, extension_file, create_list=None):
    """
  Return a list of retrieved file paths based on the specified extension like .html or .csv.
  If create_list is True, it creates a .txt file of the list.

  Parameters
  ----------
  current_dir : str
      The directory path to search for files.
  extension_file : str
      The file extension to search for (e.g., '.html', '.csv').
  create_list : bool, optional
      If True, creates a .txt file of the list. Default is None.

  Returns
  -------
  list
      A list of retrieved file paths.
  """
    #Initialize a list of valid extensions
    valid_extensions = ['.html', '.csv', '.idf', '.eso', '.xml', 'TH.out']

   
    #this is a while loop to ensure it matches one of the valid extensions
    while extension_file not in valid_extensions:
        print("Invalid extension file")
        extension_file = input("Please enter a valid file extension: ")

    files_found = [] # list to store the retrieved files

    # use .walk funtion in the os library (remember it returns three values) for scan the folders
    for root, dirs, files in os.walk(current_dir):
        
        #use fnmatch to filter the lists of files in each directory
        for filename in fnmatch.filter(files, f'*{extension_file}'):
            
            #construct the full path using .join
            file_path = os.path.join(root, filename)
            
            #Append object to the end of the list
            files_found.append(file_path)
    
    #print all the file found each in a new line with a for loop
    for file_path in files_found:
        print(file_path)
        
    #print the total number of files found   
    count_files = len(files_found) 
    print(f"-->Total files found: {count_files}")
    
    if create_list:
        file_path = os.path.join(current_dir, f"{extension_file}.txt")
        with open(file_path, 'w') as file:
            for item in files_found:
                file.write(item + "\n")
        print(f"output .txt file saved in {current_dir}")


    return files_found





###############################################################################
###                                  execute                                ###
###############################################################################

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)





###############################################################################
###                      retrieve_specific_column                           ###
###############################################################################

def retrieve_specific_column(df, col_name):
    'select colums that coutain a specific name'
    
    name_list = []  # name list of all the columns names that countain the specified name
    temp_df = pd.DataFrame()  # data frame with only the columns of interest

    for i in df.columns:  # for every columns names in my file
        if i.__contains__(col_name): # see who countain the specified name
            name_list.append(i) # and add it to name_list
            
    temp_df = df[name_list]  # fill temp_df with the columns of df that were selected before
    
    return temp_df


###############################################################################
###                    integration_with_date_and_hour                       ###
###############################################################################

def integration_with_date_and_hour(h_y):
    """
    Calculate the hour of the day (h_d), the day of the month (d_m), the month (m) based the hour of the year (h_y)
    """
    month_length = [
        ['jan', 31],
        ['feb', 28],
        ['mar', 31],
        ['apr', 30],
        ['may', 31],
        ['jun', 30],
        ['jul', 31],
        ['aug', 31],
        ['sep', 30],
        ['oct', 31],
        ['nov', 30],
        ['dec', 31]]

    d_y = h_y//24+1 #tot hours in a year 8766
    h_d = h_y%24+1

    i = 0
    d_m = d_y
    while i < 12:
        month, length = month_length[i]

        if d_m > length:
            d_m = d_m - length
            #print("This is not during {}".format(month))
            i = i + 1
        else:
            #print ("This hour of the year correspond to the {} of {} and it occurs at {}.".format(d_m, month, h_d))
            break

    return month, d_m, h_d



###############################################################################
###                           calculate_distance                            ###
###############################################################################

def calculculate_distance(df, col_reference = '', axis=1):
    
    #calculates the maximum value across rows and assigns it to a new column named 'MAX'
    df['MAX'] = df.max(axis, numeric_only=True)
        
    #calculates the minumum value across rows and assigns it to a new column named 'min'
    df['min'] = df.min(axis, numeric_only=True)
    
    #convert the column col_reference from type object to float64
    df[col_reference] = pd.to_numeric(df[col_reference], errors='coerce')
    
    #create a new column 'distance_%'
    df['distance_%'] = 0
    
    for index, row in df.iterrows():
        value = row[col_reference]
        
        if value < row['min']:
            # Calculate the distance percentage for the specific row
            df.at[index, 'distance_%'] = (value - row['min']) / abs(row['min']) * 100
            
        elif value > row['MAX']:
            # Calculate the distance percentage for the specific row
            df.at[index, 'distance_%'] = (value - row['MAX']) / abs(row['MAX']) * 100
            
        else:
            # Set a default value of 0% for the specific row
            df.at[index, 'distance_%'] = 0
    
    #round the values of the column to n decimal places
    df['distance_%'] = round(df['distance_%'], 2)
     

    return df
    






'DataFrame creators'

###############################################################################
###                              create_df_HC                               ###
###############################################################################

def create_df_HC(path_case):
    
    case = os.path.basename(path_case).strip('_TH.out')

    #open the TH.out
    TH = pd.read_csv(path_case, sep='\t') #it is a tsv file    
    
    #HEATING
    Heating = retrieve_specific_column(TH, 'Heating')
    Heating = Heating.sum(axis=1) #Sum up on every hour of the year (usefull if the building is composed of more than one thermal zone)
    #if Heating is a pd.Series type, return True
    if isinstance(Heating, pd.Series): #use isinstance to avoid warning terminal
        Heating = pd.DataFrame(Heating)
    AH = pd.DataFrame.sum(Heating) / 1000000   #Annual Heating in MWh
    APH = pd.DataFrame.max(Heating) / 1000     #Annual peak heating is kW
    h_y_APH = Heating[0].argmax() + 1 #Hour of peak heating occurence
    APH_m, APH_d_m, APH_h_d = integration_with_date_and_hour(h_y_APH) #Peak Heating integration

    #COOLING (Same operations than above, the (-) is because CS results for cooling are negative)
    Cooling = retrieve_specific_column(TH, 'Cooling')
    Cooling = Cooling.sum(axis=1)
    if isinstance(Cooling, pd.Series):
        Cooling = pd.DataFrame(Cooling)
    AC = pd.DataFrame.sum(Cooling) / -1000000   #Annual Cooling in MWh
    APC = pd.DataFrame.min(Cooling) / -1000     #Annual peak Cooling in MWh
    h_y_APC = Cooling[0].argmin() + 1
    APC_m, APC_d_m, APC_h_d = integration_with_date_and_hour(h_y_APC)
  
    
    line_results = pd.DataFrame({'AH': [AH.values], 'APH': [APH.values], 'Month_H': [APH_m], 'Day_H': [APH_d_m], 'Hour_H': [APH_h_d], 'AC': [AC.values], 'APC': [APC.values], 'Month_C': [APC_m], 'Day_C': [APC_d_m], 'Hour_C': [APC_h_d]}, index=[case])
    #Remove brackets in results
    for i in line_results:
        line_results[i] = line_results[i].apply(str).str.replace('\[|\]','', regex = True)

    return line_results








###############################################################################
'                                     Main                                    '
###############################################################################

def main():
    
    
    current_dir = os.getcwd()
    citysim_path = r"CitySimVersion\CitySim.exe"
    
    
    BESTESTcases = [
        '600', '610', '620', '630', '900', '910', '920', '930', '960', '195',
        '200', '210', '230', '240', '250', '270', '290', '300', '310', '320',
        '395', '400', '410', '420', '430', '800', '280', '440', '810', '220',
        '215']

    BESTESTresults_category = ("AH", "AC", "APH", "Month_H", "Day_H", "Hour_H", "APC", "Month_C", "Day_C", "Hour_C")
    #create a df from the BESTEST_results_category tuple
    

    
    #create a list of all xml files
    path_XMLfiles = search_extensions(current_dir, extension_file = '.xml', create_list= True)
    
    
    'Run CitySim'
    '''
    #run citysim for each file in the list
    print("Process started")
    
    for xmlfile in path_XMLfiles:
    
        for path in execute(f"{citysim_path} {xmlfile}"):
            print(path, end="")
    
    '''
    #read all TH.out file
    all_THout = search_extensions(current_dir, extension_file = 'TH.out', create_list= True)
    
    #create a df of all the THout for each case
    all_results_HC = pd.DataFrame()
    all_results_HC_peak = pd.DataFrame()
    
    for path_case in all_THout:
        
        line_results = create_df_HC(path_case)
        all_results_HC = pd.concat([all_results_HC, line_results], axis=0)
    
    for path_case in all_THout:
        
        line_results = create_df_HC(path_case)
        all_results_HC_peak = pd.concat([all_results_HC_peak, line_results], axis=0)
    
    
    # # # # # # # # # # # # # #
    'Bestest comparison part' 
    # # # # # # # # # # # # # #
    
                    
    'Heating dataframe'
    
    #read data frame of heating
    archive_heating = pd.read_csv ('archive_annual_heating.csv', index_col = 'CASE')
    
    #retrieve only the column AH in  all_results_HC
    AH_column = retrieve_specific_column(all_results_HC, 'AH')
    #change the name of the index to 'CASE'
    AH_column = AH_column.rename_axis('CASE')
    
    #change the index type from <class 'pandas.core.indexes.numeric.Int64Index'> to <class 'pandas.core.indexes.base.Index'>
    #in this way you can add the column of citysim with the index of the archive_heating
    archive_heating.index=archive_heating.index.astype(str)
    
    #add the retrieved column to the bestest archive
    archive_heating_with_citysim = archive_heating.join(AH_column, how = 'left')
    
    #change the name from AH to CitySim. With inplace=True it modifies the existing DataFrame itself instead of creating a new one
    archive_heating_with_citysim.rename(columns = {'AH':'CitySim'}, inplace=True)
    
       
    'Cooling dataframe'
    
    #read data frame of heating
    archive_cooling = pd.read_csv ('archive_annual_cooling.csv', index_col = 'CASE')
    
    #retrieve only the column AC in  all_results_HC
    AC_column = retrieve_specific_column(all_results_HC, 'AC')
    #change the name of the index to 'CASE'
    AC_column = AC_column.rename_axis('CASE')
    
    #change the index type from <class 'pandas.core.indexes.numeric.Int64Index'> to <class 'pandas.core.indexes.base.Index'>
    #in this way you can add the column of citysim with the index of the archive_cooling
    archive_cooling.index=archive_cooling.index.astype(str)
    
    #add the retrieved column to the bestest archive
    archive_cooling_with_citysim = archive_cooling.join(AC_column, how = 'left')
    
    #change the name from AH to CitySim. With inplace=True it modifies the existing DataFrame itself instead of creating a new one
    archive_cooling_with_citysim.rename(columns = {'AC':'CitySim'}, inplace=True)
  
    
  
    
    'Annual peak heating dataframe'
    
    #read data frame of heating
    archive_peak_heating = pd.read_csv ('peak_heating_loads_archive.csv', index_col = 'CASE')
    
    #retrieve only the column AH in  all_results_HC
    AHP_column = retrieve_specific_column(all_results_HC_peak, 'APH')
    #change the name of the index to 'CASE'
    AHP_column = AHP_column.rename_axis('CASE')
    
    #change the index type from <class 'pandas.core.indexes.numeric.Int64Index'> to <class 'pandas.core.indexes.base.Index'>
    #in this way you can add the column of citysim with the index of the archive_peak_heating
    archive_peak_heating.index=archive_peak_heating.index.astype(str)
    
    #add the retrieved column to the bestest archive
    archive_peak_heating_with_citysim = archive_peak_heating.join(AHP_column, how = 'left')
    
    #change the name from AH to CitySim. With inplace=True it modifies the existing DataFrame itself instead of creating a new one
    archive_peak_heating_with_citysim.rename(columns = {'APH':'CitySim'}, inplace=True)
    
        
    'Annual peak cooling dataframe'
        
    #read data frame of heating
    archive_peak_cooling = pd.read_csv ('peak_cooling_loads_archive.csv', index_col = 'CASE')
    
    #retrieve only the column AC in  all_results_HC_peak
    ACP_column = retrieve_specific_column(all_results_HC_peak, 'APC')
    #change the name of the index to 'CASE'
    ACP_column = ACP_column.rename_axis('CASE')
    
    #change the index type from <class 'pandas.core.indexes.numeric.Int64Index'> to <class 'pandas.core.indexes.base.Index'>
    #in this way you can add the column of citysim with the index of the archive_peak_cooling
    archive_peak_cooling.index=archive_peak_cooling.index.astype(str)
    
    #add the retrieved column to the bestest archive
    archive_peak_cooling_with_citysim = archive_peak_cooling.join(ACP_column, how = 'left')
    
    #change the name from AH to CitySim. With inplace=True it modifies the existing DataFrame itself instead of creating a new one
    archive_peak_cooling_with_citysim.rename(columns = {'APC':'CitySim'}, inplace=True)
    
   
    
   
    
   
    'calculate min and MAX and the distance % from the boundaries'    
    
    #calculates the maximum value across rows and assigns it to a new column named 'MAX'
    archive_heating_with_citysim = calculculate_distance(archive_heating_with_citysim, col_reference ='CitySim')
    archive_cooling_with_citysim = calculculate_distance(archive_cooling_with_citysim, col_reference ='CitySim')
    
    archive_peak_heating_with_citysim = calculculate_distance(archive_peak_heating_with_citysim, col_reference ='CitySim')
    archive_peak_cooling_with_citysim = calculculate_distance(archive_peak_cooling_with_citysim, col_reference ='CitySim')
    
    
    
    #round all the values
    archive_heating_with_citysim = round(archive_heating_with_citysim, 3)
    archive_cooling_with_citysim = round(archive_cooling_with_citysim, 3)
    
    archive_peak_heating_with_citysim = round(archive_peak_heating_with_citysim, 3)
    archive_peak_cooling_with_citysim = round(archive_peak_cooling_with_citysim, 3)


    return archive_heating_with_citysim, archive_cooling_with_citysim, archive_peak_heating_with_citysim, archive_peak_cooling_with_citysim
 



   
if __name__ == "__main__":
    archive_heating_with_citysim, archive_cooling_with_citysim, archive_peak_heating_with_citysim, archive_peak_cooling_with_citysim = main()
    