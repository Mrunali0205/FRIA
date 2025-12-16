from pydantic import BaseModel


class ReverseGeocodeRequest(BaseModel):
    lat: float
    lon: float
class ForwardSearchRequest(BaseModel):
    query: str
class AddressCandidate(BaseModel):
    address: str
    lat: float
    lon: float