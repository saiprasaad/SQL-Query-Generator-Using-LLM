import requests
import re
OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_sql(user_query, schema_context):
    prompt = f"""
    You are an expert MySQL query generator.

    RULES:
    1. Use ONLY the tables and columns from the schema provided.
    2. If multiple tables are related via foreign keys, use JOINs where appropriate.
    3. Prefer returning human-readable columns (like project_name) over IDs when possible.
    4. Return only the SQL query (no explanation).

    SCHEMA:
    {schema_context}

    User question: {user_query}

    Return only the SQL query:
    """

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })

    text = response.json().get("response", "").strip()
    sql = text.replace("```sql", "").replace("```", "").replace("\n", " ").strip()
    sql = re.sub(r"\s+", " ", sql).strip()
    return sql
    
