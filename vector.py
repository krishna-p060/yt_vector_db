import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Load the comments from the CSV file
df = pd.read_csv('results.csv', encoding='utf-16')

# Data cleaning: Fill missing usernames with a placeholder
df['Username'].fillna('unknown', inplace=True)

# Initialize the Sentence-Transformers model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Pinecone configuration
api_key = 'API'  # Replace with your actual Pinecone API key
index_name = 'youtube-commets-kp'
dimension = 384  # Embedding dimension from 'sentence-transformers/all-MiniLM-L6-v2'
region = 'us-east-1'
host_url = 'https://youtube-commets-kp-vxa0zku.svc.aped-4627-b74a.pinecone.io'

# Initialize Pinecone
pc = Pinecone(api_key=api_key)

# Create the index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region=region
        )
    )

# Connect to the index
index = pc.Index(index_name, host=host_url)

# Embed the comments and prepare them for upsertion
vectors = []
for idx, row in df.iterrows():
    comment = row['Comment']
    embedding = model.encode(comment).tolist()
    vectors.append({
        "id": f'comment-{idx}',
        "values": embedding,
        "metadata": {
            "username": row['Username'],
            "text": comment
        }
    })

# Upsert vectors into Pinecone
index.upsert(vectors=vectors, namespace='youtube-comments')
print("Data stored in Pinecone successfully.")

# Example query
query_vector = model.encode("Example query comment").tolist()

response = index.query(
    namespace='youtube-comments',
    vector=query_vector,
    top_k=5,  # Number of top results to retrieve
    include_values=True,
    include_metadata=True,
    filter={"username": {"$eq": "some-username"}}  # Example filter, modify as needed
)

# Print the query results
for match in response["matches"]:
    print(f'ID: {match["id"]}, Score: {match["score"]}, Metadata: {match["metadata"]}')

# Cleanup
index.close()
