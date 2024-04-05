from kafka import KafkaConsumer
import os
from dotenv import load_dotenv
load_dotenv()
import json
import neomodel
from neomodel import db, DoesNotExist
from recommend_engine.models import Recipe, Chef, Tag
from utils.recommend_feed import recommend_feed_for_user



# different topics are needed for different operations on nodes and relationships

# Topics Names:

# CREATE_RECIPE: this topic is responsible for creating new recipe nodes, once a recipe is published from the recipe service.
# the function handling this topic would also creating new tag nodes representing tags of the recipe published.
# the function is also responsible for creating new chef nodes when a new recipe is created.
# the function would also be responsible for creating -[IS_TAGGED]-> relationship between the recipe and tag nodes 
# the function would also be responsible for creating -[PUBLISHED]-> relationship between the chef and the recipe

# UPDATE_CHEF_USERNAME_TOPIC: this topic is responsible for changing the username attribute of a chef node

# CHEF_LIKE_REL_RECIPE: this topic is responsible for creating the -[LIKED]-> relationship between a chef and a recipe

def consume_kafka_neo_graph_messages():
  consumer_config = {
    'bootstrap_servers': os.environ.get('UPSTASH_KAFKA_ENDPOINT'),
    'sasl_mechanism': 'SCRAM-SHA-256',
    'security_protocol': 'SASL_SSL',
    'sasl_plain_username': os.environ.get('UPSTASH_KAFKA_USERNAME'),
    'sasl_plain_password': os.environ.get('UPSTASH_KAFKA_PASSWORD'),
    'auto.offset.reset': 'latest'
  }

  # topic = None
  UPSTASH_KAFKA_CREATE_RECIPE_NODE_TOPIC = os.environ.get('UPSTASH_KAFKA_CREATE_RECIPE_NODE_TOPIC')
  UPSTASH_KAFKA_CHEF_LIKE_REL_RECIPE_TOPIC = os.environ.get('UPSTASH_KAFKA_CHEF_LIKE_REL_RECIPE_TOPIC')
  UPSTASH_KAFKA_CHEF_UNLIKE_REL_RECIPE_TOPIC = os.environ.get('UPSTASH_KAFKA_CHEF_UNLIKE_REL_RECIPE_TOPIC')
  UPSTASH_KAFKA_CHEF_USERNAME_TOPIC = os.environ.get('UPSTASH_KAFKA_CHEF_USERNAME_TOPIC')
  UPSTASH_KAFKA_REQUEST_USER_RECOMMENDATIONS_TOPIC = os.environ.get('UPSTASH_KAFKA_REQUEST_USER_RECOMMENDATIONS_TOPIC')

  topics = [ UPSTASH_KAFKA_CREATE_RECIPE_NODE_TOPIC, UPSTASH_KAFKA_CHEF_LIKE_REL_RECIPE_TOPIC, UPSTASH_KAFKA_CHEF_UNLIKE_REL_RECIPE_TOPIC, UPSTASH_KAFKA_CHEF_USERNAME_TOPIC, UPSTASH_KAFKA_REQUEST_USER_RECOMMENDATIONS_TOPIC ]

    # adding "api_version" on initialization fixes the issue "kafka.errors.NoBrokersAvailable"
  consumer = KafkaConsumer(
    # topic,
    bootstrap_servers=consumer_config['bootstrap_servers'],
    sasl_mechanism=consumer_config['sasl_mechanism'],
    security_protocol=consumer_config['security_protocol'],
    sasl_plain_username=consumer_config['sasl_plain_username'],
    sasl_plain_password=consumer_config['sasl_plain_password'],
    auto_offset_reset=consumer_config['auto.offset.reset'],
    value_deserializer=lambda m: json.loads(m.decode('ascii')),
    api_version=(0, 10, 2)
  )
  consumer.subscribe(topics)
  while True:
    # fetch and return records in batches by topic-partition by polling
    all_records = consumer.poll(timeout_ms=100, max_records=100)
    
    # for each topic, retrieve all messages in the record
    # call the functions for their respective messages
    for topic_partition, messages in all_records.items():
      if topic_partition.topic == UPSTASH_KAFKA_CREATE_RECIPE_NODE_TOPIC:
        create_nodes(messages)
      elif topic_partition.topic == UPSTASH_KAFKA_CHEF_LIKE_REL_RECIPE_TOPIC:
        chef_like_recipe(messages)
      elif topic_partition.topic == UPSTASH_KAFKA_CHEF_UNLIKE_REL_RECIPE_TOPIC:
        delete_chef_like_rel(messages)
      elif topic_partition.topic == UPSTASH_KAFKA_REQUEST_USER_RECOMMENDATIONS_TOPIC:
        recommend_feed_for_user(messages)



