# 🔒 SQL Query Generator Using LLM (Schema-Aware & Privacy-Focused)

This project is a **private, schema-aware SQL query generator** that uses a **local LLM** to generate SQL queries **without exposing any database data**.  
The system only uses **table structures (schema)**—not the actual data—ensuring **data privacy and security**.

---

## ✅ 1. What This Project Does
- Reads your `schema.json` (contains only table names, columns, and relationships – no data).
- Converts each table into a descriptive string for semantic understanding.
- Uses **SentenceTransformer** to create embeddings of these table descriptions.
- Stores these embeddings in a **FAISS index** to enable fast and relevant schema retrieval.
- Integrates with a **local LLM** (via Ollama) to generate **SQL queries** from natural language.
- Guarantees **no sensitive data** is accessed or sent to the model.

---

## ✅ 2. Step-by-Step Code Flow

### **Step 1: Load Schema**
```python
with open("schema.json") as f:
    schema = json.load(f)["tables"]
```
- Loads schema containing only table and column information.

---

### **Step 2: Build Table Descriptions**
```python
docs = [f"Table {t}: columns {', '.join(c['column'] for c in cols)}" for t, cols in schema.items()]
```
- Creates human-readable descriptions for each table, e.g.:
  ```
  Table employees: columns employee_id, first_name, last_name, department_id
  ```

---

### **Step 3: Create Embeddings**
```python
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(docs, normalize_embeddings=True)
```
- Converts each table description into a **dense vector embedding**.
- Normalization ensures cosine similarity works correctly.

---

### **Step 4: Build FAISS Index**
```python
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)
```
- Creates a FAISS index using **Inner Product (cosine similarity)**.
- Stores each table embedding for fast semantic search.

---

### **Step 5: Retrieve Most Relevant Table**
```python
def retrieve_schema(user_query, top_k=1):
    q_emb = model.encode([user_query], normalize_embeddings=True)
    scores, idxs = index.search(q_emb, top_k)
    return [docs[i] for i in idxs[0]]
```
- Converts the user query into an embedding.
- Searches the FAISS index for the most similar table(s).
- Returns matching table descriptions.

---

### **Step 6: Retrieve Related Tables for JOINs**
```python
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
```
- Identifies foreign key relationships from the schema.
- Adds related tables to the retrieved schema context.
- Returns a combined schema string for JOIN-aware SQL generation.

---

## ✅ 3. Why This is Privacy-Focused
- ✅ **No actual database data** is used—only schema structure is exposed.
- ✅ **Local LLM** ensures no external API calls leak information.
- ✅ **FAISS Index** runs locally, storing only embeddings derived from schema text.

---

## ✅ 4. Output Example

**User Query:**  
> “Show total hours worked per project for the last 30 days”

**LLM Output:**  
```sql
SELECT p.project_name, SUM(t.hours_worked) AS total_hours
FROM timesheets t
JOIN projects p ON t.project_id = p.project_id
WHERE t.work_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY p.project_name;
```

---

🚀 This project enables **safe SQL generation** by leveraging **only schema metadata** and a **private local LLM**.
