# Conway Yao's Recipe Project Description

## Data

Online recipe data is fairly disjointed. There are a multitude of recipe and cooking websites, including media networks (Food Network, Cooking Channel), professional and amateur bloggers (SeriousEats, FoodWishes, TheKitchn), and food industry sites (Betty Crocker, Kraft). There is fierce competition to have the most attractive presentations in order to draw viewership. This degrades the consistency of recipe documentation from site-to-site. The open-source hRecipe microformat, which defines a machine-readable structure for ingredients, instructions, yields, licenses, and other recipe data, has not yet been widely adopted.

There are several companies with proprietary APIs and databases acquired through scraping these recipe websites. These companies then sell licenses to developers. These APIs vary in their quality, database size, and fees:

- BigOven: 350,000 recipes; REST JSON and XML output
- Yummly: 1 million recipes, ratings, ingredients; REST JSON output; Academic plan available with 30,000 lifetime calls
- Food2Fork: 250,000 recipes; JSON output; Free plan with 500 calls per day
- Spoonacular: 350,000 recipes; UNIREST JSON output; Free plan for hackathons and academic purposes
- Edamam: 1.5 million recipes; Free Trial with up to 1000 lifetime calls

Of these five APIs, Food2Fork was the most basic and offered very limited documentation. BigOven and Yummly are the most widely-known and seemed to have the highest-quality data. I did receive a Spoonacular Academic plan and liked its documentation, but I eventually switched to Yummly's Academic plan after my access was approved. Yummly has great documentation, data already classified by course and cuisine, and flexible querying functions. Since I do not plan on analyzing more than 25,000 recipes, the number of recipes that each API offers is more than sufficient for my purposes.

Yummly allows recipe searches using the following parameters: 

- keyword (e.g. pizza)
- ingredients (e.g. tomatoes, no tomatoes)
- allergies (e.g. gluten, dairy, seafood; 10 in total)
- diets (e.g. vegan, pescetarian; 5 in total)
- cuisines (e.g. Portuguese, Greek; 25 in total)
- courses (e.g. Main Dishes, Appetizers; 12 in total)
- holidays (e.g. Thanksgiving, Super Bowl; 8 in total)

As the purpose of this project is to primarily investigate dishes and cuisines, I built two scripts to query Yummly's API for these two searches. In total, I collected data on 44 dishes for a total of 16967 recipes, amd all 25 cuisines for 8665 recipes. For each recipe, I have stored the recipe name, rating, cooking time, course, cuisine, and ingredients.

The biggest omission from the dataset is recipe instructions. None of the APIs offer parsed recipe instructions, only URL links that direct the developer or user to the source website of the recipe. This is extremely frustrating because it prohibits the comparison of cooking techniques or methods, and thus only allows an ingredient-based comparison of recipes. 

## Why this project?

Ironically, I enjoy cooking but I hate using recipes. In my opinion, recipes tend to encourage a slavish devotion to the recipe and divert attention from the more important part of cooking, the physical abilities (or, in my case, the lack thereof) of the chef. Foodies tend to privilege the provenance of obscure ingredients ("coulis of feather saffron hand-picked from a seaside village in Morocco"); I prefer the mundane but practical parts of cooking that get ignored in recipes (like freezing leftover sauce in ice cube trays, or the proper way to peel a mango).

I am curious how much variation exists between dishes, and whether such variation is warranted. Are there really 5000 ways to cook a steak, or are many of these variations superfluous? Some chefs like Heston Blumenthal have taken an experimental approach to answering these questions, systematically and scientifically investigating every property of a dish, its ingredients, and its cooking methods to determine the "best" way to cook a dish. Since I do not have access to recipe instructions, I can only examine these recipes based on its ingredients. Nevertheless, I hope to use a data-science approach to see if the cooking wisdom of the crowds have arrived at the same answers, and if they match those of traditional experts.

## Questions

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

## Data Processing

