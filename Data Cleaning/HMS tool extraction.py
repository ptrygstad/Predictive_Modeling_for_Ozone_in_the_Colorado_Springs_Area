#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 21:04:58 2023

@author: paultrygstad
"""


#smoke data scraper
import os
import requests 
import pandas as pd 
from bs4 import BeautifulSoup 
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


os.chdir("/Users/paultrygstad/Documents/Grad School/Classes/Fall 2023/DS785/Data/Source Data/Smoke")


driver = webdriver.Firefox() #open webdriver
driver.get("https://www.ospo.noaa.gov/Products/land/hms.html#data")        #go to NOAA HMS website

menu = driver.find_element(By.NAME, "sat")


menu = Select(driver.find_element(By.NAME, 'sat'))
menu.select_by_index(2)

next_menu = Select(driver.find_element(By.CLASS_NAME, 'drop'))
menu.select_by_index()


menu.click()
smoke = menu.select_by_visible_text("SMOKE")
smoke.click
menu = Select(driver.find_element(By.NAME, 'sat'))

select.select_by_index(index)
select.select_by_visible_text("text")
select.select_by_value(value)




menu = driver.find_element(By.NAME, "sat")
menu.click()
option = menu.find_elements(By.TAG_NAME, "option")
smoke = option.get_attribute("smoke")
smoke.click()
Select(smoke)


urls = driver.find_elements(By.PARTIAL_LINK_TEXT, '"https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/KML') #fine downlaod links more button

sub_driver = webdriver.Firefox() #open webdriver
for url in urls:
        sub_driver.get(url)  
sub_driver.close()
driver.close()



"""
html = '' #initiate storage variables 
names = [] #initiate storage variables
for i in range(0,100): #100 is just a large number limit, loop will terminate before it reaches this
    names = [] #empty names container at beginning of each loop to avoid duplicates
    content.click() #click "load more" button
    html = driver.page_source #read html
    soup = BeautifulSoup(html, 'html.parser') #parse with BeautifulSoup
    for data in soup.find_all("img"): #inner loop to pull out episode names
        names.append(data.get("alt"))
    #check to make sure we have everything
    if names[len(names)-1] == "Ep 1 - Mad Max Fury Road":
        driver.close()
        break
len(names) #check length   
names = names[::-1] #reverse string to sort first to last
names_df = pd.DataFrame(names)

os.chdir("/Users/paultrygstad/Desktop/Extra Ciricular")
names_df.to_csv("Only_Movie_Pod_Episodes.csv", index=False)
"""



for year in range(2014, 2024):
    for month in range (1:13):
        month ="{:02d}".format(month)
        site = "https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/KML/" + year+"/"+month+"/"
        driver = webdriver.Firefox() #open webdriver
        driver.get(site)
        file = driver.find_element(By.NAME, "sat")
        

number = 1
"{:02d}".format(number)
https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/KML/2005/08/