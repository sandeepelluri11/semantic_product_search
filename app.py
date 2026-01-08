import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import faiss
from fastapi import FastAPI
from pydantic import BaseModel
import pickle

df = pd.read_csv("products.csv")

model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.eval()

def embed_text(text_list):
    inputs = tokenizer(text_list, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, return_dict=True)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.numpy()

try:
    with open("embeddings.pkl", "rb") as f:
        embeddings_matrix = pickle.load(f)
except FileNotFoundError:
    embeddings_matrix = embed_text(df["description"].tolist())
    with open("embeddings.pkl", "wb") as f:
        pickle.dump(embeddings_matrix, f)

df["embedding"] = list(embeddings_matrix)

embedding_dim = embeddings_matrix.shape[1]
index = faiss.IndexFlatL2(embedding_dim)
index.add(embeddings_matrix)


app = FastAPI(title="Advanced Semantic Product Search API")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

def semantic_search(query, top_k=5):
    query_vec = embed_text([query])
    distances, indices = index.search(query_vec, top_k)
    results = []
    for idx, dist in zip(indices[0], distances[0]):
        product = df.iloc[idx]
        results.append({
            "id": int(product["id"]),
            "name": product["name"],
            "category": product["category"],
            "brand": product["brand"],
            "price": float(product["price"]),
            "popularity": float(product["popularity"]),
            "description": product["description"],
            "similarity": float(1 / (1 + dist))
        })
    return results

def rank_results(results, query):
    query_lower = query.lower()
    for r in results:
        if r["category"].lower() in query_lower:
            r["similarity"] *= 1.1
        for word in query_lower.split():
            if word in r["name"].lower():
                r["similarity"] *= 1.2
        r["similarity"] *= r["popularity"]
    return sorted(results, key=lambda x: x["similarity"], reverse=True)


@app.post("/search")
def search_products(req: QueryRequest):
    results = semantic_search(req.query, req.top_k)
    ranked = rank_results(results, req.query)
    return {"query": req.query, "results": ranked}


@app.get("/")
def root():
    return {"message": "Advanced Semantic Search API running. Use POST /search endpoint."}
