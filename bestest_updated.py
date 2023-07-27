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
    valid_extensions = ['.html', '.csv', '.idf', '.eso', '.xml', 'TH.out', '.xlsx']

   
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
    
    #calculates the minumum value across rows and assigns it to a new column named 'min'
    df['min'] = df.min(axis, numeric_only=True)
    
    #calculates the maximum value across rows and assigns it to a new column named 'MAX'
    df['MAX'] = df.max(axis, numeric_only=True)
    
    return df

###############################################################################
###                           calculate_distance                            ###
###############################################################################

def calculate_distance(df, col_reference = '', axis=1):

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
    df['distance_%'] = round(df['distance_%'], 1)
     

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
###                              color_bestest                              ###
###############################################################################
                                
def color_bestest(df, col_reference, out_name= '', *columns):
    
    #get the number position of the columns' names
    col_nbs = [df.columns.get_loc(col) for col in columns] #columns numbers
    ref_nb = df.columns.get_loc(col_reference) # reference number
      
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(f'{out_name}.xlsx', engine='xlsxwriter')
      
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='general')
      
    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    worksheet = writer.sheets['general']
          
    # Add a format. Light red fill with dark red text.
    red_format = workbook.add_format({'bg_color': '#FFC7CE',
                                      'font_color': '#9C0006'})
          
    # Add a format. Light blue fill with dark blue text.
    blue_format = workbook.add_format({'bg_color': '#0096FF',
                                      'font_color': '#00008B'})
      
    # Add a format. Green fill with black text for =0
    green_format = workbook.add_format({'bg_color': '#a8e16c',
                                        'font_color': '#000000'})
    
    # Add a format. Grey fill with black text for =0
    grey_format = workbook.add_format({'bg_color': '#b7b7b7',
                                        'font_color': '#000000'})
            
    for col_nb in col_nbs:
        # Calculate the range to which the conditional format is applied (only for the desired columns).
        (min_row, max_row) = (1, df.shape[0])  # Skip header.
        (min_col, max_col) = (col_nb +1, col_nb +1)  # Only one columns.
        
        # Apply a conditional format to the cell range.
        worksheet.conditional_format(min_row, min_col, max_row, max_col,
                                       {'type':     'cell',
                                        'criteria': '<',
                                        'value':    0,
                                        'format':   blue_format})
          
        worksheet.conditional_format(min_row, min_col, max_row, max_col,
                                       {'type':     'cell',
                                        'criteria': '>',
                                        'value':    0,
                                        'format':   red_format})
          
        worksheet.conditional_format(min_row, min_col, max_row, max_col,
                                       {'type':     'cell',
                                        'criteria': '=',
                                        'value':    0,
                                        'format':   green_format})
       
    #col_reference color
    (min_row, max_row) = (1, df.shape[0])  # Skip header.
    (min_col, max_col) = (ref_nb +1, ref_nb +1)  # Only one columns. 
    
    worksheet.conditional_format(min_row, min_col, max_row, max_col,
                                   {'type':     'cell',
                                    'criteria': '!=',
                                    'value':    0,
                                    'format':   grey_format})
    
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    
    file_name = f'{out_name}.xlsx'
    
    return file_name
    



###############################################################################
'                                     Main                                    '
###############################################################################

