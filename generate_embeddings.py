from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["Livres_indexes_database"]
collection = db["indexed_manga"]

model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

# Récupérer tous les livres avec une description
books = list(collection.find({"Description": {"$exists": True, "$ne": ""}}))

print(f"{len(books)} livres trouvés, génération des embeddings...")

for doc in books:
    desc = doc["Description"]
    emb = model.encode(desc).tolist()  # liste de floats

    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"embedding": emb}}
    )

print("✅ Embeddings enregistrés dans le champ 'embedding'.")
