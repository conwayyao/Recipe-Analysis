# Why this project?

Ironically, I enjoy cooking but I hate using recipes. In my opinion, recipes tend to encourage a slavish devotion to the recipe and divert attention from the more important part of cooking, the physical abilities (or, in my case, the lack thereof) of the chef. Foodies tend to privilege the provenance of obscure ingredients ("coulis of feather saffron hand-picked from a seaside village in Morocco"); I prefer the mundane but practical parts of cooking that get ignored in recipes (like freezing leftover sauce in ice cube trays, or the proper way to peel a mango).

I am curious how much variation exists between dishes, and whether such variation is warranted. Are there really 5000 ways to cook a steak, or are many of these variations superfluous? Some chefs like Heston Blumenthal have taken an experimental approach to answering these questions, systematically and scientifically investigating every property of a dish, its ingredients, and its cooking methods to determine the "best" way to cook a dish. Since I do not have access to recipe instructions, I can only examine these recipes based on its ingredients. Nevertheless, I hope to use a data-science approach to see if the cooking wisdom of the crowds have arrived at the same answers, and if they match those of traditional experts.

# Questions

Dish explorer:

1. What are the most common ingredients for a particular dish?
2. What is the most unique recipe for each dish based on its ingredients?
3. Given a recipe, which recipes are most similar to it? (Recipe comparison)
4. Given a set of ingredients, which recipes can I make? ("What's-in-the-fridge" prediction)
  - Which recipes can I make with a few more ingredients?
6. Given a set of ingredients, which dish and recipe is it most like? (Dish/recipe classifier)

Cuisine explorer:

1. What are the most common ingredients for a particular cuisine?
2. What is the most unique recipe for each cuisine based on its ingredients?
3. Given a recipe, which recipes are most similar to it? (Recipe comparison)
4. Given a set of ingredients, which recipes can I make? ("What's-in-the-fridge" prediction)
  - Which recipes can I make with a few more ingredients?
6. Given a set of ingredients, which dish and recipe is it most like? (Dish/recipe classifier)

Ratings and general exploration:

1. Is there a relationship between recipe rating and number of ingredients?
2. Is there a relationship between recipe rating and recipe cost?
4. What other interesting relationships exist in the data?

# Data Collection

In my preliminary project discussion, I had chosen to use the Spoonacular API, whose team had granted me an academic usage key. Spoonacular's API was generally very satisfactory but I had concerns with the number and quality of recipes on their website, and the quality of the ingredients provided for each recipe. A week after the preliminary project presentation, I received academic usage approval for Yummly's recipe API. While Spoonacular's API had more bells and whistles and advanced features, I believed that Yummly's database of recipes was generally of higher quality than Spoonacular's. It also had access to over 1 million recipes compared to Spoonacular's, and had better-formatted ingredients for each recipe. For these advantages, I switched data collection from Spoonacular to Yummly's API.

Yummly's API is accessed by querying an API endpoint and returns JSON-encoded recipe data. It was easy to set up and use. Since I divided the project into two parallel paths (cuisine and dish), the search queries were straightforward: either search by dish name (e.g. "burger") or specify a search by cuisine (e.g. cuisine-Chinese). JSON data was translated to Pandas dataframe structures using the Requests package and Pandas.

I encountered difficulties with the API when I tried to retrieve too many recipes at once. Initially, I hoped to create a list of all cuisines or dishes and loop through those lists, requesting recipes during each loop. Unfortunately, the loop would break after a few cuisines or dishes due to problems on Yummy's end. I opted to write separate CSV files for each dish and cuisine and concatenate them together into a master cuisines.csv and a master dishes.csv at the end rather than try to do it all in one go.

In total I made 454 calls to Yummly's API over four days of data collection (accounting for missteps and experimentation). I wrote cuisine data into 25 separate CSVs before assembling them into cuisines_data.csv, and wrote dishes data into 45 separate CSVs before assembling into dishes_data.csv.

Each row of data contained:

- Yummly Recipe ID (string)
- Recipe Name (string)
- Yummly Rating (integer, 0-5)
- Cooking Time in Seconds (integer)
- Course (string)
- Cuisine (string)
- Ingredients (string)

# Data Pre-Processing

I conducted several processing steps on the two master data CSVs (dishes and cuisines):

1. Ingredient parsing:

	Each recipe's ingredients were encoded as a single, unseparated string, including brackets: "[ingredient 1, ingredient 2, ingredient 3]". Since I wanted to examine each ingredient separately, I dropped the brackets from each string by reading from [1:-1]. Next, I separated by comma, then returned a list of these ingredient strings.

	Yummly's ingredient specifications are imperfect. A human would be able to recognize that "fresh pasta", "pasta", and "Giorgino pasta" are essentially the same ingredient, but this code necessarily treats these as three separate and unique ingredients.

