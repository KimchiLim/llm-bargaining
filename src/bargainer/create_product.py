import sys
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import json
from base_models import ProductPayload

if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    print("Usage: python create_product.py <path-to-json>")
    exit(1)
load_dotenv()
DB_URL = os.getenv('MONGODB_URL')
db = MongoClient(DB_URL)["bargaining_db"]
with open(path, 'r') as f:
    raw_data = json.load(f)
    try:
        product = ProductPayload(**raw_data)
        result = db["products"].insert_one(product.model_dump())
        if result:
            print(f"Successfully inserted product id {result.inserted_id}")
        else:
            print("Insertion error")
    except Exception as e:
        print("Validation error: ", e)
