from pydantic import BaseModel

class NewConversationPayload(BaseModel):
    max_rounds: int
    product_id: str

class ReplyPayload(BaseModel):
    message: str
    offer: float
    accept: bool

class ProductPayload(BaseModel):
    name: str
    listing_price: float
    min_price: float
    product_features: dict[str, float]
    information: str
    opening: str