2. Ingredient counts:

	After parsing the ingredients from a single string to a list of strings, it was easy to calculate the number of ingredients in each recipe by creating a new column named "ingredCount" and setting each value to len(ingredients).

3. Time conversion:

	As we are more accustomed to thinking about cooking times in minutes rather than seconds, I converted each recipe's cooking time from seconds to minutes by dividing by 60 and populated a column named "timeMins".

4. Munging:

	I conducted an initial round of munging to ensure my data was sufficiently clean for analysis. 

	The most important one was to drop any rows of cuisines data that had an empty "cuisine" value. Yummly's "Search by Cuisine" API call returns recipes that have "Chinese" in the recipe in some shape or form-- even in the ingredients! So a sandwich recipe that employs "French bread" or an "English muffin" might have a cuisine value of "French" or "English". To avoid these ambiguities, I dropped any empty recipes without an explicit cuisine. This greatly reduced the number of recipes for some cuisines like English. I only did this for my cuisines_data.csv; since dishes_data.csv is unconcerned with dish origin, there was no need to drop dishes with empty cuisine values.

	For dishes_data.csv, I explicitly assigned each recipe to the search query that it was gathered from, using a new column named "dish". For example, all recipes from the burger.csv file were appended with "dish=burger". This dramatically simplified later analyses at the expense of some accuracy. I could not do this with cuisines_data, because a lot of the belonged to multiple cuisines and I wanted to preserve this complexity.

	For both dishes_data and cuisines_data, I filled in empty course values with "Unknown" rather than dropping these recipes.

	Finally, I dropped duplicate recipes from both datasets. For example, a recipe for pad thai that is listed as both "Asian" and "Thai" within its cuisine value will show up twice in the dataset: first during the search for Asian dishes, then again during the search for Thai dishes.

# Data Analysis:

## Dish Dataset:

Dish dataset basic stats:

- 16402 recipes
- 44 dishes (e.g. burger, burrito, steak, gumbo)
  - Dishes with the most recipes: cake (633), chowder (545), pancakes (457), roast chicken (444)
  - Dishes with the least recipes: donut (202), tacos (221), chili (265), turkey (275)
- 25 Cuisines: American is the most well-represented, with 396 recipes. Portuguese the least, with just 2 recipes
- Ratings: overwhelmingly 4-star (10984 of the 16402), some 3-star (3646) and 5-star (1683), very few 0, 1, or 2 stars (89 combined recipes)
- Cooking Time: mean of 65 minutes, max of 5760 minutes (4 days), min of 1 minute, median of 45 minutes
- Ingredients per recipe: mean of 9.9, max of 59 (swordfish ceviche), min of 1, median of 9
- 5385 unique ingredients:
  - Most common ingredients: Salt (6978 occurences, 0.43 frequency), butter (0.21), eggs (0.17), sugar (0.16), onions (0.15)
  - Least common ingredients: 1675 unique ingredients are only used in one recipe throughout the dataset. Examples: buckwheat noodles, gluten-free pie crust, canned snails, sugar-free Jell-O gelatin

## Cuisine Dataset:

Cuisine dataset basic stats:

- 8037 recipes
- 25 cuisines: Asian is the most well-represented, with 1414 recipes. English the least, with just 32 recipes.
- Ratings: overwhelmingly 4-star (4988 of the 8037), some 3-star (1517) and 5-star (1379), very few 0, 1, or 2 stars (153 combined recipes)
- Cooking Time: mean of 65 minutes, max of 1970 minutes (33 hours), min of 1 minute, median of 40 minutes
- Ingredients per recipe: mean of 10.1, max of 35 (Thai chicken tacos), min of 1, median of 9
- 3958 unique ingredients:
  - Most common ingredients: Salt (3325 occurences, 0.41 frequency), garlic (0.22), onions (0.20), olive oil (0.18)
  - Least common ingredients: 1401 unique ingredients are only used in one recipe throughout the dataset. Examples: chocolate candy, melon seeds, canned tuna, vegan yogurt, tarragon vinegar, unsalted almonds

## Unique Ingredient Analysis:

I wanted to examine the frequency and type of unique ingredients employed by each cuisine or each dish. I created a function with an input of a DataFrame that iterates through each recipe in the DataFrame and adds the contents of each recipe's ingredients list to a summation list. This list is converted to a Pandas Series so that I can take advantage of Pandas' value_counts() method to count each appearance of an ingredient. The output of the value_counts() is saved as a column named "instances" representing the number of recipes that the ingredient appears in. I then calculated ingredient frequency by dividing the instances by the number of recipes in the dataset, and appended as a new column "frequency".

