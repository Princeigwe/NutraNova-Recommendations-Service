import json
from recommend_engine.models import Tag, Chef, Recipe
from neomodel import db, DoesNotExist
import numpy as np
from numpy.linalg import norm
from django.conf import settings


ttp = f"{settings.BASE_DIR}/utils/tags.to.preferences.json"
tag_to_preference_file = open(ttp)
tag_to_preference_file_content = tag_to_preference_file.read()

tag_to_preference_mapping = json.loads(tag_to_preference_file_content)

# this is the universal list of tags from the recipe service that is 
# used to calculate vector embeddings of both user preferences
# and recipe ratings-to-tags
#! whatever tag present in this list, must be present in the tags.to.preferences.json file, assigned to choices 

universal_tag_list = [
  "African",
  "American",
  "Anti-Cancer",
  "Anti-Inflammatory",
  "Aromatic",
  "Asian",
  "Balanced",
  "Better-Sleep",
  "Bitter",
  "Bone-Health",
  "Breakfast",
  "Citrusy",
  "Clean-Eating",
  "Creamy",
  "Dairy-Free",
  "Desserts",
  "Diabetic-Friendly",
  "Digestive",
  "Dinner",
  "Egg-Free",
  "Energy-Boosting",
  "French",
  "Fructose-Intolerance",
  "Garlic-Free",
  "Garlicky",
  "Gluten-Free",
  "Gut-Healing",
  "Heart-Healthy",
  "Herbaceous",
  "High-Fiber",
  "High-Protein",
  "Hydrating",
  "Hypertension",
  "Immunity",
  "Indian",
  "Iron-Rich",
  "Italian",
  "Kidney-Friendly",
  "Lactose-Intolerance",
  "Low-Calorie",
  "Low-Carb",
  "Low-Cholesterol",
  "Low-Fat",
  "Low-Glycemic",
  "Lunch",
  "Mediterranean",
  "Metabolism-Boosting",
  "Mexican",
  "Middle Eastern",
  "Mild",
  "Milk-Free",
  "Mind-Boosting",
  "Mobility",
  "Nut-Free",
  "Omega-3 Rich",
  "Paleo",
  "Peanut-Free",
  "Post-Workout",
  "Prebiotic",
  "Pregnancy",
  "Probiotic",
  "Salad",
  "Satiating",
  "Savoury",
  "Sesame-Free",
  "Shellfish-Free",
  "Snack",
  "Sour",
  "Soy-Free",
  "Spicy",
  "Sugar-Free",
  "Sweet",
  "Tree Nuts-Free",
  "Umami",
  "Vegan",
  "Vegetarian",
  "Vitamin-Rich",
  "Weight Management",
  "Wheat-Free"
  ]

###* the tag_data_choice is/are the choices key in the tags.to.preferences.json

def tag_to_preference_unit(chef_preference, tag_data_choice):
  """ this function calculates the presence rate of the node a chef_preference attribute to the tag_data_choice value """
  print("  ")
  print("starting new matching process")
  print(tag_data_choice)

  print("the current user preference: ",chef_preference)


  for value in tag_data_choice.values():
    tag_data_choice_value = value

  if (isinstance(chef_preference, str) and isinstance(tag_data_choice_value, str)):
    print("both tag and user preference are of string type")
    if chef_preference == tag_data_choice_value:
      unit = 1
    else:
      unit = 0
    return unit
    
  if (isinstance(tag_data_choice_value, str) and isinstance(chef_preference , list)):
    print("a tag to multiple user preference")
    if tag_data_choice_value in chef_preference:
      unit = 1
    else:
      unit = 0
    return unit
  

  if ( isinstance(chef_preference, list) and isinstance(tag_data_choice_value, list)):
    print("set preparation for both lists")
    print(chef_preference)
    print(tag_data_choice_value)
    chef_preference_set = set(chef_preference)
    tag_data_choice_set = set(tag_data_choice_value)
    print(chef_preference_set)
    print(tag_data_choice_set)
    if (chef_preference_set & tag_data_choice_set):
      print ("common element: ",chef_preference_set & tag_data_choice_set)
    else:
      print("no common elements in sets")
    unit = len( chef_preference_set.intersection(tag_data_choice_set) )
    print("intersection between chef preference and tag data choice value: ", chef_preference_set.intersection(tag_data_choice_set))
    return unit
  
  if ( isinstance(chef_preference, str) and isinstance(tag_data_choice_value, list) ):
    if chef_preference in tag_data_choice_value:
      unit = 1
    else:
      unit = 0
    return unit


def sorted_tags_list():
  #todo: uncomment this if plan does not work
  # recipe_tags = Tag.nodes.all()
  # tags_list = []
  # for recipe_tag in recipe_tags:
  #   tags_list.append(recipe_tag.name)
  # tags_list.sort()
  # print("existing tags: ", tags_list)

  #todo: remove this if plan does not work
  tags_list = universal_tag_list
  tags_list.sort()
  return tags_list

