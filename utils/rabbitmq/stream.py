import os
from .channels.consuming_channel import channel
from .consumers.consume_chef_data import consume_and_update_chef_node_data
from .consumers.consume_published_recipe import create_nodes
from .consumers.consume_recommendation_feed_request import consume_recommend_feed_request
from .consumers.consume_recipe_vote import chef_vote_recipe
from django.conf import settings
from utils.neomodel_rabbitmq_neo4j_operations import add_consumed_rabbitmq_user_message_id, add_consumed_rabbitmq_recipe_message_id
import json

# stream declaration
stream_name=os.environ.get('RABBITMQ_STREAM')

channel.queue_declare(queue=stream_name, durable=True, arguments={
  "x-queue-type": "stream", 
  "x-max-age": "1D",
  "x-max-length-bytes": 5000000, 
  "x-stream-max-segment-size-bytes":5000
  }) 

chef_data_update_message_type = os.environ.get('CHEF_DATA_UPDATE_MESSAGE_TYPE')
recipe_published_message_type = os.environ.get('RECIPE_PUBLISHED_MESSAGE_TYPE')
recommendation_feed_request_message_type = os.environ.get('REQUEST_RECOMMENDED_FEED_MESSAGE_TYPE')
vote_recipe_message_type = os.environ.get('VOTE_RECIPE_MESSAGE_TYPE')

def stream_message(message):
  if message['type'] == chef_data_update_message_type:
    consumed_rabbitmq_user_data_message_ids = settings.RABBITMQ_USER_MESSAGE_IDS
    if message['message_id'] not in consumed_rabbitmq_user_data_message_ids:
      print("Consuming user data rabbitmq message...")
      consume_and_update_chef_node_data(message)
      add_consumed_rabbitmq_user_message_id(message['message_id'], message['created_at']) # insert the consumed message id in the custom rabbitmq user message id node
    else:
      print("Message already consumed")

  elif message['type'] == recipe_published_message_type:
    consumed_rabbitmq_recipe_message_ids = settings.RABBITMQ_RECIPE_MESSAGE_IDS
    if message['message_id'] not in consumed_rabbitmq_recipe_message_ids:
      print("Consuming published recipe rabbitmq message...")
      create_nodes(message)
      add_consumed_rabbitmq_recipe_message_id(message['message_id'], message['created_at'])
    else:
      print("Message already consumed")

  elif message['type'] == recommendation_feed_request_message_type:
    if message['message_id'] not in settings.RABBITMQ_RECIPE_MESSAGE_IDS:
      print("Consuming recommendation feed request rabbitmq message...")
      consume_recommend_feed_request(message)
      add_consumed_rabbitmq_recipe_message_id(message['message_id'], message['created_at'])
    else:
      print("Message already consumed")
    # consume_recommend_feed_request(message)

  elif message['type'] == vote_recipe_message_type:
    if message['message_id'] not in settings.RABBITMQ_RECIPE_MESSAGE_IDS:
      print("Consuming recipe vote rabbitmq message...")
      chef_vote_recipe(message)
      add_consumed_rabbitmq_recipe_message_id(message['message_id'], message['created_at'])
    else:
      print("Message already consumed")



# def callback(ch, method, properties, body):
#   body = json.loads(body)
#   stream_message(body)

def callback(channel, method_frame, header_frame, body):
  number_of_ackd_message = 0

  # Getting the delivery tag of the current message
  latest_delivery_tag = method_frame.delivery_tag

  body = json.loads(body)
  stream_message(body)

  channel.basic_ack(latest_delivery_tag)

def consume():
  channel.basic_qos(prefetch_count=100) # setting the maximum number of in-progress mesesages to 100
  channel.basic_consume(stream_name, callback, arguments={"x-stream-offset": "first"})
  channel.start_consuming()