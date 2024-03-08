from django.db import models

# Create your models here.
import neomodel

class Chef(neomodel.StructuredNode):
  username = neomodel.StringProperty(required=True)
  first_name = neomodel.StringProperty()
  last_name = neomodel.StringProperty()

  liked = neomodel.RelationshipTo('Recipe', 'LIKED')
  un_liked = neomodel.RelationshipTo('Recipe', 'UN_LIKED')
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