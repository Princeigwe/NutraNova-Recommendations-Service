from django.db import models
import datetime
import pytz

# Create your models here.
import neomodel

class VotedRel(neomodel.StructuredRel):
  date = neomodel.DateTimeProperty(default=lambda: datetime.datetime.now(pytz.utc), index=True)
class Chef(neomodel.StructuredNode):
  username = neomodel.StringProperty(required=True)
  first_name = neomodel.StringProperty()
  last_name = neomodel.StringProperty()
  preferences = neomodel.JSONProperty()

  up_voted = neomodel.RelationshipTo('Recipe', 'UP_VOTED', model=VotedRel)
  down_voted = neomodel.RelationshipTo('Recipe', 'DOWN_VOTED', model=VotedRel)
  published = neomodel.RelationshipTo('Recipe', 'PUBLISHED')


class Recipe(neomodel.StructuredNode):
  title = neomodel.StringProperty()
  description = neomodel.StringProperty()
  ingredients = neomodel.ArrayProperty(base_property=neomodel.JSONProperty())
  instructions = neomodel.ArrayProperty(base_property=neomodel.StringProperty())
  preparation_time = neomodel.StringProperty()
  cooking_time = neomodel.StringProperty()
  servings = neomodel.IntegerProperty()
  nutritional_value = neomodel.JSONProperty()
  published_date = neomodel.StringProperty()

  is_tagged = neomodel.RelationshipTo('Tag', 'IS_TAGGED')

  # images, video, thumbnail, status, created and published properties from the Recipe Service data model are not relevant data for the recommendations database


class Tag(neomodel.StructuredNode):
  name = neomodel.StringProperty()