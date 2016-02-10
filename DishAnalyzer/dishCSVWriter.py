# -*- coding: utf-8 -*-
"""
This script finds the most common ingredients for recipes that meet a certain keyword (e.g. 'burger'), using Yummly's API.
This script writes this data to individual CSV files by dish.

"""

import requests
import pprint
pp = pprint.PrettyPrinter()
import pandas as pd
import os

# store API access key
cykey = '_app_id=f2a8aed2&_app_key=2e1518e4407a359e7db7b496841bc713'

## create csv writer function
def recipeOutputter(food):
    skeyword = '&q=' + str(food)
    sresults = '&maxResult=' + str(resultsPerFood)
    
    # retrieve and store results in a DataFrame
    r = (requests.get('http://api.yummly.com/v1/api/recipes?' + cykey + skeyword + sresults)).json()
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
    
    # drop entries with empty cuisines or courses
    recipes=recipes[(recipes.cuisine.str.len() != 0) & (recipes.course.str.len() != 0)]
    
    # write search criteria to column
    recipes['dish'] = food
    
    # write to CSV file
    os.chdir(os.getcwd() + '\\dishdata')
    recipes.to_csv(food + '.csv', encoding = 'utf-8')
    return recipes

# store search criteria
foods = ['burger', 'cake', 'chili', 'chowder', 'cookies', 'curry', 'donut', 'duck', 'fish+and+chips', 'lobster', 'meatloaf', 'paella', 'pancakes', 'pasta', 'pie', 'brownies', 'pizza', 'pork+chops', 'ramen', 'ribs', 'roast+chicken', 'salad', 'salmon', 'sandwich', 'steak', 'stir+fry', 'sushi', 'tacos', 'turkey', 'crab+cakes']
resultsPerFood = 500

## call function on foods
recipes = recipeOutputter(foods[0])
print recipes.count()

## merge data from individual dish CSV files to a master DataFrame
import glob
import ntpath

dishes = pd.DataFrame()
allFiles = glob.glob(os.getcwd() + "/*.csv")
allFiles
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_)
    df['dish'] = ntpath.basename(file_)[:-4]
    list_.append(df)

dishes = pd.concat(list_)
dishes.sort_values(by='dish', inplace=True)
dishes.set_index('id', inplace=True)

# convert cooking time to minutes
dishes['timeMins'] = dishes.totalTimeInSeconds.apply(lambda x: x/60) 

# convert ingredients from str to list
ingred = dishes['ingredients'].values
ingredlist = []
for i in range(0, len(ingred)):
    ingredlist.append([x.strip() for x in ingred[i][1:-1].split(',')])
dishes['ingredients']= ingredlist

# store ingredient count for each recipe
ingredcount = []
for i in range(0, len(ingredlist)):
    ingredcount.append(len(ingredlist[i]))
dishes['ingred_count'] = ingredcount

# fill in missing courses and cuisines
dishes.course.fillna('Unknown', inplace=True)
dishes.cuisine.fillna('Unknown', inplace=True)

# drop duplicates
dishes = dishes[dishes.index.duplicated() == False]

## write master DataFrame to a master CSV data file
dishes.to_csv('dishes_data.csv', encoding = 'utf-8')










