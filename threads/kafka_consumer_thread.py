from threading import Thread
from utils.kafka.subscribe.nodes_and_relationships import consume_kafka_neo_graph_messages


class NeoMessagesThread(Thread):
  def __init__(self):
    Thread.__init__(self)
  
  def run(self):
    print("Neo4j thread running in background")
    consume_kafka_neo_graph_messages()