import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Initialize Pinecone
api_key = 'API'  # Replace with your actual Pinecone API key
index_name = 'youtube-commets-kp'
dimension = 384  # Embedding dimension from 'sentence-transformers/all-MiniLM-L6-v2'
region = 'us-east-1'
host_url = 'https://youtube-commets-kp-vxa0zku.svc.aped-4627-b74a.pinecone.io'

pc = Pinecone(api_key=api_key)

# Load the model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Example query keywords related to the car's engine
query_keywords = ["engine performance", "engine specs", "under the hood"]

# Perform the query
query_vector = model.encode(" ".join(query_keywords)).tolist()

index = pc.Index(index_name, host=host_url)

response = index.query(
    namespace='youtube-comments',
    vector=query_vector,
    top_k=10,  # Adjust as needed based on the expected number of results
    include_values=True,
    include_metadata=True
)

# Extract usernames from the query results
engine_comment_usernames = set()
for match in response["matches"]:
    engine_comment_usernames.add(match["metadata"]["username"])

# Count the number of unique usernames
num_engine_comment_users = len(engine_comment_usernames)
print(f"Number of people commenting about the engine of the car: {num_engine_comment_users}")
print("Usernames commenting about the engine:", engine_comment_usernames)