Since this function takes a DataFrame as an input, it can be called on any dish, cuisine, or subset of dishes or cuisines to examine their unique ingredient counts and frequencies.

From just cursory examination, it is easy to see how cuisines cook with different ingredients, and see which cuisines are similar to each other. For example, here are the most popular ingredients for some cuisines:

- American: salt, butter, all-purpose flour, sugar, olive oil, water, onions, pepepr, unsalted butter, coarse salt
- French: salt, unsalted butter, sugar, butter, all-purpose flour, water, eggs, heavy cream, milk
- Chinese: soy sauce, corn starch, salt, sesame oil, garlic, sugar, water, scallions, ginger, oil
- Indian: salt, onions, garam masala, cumin seed, ground turmeric, garlic, ground cumin, oil, ginger, water
- Italian: salt, olive oil, parmesan cheese, garlic, extra-virgin olive oil, onions, garlic, pepper, eggs
- Thai: fish sauce, coconut milk, garlic, lime, soy sauce, salt, lime juice, vegetable oil, brown sugar

It is easy to see that American and French cuisine have many similarities, with frequent use of butter, sugar, flour, and salt. Chinese, Thai, and Indian cooking uses completely separate palettes of ingredients. This answers one of my questions, what are the most indicative ingredients for each cuisine?

## Recipe Uniqueness Scoring:

Next, I identified which recipes within a given dataset are the most 'unique' in terms of their ingredients. For example, one expects that most chili recipes will contain tomato sauce, beans, ground beef, and onions. If a chili recipe does not use any of these ingredients and instead uses fruits or obscure meats, it is very different from the norm and should receive a high uniqueness score.

The first method of scoring is to take the mean of each recipe's ingredient frequencies (e.g. (0.4+0.2+0.1) / 3 ). For each recipe's ingredients, I sum the ingredients' unique ingredient frequency score calculated above, then divide by the number of ingredients in the recipe so as to not bias the scoring towards recipes with dozens of ingredients. I assign this score to a column named "uniq_score1".

The second method of scoring is to take the product of each recipe's ingredient frequencies (e.g. 0.4 * 0.2 * 0.1). I assign this score to a column named "uniq_score2".

Both methods have their pros and cons and some more thinking is required to assess which better fits our intuition. Both methods produce broadly similar results, but the mean score seems to match our intuition slightly better than the product. The product tends to 'reward' recipes with extremely rare ingredients whereas the mean method 'rewards' these recipes to far lower extent.

Nevertheless, by examining the results I am more or less satisfied with these scoring methods. The most 'typical' American Main Course, for example, is Southern Fried Chicken, which uses salt, butter, chicken, and oil. An extremely 'atypical' dish is the swordfish ceviche, which uses 59 ingredients that are each very rare.

## Data Relationships:

I was disappointed by the inability to discover any meaningful relationships between some key metrics. For example, I hypothesized that recipes with extremely long (arduous) or extremely short (too simple) cooking times would receive lower ratings than recipes with a reasonable cooking time. Likewise recipes with many ingredients or very few ingredients. However, the ratings provided by Yummly were extremely uneven and extremely unlikely, with more than half the recipes in both cuisines_data and dishes_data holding a rating of 4. Almost no 0, 1, or 2-star recipes exist in either dataset, suggesting that Yummly is cooking the rating data somehow like Fandango's movie ratings. 

After plotting cooking time vs. ratings and ingredient counts vs. ratings, it was clear that there are no correlations because of the incompleteness of the underlying ratings. 

There may or may not be a relationship between ingredient counts and cooking times. According to the scatterplot it does not appear linear but rather bell-shaped. I did not yet fit a multidimensional regression curve to it yet.

# Data Dictionary:

My final data dictionary:

- Recipe ID ('id', string): set as index of both dishes_data.csv and cuisines_data.csv
- Recipe Name ('recipeName', string)
- Cooking Time in Seconds ('totalTimeInSeconds', integer)
- Cooking Time in Minutes ('timeMins', integer): calculated during processing stage
- Yummly Rating ('rating', integer): ratings from 0 to 5
- Course ('course', string): "Unknown" filled in for null values during processing stage
- Cuisine ('cuisine', string)
- Dish ('dish', string): for dishes_data.csv ONLY
- Ingredients ('ingredients', list of strings): parsed during processing stage
- Ingredient Count ('ingred_count', integer): calculated during processing stage
- Uniqueness Score #1 ('uniq_score1', floating): calculated during analysis stage; mean of ingredient frequencies
- Uniqueness Score #2 ('uniq_score2', floating): calculated during analysis stage; product of ingredient frequencies
- Can I Make This Dish? ('possible', boolean): determined during "What Can I Make?" analysis

