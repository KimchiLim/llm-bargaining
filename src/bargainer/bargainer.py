from openai import OpenAI
from pymongo import MongoClient
from multiplicative_weights import MultWeights
import textfile
from bson.objectid import ObjectId
import random

class Bargainer:
    def __init__(
            self,
            openai_api_key,
            db_url,
            model="gpt-4o-mini",
            temp=0.7,
            sentiment_analyzer=None,
            epsilon=0.2
            ):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.temp = temp
        self.db = MongoClient(db_url)["bargaining_db"]
        self.epsilon = epsilon

        if sentiment_analyzer == None:
            self.sentiment_analyzer = MultWeights(self.openai_client)
        else:
            self.sentiment_analyzer = sentiment_analyzer

    def start_conversation(self, product_id, max_rounds):
        '''
        Initializes a conversation in the database.
        '''
        object_id = ObjectId(product_id)
        if (product := self.db["products"].find_one(
            {'_id': object_id}, {'_id': 0})) == None:
            # Handle bad product_id input
            return {
                "success": False
            }
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            temperature=self.temp,
            messages=[
                {"role": "system", "content": textfile.preamble},
                {"role": "system", "content": product["information"]},
                {"role": "system", "content": textfile.opening_prompt}
            ]
        )
        opening = response.choices[0].message.content

        conversation = {
            "product_id": product_id,
            "max_rounds": max_rounds,
            "round": 0,
            "messages": [{"role": "system", "content": opening}],
            "latest_offer": product["listing_price"],
            "latest_counteroffer": 0,
            "closed": False,
            "weights": {
                feature: 1 for feature in product["product_features"].keys()
            }
        }
        result = self.db["conversations"].insert_one(conversation)

        return {
            "success": True,
            "conversation_id": str(result.inserted_id),
            "message": opening,
            "offer": product["listing_price"]
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
    
    def update_weights(self,
                       weights,
                       counteroffer,
                       prev_offer,
                       prev_counteroffer,
                       m1,
                       m2):
        '''
        Performs a weight update with attribution
        '''
        gap = prev_offer - prev_counteroffer
        penalty = 2 * (prev_offer - counteroffer) / gap - 1
        attribution = dict()
        for feature in weights.keys():
            response = self.openai_client.chat.completions.create(
                model=self.model,
                temperature=self.temp,
                messages=[
                    {"role": "system", "content": textfile.attribution_prompt_1(feature)},
                    {"role": "user", "content": m1},
                    {"role": "user", "content": m2},
                    {"role": "system", "content": textfile.attribution_prompt_2}
                ]
            )
            attribution[feature] = float(response.choices[0].message.content)
        attr_sum = sum(attribution.values())
        updated_weights = dict()
        for feature in weights.keys():
            if penalty >= 0:
                updated_weights[feature] = weights[feature] * (1 - self.epsilon) ** (attribution[feature] * penalty / attr_sum)
            else:
                updated_weights[feature] = weights[feature] * (1 + self.epsilon) ** (-attribution[feature] * penalty / attr_sum)
        print(f"In update_weights. Attributions: {[attribution]}, penalty: {penalty}")
        return updated_weights
    
    def select_next_topic(self, weights):
        kv = weights.items()
        topics = [item[0] for item in kv]
        weights = [item[1] for item in kv]
        return random.choices(topics, weights=weights)

    def update_price(self, weights, counteroffer, offer, min_price):
        '''
        Calculates a new selling price for the product given a recent history
        and current attribute weights
        '''
        gap = offer - counteroffer
        return max(min_price, counteroffer, offer - gap * (1/2))
    
    def reply(self, conversation_id, message, counteroffer):
        '''
        Things we need to do here:
            0. Perform analysis of user reply and update user features
            1. Query the model for the latest offer/price
            2. Calculate updated offer
            3. Use user and product features to choose next topic
            4. Update messages (messages += [reply + price update + feature selection])
            4. Construct conversation history (preamble + information + opening + messages)
            5. Generate response
            6. Update database entry
        '''
        if (conversation := self.db["conversations"].find_one(
            {'_id': ObjectId(conversation_id)}, {'_id': 0})) == None:
            # Handle bad conversation_id
            return {
                "success": False
            }
        if conversation["max_rounds"] == conversation["round"]:
            return {
                "success": False
            }

        product = self.db["products"].find_one(
            {"_id": ObjectId(conversation["product_id"])},
            {'_id': 0}
        )
        # Perform feature update
        if len(conversation["messages"]) == 1:
            prev_counteroffer = counteroffer
        else:
            prev_counteroffer = conversation["latest_counteroffer"]
        updated_weights = self.update_weights(
            conversation["weights"],
            counteroffer,
            conversation["latest_offer"],
            prev_counteroffer,
            conversation["messages"][-1]["content"],
            message
        )
        print("Updated weights: ", updated_weights)
        
        new_price = self.update_price(updated_weights, counteroffer, conversation["latest_offer"], product["min_price"])
        # TODO: If new_price == counteroffer, then accept counteroffer

        # Choose next topic
        next_topic = self.select_next_topic(updated_weights)
        print("Selected topic: ", next_topic)
        
        # Generate response and update database entry
        messages = (conversation["messages"] 
                    + [{"role": "user", "content": message},]
        )
        response = self.openai_client.chat.completions.create(
            model=self.model,
            temperature=self.temp,
            messages=(
                [
                    {"role": "system", "content": textfile.preamble},
                    {"role": "system", "content": product["information"]}
                ] 
                + messages
                + [
                    {"role": "system", "content": textfile.price_update(new_price, product["name"])},
                    {"role": "system", "content": textfile.feature_selection(next_topic, product["name"])},
                    {"role": "system", "content": textfile.remaining_rounds(conversation["max_rounds"] - conversation["round"])}
                ]
            )
        )
        messages += [{"role": "system", "content": response.choices[0].message.content}]
        db_filter = {"_id": ObjectId(conversation_id)}
        db_newvalues = {"$set": {
            "round": conversation["round"] + 1,
            "messages": messages, 
            "latest_offer": new_price,
            "latest_counteroffer": counteroffer,
            "weights": updated_weights
            }}
        self.db["conversations"].update_one(db_filter, db_newvalues)

        return {
            "success": True,
            "message": response.choices[0].message.content,
            "closed": False,
            "offer": new_price
        }

    def create_product(self, product):
        if (result := self.db["products"].insert_one(product)) == None:
            return {
                "success": False
            }
        return {
            "success": True,
            "product_id": result.inserted_id
        }