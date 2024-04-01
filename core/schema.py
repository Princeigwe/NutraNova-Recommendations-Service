from ariadne import QueryType, load_schema_from_path, make_executable_schema, MutationType, SubscriptionType
from recommend_engine import resolvers

type_defs = load_schema_from_path('schemas')

query = QueryType()
query.set_field("userPreferenceVector", resolvers.resolve_user_preference_vector)
query.set_field("recipesTagsVector", resolvers.resolve_recipes_tags_vector)
query.set_field("cosineSimilarities", resolvers.resolve_cosine_similarities)

mutation = MutationType()


schema = make_executable_schema(type_defs, query, mutation, convert_names_case=True)