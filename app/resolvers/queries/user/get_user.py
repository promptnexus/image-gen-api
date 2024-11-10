# app/resolvers/user/queries.py
import strawberry
from typing import List


@strawberry.type
class UserQueries:
    @strawberry.field
    async def users(self) -> List[str]:
        return ["user1", "user2"]