def chef_preference_to_tag_vector_embedding(username):
  ##* create a sorted list of recipe tags
  tags_list = sorted_tags_list()
  print("length of tags list for chef_pref vector embedding: ", len(tags_list))

  #* create a vector embedding of user user preferences to sorted tags
  chef = Chef.nodes.get(username=username)
  chef_preferences = chef.preferences
  print("chef preferences: ", chef_preferences)

  # the list to hold the values for vector embeddings of user preferences to tag_data_choice value
  chef_to_tags_rates = []

  ##* calculate the ratings of each tag to user preferences
  for tag in tags_list:
    if tag in tag_to_preference_mapping:
      tag_data_choice = tag_to_preference_mapping[tag]
      # print(tag_data_choice)

      if "DIETARY_PREFERENCES_CHOICES" in tag_data_choice:
        tag_data_choice == "DIETARY_PREFERENCES_CHOICES"
        chef_dietary_preference = chef_preferences["dietary_preference"]
        print(chef_dietary_preference)
        unit = tag_to_preference_unit(chef_dietary_preference, tag_data_choice)
        print("unit is: ", unit)

        chef_to_tags_rates.append(unit)
        print( "user preference feature vector: ", chef_to_tags_rates )

      elif "HEALTH_GOALS_CHOICES" in tag_data_choice:
        tag_data_choice == "HEALTH_GOALS_CHOICES"
        chef_health_goal = chef_preferences["health_goal"]
        print(chef_health_goal)
        unit = tag_to_preference_unit(chef_health_goal, tag_data_choice)
        print("unit is: ",unit)

        chef_to_tags_rates.append(unit)
        print( "user preference feature vector: ", chef_to_tags_rates )
      
      elif "ALLERGEN_CHOICES" in tag_data_choice:
        tag_data_choice == "ALLERGEN_CHOICES"
        chef_allergens = chef_preferences["allergens"] ##* chef_preferences["allergens"] is of multi-values
        chef_allergens_list = chef_allergens.split(",")
        unit = tag_to_preference_unit(chef_allergens_list, tag_data_choice)
        print("unit is: ",unit)

        # since allergens was an optional field during onboarding it process, it may have no value in processing user recommendations
        # if len(chef_allergens) == 0:
        #   print("unit for optional field is being calculated here")
        #   unit = 0
        #   print("unit for user allergen is 0")
        #   return unit
        
        # # user can have more than one allergens
        # elif "," in chef_allergens:
        #   chef_allergens_list = chef_allergens.split(",")
        #   unit = tag_to_preference_unit(chef_allergens_list, tag_data_choice)
        #   print("unit is: ",unit)
        
        # # user can have just one allergen
        # elif "," not in chef_allergens:
        #   chef_allergen = chef_allergens
        #   unit = tag_to_preference_unit(chef_allergen, tag_data_choice)

        chef_to_tags_rates.append(unit)
        print( "user preference feature vector: ", chef_to_tags_rates )
      
      elif "ACTIVITY_LEVELS" in tag_data_choice:
        chef_activity_level = chef_preferences["activity_level"]
        unit = tag_to_preference_unit(chef_activity_level, tag_data_choice)
        print("unit is: ",unit)

        chef_to_tags_rates.append(unit)
        print( "user preference feature vector: ", chef_to_tags_rates )
      
      elif "CUISINES_CHOICES" in tag_data_choice:
        tag_data_choice == "CUISINES_CHOICES"
        chef_cuisines = chef_preferences["cuisines"] ##* chef_preferences["cuisines"] is of multi-values
        chef_cuisines_list = chef_cuisines.split(",")
        unit = tag_to_preference_unit(chef_cuisines_list, tag_data_choice)
        print("unit is: ",unit)

        chef_to_tags_rates.append(unit)
        print( "user preference feature vector: ", chef_to_tags_rates )
      
      elif "MEDICAL_CONDITIONS_CHOICES" in tag_data_choice:
        tag_data_choice == "MEDICAL_CONDITIONS_CHOICES"
        chef_medical_conditions = chef_preferences["medical_conditions"] ##* chef_preferences["medical_conditions"] is of multi-values
        chef_medical_conditions_list = chef_medical_conditions.split(",")
        unit = tag_to_preference_unit(chef_medical_conditions_list, tag_data_choice)
        print("unit is: ",unit)

        chef_to_tags_rates.append(unit)
        print( "user preference feature vector: ", chef_to_tags_rates )
      
      elif "TASTE_PREFERENCES_CHOICES" in tag_data_choice:
        tag_data_choice == "TASTE_PREFERENCES_CHOICES"
        chef_taste_preferences = chef_preferences["taste_preferences"] ##* chef_preferences["taste_preferences"] is of multi-values
        chef_taste_preferences_list = chef_taste_preferences.split(",")
        unit = tag_to_preference_unit(chef_taste_preferences_list, tag_data_choice)
        print("unit is: ",unit)

        chef_to_tags_rates.append(unit)
        print( "user preference feature vector: ", chef_to_tags_rates )
      

      # ##* operation for "Vitamin-Rich" tag in the tag to preference mapping
      # if tag == "Vitamin-Rich":
      #   tag_data_choice = tag_to_preference_mapping[tag]

      #   if "TASTE_PREFERENCES_CHOICES" in tag_data_choice:
      #     chef_taste_preferences = chef_preferences["taste_preferences"] ##* chef_preferences["taste_preferences"] is of multi-values
      #     chef_taste_preferences_list = chef_taste_preferences.split(",")
      #     unit = tag_to_preference_unit(chef_taste_preferences_list, tag_data_choice)
      #     print("unit is: ",unit)

      #     chef_to_tags_rates.append(unit)
      #     print( "user preference feature vector: ", chef_to_tags_rates )
        
      #   elif "HEALTH_GOALS_CHOICES" in tag_data_choice:
      #     tag_data_choice == "HEALTH_GOALS_CHOICES"
      #     chef_health_goal = chef_preferences["health_goal"]
      #     print(chef_health_goal)
      #     unit = tag_to_preference_unit(chef_health_goal, tag_data_choice)
      #     print("unit is: ",unit)

      #     chef_to_tags_rates.append(unit)
      #     print( "user preference feature vector: ", chef_to_tags_rates )
  
    # print( "overall user preference to tags vector embedding: ", chef_to_tags_rates )
    chef_profile_vector = np.array(chef_to_tags_rates)
    print( "overall user preference to tags vector embedding: ", chef_profile_vector )
    print("user preference vector length: ", len(chef_profile_vector))
  return chef_profile_vector



