import os
from dotenv import load_dotenv
load_dotenv()
import json
import neomodel
from neomodel import db, DoesNotExist
from recommend_engine.models import Chef, Recipe, Tag
import os


def chef_vote_recipe(message):
  message_chef_username = message['voter_username']
  message_chef_first_name = message['voter_first_name']
  message_chef_last_name  = message['voter_last_name']
  message_chef_preferences = message['voter_preferences']
  message_vote_type = message['vote_type']
  message_recipe_title = message['recipe_title']
  message_recipe_published = message['recipe_published']

  try:
      print(f"fetching {message_chef_username} node")
      chef = Chef.nodes.get(username=message_chef_username, first_name=message_chef_first_name, last_name=message_chef_last_name)
  except DoesNotExist:
      print("node does not exist, creating node")
      chef = Chef(username=message_chef_username, first_name=message_chef_first_name, last_name=message_chef_last_name, preferences=message_chef_preferences).save()

  recipe = Recipe.nodes.get(title=message_recipe_title, published_date=message_recipe_published)
      

  if message_vote_type == "UP_VOTED":
      print("processing -[:UP_VOTED]-> relationship")
      if chef.up_voted.is_connected(recipe):
        pass
      else:
        chef.up_voted.connect(recipe)
  elif message_vote_type == "DOWN_VOTED":
      print("processing -[:DOWN_VOTED]-> relationship")
      if chef.down_voted.is_connected(recipe):
        pass
      else:
        chef.down_voted.connect(recipe)

    #* on the neo4j workspace the date attribute of the UP_VOTED or DOWN_VOTED relationship is not giving data properly.
    #* to see the date, try:
    #* rel = chef.up_voted.connect(recipe)
    #* print(rel.date)
  
  print("process complete")