def main(run_citysim=False, new_ref=False, concat_outs=True):
    
    
    current_dir = os.getcwd()
    citysim_path = r"CitySimVersion\CitySim.exe"
    
    
    #create a list of all xml files
    path_XMLfiles = search_extensions(current_dir, extension_file = '.xml')
    
    
    'Run CitySim option'
    
    if run_citysim == True:
        
        #run citysim for each file in the list
        print("Process started")
        
        for xmlfile in path_XMLfiles:
        
            for path in execute(f"{citysim_path} {xmlfile}"):
                print(path, end="")
    
    
    #read all TH.out file
    all_THout = search_extensions(current_dir, extension_file = 'TH.out')
    
    
    'create a df of all the THout for each case'
    
    all_results_HC = pd.DataFrame()
    all_results_HC_peak = pd.DataFrame()
    
    for path_case in all_THout:
        
        line_results = create_df_HC(path_case)
        all_results_HC = pd.concat([all_results_HC, line_results], axis=0)
    
    for path_case in all_THout:
        
        line_results = create_df_HC(path_case)
        all_results_HC_peak = pd.concat([all_results_HC_peak, line_results], axis=0)
    
                       
    'Heating dataframes: annual / peak hourly'
    
    #read data frame of annual heating
    heating = pd.read_csv ('Archives/archive_annual_heating.csv', index_col = 'CASE')    
    #add the min and max column
    heating = add_minmax(heating)
    
    #read data frame of hourly peak heating
    peak_heating = pd.read_csv ('Archives/peak_heating_loads_archive.csv', index_col = 'CASE')
    #add min and max column
    peak_heating = add_minmax(peak_heating)
    
    
    'Cooling dataframes: annual / peak hourly'
 
    #read data frame of cooling
    cooling = pd.read_csv ('Archives/archive_annual_cooling.csv', index_col = 'CASE')
    # add min and max column
    cooling = add_minmax(cooling)
    
    #read data frame of hourly peak cooling
    peak_cooling = pd.read_csv ('Archives/peak_cooling_loads_archive.csv', index_col = 'CASE')
    # add min and max
    peak_cooling = add_minmax(peak_cooling)

    

 

    'add citysim reference to the dataframes'
    
    heating_with_citysim = add_reference('AH', all_results_HC, heating, 'CitySim')
    peak_heating_with_citysim = add_reference('APH', all_results_HC_peak, peak_heating, 'CitySim')
    
    cooling_with_citysim = add_reference('AC', all_results_HC, cooling, 'CitySim')
    peak_cooling_with_citysim = add_reference('APC', all_results_HC_peak, peak_cooling, 'CitySim')

    
    'calculate the distance % from the boundaries (min and MAX)'    

    #calculate the distance
    heating_with_citysim = calculate_distance(heating_with_citysim, col_reference ='CitySim')
    cooling_with_citysim = calculate_distance(cooling_with_citysim, col_reference ='CitySim')
    
    peak_heating_with_citysim = calculate_distance(peak_heating_with_citysim, col_reference ='CitySim')
    peak_cooling_with_citysim = calculate_distance(peak_cooling_with_citysim, col_reference ='CitySim')
    
    
    
    #round all the values
    heating_with_citysim = round(heating_with_citysim, 3)
    cooling_with_citysim = round(cooling_with_citysim, 3)
    
    peak_heating_with_citysim = round(peak_heating_with_citysim, 3)
    peak_cooling_with_citysim = round(peak_cooling_with_citysim, 3)
     
    
    'dataframes colored'
    
    #create a folder to store the outputs
    dir_xlsx = 'xlsx_ouputs'
    if not os.path.exists(dir_xlsx):
        os.makedirs(dir_xlsx)
        print("Directory '% s' created" % dir_xlsx)
    else:
        print("Directory '% s' already exists" % dir_xlsx)

    #change the current directory
    os.chdir(dir_xlsx)

    
    '''
    If new_ref = True then add the new values found in the simulation into the
    old excels files. It add 2 new column with citysim and distance.
    Use new_ref=True if you want to add new values with a new CitySim version
    and make a comparison.
    '''
    if new_ref == True:
        
        #create a dictionary with the output dataframes
        df_dict = {
            "heating_with_citysim.xlsx": heating_with_citysim,
            "cooling_with_citysim.xlsx": cooling_with_citysim,
            "peak_heating_with_citysim.xlsx": peak_heating_with_citysim,
            "peak_cooling_with_citysim.xlsx": peak_cooling_with_citysim,
            }
        #find all the xlsx files in the directory
        excel_paths = search_extensions(os.getcwd(), extension_file='.xlsx') #is a list
        #extract only the 'names.xlsx'
        excel_names = [os.path.basename(file_path) for file_path in excel_paths]
        
        #for each file (string) in the list:
        for file in excel_names:
            #read the excel file adn convert it into a df
            new_df = pd.read_excel(file, index_col='CASE')
            
            #check if there's already the new value
            if 'new_CitySim' in new_df.columns:
                print(f'new_CitySim column already in the {file}')
            #if not then:
            else:
                #rename column to avoid conflicts
                new_df.rename(columns={"CitySim": "old_CitySim", "distance_%":"old_distance_%"}, inplace=True)
                #df_dict.get will get the right value name. With the dict you can
                #do the for loop in automatic
                new_df = add_reference('CitySim', df_dict.get(f'{file}'), new_df, 'new_CitySim')
                new_df = calculate_distance(new_df, 'new_CitySim')
                #overwrite the xlsx files with the 2 new columns
                color_bestest(new_df, 'new_CitySim',f'{file}'.strip('.xlsx'), 'distance_%') 

    else:
        #export a xlsx file with the color of the bestest
        color_bestest(heating_with_citysim, 'CitySim', 'heating_with_citysim', 'distance_%')
        color_bestest(cooling_with_citysim, 'CitySim', 'cooling_with_citysim', 'distance_%')
        color_bestest(peak_heating_with_citysim, 'CitySim', 'peak_heating_with_citysim', 'distance_%')
        color_bestest(peak_cooling_with_citysim, 'CitySim', 'peak_cooling_with_citysim', 'distance_%')
    

    if concat_outs:
        
        AH_APH = pd.concat([heating_with_citysim, peak_heating_with_citysim], axis=1)
        AC_APC = pd.concat([cooling_with_citysim, peak_cooling_with_citysim], axis=1)
        

    #return to the current dir
    os.chdir(current_dir)

    return heating_with_citysim, cooling_with_citysim, peak_heating_with_citysim, peak_cooling_with_citysim,AH_APH, AC_APC
 



   
if __name__ == "__main__":
    
    #create an argument parser
    parser = argparse.ArgumentParser()
    
    # Add the desired command-line arguments
    parser.add_argument('--run_citysim', help='Turn run_citysim to True if you want to run all the xml files.', action='store_true')
   
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Call the main function with the parsed arguments
    main(args.run_citysim)
    
    heating_with_citysim, cooling_with_citysim, peak_heating_with_citysim, peak_cooling_with_citysim, AH_APH, AC_APC = main()




