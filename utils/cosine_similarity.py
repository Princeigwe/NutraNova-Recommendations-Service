import json
from recommend_engine.models import Tag, Chef

# tag_to_preference_mapping = open("tags.to.preferences.json", "r")
tag_to_preference_file = open("/home/princeigwe/NutraNova-Services/Recommendations-Service/utils/tags.to.preferences.json")
tag_to_preference_file_content = tag_to_preference_file.read()

# tag_to_preference_mapping = json.loads(tag_to_preference_file)
tag_to_preference_mapping = json.loads(tag_to_preference_file_content)

###* the tag_data_choice are the is/are the choices key in the tags.to.preferences.json

# def tag_to_preference_unit(chef_preference, tag, tag_data_choice):
def tag_to_preference_unit(chef_preference, tag_data_choice):
  print("lljl")
  print(tag_data_choice)

  
  # if chef_preference == tag_data_choice:
  #   unit = 1
  # else:
  #   unit = 0
  # return unit
  for value in tag_data_choice.values():
    tag_data_choice_value = value
  if (isinstance(chef_preference, str) and isinstance(tag_data_choice_value, str)):
    if chef_preference == tag_data_choice_value:
      unit = 1
    else:
      unit = 0
    return unit
    
  # elif ( isinstance(chef_preference, str) and isinstance(tag_data_choice_value, list)):
  #   if chef_preference in tag_data_choice_value:
  #     unit = 1
  #   else:
  #     unit = 0
  #   return unit
    
  elif "," in chef_preference:
    print("the preference: ...",chef_preference)
    chef_preference_list = chef_preference.split(",")
    print("set: preparation")
    print(chef_preference_list)
    print(tag_data_choice_value)
    if ( isinstance(chef_preference_list, list) and isinstance(tag_data_choice_value, list)):
      chef_preference_set = set(chef_preference_list)
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
  # elif ( isinstance(chef_preference, list) and isinstance(tag_data_choice_value, list)):
  #     chef_preference_set = set(chef_preference)
  #     tag_data_choice_set = set(tag_data_choice_value)
  #     unit = len( chef_preference_set.intersection(tag_data_choice_set) )
  #     return unit



