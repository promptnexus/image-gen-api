import strawberry
from app.resolvers.queries import Query
from app.resolvers.mutations import Mutation

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # description="Image Generation API for creating AI-generated images with various styles and options",
)
