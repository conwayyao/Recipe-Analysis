# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 17:08:56 2015

@author: Conway
"""

## read in cuisine data
import pandas as pd
import numpy as np
import os
os.getcwd()

cuisines = pd.read_csv('cuisinedata\cuisine_data.csv', index_col = 'id')

# convert cooking time to minutes
cuisines['timeMins'] = cuisines.totalTimeInSeconds.apply(lambda x: x/60) 
cuisines.drop(['Unnamed: 0'], axis=1, inplace=True)

# convert ingredients from str to list
ingred = cuisines['ingredients'].values
ingredlist = []
for i in range(0, len(ingred)):
    ingredlist.append([x.strip() for x in ingred[i][1:-1].split(',')])
cuisines['ingredients']= ingredlist

# store ingredient count for each recipe
ingredcount = []
for i in range(0, len(ingredlist)):
    ingredcount.append(len(ingredlist[i]))
cuisines['ingred_count'] = ingredcount

# fill in missing courses
cuisines.course.fillna('Unknown', inplace=True)

# drop duplicates
cuisines = cuisines[cuisines.index.duplicated() == False]

## functions to generate a cuisine-specific dataframe for analysis

cuisineslist = ['american', 'italian', 'asian', 'mexican', 'southern', 'french', 'southwestern', 'barbecue', 'indian', 'chinese', 'cajun', 'mediterranean', 'greek', 'english', 'spanish', 'thai', 'german', 'moroccan', 'irish', 'japanese', 'cuban','hawaiian', 'swedish', 'hungarian', 'portuguese']

courselist = ['Main Dishes', 'Desserts', 'Side Dishes', 'Lunch and Snacks', 'Appetizers', 'Salads', 'Breakfast and Brunch', 'Breads', 'Soups', 'Beverages', 'Condiments and Sauces', 'Cocktails']

# function: generate a new dataframe filtered by cuisine
def cuisine_df_generator(cuis):
    cuisdf = cuisines[cuisines.cuisine.str.contains(cuis, case=False)].copy()
    return cuisdf

# function: inspect ratings
def cuisine_ratings(cuisdf):   
    print 'rating distribution: \n', cuisdf.rating.value_counts(), '\n\n', cuisdf.rating.describe(), '\n'

cuisine_ratings(cuisines)

# function: inspect cooking times
def cuisine_times(cuisdf): 
    print 'cooking time in mins: \n', cuisdf.timeMins.describe()
    
cuisine_times(cuisines)

# function: inspect cuisine distribution
def cuisine_cuisines(cuisdf):
    cuisine_counts = [] 
    for cuisine in cuisineslist:
        counter = 0
        for i in range(0, len(cuisdf.cuisine.value_counts())):
            if cuisine in cuisdf.cuisine.value_counts().index[i].lower():
                counter += cuisdf.cuisine.value_counts().values[i]
        cuisine_counts.append(counter)
    return dict(zip(cuisineslist, cuisine_counts))

cuisine_cuisines(cuisines)

# function: inspect count, avg time, and avg ingredients of courses
def cuisine_courses(cuisdf):
    course_counts = []    
    for course in courselist:
        print 'Count of ' + course + ': ' + str(len(cuisdf[cuisdf['course'].str.contains(course)]))
        course_counts.append(len(cuisdf[cuisdf['course'].str.contains(course)]))
        print 'Avg time in mins for ' + course + ': ' + str(cuisdf[cuisdf['course'].str.contains(course)].timeMins.mean())
        print 'Avg # of ingreds for ' + course + ': ' + str(cuisdf[cuisdf['course'].str.contains(course)].ingred_count.mean()) + '\n'
    return dict(zip(courselist, course_counts))

# function: inspect recipes based on number of ingredients
def cuisine_ingredients(cuisdf):
    print 'Ingredient distribution: \n', cuisdf.ingred_count.describe(), '\n'
    print 'Fewest ingredients: \n', cuisdf.sort('ingred_count')['ingred_count'].head(5), '\n'
    print 'Most ingredients: \n', cuisdf.sort('ingred_count')['ingred_count'].tail(5)

cuisine_ingredients(cuisines)

# function: inspect ingredient frequency (# of recipes with that ingredient/# of recipes overall)
def cuisine_unique_ingredients(cuisdf):
    cuis_ingredients = []
    for i in range(0, len(cuisdf.ingredients)):
        cuis_ingredients += list(cuisdf.ingredients[i])
    cuis_ingredients = pd.DataFrame(cuis_ingredients, columns=['instances'])
    cuis_unique_ingreds = pd.DataFrame(cuis_ingredients['instances'].value_counts(), columns=['instances'])
    cuis_unique_ingreds['frequency'] = cuis_unique_ingreds['instances']/len(cuisdf)
    return cuis_unique_ingreds

cuisine_unique_ingredients(cuisine_df_generator('thai'))

# function: calculate 2 uniqueness scores for each recipe WITHIN a cuisine
def cuisine_uniqueness(cuis):
    cuisdf = cuisine_df_generator(cuis)
    cuis_unique_ingreds = cuisine_unique_ingredients(cuisine_df_generator(cuis))
    uniq_score= []
    uniq_score2= []
    for i in range(0,len(cuisdf)):
        frequency_score = 0
        container = []
        for ingredient in cuisdf.iloc[i]['ingredients']:
            frequency_score += cuis_unique_ingreds.ix[ingredient]['frequency']
            container.append(cuis_unique_ingreds.ix[ingredient]['frequency'])
        uniq_score.append((frequency_score/cuisdf.iloc[i]['ingred_count'])*100)
        uniq_score2.append(np.product(container))
    cuisdf['uniq_score'] = uniq_score
    cuisdf['uniq_score2'] = uniq_score2
    return cuisdf

## dataframe for further analysis
italian = cuisine_uniqueness('italian')
american.sort_values(by='uniq_score')['uniq_score']
american.columns

# total recipes    
print '# of recipes: \n', american.count()

# most unique and least unique Main Dishes
print 'Most unique :'
print italian[italian['course'].str.contains('Main Dishes')].sort_values(by='uniq_score')[['uniq_score', 'ingredients']].head(4)

# inspect a recipe by id
american.ix['Boiled-Lobster-My-Recipes']['ingredients']

# other dataframe inspections / sandbox:
len(cuisines)
cuisine_unique_ingredients(cuisines)
cuisines.columns
cuisine_cuisines(cuisines)

cuisines.sort('ingred_count').head(20)
cuisines.ix['Grilled-BBQ-Zucchini-1371766']

cuisines.timeMins.value_counts()
cuisines.dropna().sort('timeMins').tail(30)

## visualizations
import matplotlib.pyplot as plt

import matplotlib.axes as ax
plt.style.available
plt.style.use('ggplot')

plt.xlabel('Cooking Time (minutes)')
plt.ylabel('Recipe Count')

labels = ['4', '3', '5', '0', '2', '1']
plt.pie(cuisines.rating.value_counts(), labels=labels, autopct='%1.1f%%', colors=['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'red'], startangle=50, pctdistance=0.6)
plt.axis('equal')
plt.title('Recipes by Rating')
plt.show()

course_data = pd.Series(cuisine_courses(cuisines))
course_data.plot(kind='barh')
plt.xlabel('Course Type')
plt.ylabel('Recipe Count')
plt.title('Recipes by Course Type')

cuisine_cuisines(cuisines)
pd.Series(cuisine_cuisines(cuisines)).plot(kind='barh')
plt.xlabel('Count')
plt.title('Recipes by Cuisine')
plt.savefig('cuisine_counts.png')

## relationships?

# ingredient/rating relationship?
import numpy as np
feature_cols = ['ingred_count']
X= cuisines[feature_cols]
y= cuisines.rating
plt.scatter(X, y)
plt.xlabel('Ingredients')
plt.ylabel('Yummly Rating')
plt.title('Ingredient Counts vs Ratings')

from sklearn.linear_model import LinearRegression
linreg= LinearRegression()
linreg.fit(X, y)
linreg.intercept_
linreg.coef_
linreg.score(X, y)

# cooking time/rating relationship?
feature_cols = ['timeMins']
X= cuisines.dropna()[feature_cols]
y= cuisines.dropna().rating
plt.scatter(X, y)
plt.xlabel('Time in Minutes')
plt.ylabel('Yummly Rating')
plt.title('Cooking Time vs Ratings')

linreg= LinearRegression()
linreg.fit(X, y)
linreg.intercept_
linreg.coef_
linreg.score(X, y)

# ingredients/cooking time relationship?
feature_cols = ['ingred_count']
X= cuisines.dropna()[feature_cols]
y= cuisines.dropna()['timeMins']
plt.scatter(X, y)
plt.xlabel('Ingredient Count')
plt.ylabel('Time in Minute')
plt.title('Ingredients vs. Cooking Times')

linreg= LinearRegression()
linreg.fit(X, y)
linreg.intercept_
linreg.coef_
linreg.score(X, y)

## find recipes that you can make given a set of supplies in the pantry
# find number of possible recipes
pantry = cuisine_unique_ingredients(cuisines).index[0:100]

def how_many_can_I_make():    
    cuisines['possible'] = False
    for i, row in cuisines.iterrows():
        possible = False
        if set(row.ingredients).issubset(set(pantry)):
            possible = True
        cuisines.set_value(i, 'possible', possible)
    return cuisines.possible.value_counts()

how_many_can_I_make()

possible_count=[]
for i in range(1, 1000):   
    print i
    possible_count.append(how_many_can_I_make(i))
possible_count_1000 = possible_count
X = range(1,1000)
y= possible_count_1000
plt.scatter(X, y)
fit = np.polyfit(X, y, 1, full=True)
fit_fn = np.poly1d(fit)
plt.plot(X, y, X, fit_fn(X))
plt.xlabel('Number of Most Common Ingredients in Pantry')
plt.ylabel('Number of Recipes You Can Make')
plt.title('What Can I Make? Count')
print fit

X = np.array([X]).T
linreg= LinearRegression()
linreg.fit(X, y)
linreg.intercept_
linreg.coef_
linreg.score(X, y)

## cuisine predictor
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split

# convert ingredients back into strings
ingredients_str = []
for i in cuisines.ingredients:
    ingredients_str.append(' '.join(i))
cuisines['ingred_str'] = ingredients_str

# convert cuisine types to integer labels
from sklearn import preprocessing
le = preprocessing.LabelEncoder()
le.fit(cuisines.cuisine)
cuisines['cuisine_label'] = le.transform(cuisines.cuisine)

# train/test/split bag of words with Multinomial NB
feature_cols = 'ingred_str'
X = cuisines[feature_cols]
y = cuisines.cuisine_label
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

len(cuisines.cuisine.value_counts())