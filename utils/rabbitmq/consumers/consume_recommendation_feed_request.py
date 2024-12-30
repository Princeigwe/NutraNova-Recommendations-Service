import logging
import os
from dotenv import load_dotenv
load_dotenv()
from utils.recommend_feed import recommend_feed_for_existing_user
import json

from utils.rabbitmq.channels.consume_recommendation_feed_request_channel import channel

rabbitmq_message_type = os.environ.get('REQUEST_RECOMMENDED_FEED_MESSAGE_TYPE')
exchange_name=os.environ.get('CLOUDAMQP_FANOUT_EXCHANGE')

# creating and bnding queue to fanout exchange
queue = os.environ.get('CLOUDAMQP_RECOMMENDATION_FEED_REQUEST_QUEUE')
result = channel.queue_declare(queue=queue, durable=True)
channel.queue_bind(exchange=exchange_name, queue=result.method.queue)

def consume_recommend_feed_request(message):
  if message['type'] == rabbitmq_message_type:
    recommend_feed_for_existing_user(message)


def callback(ch, method, properties, body):
  body = json.loads(body)
  consume_recommend_feed_request(body)


def consume():
  channel.basic_qos(prefetch_count=100) # setting the maximum number of in-progress mesesages to 100
  channel.basic_consume(queue, callback)
  channel.start_consuming()