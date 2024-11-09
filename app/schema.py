import strawberry
from .resolvers.queries import Query
from .resolvers.mutations import Mutation

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    description="Image Generation API for creating AI-generated images with various styles and options",
)
