from pydantic import BaseModel

class NewConversationPayload(BaseModel):
    max_rounds: int
    product_id: str

class ReplyPayload(BaseModel):
    message: str