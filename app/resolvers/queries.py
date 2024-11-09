import strawberry


@strawberry.type
class Query:
    @strawberry.field(description="Check if the API is healthy")
    async def health(self) -> str:
        """Returns OK if the service is healthy."""
        return "OK"
