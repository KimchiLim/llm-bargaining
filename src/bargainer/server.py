from dotenv import load_dotenv
import os
from bargainer import Bargainer
from fastapi import FastAPI
from base_models import NewConversationPayload, ReplyPayload

# Set up database and OpenAI client
load_dotenv()
DB_URL = os.environ.get("MONGODB_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize bargainer
bargainer = Bargainer(OPENAI_API_KEY, DB_URL)

app = FastAPI()

# Initiate conversation
@app.post("/conversations")
async def start_conversation(data: NewConversationPayload):
    product_id = data["product_id"]
    max_rounds = data["max_rounds"]
    return bargainer.start_conversation(product_id, max_rounds)

# Continue existing conversation
@app.post("/conversations/{conversation_id}")
async def continue_conversation(data: ReplyPayload, conversation_id: str):
    message = data["message"]
    return bargainer.reply(conversation_id, message)