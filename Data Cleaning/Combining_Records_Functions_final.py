#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 10:50:32 2023

@author: paultrygstad
"""

#import to make editing easier (spyder wont' raise warnings)
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt 
os.chdir("/Users/paultrygstad/Documents/Grad School/Classes/Fall 2023/DS785/Data/Data Cleaning")


#takes header row
def airQualityTallTable(header):
    # Go to Folder
    os.chdir("/Users/paultrygstad/Documents/Grad School/Classes/Fall 2023/DS785/Data/Source Data/Air Quality")
    source_data_path = '/Users/paultrygstad/Documents/Grad School/Classes/Fall 2023/DS785/Data/Source Data/Air Quality'
    air_qual = os.listdir(source_data_path) #get 
    air_qual.remove('.DS_Store') #remove DS_store python file
    #construct a dictionary of monitors
    monitors = {} #dict that will hold lists
    for subfolder in air_qual:
        new_path = source_data_path + "/" + subfolder
        contents = os.listdir(new_path)
        contents.remove('.DS_Store') #remove DS_store python file
        monitors[subfolder] = contents
    #read all dailies in a pollutant category and combine monitors
    #create a new df for each contaminant 
    keys = list(monitors.keys()) #save keys as list for easy indexing
    df_dict = {} #to store all dfs
    for i in keys:
        df_dict[i] = None
    #read data
    for i in range(0, len(keys)):
        contam_df = pd.DataFrame(columns=header) #initiate storage df for contaminant
        current_key = keys[i]
        subfolders = monitors[current_key] #story subfolders in list
        for folder in subfolders:
            path = source_data_path+"/"+current_key+"/"+folder+"/"+"Dailies"
            files = os.listdir(path)
            if '.DS_Store' in files:
                files.remove('.DS_Store') #remove DS_store python file
            for file in files:
                filepath = path+"/"+file
                file_df = pd.read_csv(filepath)
                contam_df = pd.concat([contam_df, file_df])
                df_dict[current_key] = contam_df #update dictionary
    ## COMBINE TO ONE LARGE DATA TABLE
    tall_master_df = pd.DataFrame() 
    for dictio in df_dict.keys():
        tall_master_df= pd.concat([tall_master_df, df_dict[dictio]])
    tall_master_df = tall_master_df.drop_duplicates().reset_index(drop=True) #drop duplicate readings, which exist because of how data was collected by contaminant
    # convert to date
    tall_master_df['Date (Local)'] = pd.to_datetime(tall_master_df['Date (Local)'])
    return tall_master_df


def airQualityWideTable(tall_master_df):
    parameters_list = list(set(tall_master_df["Parameter Name"]))
    len(parameters_list)
    durations = list(set(tall_master_df["Duration Description"]))
    len(durations)
    #Get unique sites and site numbers (as well as abbreviations)
    sites = tall_master_df[['Site Number','Local Site Name']].copy()
    sites_set = list(sites.groupby(['Site Number','Local Site Name']).size().index)  #######number of records for each monitor
    abbreviations_list = ["AFA", "HW24", "MAN", "CC"]
    numbers = []
    names = []
    abbr = []
    for i in range(0, len(sites_set)):
        numbers.append(sites_set[i][0])
        names.append(sites_set[i][1])
        abbr.append(abbreviations_list[i])
    sites_df = pd.DataFrame()
    sites_df['Site Number'] = numbers
    sites_df['Local Site Name'] = names
    sites_df["Abbreviation"] = abbr
    sites_df
    ################ CREATE LOOP FOR CAPTURING DATA ################
    #make list of desired columns
    select_cols = ["Parameter Name",
            "Duration Description",
            "Pollutant Standard",
            "Units of Measure",
            "Arithmetic Mean",
            "First Maximum Value",
            "First Maximum Hour",
            "Daily Criteria Indicator"
            ]
    ### Split table by parameters, duration descriptions, and extract desired columns
    ### Save in dictionary arranged by site, parameter, and measurement type
    site_cont = {}
    for i in range(0, len(sites_df["Abbreviation"])):
        num = sites_df["Site Number"][i]
        site_data = tall_master_df[tall_master_df["Site Number"] == num]
        param_cont = {}
        abbr = sites_df["Abbreviation"][i]
        for param in list(set(site_data["Parameter Name"])):
            param_data = site_data[site_data["Parameter Name"] == param]
            dur_extract = list(set(param_data["Duration Description"]))
            dur_cont = {}
            for meas in dur_extract:
                dur_data = param_data[param_data["Duration Description"] == meas]
                col_cont = {}
                for col in select_cols:
                    colname = abbr + "_" + param + "_" + meas + "_" + col
                    col_cont[colname] = dur_data[col]
                col_cont["Date (Local)"] = dur_data["Date (Local)"]
                dur_cont[meas] = col_cont
            param_cont[param] = dur_cont
        site_cont[abbr] = param_cont        
    site_cont            
    ##### COMBINE ALL COLUMNS INTO WIDE MASTER TABLE INDEXED BY DATE
    ##### ONE ROW PER DATE
    master_wide_df = pd.DataFrame(columns = ["Date (Local)"])
    for site in list(site_cont.keys()):
       # print() #deubg
       # print(site)#deubg
        for param in list(site_cont[site].keys()):
            #print(site+" "+param)
            #dur_combining_list = []
            for dur in list(site_cont[site][param].keys()):
                #print(site+" "+param+" "+dur) #deubg
                dur_df = pd.DataFrame()
                for col in site_cont[site][param][dur].keys():
                    #print("Fetching columns for "+site+" "+param+" "+dur) #debug
                    dur_df[col] = site_cont[site][param][dur][col]
                master_wide_df = pd.merge(master_wide_df, dur_df, how="outer", on=["Date (Local)"])
                master_wide_df.drop_duplicates(subset=["Date (Local)"], keep='last', inplace=True, ignore_index=True) #drop duplicates, which exist from join process
    return master_wide_df


def getNullPercentages(wide_filterd_df, thresh=None):
    cols = wide_filterd_df.columns
    drop_cols = []
    #get all numbers of na's for each column
    for col in cols:
        na_bool = list(wide_filterd_df[col].isna())
        percent_null = sum(na_bool)/len(na_bool) #get percentage of each col that is null
        print(col+": "+str(round(percent_null,2))) #print null percentage for each col
        if thresh!=None:
            #print('A THRESHOLD HAS BEEN ENTERED') #debug statement
            if percent_null >= thresh: #null cutoff point 
                print("Deleting " + col + " due to more than " + str(thresh*100)+"%")
                print()
                drop_cols.append(col)
    wide_filterd_df = wide_filterd_df.drop(columns = drop_cols)
    return wide_filterd_df


def nullsByYear(wide_filterd_df):
    dates = []
    counts = []
    filtered_res = pd.DataFrame()
    for date in list(wide_filterd_df["Date (Local)"].sort_values()):
        a = wide_filterd_df[wide_filterd_df['Date (Local)'] == date].isna().sum()
        count_nan = sum(a)
        #print(date+": " + str(count_nan))
        dates.append(date)
        counts.append(count_nan)
    filtered_res["Date"] = dates
    filtered_res["count_nan"] = counts 
    #bin by year
    years = []
    for i in range(0,len(filtered_res["Date"])):
                  date = str(filtered_res["Date"][i])
                  year = date[0:4]
                  years.append(year)
    filtered_res["Year"] = years
    #groupby year              
    filtered_year_nan = filtered_res.groupby(['Year']).sum()
    #Plot to check
    import matplotlib.pyplot as plt 
    fig = plt.figure(figsize = (10, 5))
    # creating the bar plot
    plt.bar(list(filtered_year_nan.index), filtered_year_nan["count_nan"], color ='maroon', 
            width = 0.4)
    plt.xlabel("Year")
    plt.ylabel("Number of NaN's")
    plt.title("NaN's by year")
    plt.rcParams.update({'font.size': 9})
    plt.show()
    return filtered_year_nan


def createYearColumn(df):
    years = []
    for i in range(0,len(df["Date (Local)"])):
                  date = str(df["Date (Local)"][i])
                  year = date[0:4]
                  years.append(year)
    df["Year"] = years
    return df


def igraData():
    igra_path = '/Users/paultrygstad/Documents/Grad School/Classes/Fall 2023/DS785/Data/Source Data/Meteorological/IGRA/DENVER:STAPLETON INT./IGRA_Mixing_Height_data_cleaned.csv'
    igra = pd.read_csv(igra_path)
    igra_filtered = igra[igra["YEAR"] >= 2015]
    igra_filtered.reset_index
    date_local = []
    for i in igra_filtered.index:
        date_local.append( pd.to_datetime(str(igra_filtered['YEAR'][i]) + "-" +  str(igra_filtered['MONTH'][i]) + "-" +  str(igra_filtered['DAY'][i])))
    igra_filtered['Date (Local)'] = date_local
    date_dict = {}
    #### GET AVERAGE FOR MIXING HEIGHT FOR DAY
    dates = set(igra_filtered['Date (Local)'])
    for date in dates:
        height_list = []
        sub_df = igra_filtered[igra_filtered['Date (Local)'] == date]
        #print(sub_df.size)
        for height in sub_df["MIXHGT"]:
            height_list.append(height)
        #print(height_list) #debug
        date_dict[date] = height_list

    avg_heights = []
    max_heights = []
    min_heights = []
    dates_col = []
    for date in date_dict.keys():
        dates_col.append(date)
        non_null_list = [i for i in date_dict[date] if not(pd.isnull(i)) == True]
        #print("Non-Null List: " + str(non_null_list)) #debug
        if len(non_null_list) == 0:
            #print("THIS LIST IS EMPTY!") #debug
            avg_h = np.NaN
            max_h = np.NaN
            min_h = np.NaN
        else:
            avg_h = np.nanmean(non_null_list)
            max_h = np.nanmax(non_null_list)
            min_h = np.nanmin(non_null_list)
        #print("AVERAGE: " + str(avg_h)) #debug
        #print("MAX: " + str(max_h))
        #print("MIN: " + str(min_h))
        avg_heights.append(avg_h)
        max_heights.append(max_h)
        min_heights.append(min_h)

    igra_cleaned_df = pd.DataFrame()
    igra_cleaned_df["Date (Local)"] = dates_col
    igra_cleaned_df["Average Mixing Height"] = avg_heights
    igra_cleaned_df["Maximum Mixing Height"] = max_heights
    igra_cleaned_df["Minimum Mixing Height"] = min_heights
    igra_cleaned_df = igra_cleaned_df.sort_values(by="Date (Local)").reset_index(drop=True)
    return igra_cleaned_df

def daysPerYear(df):
    years = list(set(df["Year"]))
    for year in years:
         df_filter = df[df["Year"] == year]
         res = str(year) + " : " + str(df_filter["Date (Local)"].count())
         print(res)
    return


def meteorologicalData():
    met_path = "/Users/paultrygstad/Documents/Grad School/Classes/Fall 2023/DS785/Data/Source Data/Meteorological/Colorado Springs Municipal Airport NCEI CDO/NCEI CDO/Cleaned_Meteorological_Data.csv"
    met = pd.read_csv(met_path)
    counts = met.groupby('Date (Local)').size()
    for i in counts:
        if i != 1:
            print("MULTIPLE RECORDS FOR THIS DAY: " )
    met_filtered = met[met["Date (Local)"] >= "2015-1-1"]
    met_filtered = met_filtered[met_filtered["Date (Local)"] <= "2022-07-09"]
    met_filtered["Date (Local)"] = pd.to_datetime(met_filtered["Date (Local)"])
    return met_filtered.reset_index(drop=True)
