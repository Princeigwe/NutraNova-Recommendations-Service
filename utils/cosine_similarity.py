import json
from recommend_engine.models import Tag, Chef
import numpy as np

# tag_to_preference_mapping = open("tags.to.preferences.json", "r")
## todo: research the correct format for finding the path of the tags.to.preferences.json file
tag_to_preference_file = open("/home/princeigwe/NutraNova-Services/Recommendations-Service/utils/tags.to.preferences.json")
tag_to_preference_file_content = tag_to_preference_file.read()

# tag_to_preference_mapping = json.loads(tag_to_preference_file)
tag_to_preference_mapping = json.loads(tag_to_preference_file_content)

###* the tag_data_choice are the is/are the choices key in the tags.to.preferences.json

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


def sorted_tags_list():
  recipe_tags = Tag.nodes.all()
  tags_list = []
  for recipe_tag in recipe_tags:
    tags_list.append(recipe_tag.name)
  tags_list.sort()
  print(tags_list)
  return tags_list

def chef_preference_to_tag_vector_embedding(username):
  ##* create a sorted list of recipe tags
  tags_list = sorted_tags_list()
  
  #* create a vector embedding of user user preferences to sorted tags
  chef = Chef.nodes.get(username=username)
  chef_preferences = chef.preferences
  print(chef_preferences)

  # the list to hold the values for vector embeddings of user preferences to tag_data_choice value
  recipe_tags_rates = []

  ##* calculate the ratings of each tag to user preferences
  for tag in tags_list:
    if tag in tag_to_preference_mapping:
      tag_data_choice = tag_to_preference_mapping[tag]
      print(tag_data_choice)

      if "DIETARY_PREFERENCES_CHOICES" in tag_data_choice:
        tag_data_choice == "DIETARY_PREFERENCES_CHOICES"
        chef_dietary_preference = chef_preferences["dietary_preference"]
        print(chef_dietary_preference)
        unit = tag_to_preference_unit(chef_dietary_preference, tag_data_choice)
        print("unit is: ", unit)

        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )

      elif "HEALTH_GOALS_CHOICES" in tag_data_choice:
        tag_data_choice == "HEALTH_GOALS_CHOICES"
        chef_health_goal = chef_preferences["health_goal"]
        print(chef_health_goal)
        unit = tag_to_preference_unit(chef_health_goal, tag_data_choice)
        print("unit is: ",unit)

        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      elif "ALLERGEN_CHOICES" in tag_data_choice:
        tag_data_choice == "ALLERGEN_CHOICES"
        chef_allergens = chef_preferences["allergens"] ##* chef_preferences["allergens"] is of multi-values
        chef_allergens_list = chef_allergens.split(",")
        unit = tag_to_preference_unit(chef_allergens_list, tag_data_choice)
        print("unit is: ",unit)

        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      elif "ACTIVITY_LEVELS" in tag_data_choice:
        chef_activity_level = chef_preferences["activity_level"]
        unit = tag_to_preference_unit(chef_activity_level, tag_data_choice)
        print("unit is: ",unit)

        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      elif "CUISINES_CHOICES" in tag_data_choice:
        tag_data_choice == "CUISINES_CHOICES"
        chef_cuisines = chef_preferences["cuisines"] ##* chef_preferences["cuisines"] is of multi-values
        chef_cuisines_list = chef_cuisines.split(",")
        unit = tag_to_preference_unit(chef_cuisines_list, tag_data_choice)
        print("unit is: ",unit)

        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      elif "MEDICAL_CONDITIONS_CHOICES" in tag_data_choice:
        tag_data_choice == "MEDICAL_CONDITIONS_CHOICES"
        chef_medical_conditions = chef_preferences["medical_conditions"] ##* chef_preferences["medical_conditions"] is of multi-values
        chef_medical_conditions_list = chef_medical_conditions.split(",")
        unit = tag_to_preference_unit(chef_medical_conditions_list, tag_data_choice)
        print("unit is: ",unit)

        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      elif "TASTE_PREFERENCES_CHOICES" in tag_data_choice:
        tag_data_choice == "TASTE_PREFERENCES_CHOICES"
        chef_taste_preferences = chef_preferences["taste_preferences"] ##* chef_preferences["taste_preferences"] is of multi-values
        chef_taste_preferences_list = chef_taste_preferences.split(",")
        unit = tag_to_preference_unit(chef_taste_preferences_list, tag_data_choice)
        print("unit is: ",unit)

        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
  
    # print( "overall user preference to tags vector embedding: ", recipe_tags_rates )
    chef_profile_vector = np.array(recipe_tags_rates)
    print( "overall user preference to tags vector embedding: ", chef_profile_vector )



