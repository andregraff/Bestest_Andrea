# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:56:58 2023

@author: andre
"""
import os
import pandas as pd
import fnmatch
import subprocess
import argparse
#from varname import nameof
import numpy as np
import matplotlib.pyplot as plt
#from matplotlib.colors import ListedColormap
#from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import sys
from PIL import Image
import cv2

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
    valid_extensions = ['.html', '.csv', '.idf', '.eso', '.xml', 'TH.out', '.xlsx', '.exe']

   
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
    print(f"-->Total [{extension_file}] files found: {count_files}")
    
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

def retrieve_specific_column(df, col_name: str):
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
###                               add_minmax                                ###
###############################################################################

def add_minmax(df, axis=1):
    # Get the name of the dataframe
    #name = nameof(df) non funziona perchè prende il nome df
    #calculates the minumum value across rows and assigns it to a new column named 'min'
    df['min'] = df.min(axis, numeric_only=True)
    
    #calculates the maximum value across rows and assigns it to a new column named 'MAX'
    df['MAX'] = df.max(axis, numeric_only=True)
    
    return df

###############################################################################
###                           calculate_distance                            ###
###############################################################################

def calculate_distance(df, col_reference='', axis=1):
    # Convert the column col_reference from object type to float64
    df[col_reference] = pd.to_numeric(df[col_reference], errors='coerce')

    position = df.columns.get_loc(col_reference) + 1
    df.insert(position, f'dist_%_{col_reference}', 0)

    for index, row in df.iterrows():
        value = row[col_reference]

        if value < row['min']:
            # Calculate the distance percentage for values below 'min'
            df.at[index, f'dist_%_{col_reference}'] = (value - row['min']) / abs(row['min']) * 100

        elif value > row['MAX']:
            # Calculate the distance percentage for values above 'MAX'
            df.at[index, f'dist_%_{col_reference}'] = (value - row['MAX']) / abs(row['MAX']) * 100

        else:
            # Set a default value of 0% if value is within 'min' and 'MAX'
            df.at[index, f'dist_%_{col_reference}'] = 0

    # Round the values of the 'distance_%' column to one decimal place
    df[f'dist_%_{col_reference}'] = round(df[f'dist_%_{col_reference}'], 1)

    # Insert the 'distance_%' column to the right of the specified reference column


    return df
    

###############################################################################
###                              add_reference                              ###
###############################################################################

def add_reference(col_in: str, df_in, df_out, col_out: str):
    '''
    Add a specific column from the reference df (df_in) to another df (df_out).
    The output is the df_out with  +1 column with the name (col_out)
    '''
    
    column = retrieve_specific_column(df_in, col_in)
    #change the name of the index to 'CASE'
    column = column.rename_axis('CASE')
    #change the index type from <class 'pandas.core.indexes.numeric.Int64Index'> to <class 'pandas.core.indexes.base.Index'>
    #in this way you can add the column of citysim with the index of the heating
    df_out.index=df_out.index.astype(str)
    #add the retrieved column to the bestest archive
    df_out_with_reference = df_out.join(column, how = 'left')
    #change the name from col_in to CitySim. With inplace=True it modifies the existing DataFrame itself instead of creating a new one
    df_out_with_reference.rename(columns = {f'{col_in}':f'{col_out}'}, inplace=True)
    
    return df_out_with_reference




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
###                            generate_heatmaps                            ###
###############################################################################
                                
def generate_heatmaps(dataframes, folder):
    
    for df_name, df in dataframes.items():
        # Transpose the data to exchange x and y
        transposed_df = df.T
        # Trim the df with only the rows containing the distance %. Function FILTER
        transposed_df = transposed_df.filter(like='dist_%', axis=0)
        # Set the size of the heatmap using figsize
        fig, ax = plt.subplots(figsize=(22, 2))  # Adjust the width and height as needed
        # Set the labels
        labels = transposed_df.applymap(lambda v: v if v != 0 else '')

        # Create a custom colormap
        cmap = sns.light_palette("seagreen", reverse=True, as_cmap=True) 
        cmap.set_over('tomato')
        cmap.set_under('tomato')

        # Plot a heatmap with annotation
        sns.heatmap(transposed_df,  
                    cmap=cmap,
                    vmin=0,
                    vmax=0.001,
                    annot=labels,
                    fmt='',
                    ax=ax,
                    linewidths=1.5,
                    square=True,
                    cbar=False)
        # Set labels and title
        ax.set_title(f'Heatmap for {df_name}', weight='bold')

        # Save the heatmap as an image in the specified folder
        output_filename = os.path.join(folder, f'{df_name}_heatmap.png')
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')

        # Display the heatmap
        plt.show()
    
###############################################################################
###                              vconcat_resize                             ###
###############################################################################

# define a function for vertically 
# concatenating images of different
# widths 
def vconcat_resize(img_list, interpolation = cv2.INTER_CUBIC):
    '''
    Concatenate images of different widths vertically: It is used to 
    combine images of different widths. here shape[0] represents height 
    and shape[1] represents width

    '''
    # take minimum width
    w_min = min(img.shape[1] 
                for img in img_list)
      
    # resizing images
    im_list_resize = [cv2.resize(img,
                      (w_min, int(img.shape[0] * w_min / img.shape[1])),
                                 interpolation = interpolation)
                      for img in img_list]
    # return final image
    return cv2.vconcat(im_list_resize)

###############################################################################
'                                     Main                                    '
###############################################################################

def main(run_citysim=False):

    
    # Set main folders
    base_folder = os.getcwd()
    # Set the CSV outputs folder path
    csv_outputs = os.path.join(base_folder, 'csv_outputs')
    images_folder = os.path.join(base_folder, 'Images')
    
    # Go to the relative path with all CS versions
    os.chdir("CitySimVersions")
    # Get a list of ".exe" files
    CS_list = search_extensions(os.getcwd(), '.exe')
    # Name the different CitySims
    CS_names = [('CS_'+os.path.basename(os.path.dirname(path))) for path in CS_list]
    # Return to main folder
    os.chdir(base_folder)
    
       
    #create a list of all xml file paths
    path_XMLfiles = search_extensions(base_folder, extension_file = '.xml')
    
    
    'Run CitySim option'
    
    if run_citysim:
        '''
        Do a for loop that run citysim and save the results in a csv file. This
        action is made for every version of CitySim in the folder CitySimVersions
        '''
        print("Process started")
        prev_idx = 0  # Variable to store the previous index

        for idx, citysim_path in enumerate(CS_list):
            CS_version = ('CS_' + os.path.basename(os.path.dirname(citysim_path)))

            if prev_idx == idx:
                print('Running CitySim for the current version:', CS_version)

                for xmlfile in path_XMLfiles:
                    os.chdir(base_folder)
                    print(f'Running {citysim_path} with {xmlfile}')

                    # Run CitySim using the execute function
                    for path in execute(f"{citysim_path} {xmlfile}"):
                        print(path, end="")

                print('Collecting results of the current CitySim version')
                all_THout = search_extensions(base_folder, extension_file='TH.out')
                annual_HC = pd.DataFrame()

                for path_case in all_THout:
                    line_results = create_df_HC(path_case)
                    annual_HC = pd.concat([annual_HC, line_results], axis=0)

                os.chdir(csv_outputs)
                csv_filename = f'HC_{CS_version}.csv'
                # Set column 0 as the index and name the index column 'CASE'
                annual_HC.index.name = 'CASE'
                annual_HC.to_csv(csv_filename)
                
                print(f'Saved results to {csv_filename}')

                print('''
                      ~~~~~~~~ CHANGING VERSION ~~~~~~~~
                      ''')

            prev_idx = idx+1



    os.chdir(base_folder) 
                 
    'Heating dataframes: annual / peak hourly'    
    #read data frame of annual heating
    AH = pd.read_csv ('Archives/archive_annual_heating.csv', index_col = 'CASE')    
    #add the min and max column
    AH = add_minmax(AH)
    
    #read data frame of hourly peak heating
    APH = pd.read_csv ('Archives/peak_heating_loads_archive.csv', index_col = 'CASE')
    #add min and max column
    APH = add_minmax(APH)
       
    'Cooling dataframes: annual / peak hourly'
    #read data frame of cooling
    AC = pd.read_csv ('Archives/archive_annual_cooling.csv', index_col = 'CASE')
    # add min and max column
    AC = add_minmax(AC)
    
    #read data frame of hourly peak cooling
    APC = pd.read_csv ('Archives/peak_cooling_loads_archive.csv', index_col = 'CASE')
    # add min and max
    APC = add_minmax(APC)

    # Trim dataframes: let only min and max
    trimmed_AH = AH[['min', 'MAX']]
    trimmed_AH.index = trimmed_AH.index.astype(str)
    trimmed_APH = APH[['min', 'MAX']]
    trimmed_APH.index = trimmed_APH.index.astype(str)
    trimmed_AC = AC[['min', 'MAX']]
    trimmed_AC.index = trimmed_AC.index.astype(str)
    trimmed_APC = APC[['min', 'MAX']]
    trimmed_APC.index = trimmed_APC.index.astype(str)
    
    'add citysim reference to the dataframes'
    os.chdir(csv_outputs)
    for csv in CS_names:
        # Read the city simulation CSV file into a DataFrame
        df = pd.read_csv(f'HC_{csv}.csv', index_col='CASE')
        name = f'{csv}'
        
        # Create new column names based on the citysim version
        new_col_name_AH = f'{name}_(AH)'
        new_col_name_APH = f'{name}_(APH)'
        new_col_name_AC = f'{name}_(AC)'
        new_col_name_APC = f'{name}_(APC)'
        
        # Add reference columns from the citysim DataFrame to the trimmed DataFrames
        AH_citysim = retrieve_specific_column(df, 'AH')
        AH_citysim.rename(columns={'AH': new_col_name_AH}, inplace=True)
        AH_citysim.index = AH_citysim.index.astype(str)
        
        APH_citysim = retrieve_specific_column(df, 'APH')
        APH_citysim.rename(columns={'APH': new_col_name_APH}, inplace=True)
        APH_citysim.index = APH_citysim.index.astype(str)
        
        AC_citysim = retrieve_specific_column(df, 'AC')
        AC_citysim.rename(columns={'AC': new_col_name_AC}, inplace=True)
        AC_citysim.index = AC_citysim.index.astype(str)
        
        APC_citysim = retrieve_specific_column(df, 'APC')
        APC_citysim.rename(columns={'APC': new_col_name_APC}, inplace=True)
        APC_citysim.index = APC_citysim.index.astype(str)
         
        # Join the citysim reference columns with the respective trimmed DataFrames
        trimmed_AH = trimmed_AH.join(AH_citysim)
        trimmed_APH = trimmed_APH.join(APH_citysim)
        trimmed_AC = trimmed_AC.join(AC_citysim)
        trimmed_APC = trimmed_APC.join(APC_citysim)
         
         
        'calculate the distance % from the boundaries (min and MAX)'    
        
        #calculate the distance
        dist_AH = calculate_distance(trimmed_AH, new_col_name_AH)
        dist_APH = calculate_distance(trimmed_APH, new_col_name_APH)
         
        dist_AC = calculate_distance(trimmed_AC, col_reference = new_col_name_AC)
        dist_APC = calculate_distance(trimmed_APC, new_col_name_APC)
         
    'Save the results'
       
    csv_dist_AH = 'dist_AH.csv'
    dist_AH.to_csv(csv_dist_AH)
          
    csv_dist_APH = 'dist_APH.csv'
    dist_APH.to_csv(csv_dist_APH)
    
    csv_dist_AC = 'dist_AC.csv'
    dist_AC.to_csv(csv_dist_AC)
    
    csv_dist_APC = 'dist_APC.csv'
    dist_APC.to_csv(csv_dist_APC)


    ' Generate Heatmaps'   
    os.chdir(images_folder)    
    # Usage
    dataframes = {
        'dist_AH': dist_AH,
        'dist_APH': dist_APH,
        'dist_AC': dist_AC,
        'dist_APC': dist_APC,
    }
    
    generate_heatmaps(dataframes, images_folder)
    
    
    ' Mount the images vertically'
    

    
    heatmap_filenames = []   
    # Iterate through the keys in the dataframes dictionary
    for key in dataframes.keys():
        # Construct the filename for the heatmap image based on the key
        heatmap_filename = f"{key}_heatmap.png"
        heatmap_filenames.append(heatmap_filename)
        

    # Create a list of Numpy array 
    img_list = []
    for img in heatmap_filenames:
        imread = cv2.imread(img)
        img_list.append(imread)
        
    # function calling      
    img_v_resize = vconcat_resize(img_list)     

    # show the output image
    cv2.imwrite('vconcat_resize.png', img_v_resize)



    return dist_AH,dist_APH, dist_AC, dist_APC
 



   
if __name__ == "__main__":
    
    #create an argument parser
    parser = argparse.ArgumentParser()
    
    # Add the desired command-line arguments
    parser.add_argument('--run_citysim', help='Turn run_citysim to True if you want to run all the xml files.', action='store_true')
   
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Call the main function with the parsed arguments
    #main(args.run_citysim)
    
    dist_AH,dist_APH, dist_AC, dist_APC = main()




