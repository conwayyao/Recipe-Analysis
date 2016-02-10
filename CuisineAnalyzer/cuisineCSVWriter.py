# -*- coding: utf-8 -*-
"""
This script finds recipes for cuisines (e.g. 'Indian'), using Yummly's API.
This script writes this data to individual CSV files, then merges them all into one master cuisine_data.csv file.

Writing to CSV files before merging reduces transmission errors.

"""

import requests
import pprint
pp = pprint.PrettyPrinter()
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# store API access key
cykey = '_app_id=f2a8aed2&_app_key=2e1518e4407a359e7db7b496841bc713'

# set cuisine search criteria
cuisinelist = ['american', 'italian', 'asian', 'mexican', 'southern', 'french', 'southwestern',
            'barbecue-bbq', 'indian', 'chinese', 'cajun', 'mediterranean', 'greek', 'english',
            'spanish', 'thai', 'german', 'moroccan', 'irish', 'japanese', 'cuban', 
            'hawaiian', 'swedish', 'hungarian', 'portuguese']
resultsPerCuisine = 500

# create wrapper function
def recipeOutputter(cuis):
    scuisine = '&allowedCuisine[]=cuisine^cuisine-' + cuis
    sresults = '&maxResult=' + str(resultsPerCuisine)
    
    # retrieve and store results in a DataFrame
    r = (requests.get('http://api.yummly.com/v1/api/recipes?' + cykey + scuisine + sresults)).json()
    recipes = pd.DataFrame(r['matches'], columns = ['id', 'recipeName', 'rating', 'totalTimeInSeconds', 'ingredients'])
    
    # extract course and cusine and add to DF
    course = []
    cuisine = []
    for i in r['matches']:
        course.append(i['attributes'].get('course', None))
        cuisine.append(i['attributes'].get('cuisine', None))
    recipes['course'] = course
    recipes['cuisine'] = cuisine
    
    # rearrange DF
    recipes.set_index('id', inplace=True)
    col = ['recipeName', 'rating', 'totalTimeInSeconds', 'course', 'cuisine', 'ingredients']
    recipes=recipes[col]
    
    # drop entries with empty cuisines
    recipes=recipes[recipes.cuisine.str.len() != 0]
    
    # write to CSV file
    os.chdir(os.getcwd() + '\\cuisinedata')
    recipes.to_csv(cuis + '.csv', encoding = 'utf-8')
    
# call function on foods to write individual CSV files
for i in cuisinelist[0:1]:
    recipeOutputter(i)

# merge data from individual cuisine CSV files to a master DataFrame
import glob

cuisines = pd.DataFrame()
allFiles = glob.glob(os.getcwd() + "/*.csv")
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_)
    print df.count()
    list_.append(df)

cuisines = pd.concat(list_)

# write master DataFrame to a master CSV data file
cuisines.to_csv('cuisine_data.csv', encoding = 'utf-8')








    







