import os
from dotenv import load_dotenv
load_dotenv()
import json
import neomodel
from neomodel import db, DoesNotExist
from recommend_engine.models import Chef, Recipe, Tag
import os


rabbitmq_message_type = os.environ.get('RECIPE_PUBLISHED_MESSAGE_TYPE')


def create_nodes(message):
  message_chef_username             = message['chef_username']
  message_chef_first_name           = message['chef_first_name']
  message_chef_last_name            = message['chef_last_name']
  message_chef_preferences          = message['chef_preferences']

  message_recipe_title              = message['recipe_title']
  message_recipe_description        = message['recipe_description']
  message_recipe_ingredients        = message['recipe_ingredients']
  message_recipe_instructions       = message['recipe_instructions']
  message_recipe_preparation_time   = message['recipe_preparation_time']
  message_recipe_cooking_time       = message['recipe_cooking_time']
  message_recipe_servings           = message['recipe_servings']
  message_recipe_nutritional_value  = message['recipe_nutritional_value']
  message_published_date            = message['recipe_published']
    
  try:
    chef = Chef.nodes.get(username=message_chef_username)

    recipe = Recipe(
    title             = message_recipe_title, 
    description       = message_recipe_description, 
    ingredients       = message_recipe_ingredients, 
    instructions      = message_recipe_instructions, 
    preparation_time  = message_recipe_preparation_time, 
    cooking_time      = message_recipe_cooking_time, 
    servings          = message_recipe_servings, 
    nutritional_value = message_recipe_nutritional_value,
    published_date    = message_published_date
    ).save()
    chef.published.connect(recipe)

    print("processing and creating published nodes relationships")

    message_tags = message['tags']
    for tag in message_tags:
      try:
        tag = Tag.nodes.get(name=tag)
      except DoesNotExist:
        tag = Tag(name=tag).save()
      
      recipe.is_tagged.connect(tag)

    print("process complete")
  except DoesNotExist:
    pass


  # print("processing and creating published nodes relationships")

  # message_tags = message['tags']
  # for tag in message_tags:
  #   try:
  #     tag = Tag.nodes.get(name=tag)
  #   except DoesNotExist:
  #     tag = Tag(name=tag).save()
    
  #   recipe.is_tagged.connect(tag)

  # print("process complete")
  