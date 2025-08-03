import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

with open("schema.json") as f:
    schema = json.load(f)["tables"]

docs = []
for tname, cols in schema.items():
    col_str = ", ".join([c["column"] for c in cols])
    docs.append(f"Table {tname}: columns {col_str}")

embeddings = model.encode(docs, normalize_embeddings=True) # Convert to embeddings using SentenceTransformer
index = faiss.IndexFlatIP(embeddings.shape[1]) # Initialize FAISS index
index.add(embeddings) # Add embeddings to the index, and this will be used for similarity search

def retrieve_schema(user_query, top_k=1):
    q_emb = model.encode([user_query], normalize_embeddings=True)
    scores, idxs = index.search(q_emb, top_k)
    return [docs[i] for i in idxs[0]]

def retrieve_related_schema(user_query, top_k=1):
    main_table_doc = retrieve_schema(user_query, top_k=1)[0]
    main_table = main_table_doc.split()[1]  
    
    with open("schema.json") as f:
        schema = json.load(f)
    relationships = schema.get("relationships", [])
    
    related_tables = []
    for rel in relationships:
        if rel["child_table"] == main_table:
            related_tables.append(rel["parent_table"])
        elif rel["parent_table"] == main_table:
            related_tables.append(rel["child_table"])
    
    docs = [main_table_doc]
    for t in related_tables:
        cols = ", ".join([c["column"] for c in schema["tables"][t]])
        docs.append(f"Table {t}: columns {cols}")
    
    return "\n".join(docs)