My first approach was to collect X number of recipes at random, then analyze and clean based on cuisine and dish. However, Yummly's API contains many recipes with incomplete metadata, meaning that I would have to collect even more data before I found a sufficient number of recipes for some small-sample cuisines like English or Hungarian. Futhermore, an unsupervised learning natural language processing approach to select dish types from recipe names would also be very challenging as many recipe names are confounded by adjectives and descriptors, or do not use standard English terms (e.g. "Garlic Aoili-Dipped Salmon Ceviche"; is this a salmon recipe or a ceviche recipe?). 

I therefore decided to create parallel scripts, one for dish exploration and one for cuisine. The 44 dishes were chosen by me to represent some common dishes that I expected would have at least 200 recipes in Yummly's database. The 25 cusines were those natively supported by Yummly. With the exception of only 32 English recipes, I was able to collect sufficient samples for both scripts. 

Initially, I attempted to query the API for all of the data using one function, but I found that the API often failed for unknown reasons. In every instance, I was able to overcome the failure by lowering the number of results per call, but this meant I was retrieving less data than optimal for some dishes and cuisines. Instead, I chose to write separate CSV files for each dish and cuisine before re-reading these CSVs into master dish_data and cuisine_data dataframes and exporting to two master CSV datafiles. 

In both instances, I converted cooking time from seconds to minutes (new column: 'timeMins'), counted the number of ingredients per recipe (new column: 'ingred_count'), converted the ingredients from a single string to a list of strings using a split/strip operation, and removed duplicate entries. 

For the cuisine_data, I dropped all entries with empty 'cuisine' fields (even though the API call should not have returned any recipes missing 'cuisine' metadata, some slipped through), while I filled in empty 'cuisine' fields with 'Unknown' for the dish_data (in which 'cuisine' is not as important).

## Data Exploration

In the course of exploration, I created several new features, including two scores for recipe uniqueness.

1. List of unique ingredients and their value counts for the given dataframe
  - Sum all ingredients, convert to Pandas dataframe, take value_counts()
2. Unique ingredient frequency. How many recipes feature 'Parmesan cheese'?
  - Ingredient frequency = (# of recipes with the ingredient) / (# of recipes)
3. Uniqueness score #1: mean of recipe ingredient frequency
  - Score #1 = (sum of recipe's unique ingredient frequencies) / (# of ingredients in the recipe)
4. Uniqueness score #2: product of recipe ingredient frequency
  - Score #2 = (product of recipe's unique ingredient frequencies)

### Uniqueness Scoring

The uniqueness scoring methods deliver broadly comparable results, but are not exactly similar. I'm still not sure which better approximates our human intuitive scoring of recipe uniqueness. For example:

- Recipe #1 with the following ingredients:
  - A, present in 90% of recipes
  - B, present in 80% of recipes
  - C, present in 1% of recipes
  - Scoring method 1 takes the mean of these frequencies: (0.9+0.8+0.01)/3 = 0.6
  - Scoring method 2 takes the product of the frequencies: (0.9*0.8*0.01) = 0.0072 

- Recipe #2 with the following ingredients:
  - D, present in 30% of recipes
  - E, present in 40% of recipes
  - F, present in 20% of recipes
  - Method 1: 0.3
  - Method 2: 0.024

By Score #1, Recipe #2 is more uncommon, whereas by Score #2, Recipe #1 is more uncommon. This demonstrates how the product of frequencies is much more sensitive to one-off ingredients (perhaps as weird garnishes).

I am still working on deciding how to use these two scoring algorithms. Perhaps take the mean of both? Or find the ones that achieve a high score on one but not the other and classify them separately?

## Data Modeling

### What Can I Make?

This is actually a fairly simple task: ask Python if every item in a recipe's ingredients list also exists in your pantry using the .issubset() method. I hope to expand this with the addition of a "What can I make if I had one more ingredient?" feature.

### Dish or Cuisine Classifier

This model takes in a recipe's ingredients, cooking times, course, or some combination of this information and predicts the cuisine or dish.

The easiest method is to find recipes with exact or similar ingredient matches, but a more complex method is to infer the cuisine or dish based on generalized characteristics (e.g. fish sauce would probably indicate Thai food).





