from pydantic import BaseModel

class ForwardSearchRequest(BaseModel):
    query: str