def chef_preference_to_tag_vector_embedding(username):
  ##* create a sorted list of recipe tags
  recipe_tags = Tag.nodes.all()
  tags_list = []
  for recipe_tag in recipe_tags:
    tags_list.append(recipe_tag.name)
  tags_list.sort()
  print(tags_list)

  ##* create a vector embedding of user user preferences to sorted tags
  chef = Chef.nodes.get(username=username)
  chef_preferences = chef.preferences
  print(chef_preferences)
  # list of how each tag is rated based on user preferences
  recipe_tags_rates = []

  ##* calculate the ratings of each tag to user preferences
  for tag in tags_list:
    if tag in tag_to_preference_mapping:
      tag_data_choice = tag_to_preference_mapping[tag]
      print(tag_data_choice)

      # if "DIETARY_PREFERENCES_CHOICES" in tag:
      if "DIETARY_PREFERENCES_CHOICES" in tag_data_choice:
        tag_data_choice == "DIETARY_PREFERENCES_CHOICES"
        chef_dietary_preference = chef_preferences["dietary_preference"]
        print(chef_dietary_preference)
        #* calculate average presence rate of the node chef_dietary_preference in the tag_preference_data value
        # tag_to_preference_unit(chef_dietary_preference, tag, tag_data_choice)
        unit = tag_to_preference_unit(chef_dietary_preference, tag_data_choice)
        print("unit is: ", unit)

        #* append the average preference rate to the recipe_tags_rates list
        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )

      # elif "HEALTH_GOALS_CHOICES" in tag:
      elif "HEALTH_GOALS_CHOICES" in tag_data_choice:
        tag_data_choice == "HEALTH_GOALS_CHOICES"
        chef_health_goal = chef_preferences["health_goal"]
        print(chef_health_goal)
        #* calculate average presence rate of the node chef_health_goal in the tag_preference_data value
        # unit = tag_to_preference_unit(chef_health_goal, tag, tag_data_choice)
        unit = tag_to_preference_unit(chef_health_goal, tag_data_choice)
        print("unit is: ",unit)


        #* append the average preference rate to the recipe_tags_rates list
        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      # elif "ALLERGEN_CHOICES" in tag:
      elif "ALLERGEN_CHOICES" in tag_data_choice:
        tag_data_choice == "ALLERGEN_CHOICES"
        chef_allergens = chef_preferences["allergens"] # chef_preferences["allergens"] is a list data type
        #* calculate average presence rate of the node chef_allergens in the tag_preference_data value
        # tag_to_preference_unit(chef_allergens, tag, tag_data_choice)
        # unit = tag_to_preference_unit(chef_allergens, tag, tag_data_choice)
        unit = tag_to_preference_unit(chef_allergens, tag_data_choice)
        print("unit is: ",unit)

        #* append the average preference rate to the recipe_tags_rates list
        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      # elif "ACTIVITY_LEVELS" in tag:
      elif "ACTIVITY_LEVELS" in tag_data_choice:
        chef_activity_level = chef_preferences["activity_level"]
        #* calculate average presence rate of the node chef_activity_level in the tag_preference_data value
        # tag_to_preference_unit(chef_activity_level, tag, tag_data_choice)
        # unit = tag_to_preference_unit(chef_activity_level, tag, tag_data_choice)
        unit = tag_to_preference_unit(chef_activity_level, tag_data_choice)
        print("unit is: ",unit)

        #* append the average preference rate to the recipe_tags_rates list
        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      # elif "CUISINES_CHOICES" in tag:
      elif "CUISINES_CHOICES" in tag_data_choice:
        tag_data_choice == "CUISINES_CHOICES"
        chef_cuisines = chef_preferences["cuisines"] # chef_preferences["cuisines"] is a list data type
        #* calculate average presence rate of the node chef_cuisines in the tag_preference_data value
        # tag_to_preference_unit(chef_cuisines, tag, tag_data_choice)
        # unit = tag_to_preference_unit(chef_cuisines, tag, tag_data_choice)
        unit = tag_to_preference_unit(chef_cuisines, tag_data_choice)
        print("unit is: ",unit)

        #* append the average preference rate to the recipe_tags_rates list
        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      # elif "MEDICAL_CONDITIONS_CHOICES" in tag:
      elif "MEDICAL_CONDITIONS_CHOICES" in tag_data_choice:
        tag_data_choice == "MEDICAL_CONDITIONS_CHOICES"
        chef_medical_conditions = chef_preferences["medical_conditions"] # chef_preferences["medical_conditions"] is a list data type
        #* calculate average presence rate of the node chef_medical_conditions in the tag_preference_data value
        # tag_to_preference_unit(chef_medical_conditions, tag, tag_data_choice)
        # unit = tag_to_preference_unit(chef_medical_conditions, tag, tag_data_choice)
        unit = tag_to_preference_unit(chef_medical_conditions, tag_data_choice)
        print("unit is: ",unit)

        #* append the average preference rate to the recipe_tags_rates list
        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
      
      # elif "TASTE_PREFERENCES_CHOICES" in tag:
      elif "TASTE_PREFERENCES_CHOICES" in tag_data_choice:
        tag_data_choice == "TASTE_PREFERENCES_CHOICES"
        chef_taste_preferences = chef_preferences["taste_preferences"] # chef_preferences["taste_preferences"] is a list data type
        #* calculate average presence rate of the node chef_taste_preferences in the tag_preference_data value
        # tag_to_preference_unit(chef_taste_preferences, tag, tag_data_choice)
        # unit = tag_to_preference_unit(chef_taste_preferences, tag, tag_data_choice)
        unit = tag_to_preference_unit(chef_taste_preferences, tag_data_choice)
        print("unit is: ",unit)

        #* append the average preference rate to the recipe_tags_rates list
        recipe_tags_rates.append(unit)
        print( "user preference feature vector: ", recipe_tags_rates )
  
    print( "user preference feature vector: ", recipe_tags_rates )



