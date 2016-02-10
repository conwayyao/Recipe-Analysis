# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 17:08:56 2015

Analyze and predict dish data.

@author: Conway
"""

## read in dishes data
import pandas as pd
import numpy as np
import matplotlib
import os
os.getcwd()

dishes = pd.read_csv('dishdata\dishes_data.csv', index_col = 'id')
dishes.dropna(inplace=True)
dishes.count()

# convert ingredients from str to list
ingred = dishes['ingredients'].values
ingredlist = []
for i in range(0, len(ingred)):
    ingredlist.append([x.strip() for x in ingred[i][1:-1].split(',')])
dishes['ingredients']= ingredlist

## dataframe inspection

cuisinelist = ['American', 'Italian', 'Asian', 'Mexican', 'Southern', 'French', 'Southwestern', 'Barbecue', 'Indian', 'Chinese', 'Cajun', 'Mediterranean', 'Greek', 'English', 'Spanish', 'Thai', 'German', 'Moroccan', 'Irish', 'Japanese', 'Cuban', 'Hawaiian', 'Swedish', 'Hungarian', 'Portuguese']

courselist = ['Main Dishes', 'Desserts', 'Side Dishes', 'Lunch and Snacks', 'Appetizers', 'Salads', 'Breakfast and Brunch', 'Breads', 'Soups', 'Beverages', 'Condiments and Sauces', 'Cocktails', 'Unknown']

dishlist = sorted(list(set(dishes.dish.tolist())))

# function: select a dish
def dish(food):
    return dishes[dishes.dish== food].copy()

# function: inspect ratings
def dish_ratings(dataframe):
    print dataframe.rating.value_counts()
    print dataframe.rating.describe()

dish_ratings(dish('pie'))
dish_ratings(dishes)

# function: inspect cooking times 
def dish_times(dataframe):
    print dataframe.timeMins.sort(inplace=False)
    print dataframe.timeMins.describe()

dish_times(dish('pie'))
dish_times(dishes)

# function: inspect course distribution
def dish_courses(dataframe):
    for course in courselist:
        counter = 0
        for i in range(0, len(dataframe.course.value_counts().values)):
            if course in dataframe.course.value_counts().index[i]:
                counter += dataframe.course.value_counts().values[i]
        print 'Number of ' + course + ':  ' + str(counter) 

dish_courses(dishes)
dish_courses(dish('pie'))

# function: inspect cuisine distribution
def dish_cuisines(dataframe):
    for cuisine in cuisinelist:
        counter = 0
        for i in range(0, len(dataframe.cuisine.value_counts().values)):
            if cuisine in dataframe.cuisine.value_counts().index[i]:
                counter += dataframe.cuisine.value_counts().values[i]
        print 'Number of ' + cuisine + ':  ' + str(counter) 

dish_cuisines(dishes)
dish_cuisines(dish('pie')) 

# function: inspect ingredient counts
def dish_ingreds(dataframe):
    print dataframe.ingred_count.value_counts()
    print dataframe.ingred_count.describe()

dish_ingreds(dish('pie')) 
dish_ingreds(dishes)

# function: inspect ingredient frequency (# of recipes with that ingredient/# of recipes overall)
def dish_unique_ingreds(df):
    ingredients_sum = []
    for i in range(0, len(df.ingredients)):
        ingredients_sum += list(df.ingredients[i])
    unique_ingreds = pd.DataFrame(pd.DataFrame(ingredients_sum)[0].value_counts(), columns= ['ingredient'])
    unique_ingreds['frequency'] = unique_ingreds['ingredient']/len(df)
    return unique_ingreds

dish_unique_ingreds(dish('pie'))
dish_unique_ingreds(dishes)[dish_unique_ingreds(dishes)['ingredient'] ==2]

# function: calculate 2 uniqueness scores for each recipe
def dish_uniqueness(df):
    unique_ingreds = dish_unique_ingreds(df)
    uniq_score= []
    uniq_score2= []
    for i in range(0,len(df)):
        frequency_score = 0 # first uniqueness score is mean of frequencies
        container = [] # second uniqueness score is product of frequencies
        for ingredient in df.iloc[i]['ingredients']:
            frequency_score += unique_ingreds.ix[ingredient]['frequency']
            container.append(unique_ingreds.ix[ingredient]['frequency'])
        uniq_score.append((frequency_score/df.iloc[i]['ingred_count'])*100)
        uniq_score2.append(np.product(container))
    df['uniq_score'] = uniq_score
    df['uniq_score2'] = uniq_score2
    return df

## dataframe for further analysis
dishes = dish_uniqueness(dishes)
pies = dish_uniqueness(dish('pie'))

# total recipes    
dishes.count()
pies.count()

# most unique and least unique Main Dishes
dishes[dishes['course'].str.contains('Main Dishes')][['uniq_score', 'uniq_score2']].sort('uniq_score2')

# inspect a recipe by id
dishes.ix['Pineapple-_-Mango-Swordfish-Ceviche-1368415']

# other inspection tasks
len(dishes.dish.value_counts())

## find recipes that you can make given a set of supplies in the pantry
pantry = dish_unique_ingreds(dishes).index[0:100]

dishes['possible'] = ''

for i, row in dishes.iterrows():
    possible = False
    if set(row.ingredients).issubset(set(pantry)):
        possible = True
    dishes.set_value(i, 'possible', possible)

dishes[dishes.possible][['course', 'dish']]

## visualizations
import matplotlib.pyplot as plt
course_data = pd.Series(dishes.dish.value_counts()[20:40])
course_data
course_data.plot(kind='barh')
plt.xlabel('Dish Type')
plt.ylabel('Recipe Count')
plt.title('Recipes by Dish Type')
    
## classify dishes based on ingredients
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split

# convert ingredients back into strings
ingredients_str = []
for i in dishes.ingredients:
    ingredients_str.append(' '.join(i))
dishes['ingred_str'] = ingredients_str

# convert cuisine types to integer labels
from sklearn import preprocessing
le = preprocessing.LabelEncoder()
le.fit(dishes.dish)
dishes['dish_label'] = le.transform(dishes.dish)

# train/test/split bag of words with Multinomial NB
feature_cols = 'ingred_str'
X = dishes[feature_cols]
y = dishes.dish_label
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=99)

vect = CountVectorizer()
X_train_dtm = vect.fit_transform(X_train)
X_test_dtm = vect.transform(X_test)

from sklearn.naive_bayes import MultinomialNB
nb = MultinomialNB()
nb.fit(X_train_dtm, y_train)
y_pred_class = nb.predict(X_test_dtm)
from sklearn import metrics
print metrics.accuracy_score(y_test, y_pred_class)

# train/test/split with Logistic Regression
from sklearn.linear_model import LogisticRegression
logreg = LogisticRegression(C=1e9)
logreg.fit(X_train_dtm, y_train)
y_logreg_pred_class = logreg.predict(X_test_dtm)
print metrics.accuracy_score(y_test, y_logreg_pred_class)

dishes.dish.value_counts()
    