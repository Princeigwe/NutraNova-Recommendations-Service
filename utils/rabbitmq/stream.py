import os
from .channels.consuming_channel import channel
from .consumers.consume_chef_data import consume_and_update_chef_node_data
from .consumers.consume_published_recipe import create_nodes
from .consumers.consume_recommendation_feed_request import consume_recommend_feed_request
from .consumers.consume_recipe_vote import chef_vote_recipe
import json

# stream declaration
stream_name=os.environ.get('RABBITMQ_STREAM')
channel.queue_declare(queue=stream_name, durable=True, arguments={"x-queue-type": "stream"})

chef_data_update_message_type = os.environ.get('CHEF_DATA_UPDATE_MESSAGE_TYPE')
recipe_published_message_type = os.environ.get('RECIPE_PUBLISHED_MESSAGE_TYPE')
recommendation_feed_request_message_type = os.environ.get('REQUEST_RECOMMENDED_FEED_MESSAGE_TYPE')
vote_recipe_message_type = os.environ.get('VOTE_RECIPE_MESSAGE_TYPE')

def stream_message(message):
  if message['type'] == chef_data_update_message_type:
    consume_and_update_chef_node_data(message)
  elif message['type'] == recipe_published_message_type:
    create_nodes(message)
  elif message['type'] == recommendation_feed_request_message_type:
    consume_recommend_feed_request(message)
  elif message['type'] == vote_recipe_message_type:
    chef_vote_recipe(message)


def callback(ch, method, properties, body):
  body = json.loads(body)
  stream_message(body)


def consume():
  channel.basic_qos(prefetch_count=100) # setting the maximum number of in-progress mesesages to 100
  channel.basic_consume(stream_name, callback, arguments={"x-stream-offset": "first"})
  channel.start_consuming()