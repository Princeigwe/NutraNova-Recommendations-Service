from ariadne import QueryType, load_schema_from_path, make_executable_schema, MutationType, SubscriptionType
from recommend_engine import resolvers

type_defs = load_schema_from_path('schemas')

query = QueryType()
query.set_field("userPreferenceVector", resolvers.resolve_user_preference_vector)


mutation = MutationType()


schema = make_executable_schema(type_defs, query, mutation, convert_names_case=True)