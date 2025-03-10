from threading import Thread
from utils.rabbitmq.consumers.consume_recommendation_feed_request import consume

class ConsumeRecommendationsFeedRequestThread(Thread):
  """this thread will be responsible for running the rabbitmq consumer that will be listening for recommendations feed request, in the background"""
  def __init__(self):
    Thread.__init__(self)
  
  def run(self):
    print("[RabbitMQ]: 'consume recommendations feed request' consumer thread running in background")
    consume()