# function for CREATE_RECIPE topic
def create_nodes(messages):
  # topic message for creating nodes would have the value:
  # { 
  #   "recipe": <Recipe neomodel> 
  #   "chef": <Chef neomodel>
  #   "tags": [<Tag neomodel>]
  # }
  print("new message received for creating new published recipes")
  for message in messages:
    # print(message)
    message_chef_username             = message.value['chef_username']
    message_chef_first_name           = message.value['chef_first_name']
    message_chef_last_name            = message.value['chef_last_name']
    message_chef_preferences          = message.value['chef_preferences']

    message_recipe_title              = message.value['recipe_title']
    message_recipe_description        = message.value['recipe_description']
    message_recipe_ingredients        = message.value['recipe_ingredients']
    message_recipe_instructions       = message.value['recipe_instructions']
    message_recipe_preparation_time   = message.value['recipe_preparation_time']
    message_recipe_cooking_time       = message.value['recipe_cooking_time']
    message_recipe_servings           = message.value['recipe_servings']
    message_recipe_nutritional_value  = message.value['recipe_nutritional_value']
    message_published_date            = message.value['recipe_published']

    try:
      chef = Chef.nodes.get(username=message_chef_username)
    except DoesNotExist:
      chef = Chef(username=message_chef_username, first_name=message_chef_first_name, last_name=message_chef_last_name, preferences=message_chef_preferences).save()
    
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

    print("processing and creating nodes relationship")

    message_tags = message.value['tags']
    for tag in message_tags:
      try:
        tag = Tag.nodes.get(name=tag)
      except DoesNotExist:
        tag = Tag(name=tag).save()
      
      recipe.is_tagged.connect(tag)

  print("process complete")


def chef_like_recipe(messages):
  # this function is responsible for creating -[:LIKE]-> relationship between the chef(user) and the recipe they liked
  print("new message received for creating -[:LIKE]-> between chef and recipe node")

  for message in messages:
    message_chef_username = message.value['liker_username']
    message_chef_first_name = message.value['liker_first_name']
    message_chef_last_name  = message.value['liker_last_name']
    message_chef_preferences = message.value['liker_preferences']
    message_recipe_title = message.value['recipe_title']
    message_recipe_published = message.value['recipe_published']

    try:
      print(f"fetching {message_chef_username} node")
      chef = Chef.nodes.get(username=message_chef_username, first_name=message_chef_first_name, last_name=message_chef_last_name)
    except DoesNotExist:
      print("node does not exist, creating node")
      chef = Chef(username=message_chef_username, first_name=message_chef_first_name, last_name=message_chef_last_name, preferences=message_chef_preferences).save()

    recipe = Recipe.nodes.get(title=message_recipe_title, published_date=message_recipe_published)
      

    print("processing -[:LIKE]-> relationship")

    if chef.liked.is_connected(recipe):
      pass
    else:
      chef.liked.connect(recipe)
    #* on the neo4j workspace the date attribute of the LIKE relationship is not giving data properly.
    #* to see the date, try:
    #* rel = chef.liked.connect(recipe)
    #* print(rel.date)
  
  print("process complete")


def delete_chef_like_rel(messages):
  print("new message received for deleting -[:LIKE]-> between chef and recipe node")

  for message in messages:
    message_chef_username = message.value['liker_username']
    message_chef_first_name = message.value['liker_first_name']
    message_chef_last_name  = message.value['liker_last_name']
    message_recipe_title = message.value['recipe_title']
    message_recipe_published = message.value['recipe_published']

    query = " MATCH (:Chef{username: $message_chef_username, first_name: $message_chef_first_name, last_name: $message_chef_last_name})-[l: LIKED]->(:Recipe{title: $message_recipe_title, published_date: $message_recipe_published}) DELETE l "

    
    result, meta = db.cypher_query(query=query, params={ "message_chef_username": message_chef_username, "message_chef_first_name": message_chef_first_name, "message_chef_last_name": message_chef_last_name,"message_recipe_title": message_recipe_title, "message_recipe_published": message_recipe_published })
    print("LIKE relationship deleted")
    return result

  # try:
  #   for message in consumer:
      
  # except KeyboardInterrupt:
  #   pass
  # finally:
  #   consumer.close