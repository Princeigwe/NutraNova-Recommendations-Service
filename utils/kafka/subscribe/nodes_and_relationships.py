from kafka import KafkaConsumer
import os
from dotenv import load_dotenv
load_dotenv()
import json
import neomodel
from neomodel import db, DoesNotExist
from recommend_engine.models import Recipe, Chef, Tag
from utils.recommend_feed import recommend_feed_for_existing_user


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
  UPSTASH_KAFKA_CHEF_VOTE_RECIPE_REL_TOPIC = os.environ.get('UPSTASH_KAFKA_CHEF_VOTE_RECIPE_REL_TOPIC')
  UPSTASH_KAFKA_REQUEST_USER_RECOMMENDATIONS_TOPIC = os.environ.get('UPSTASH_KAFKA_REQUEST_USER_RECOMMENDATIONS_TOPIC')
  UPSTASH_KAFKA_USER_DATA_UPDATE_TOPIC = os.environ.get('UPSTASH_KAFKA_USER_DATA_UPDATE_TOPIC')


  topics = [ UPSTASH_KAFKA_CREATE_RECIPE_NODE_TOPIC, UPSTASH_KAFKA_CHEF_VOTE_RECIPE_REL_TOPIC, UPSTASH_KAFKA_USER_DATA_UPDATE_TOPIC, UPSTASH_KAFKA_REQUEST_USER_RECOMMENDATIONS_TOPIC ]

    # adding "api_version" on initialization fixes the issue "kafka.errors.NoBrokersAvailable"
  consumer = KafkaConsumer(
    # topic,
    bootstrap_servers=consumer_config['bootstrap_servers'],
    sasl_mechanism=consumer_config['sasl_mechanism'],
    security_protocol=consumer_config['security_protocol'],
    sasl_plain_username=consumer_config['sasl_plain_username'],
    sasl_plain_password=consumer_config['sasl_plain_password'],
    auto_offset_reset="latest",
    group_id="recommendation_relation",
    auto_commit_interval_ms=1000,
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
      elif topic_partition.topic == UPSTASH_KAFKA_CHEF_VOTE_RECIPE_REL_TOPIC:
        chef_vote_recipe(messages)
      # elif topic_partition.topic == UPSTASH_KAFKA_REQUEST_USER_RECOMMENDATIONS_TOPIC:
      #   recommend_feed_for_existing_user(messages)
      elif topic_partition.topic == UPSTASH_KAFKA_USER_DATA_UPDATE_TOPIC:
        update_chef_node_data(messages)



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


def chef_vote_recipe(messages):

  for message in messages:
    message_chef_username = message.value['voter_username']
    message_chef_first_name = message.value['voter_first_name']
    message_chef_last_name  = message.value['voter_last_name']
    message_chef_preferences = message.value['voter_preferences']
    message_vote_type = message.value['vote_type']
    message_recipe_title = message.value['recipe_title']
    message_recipe_published = message.value['recipe_published']

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


def update_chef_node_data(messages):
  for message in messages:
    try:
      print(f"Received message: {message.value}")

      # checking if 'old_username' key is in kafka message. this handles the operation for just updating the username of the Chef node
      if 'old_username' in message.value:
        chef = Chef.nodes.get(username=message.value['old_username'])
        chef.username = message.value['new_username']
        chef.save()
        print(f"{chef.first_name} username is now {chef.username}")
      
      # this is a response operation for the 'updateProfile' resolver in the user microservice
      else:
        chef = Chef.nodes.get(username=message.value['username'])
        chef.first_name = message.value['first_name'] if 'first_name' in message.value else chef.first_name
        chef.last_name = message.value['last_name'] if 'last_name' in message.value else chef.last_name
        chef.preferences = message.value['preferences'] if 'preferences' in message.value else chef.preferences
        chef.save()
        print(f"{chef.username} data updated")
      

    except DoesNotExist:
      pass
      # chef = Chef(username=message.value['username'] if 'username' in message.value else message.value['new_username'], first_name=message.value['first_name'], last_name=message.value['last_name'], preferences=message.value['preferences']).save()

    except KeyboardInterrupt:
      pass

  # try:
  #   for message in consumer:
      
  # except KeyboardInterrupt:
  #   pass
  # finally:
  #   consumer.close