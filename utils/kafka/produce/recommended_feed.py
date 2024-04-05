from kafka.errors import KafkaError
import logging
import os
from dotenv import load_dotenv
load_dotenv()
from utils.kafka import kafka_config


topic = os.environ.get('UPSTASH_KAFKA_SEND_USER_RECOMMENDATIONS_TOPIC')
if type(topic) == bytes:
  topic = topic.decode('utf-8')

def send_user_recommended_feed(message:dict):
  future = kafka_config.producer.send(topic, message)

  try:
    metadata = future.get()
    print(metadata)
    print("user recommendations feed message sent")
  except KafkaError as e:
    logging.exception(e)