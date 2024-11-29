from typing import List
from pydantic import BaseModel

from app.services.api_key_service.models.user import User

# We can attach a customer id to an organization as a whole company is billed together based on its app usage by api key. API keys trigger this customer id as they are associated with an organization and they fetch a customer id from here on use.
# See: DatabaseService.get_organization_by_api_key, DatabaseService.get_organization_customer_id_by_api_key

# We can create a customer id in two cases:

# 1. When an admin service like PromptNexus allows using the app, it can first request they go through stripe checkout which will create a customer id for them. The admin API for this app will allow passing a customer as it's a trusted source, but user api keys will never allow this.

# 2. In the case of a user independently using the app, they must open the application interface to go through stripe checkout manually as well. This is because stripe requires certain details on a customer, such as address, which is a user must enter somewhere anyway before being charged.

# Then, we can use a webhook to add the customer ID to their organization, or use some other method stripe provides.


class Organization(BaseModel):
    id: str
    name: str
    admin: str
    members: List[str] = []
    customer_id: str = None
