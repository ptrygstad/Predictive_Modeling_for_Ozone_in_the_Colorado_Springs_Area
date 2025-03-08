#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 10:50:17 2023

@author: paultrygstad
"""


import pandas as pd
import os
import numpy as np
#import matplotlib.pyplot as plt 
os.chdir("/Users/paultrygstad/Documents/Grad School/Classes/Fall 2023/DS785/Data/Data Cleaning")
from Combining_Records_Functions_final import airQualityTallTable, airQualityWideTable, getNullPercentages, nullsByYear, createYearColumn, igraData, daysPerYear, meteorologicalData

"""
############################## AQS DATA ########################################################################################################################

############################## TALL TABLE ##############################
"""
#get column headers as list (standard for all AQS data)
path = "/Users/paultrygstad/Documents/Grad School/Classes/Fall 2023/DS785/Data/Source Data/Air Quality/Ozone Monitors/08-041-0013 Air Force Academy Dailies/Dailies"
dir_list = os.listdir(path)

#### explore sample and get headers
filename = dir_list[0] #select sample file
filepath = path + "/" + filename
df_1 = pd.read_csv(filepath)
df_1
header = list(df_1.columns) # get headers
tall_master_df = airQualityTallTable(header)

#filter by date before creation of wide table. Through exloration discovered cuttoff date of 2015-01-01
tall_filtered_df = tall_master_df[tall_master_df["Date (Local)"] >= "2015-01-01"] #missingness is notably increased before 2015 for many AQ parameters 
tall_filtered_df = tall_filtered_df[tall_filtered_df["Date (Local)"] <= "2022-07-09"] #from IGRA dataset

"""
############################## WIDE TABLE ##############################
"""
master_wide_df = airQualityWideTable(tall_filtered_df)
#master_wide_df_1 = airQualityWideTable(tall_master_df) #CONFRIM IT'S THE SAME AS NON-TIDY ANSWER


############################## NA's ##############################

#wide_filterd_df = getNullPercentages(master_wide_df)
#look at null percentages and filter
wide_filterd_df = getNullPercentages(master_wide_df, thresh=0.1) #10% null cutoff point
wide_filterd_df.columns #view which columns are left 
getNullPercentages(wide_filterd_df) #check null percentages
wide_filterd_df = createYearColumn(wide_filterd_df) #creat year column for exploration
daysPerYear(wide_filterd_df) #check days per year in table

########## NA's by Year ##########

filtered_year_nan = nullsByYear(wide_filterd_df)


"""
############################## IGRA DATA ########################################################################################################################
"""
# use function to read in data
igra = igraData()
igra.columns


igra.columns #look at columns
igra = createYearColumn(igra) #create year column

daysPerYear(igra) #check days per year in table


#getNullPercentages(igra) # check percentages of nulls
igra_nulls_by_year_df = nullsByYear(igra) # see nulls by year
#combine AQS data and IGRA data
combined_IGRA_AQ_data = pd.merge(wide_filterd_df, igra, how = "outer", on=["Date (Local)", "Year"]) 

daysPerYear(combined_IGRA_AQ_data) #check to make sure days per year makes sense
getNullPercentages(combined_IGRA_AQ_data) # check percentages of nulls
combined_IGRA_AQ_data_nulls_by_year_df = nullsByYear(combined_IGRA_AQ_data) # see nulls by year


"""
############################## METEOROLOGICAL DATA ########################################################################################################################
"""
# use function to read in data
metData = meteorologicalData()
metData = createYearColumn(metData.reset_index(drop=True))
#combine AQS data and IGRA data
combined_IGRA_AQ_MET_data = pd.merge(combined_IGRA_AQ_data, metData, how = "outer", on=["Date (Local)", "Year"]) 

daysPerYear(combined_IGRA_AQ_MET_data) #check days per year in table
combined_IGRA_AQ_MET_data_null_df = getNullPercentages(combined_IGRA_AQ_MET_data) # check percentages of nulls
combined_IGRA_AQ_MET_data_nulls_by_year_df = nullsByYear(combined_IGRA_AQ_MET_data) # see nulls by year


########## FILTERED ##########
#drop 2015 due to high number of nulls

combined_IGRA_AQ_MET_data_filtered = combined_IGRA_AQ_MET_data[combined_IGRA_AQ_MET_data["Year"]>"2015"] # filter 
daysPerYear(combined_IGRA_AQ_MET_data_filtered) #check days per year in table
getNullPercentages(combined_IGRA_AQ_MET_data_filtered) # check percentages of nulls
combined_IGRA_AQ_MET_data_nulls_by_year_df = nullsByYear(combined_IGRA_AQ_MET_data_filtered) # see nulls by year


#drop 2019 as well due to high number of nulls
combined_IGRA_AQ_MET_data_filtered_no_2019 = combined_IGRA_AQ_MET_data_filtered[combined_IGRA_AQ_MET_data_filtered["Year"]!="2019"] # filter further 
daysPerYear(combined_IGRA_AQ_MET_data_filtered_no_2019) #check days per year in table
getNullPercentages(combined_IGRA_AQ_MET_data_filtered_no_2019) # check percentages of nulls
combined_IGRA_AQ_MET_data_nulls_by_year_df = nullsByYear(combined_IGRA_AQ_MET_data_filtered_no_2019) # see nulls by year

#convert to numerics only
res_df = combined_IGRA_AQ_MET_data_filtered_no_2019.select_dtypes(include=np.number) #removes date column
#add date back in
res_df["Date"] = combined_IGRA_AQ_MET_data_filtered_no_2019["Date (Local)"]

#rename columns
res_cols = res_df.columns
final_df = pd.DataFrame()
for ii in range(0,len(res_cols)):
    col = res_cols[ii]
    if col.endswith("First Maximum Value")==False and col.startswith("Maximum")==False and col.startswith("Minimum")==False: #filter for averages only
     final_df[col] = res_df[col]
final_df.columns
final_df_sorted = final_df[["AFA_Ozone_1 HOUR_Arithmetic Mean",
                            "AFA_Ozone_8-HR RUN AVG BEGIN HOUR_Arithmetic Mean",
                            "HW24_Wind Speed - Scalar_1 HOUR_Arithmetic Mean",
                            "HW24_Wind Direction - Scalar_1 HOUR_Arithmetic Mean",
                            "HW24_Carbon monoxide_8-HR RUN AVG END HOUR_Arithmetic Mean",
                            "HW24_Carbon monoxide_1 HOUR_Arithmetic Mean",
                            "HW24_Wind Direction - Resultant_1 HOUR_Arithmetic Mean",
                            "HW24_Wind Speed - Resultant_1 HOUR_Arithmetic Mean",
                            "HW24_Sulfur dioxide_1 HOUR_Arithmetic Mean",
                            "HW24_Sulfur dioxide_3-HR BLK AVG_Arithmetic Mean",
                            "HW24_SO2 max 5-min avg_1 HOUR_Arithmetic Mean", 
                            "HW24_Relative Humidity_1 HOUR_Arithmetic Mean",
                            "HW24_Outdoor Temperature_1 HOUR_Arithmetic Mean",
                            "HW24_Std Dev Hz Wind Direction_1 HOUR_Arithmetic Mean",
                            "MAN_Ozone_1 HOUR_Arithmetic Mean",
                            "MAN_Ozone_8-HR RUN AVG BEGIN HOUR_Arithmetic Mean",
                            "Average Mixing Height",
                            "Met_Lat",
                            "Met_long",
                            "Met_elevation",
                            "Average daily wind speed",
                            "Precipitation",
                            "Snowfall",
                            "Snow depth",
                            "Temperature Average",
                            "Direction of fastest 2-minute wind",
                            "Direction of fastest 5-second wind",
                            "Fastest 2-minute wind speed",
                            "Fastest 5-second wind speed",
                            "Date" ]]

#export
os.chdir("/Users/paultrygstad/Documents/Grad School/Classes/Fall 2023/DS785/Data/Data Cleaning/Cleaned Data")
#final_df.to_csv("Cleaned_Model_Data_revision_11.24.23.csv", index=False)
final_df_sorted.to_csv("Cleaned_Model_Data_final.csv", index=False)



