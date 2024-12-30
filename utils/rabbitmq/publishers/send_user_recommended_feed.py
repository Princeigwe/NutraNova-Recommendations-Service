import logging
import json
from pika.exceptions import AMQPError
from utils.rabbitmq.channels.publish_user_recommended_feed_channel import channel
import os

exchange_name=os.environ.get('CLOUDAMQP_FANOUT_EXCHANGE')


def send_user_recommended_feed(message: dict):
  try:
    channel.basic_publish(exchange=exchange_name, routing_key='', body=json.dumps(message)) # publishing to fanout exchange
    print ("[RabbitMQ]: user recommendations feed message sent")
  except AMQPError as e:
    logging.exception(e)