from kafka import KafkaConsumer
import os
from dotenv import load_dotenv
load_dotenv()
import json
import neomodel
from neomodel import db, DoesNotExist
from recommend_engine.models import Recipe, Chef, Tag



# different topics are needed for different operations on nodes and relationships

# Topics Names:

# CREATE_RECIPE: this topic is responsible for creating new recipe nodes, once a recipe is published from the recipe service.
# the function handling this topic would also creating new tag nodes representing tags of the recipe published.
# the function is also responsible for creating new chef nodes when a new recipe is created.
# the function would also be responsible for creating -[IS_TAGGED]-> relationship between the recipe and tag nodes 
# the function would also be responsible for creating -[PUBLISHED]-> relationship between the chef and the recipe

# UPDATE_CHEF_USERNAME_TOPIC: this topic is responsible for changing the username attribute of a chef node

# CHEF_LIKE_REL_RECIPE: this topic is responsible for creating the -[LIKED]-> relationship between a chef and a recipe
# CHEF_UNLIKE_REL_RECIPE: this topic is responsible for creating the -[UN_LIKED]-> relationship between a chef and a recipe

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

  topics = [ UPSTASH_KAFKA_CREATE_RECIPE_NODE_TOPIC, UPSTASH_KAFKA_CHEF_LIKE_REL_RECIPE_TOPIC, UPSTASH_KAFKA_CHEF_UNLIKE_REL_RECIPE_TOPIC, UPSTASH_KAFKA_CHEF_USERNAME_TOPIC ]

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



# function for CREATE_RECIPE topic
def create_nodes(messages):
  # topic message for creating nodes would have the value:
  # { 
  #   "recipe": <Recipe neomodel> 
  #   "chef": <Chef neomodel>
  #   "tags": [<Tag neomodel>]
  # }


  for message in messages:
    # print(message)
    message_chef_username             = message.value['chef_username']
    message_chef_first_name           = message.value['chef_first_name']
    message_chef_last_name            = message.value['chef_last_name']
    message_recipe_title              = message.value['recipe_title']
    message_recipe_description        = message.value['recipe_description']
    message_recipe_ingredients        = message.value['recipe_ingredients']
    message_recipe_instructions       = message.value['recipe_instructions']
    message_recipe_preparation_time   = message.value['recipe_preparation_time']
    message_recipe_cooking_time       = message.value['recipe_cooking_time']
    message_recipe_servings           = message.value['recipe_servings']
    message_recipe_nutritional_value  = message.value['recipe_nutritional_value']

    chef = Chef(username=message_chef_username, first_name=message_chef_first_name, last_name=message_chef_last_name).save()
    recipe = Recipe(title=message_recipe_title, description=message_recipe_description, ingredients=message_recipe_ingredients, instructions=message_recipe_instructions, preparation_time=message_recipe_preparation_time, cooking_time=message_recipe_cooking_time, servings=message_recipe_servings, nutritional_value=message_recipe_nutritional_value).save()

    chef.published.connect(recipe)
  ##################################
    # query = """
    #           merge (chef :Chef{ username: $message_chef_username, first_name: $message_chef_first_name, last_name: $message_chef_last_name}),
    #                 (recipe :Recipe{ title: $message_recipe_title, description: $message_recipe_description, ingredients: $message_recipe_ingredients, instructions: $message_recipe_instructions, preparation_time: $message_recipe_preparation_time, cooking_time: $message_recipe_cooking_time, servings: $message_recipe_servings, nutritional_value: $message_recipe_nutritional_value })
    #           create (chef)-[:PUBLISHED]->(recipe);
    #         """
    # chef_and_recipe, meta = db.cypher_query(
    #   query=query,
    #   params={
    #     "message_chef_username"             : message_chef_username,
    #     "message_chef_first_name"           : message_chef_first_name,
    #     "message_chef_last_name"            : message_chef_last_name,
    #     "message_recipe_title"              : message_recipe_title,
    #     "message_recipe_description"        : message_recipe_description,
    #     "message_recipe_ingredients"        : message_recipe_ingredients,
    #     "message_recipe_instructions"       : message_recipe_instructions,
    #     "message_recipe_preparation_time"   : message_recipe_preparation_time,
    #     "message_recipe_cooking_time"       : message_recipe_cooking_time,
    #     "message_recipe_servings"           : message_recipe_servings,
    #     "message_recipe_nutritional_value"  : message_recipe_nutritional_value
    #   }
    # )
    ############################
    message_tags = message.value['tags']
    for tag in message_tags:
      try:
        tag = Tag.nodes.get(name=tag)
      except DoesNotExist:
        tag = Tag(name=tag).save()
        recipe.is_tagged.connect(tag)



  # try:
  #   for message in consumer:
      
  # except KeyboardInterrupt:
  #   pass
  # finally:
  #   consumer.close