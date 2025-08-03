from flask import Flask, request, jsonify
from rag import retrieve_related_schema
from llm_client import generate_sql

app = Flask(__name__)

@app.route("/generate-sql", methods=["POST"])
def generate_sql_endpoint():
    data = request.get_json()
    user_query = data.get("queryInText")
    
    relevant_schema = retrieve_related_schema(user_query)
    
    sql = generate_sql(user_query, relevant_schema)
    
    return jsonify({"query": sql})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
