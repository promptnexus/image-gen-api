# schema.py
from app.validators import load_validators
import strawberry
from strawberry.extensions import AddValidationRules
from app.resolvers.queries import Query
from app.resolvers.mutations import Mutation

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        AddValidationRules(load_validators()),
    ],
)