def recipe_to_tag_vector_embedding(recipe):
  """this function creates a vector embedding for a recipe fetched
    to the tags
  """

  #todo: uncomment this if plan does not work
  # tags_list = sorted_tags_list()
  # tag_nodes = [ Tag.nodes.get(name=tag) for tag in tags_list ]
  # recipe_to_tags_rates = []

  # for tag_node in tag_nodes:
  #   if recipe.is_tagged.is_connected(tag_node):
  #     unit = 1
  #   else:
  #     unit = 0
  #   recipe_to_tags_rates.append(unit)
  # return recipe_to_tags_rates

  # todo: remove this if plan does not work
  tags_list = sorted_tags_list()
  print("length of tags list for recipe vector embedding: ", len(tags_list))
  recipe_to_tags_rates = []
  for name in tags_list:
    try:
      tag_node = Tag.nodes.get(name=name)
      if recipe.is_tagged.is_connected(tag_node):
        unit = 1
      else:
        unit = 0
      recipe_to_tags_rates.append(unit)
    except DoesNotExist:
      unit = 0
      recipe_to_tags_rates.append(unit)
  
  print(f"length of {recipe.title} vector: ", len(recipe_to_tags_rates))
  return recipe_to_tags_rates






# todo: for now, all recipes nodes are fetched, but later on fetch a few based on when they were recently published
def recipe_to_tag_embeddings():
  recipes = Recipe.nodes.all()
  recipe_to_tags_vectors = []
  for recipe in recipes:
    recipe_to_tags_rating = recipe_to_tag_vector_embedding(recipe)
    recipe_to_tags_vector = np.array(recipe_to_tags_rating)
    print(f"Vector embedding for {recipe.title} on {recipe.published_date}: ", recipe_to_tags_vector)
    # recipe_to_tags_vectors.append(recipe_to_tags_vector)
    recipe_vector_data = {
      "recipe_title": recipe.title,
      "recipe_published_date": recipe.published_date,
      "recipe_to_tag_vector": recipe_to_tags_vector
    }
    # recipe_to_tags_vectors.append(recipe_to_tags_vector)
    recipe_to_tags_vectors.append(recipe_vector_data)
  
  print(" ")
  print("overall recipe to tags vector embeddings: ", recipe_to_tags_vectors)
  return recipe_to_tags_vectors


def cosine_similarities_for_chef_preference(username):
  chef_preference_vector = chef_preference_to_tag_vector_embedding(username)
  recipe_vectors = recipe_to_tag_embeddings()
  recipe_cosine_similarities = []
  print("chef_vector: ", chef_preference_vector)
  print("recipe vectors: ", recipe_vectors)
  for recipe_vector in recipe_vectors:
    recipe_vector_cosine_similarity = np.dot(recipe_vector["recipe_to_tag_vector"], chef_preference_vector) / ( norm(recipe_vector["recipe_to_tag_vector"]) * norm(chef_preference_vector) )
    print("cosine similarity: ", recipe_vector_cosine_similarity)
    user_preference_recipe_cosine_similarity = {
      "recipe_title": recipe_vector["recipe_title"],
      "recipe_published_date": recipe_vector["recipe_published_date"],
      "recipe_cos_similarity": recipe_vector_cosine_similarity
    }
    recipe_cosine_similarities.append(user_preference_recipe_cosine_similarity)

    # arrange recipes based on highest cosine similarity
    sorted_recipe_cosine_similarities = sorted(recipe_cosine_similarities, key=lambda x: x['recipe_cos_similarity'], reverse=True)
    print(sorted_recipe_cosine_similarities)
  
  return sorted_recipe_cosine_similarities

