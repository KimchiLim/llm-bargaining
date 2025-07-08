from openai import OpenAI
from pymongo import MongoClient
from multiplicative_weights import MultWeights
import textfile

class Bargainer:
    def __init__(
            self,
            openai_api_key,
            db_url,
            model="gpt-4o-mini",
            temp=0.7,
            sentiment_analyzer=None
            ):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.temp = temp
        self.db = MongoClient(db_url)["bargaining_db"]

        if sentiment_analyzer == None:
            self.sentiment_analyzer = MultWeights(self.openai_client)
        else:
            self.sentiment_analyzer = sentiment_analyzer

    def start_conversation(self, product_id, max_rounds):
        '''
        Initializes a conversation in the database.
        '''
        if (product := self.db["products"].find_one({'_id': product_id})) == None:
            # Handle bad product_id input
            return {
                "success": False
            }

        conversation = {
            "product_id": product_id,
            "max_rounds": max_rounds,
            "messages": [],
            "latest_offer": product["listing_price"],
            "closed": False,
            "user_features": None
        }

        result = self.db["conversations"].insert_one(conversation)

        return {
            "success": True,
            "conversation_id": result.inserted_id,
            "message": product["opening"]
        }
    
    def query_price(self, message):
        '''
        Returns the latest price based on the final message 
        in the bargain, or -1 if no recent offer was made.
        '''
        response = self.openai_client.chat.completions.create(
            model=self.model,
            temperature=self.temp,
            messages=[
                {"role": "system", "content": textfile.current_price_preamble},
                {"role": "user", "content": message},
                {"role": "system", "content": textfile.current_price_query}
            ]
        )
        return float(response.choices[0].message.content)
    
    def select_next_topic(self, user_features, product_features):
        #TODO
        return 'idk'
    
    def reply(self, conversation_id, message):
        '''
        Things we need to do here:
            0. Perform sentiment analysis of user reply and update user features (or set them, if first reply)
            1. Query the model for the latest offer/price
            2. Calculate updated offer
            3. Use user and product features to choose next topic
            4. Update messages (messages += [reply + price update + feature selection])
            4. Construct conversation history (preamble + messages)
            5. Generate response
            6. Update database entry
        '''
        if (conversation := self.db["conversations"].find_one(
            {'_id': conversation_id})) == None:
            # Handle bad conversation_id
            return {
                "success": False
            }
        product = self.db["products"].find_one(
            {"_id": conversation["product_id"]}
        )
        # Perform feature update
        if len(conversation["messages"]) == 0:
            user_features = {
                feature: 5 for feature in product["product_features"].keys()
            }
            updated_user_features = self.sentiment_analyzer.analyze(
                conversation["preamble"][-1]["content"],
                message,
                user_features
            )
        else:
            updated_user_features = self.sentiment_analyzer.analyze(
                conversation["messages"][-1]["content"],
                message,
                conversation["user_features"]
            )

        # Query model for latest offer
        latest_offer = self.query_price(message)

        # Calculate updated offer (change this later)
        if latest_offer == -1:
            latest_offer = conversation["latest_offer"]
        else:
            latest_offer = (latest_offer + conversation["latest_offer"]) / 2
        
        # Choose next topic
        next_topic = self.select_next_topic(
            updated_user_features,
            product["product_features"]
        )
        
        # Generate response and update database entry
        messages = (conversation["messages"] 
                    + message 
                    + textfile.price_update(latest_offer)
                    + textfile.feature_selection(next_topic, product["name"]))
        response = self.openai_client.chat.completions.create(
            model=self.model,
            temperature=self.temp,
            messages=product["preamble"] + messages
        )
        db_filter = {"_id": conversation_id}
        db_newvalues = {"$set": {
            "messages": messages, 
            "latest_offer": latest_offer,
            "user_features": updated_user_features
            }}
        self.db["conversations"].update_one(db_filter, db_newvalues)

        return {
            "success": True,
            "message": response.choices[0].message.content,
            "closed": False,
            "offer": latest_offer
        }