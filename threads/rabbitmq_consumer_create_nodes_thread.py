from threading import Thread
# from utils.rabbitmq.consumers.consume_published_recipe import consume


class CreatePublishedRecipeThread(Thread):
  """this thread will be responsible for running the rabbitmq consumer that will be listening for published recipes, in the background"""
  def __init__(self):
    Thread.__init__(self)
  
  def run(self):
    print("[RabbitMQ]: 'published recipe' consumer thread running in background")
    # consume()