import pandas as pd
from pymongo import MongoClient
import dotenv
import os
from urllib.parse import quote_plus
import random

dotenv.load_dotenv()
username = quote_plus(os.getenv("DB_USERNAME"))
password = quote_plus(os.getenv("DB_PASSWORD"))
client = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.qovpu.mongodb.net/")

# Read the CSV file
csv_file_path = 'updated_books_new.csv'
df = pd.read_csv(csv_file_path)

db = client['library_management']
books_collection = db['books']

# Add random available copies to each book
df['available_copies'] = df.apply(lambda x: random.randint(1, 100), axis=1)

# Convert DataFrame to dictionary and insert into MongoDB
books_data = df.to_dict(orient='records')
books_collection.insert_many(books_data)

print("Books data inserted successfully into MongoDB")

# Create a users collection and add test users
users_collection = db['users']

test_users = [
    {"user_id": "user1", "name": "Alice", "email": "alice@example.com", "status": "active"},
    {"user_id": "user2", "name": "Bob", "email": "bob@example.com", "status": "active"},
    {"user_id": "user3", "name": "Charlie", "email": "charlie@example.com", "status": "inactive"},
    {"user_id": "user4", "name": "David", "email": "david@example.com", "status": "active"},
    {"user_id": "user5", "name": "Eve", "email": "eve@example.com", "status": "inactive"}
]

users_collection.insert_many(test_users)

print("Test users inserted successfully into MongoDB")