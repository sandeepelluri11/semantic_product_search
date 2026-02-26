from elasticsearch import helpers

from app.search import get_es_client
from app.config import get_settings


def create_index_and_seed():
    settings = get_settings()
    client = get_es_client()

    index_name = settings.es_index

    if client.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists. Skipping creation.")
        return

    mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "name": {"type": "text"},
                "description": {"type": "text"},
                "category": {"type": "keyword"},
                "brand": {"type": "keyword"},
                "price": {"type": "float"},
                "currency": {"type": "keyword"},
                "popularity": {"type": "integer"},
                "click_through_rate": {"type": "float"},
                "rating": {"type": "float"},
                "tags": {"type": "keyword"},
            }
        }
    }

    client.indices.create(index=index_name, body=mapping)
    print(f"Created index '{index_name}'. Seeding demo products...")

    docs = [
        {
            "_index": index_name,
            "_id": "1",
            "_source": {
                "title": "Wireless Noise-Cancelling Headphones",
                "description": "Over-ear wireless headphones with active noise cancellation and 30-hour battery life.",
                "category": "electronics",
                "brand": "SoundMax",
                "price": 199.99,
                "currency": "USD",
                "popularity": 1200,
                "click_through_rate": 0.18,
                "rating": 4.6,
                "tags": ["wireless", "headphones", "noise cancelling"],
            },
        },
        {
            "_index": index_name,
            "_id": "2",
            "_source": {
                "title": "Running Shoes - Lightweight",
                "description": "Breathable, cushioned running shoes designed for long-distance comfort.",
                "category": "sports",
                "brand": "FleetRun",
                "price": 89.99,
                "currency": "USD",
                "popularity": 800,
                "click_through_rate": 0.12,
                "rating": 4.3,
                "tags": ["running", "shoes", "lightweight"],
            },
        },
        {
            "_index": index_name,
            "_id": "3",
            "_source": {
                "title": "4K UHD Smart TV 55\"",
                "description": "55-inch 4K Ultra HD smart TV with HDR and built-in streaming apps.",
                "category": "electronics",
                "brand": "VisionPlus",
                "price": 499.0,
                "currency": "USD",
                "popularity": 600,
                "click_through_rate": 0.09,
                "rating": 4.2,
                "tags": ["tv", "4k", "smart"],
            },
        },
        {
            "_index": index_name,
            "_id": "4",
            "_source": {
                "title": "Noise-Isolating In-Ear Earbuds",
                "description": "Compact in-ear earbuds with rich bass and inline microphone.",
                "category": "electronics",
                "brand": "SoundMax",
                "price": 39.99,
                "currency": "USD",
                "popularity": 2200,
                "click_through_rate": 0.22,
                "rating": 4.4,
                "tags": ["earbuds", "in-ear", "audio"],
            },
        },
    ]

    helpers.bulk(client, docs)
    client.indices.refresh(index=index_name)
    print("Seeding complete.")


if __name__ == "__main__":
    create_index_and_seed()

