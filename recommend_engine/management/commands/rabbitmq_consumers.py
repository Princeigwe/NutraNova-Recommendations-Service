## this file is a custom command created from running rabbitmq consumer in the background, in order to update chef details. "python3 manage.py rabbitmq_consumers"

from typing import Any
from django.core.management.base import BaseCommand
from threads import rabbitmq_consumer_update_chef_thread
from threads import rabbitmq_consumer_create_nodes_thread
from threads import rabbitmq_consumer_consume_recommendation_feed_request_channel


class Command(BaseCommand):
  help = "Starting RabbitMQ consumers"

  def handle(self, *args: Any, **options: Any) -> str | None:
    # start rabbitmq consumer thread for updating chef data
    update_chef_data_consumer = rabbitmq_consumer_update_chef_thread.UpdateChefThread()
    update_chef_data_consumer.start()

    # start rabbitmq consumer thread for creating nodes on published recipes
    published_recipe_consumer = rabbitmq_consumer_create_nodes_thread.CreatePublishedRecipeThread()
    published_recipe_consumer.start()

    # start rabbitmq consumer thread for consuming requests for users recommended feeds
    recommendations_feed_requests_consumer = rabbitmq_consumer_consume_recommendation_feed_request_channel.ConsumeRecommendationsFeedRequestThread()
    recommendations_feed_requests_consumer.start()
