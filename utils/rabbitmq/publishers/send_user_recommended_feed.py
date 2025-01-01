import logging
import json
from pika.exceptions import AMQPError
from utils.rabbitmq.channels.publishing_channel import channel
import os

stream_name=os.environ.get('RABBITMQ_STREAM')


def send_user_recommended_feed(message: dict):
  try:
    channel.basic_publish(exchange='', routing_key=stream_name, body=json.dumps(message))
    print (f"[RabbitMQ]: user recommendations feed message sent with message type: {message['type']}")
  except AMQPError as e:
    logging.exception(e)