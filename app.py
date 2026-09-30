import os
from flask import Flask, render_template, request, jsonify
from nlp_engine import query_legal_database, summarize_legal_document, draft_statutory_notice, analyze_document_risks
from database import save_record, fetch_recent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nyaya-ai-secret-key-2026')
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/query", methods=["POST"])
def handle_query():
    data = request.get_json() or {}
    user_query = data.get("query", "").strip()
    if not user_query:
        return jsonify({"error": "Empty query received."}), 400

    results = query_legal_database(user_query)
    save_record("queries", {"query": user_query, "results": results})
    return jsonify({"success": True, "data": results})

@app.route("/api/summarize", methods=["POST"])
def handle_summarize():
    data = request.get_json() or {}
    document_text = data.get("text", "").strip()
    if not document_text:
        return jsonify({"error": "No text provided for summarization."}), 400

    summary = summarize_legal_document(document_text)
    save_record("summaries", {"original_len": len(document_text), "summary": summary})
    return jsonify({"success": True, "summary": summary})

@app.route("/api/draft", methods=["POST"])
def handle_draft():
    data = request.get_json() or {}
    client_name = data.get("client_name", "Aggrieved Party").strip()
    opposite_party = data.get("opposite_party", "Opposite Party").strip()
    issue_type = data.get("issue_type", "general").strip()
    amount = data.get("amount", "0.00").strip()
    details = data.get("details", "").strip()

    draft = draft_statutory_notice(client_name, opposite_party, issue_type, amount, details)
    save_record("drafts", {"client": client_name, "type": issue_type})
    return jsonify({"success": True, "draft": draft})

@app.route("/api/analyze", methods=["POST"])
def handle_analyze():
    data = request.get_json() or {}
    document_text = data.get("text", "").strip()
    if not document_text:
        return jsonify({"error": "No document text supplied."}), 400

    analysis = analyze_document_risks(document_text)
    summary = summarize_legal_document(document_text, num_sentences=2)
    save_record("analyses", {"risk_count": analysis["risk_count"]})
    return jsonify({"success": True, "analysis": analysis, "summary": summary})

@app.route("/api/history", methods=["GET"])
def get_history():
    recent_queries = fetch_recent("queries", limit=5)
    return jsonify({"success": True, "history": recent_queries})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)