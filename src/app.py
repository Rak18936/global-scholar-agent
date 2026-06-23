from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database
from agents.orchestrator import ScholarAgentOrchestrator

app = Flask(__name__)
CORS(app)

orchestrator = ScholarAgentOrchestrator()

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    scholarships = database.get_scholarships()
    universities = database.get_universities()
    
    total_stipend_value_est = 150000 # Mock calculation of average stipend in USD
    average_acceptance_est = 12.5 # Mock percentage
    
    return jsonify({
        "metrics": {
            "total_programs": len(scholarships),
            "total_universities": len(universities),
            "average_acceptance": average_acceptance_est,
            "average_value_usd": total_stipend_value_est
        },
        "scholarships": scholarships,
        "universities": universities
    })

@app.route("/api/chat", methods=["POST"])
def run_chat():
    data = request.json or {}
    
    # Execute orchestrator task in asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(orchestrator.execute_task(data))
    finally:
        loop.close()

    return jsonify(response)

@app.route("/api/evaluate", methods=["POST"])
def evaluate_profile():
    data = request.json or {}
    sch_id = data.get("scholarship_id")
    gpa = data.get("gpa")
    ielts = data.get("ielts")
    resume_text = data.get("resume_text", "")

    if not all([sch_id, gpa, ielts, resume_text]):
        return jsonify({"error": "Missing profile values"}), 400

    # Trigger raw evaluation handler from MCP server logically
    from mcp_server import ScholarMCPServer
    server = ScholarMCPServer()
    try:
        raw_result = server.handle_evaluate_resume_match({
            "scholarship_id": sch_id,
            "gpa": float(gpa),
            "ielts": float(ielts),
            "resume_text": resume_text
        })
        # Parse output string block back into JSON for API convenience
        json_str = raw_result.replace("Match Evaluation Report:\n", "", 1)
        result_json = json.loads(json_str)
        return jsonify({"status": "Success", "report": result_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/sop", methods=["POST"])
def generate_sop():
    data = request.json or {}
    sch_name = data.get("scholarship_name")
    major = data.get("target_major")
    resume_text = data.get("resume_text", "")

    if not all([sch_name, major, resume_text]):
        return jsonify({"error": "Missing target fields"}), 400

    from mcp_server import ScholarMCPServer
    server = ScholarMCPServer()
    try:
        raw_result = server.handle_generate_sop_template({
            "scholarship_name": sch_name,
            "target_major": major,
            "resume_text": resume_text
        })
        return jsonify({"status": "Success", "sop_outline": raw_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/upload-resume", methods=["POST"])
def upload_resume():
    from pypdf import PdfReader
    import io
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    filename = file.filename.lower()
    text = ""
    try:
        if filename.endswith(".pdf"):
            pdf_bytes = io.BytesIO(file.read())
            reader = PdfReader(pdf_bytes)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif filename.endswith(".txt") or filename.endswith(".md"):
            text = file.read().decode("utf-8", errors="ignore")
        else:
            return jsonify({"error": "Unsupported file format. Please upload PDF, TXT, or MD."}), 400
            
        return jsonify({"status": "Success", "text": text.strip()})
    except Exception as e:
        return jsonify({"error": f"Failed to parse file: {str(e)}"}), 500

if __name__ == "__main__":
    database.initialize_dbs()
    app.run(host="127.0.0.1", port=5000, debug=True)