Unique ingredient data dictionary:

- Ingredient name ('ingredient', string): set as index of uniq_ingred DataFrame
- Count ('instances', integer): number of recipes that the ingredient appears in
- Frequency ('frequency', floating): percentage of recipes that the ingredient appears in; calculated by dividing count by the number of recipes in the dataset

# What Can I Make?

In order to find which recipes are possible given a set of supplies in a pantry, I employed Python's .issubset() method, which determines if all of the objects in one set (the recipe) exist in another set (your pantry). I created a function which iterates through a dataset's recipes and sets a boolean named "possible" to True if all ingredients in the recipe exist in your pantry. Again, the ingredients were parsed naively; the code has no way of knowing that "fresh basil leaves" can satisfy a requirement for "basil leaves". The computer treats these as two distinct ingredients.

Rather than type out a long list of items in a pantry, I decided the logical way for someone to stock a pantry would be to purchase the most common unique ingredients for whichever cuisine or dish the person was interested in making. For both cuisines_data and dishes_data, I stocked the pantry with the 100 most common unique ingredients in the dataset, then ran my function to see how many dishes were possible.

I was suprised to see how few dishes were possible even with a well-stocked pantry. With the 100 most common unique ingredients, one can only make 114 out of the 8037 recipes in the cuisines_data dataset. To explore how adding additional ingredients to your pantry increased the number of recipes you can make, I successively added to the pantry and plotted how many recipes were possible. Surprisingly, the relationship is fairly linear, with an R^2 of 0.994, at least up to the 1000 most common ingredients (due to running time, I did not extend all the way to 3958 ingredients). With 1000 of the most common ingredients, one can make roughly 3500 recipes. The curve does show a slight logistic tendency, as would be expected: adding ingredients rapidly expands the number of recipes you can make before petering out.

# Machine Learning and Classification

In order to add a predictive component to this project, I utilized machine learning to predict the cuisine or dish of a recipe given its ingredients. Since we have established that cuisines differ substantially in terms of their ingredient usages, I expected fairly good results for these Cuisine and Dish classifiers.

For each recipe, I converted the ingredients of each recipe from a list of strings back to a single string so that I could utilize the bag-of-words model. This is admittedly a very inelegant solution, as there should exist a method to use the ingredients as the tokens for a model rather than deconvert back to a bag-of-words. Then I train-test-split with sklearn and fit a Naive Bayes and Logistic Regression model. I compared the predicted cuisines or dishes with the real cuisines and dishes and achieved surprisingly accurate results out-of-the-box:

Null accuracy of cuisine prediction is "Asian", 555/8037 = 0.06906:

- Multinomial Naive Bayes: 0.53383 accuracy. 7x better than null accuracy
- Logistic Regression: 0.43881 accuracy, 6x better tha null accuracy

Null accuracy of dish prediction is "Cake", 633/16402 = 0.038592:

- Multinomial Naive Bayes: 0.71080, 18x better than null accuracy
- Logistic Regression: 0.70299, 18x better than null accuracy

A major reason why cuisine prediction was less accurate than dish prediction was that the cuisine data was not encoded as cleanly. Every recipe in the dishes_data dataset was assigned an explicit "dish" value, whereas every recipe in the cuisines_data dataset was NOT assigned an explicit cuisine. Many of the recipes in the cuisines_data dataset had multiple listings under cuisine. For example, a recipe could be listed as "[Asian, Chinese]". When previously counting the number of recipes that were Asian, I boolean-filtered for all recipes that had "Asian" within the string of "cuisine". So this recipe would have been counted twice, once for "Asian" and once for "Chinese"-- hence the total number of recipes does not add up.

When doing this classification for cuisines, there is no easy way to disaggregate Asian and Chinese, as the computer must decide which of the two to classify any one recipe. So I kept all multi-cuisine designations rather than try to impute one over another. Rather than 25 cuisines to predict, I had 206, many combos of which only existed once in the dataset (e.g. "[Barbecue, Mediterranean, Greek]" or "[Italian, Japanese]"). Given this messiness, I was very pleased that the overall accuracy was still 7x better than null.

# Next Steps

My next steps include:

1. Refining cuisine and dish prediction. I only did minimal experimentation with model hyperparameters. I want to revisit the multiple-cuisine designation problem and ingredient-tokenization problem I mentioned above. I believe I can improve accuracy by another 15% for cuisines prediction, and perhaps another 10% for dish prediction.

2. Publishing interesting results or infographics online, using static images or Bokeh/ D3

3. Clustering analysis

3. Pricing analysis if I can find an API that accepts ingredients and returns price per serving.




