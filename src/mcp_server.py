import sys
import json
import re
import database

def log_debug(message):
    print(f"DEBUG: {message}", file=sys.stderr, flush=True)

class ScholarMCPServer:
    def __init__(self):
        self.tools = {
            "search_scholarships": {
                "name": "search_scholarships",
                "description": "Search for fully-funded scholarships by target country or academic field.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "country": {"type": "string", "description": "Target country: South Korea, Japan, Germany, Singapore, Taiwan (or 'Any')"},
                        "field": {"type": "string", "description": "Academic major: Engineering, Science, Business, Humanities (or 'Any')"}
                    },
                    "required": ["country", "field"]
                },
                "handler": self.handle_search_scholarships
            },
            "get_university_suggestions": {
                "name": "get_university_suggestions",
                "description": "Suggest top ranking universities in target countries matching a student's field of study.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "country": {"type": "string", "description": "Target country (or 'Any')"},
                        "field": {"type": "string", "description": "Field of study (major)"}
                    },
                    "required": ["country", "field"]
                },
                "handler": self.handle_get_university_suggestions
            },
            "evaluate_resume_match": {
                "name": "evaluate_resume_match",
                "description": "Compare a student's profile (GPA, IELTS) against a scholarship's requirements to determine eligibility and gaps.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "scholarship_id": {"type": "string", "description": "The ID of the target scholarship (e.g. SCH-GKS)"},
                        "gpa": {"type": "number", "description": "Student's GPA (on a 4.0 scale)"},
                        "ielts": {"type": "number", "description": "Student's IELTS Band Score (range 0.0 to 9.0)"},
                        "resume_text": {"type": "string", "description": "Pasted text content of the student's resume/profile"}
                    },
                    "required": ["scholarship_id", "gpa", "ielts", "resume_text"]
                },
                "handler": self.handle_evaluate_resume_match
            },
            "generate_sop_template": {
                "name": "generate_sop_template",
                "description": "Generate a custom, tailored Statement of Purpose (SOP) outline based on the student's resume and target scholarship.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "scholarship_name": {"type": "string", "description": "Name of the target scholarship"},
                        "target_major": {"type": "string", "description": "The major/course the student is applying for"},
                        "resume_text": {"type": "string", "description": "Resume text detailing past projects and background"}
                    },
                    "required": ["scholarship_name", "target_major", "resume_text"]
                },
                "handler": self.handle_generate_sop_template
            }
        }

    def handle_search_scholarships(self, arguments):
        country = arguments.get("country", "Any").strip()
        field = arguments.get("field", "Any").strip()

        # Input sanitization
        if not re.match(r"^[a-zA-Z0-9\s\-]+$", country) or not re.match(r"^[a-zA-Z0-9\s\-]+$", field):
            raise ValueError("Security Violation: Invalid character format in arguments.")

        scholarships = database.get_scholarships()
        results = []

        for sch in scholarships:
            country_match = (country.lower() == "any" or sch["country"].lower() == country.lower())
            field_match = (field.lower() == "any" or any(f.lower() == field.lower() for f in sch["eligible_fields"]))
            if country_match and field_match:
                results.append(sch)

        return f"Found {len(results)} fully-funded scholarship matching criteria:\n" + json.dumps(results, indent=2)

    def handle_get_university_suggestions(self, arguments):
        country = arguments.get("country", "Any").strip()
        field = arguments.get("field", "Any").strip()

        if not re.match(r"^[a-zA-Z0-9\s\-]+$", country) or not re.match(r"^[a-zA-Z0-9\s\-]+$", field):
            raise ValueError("Security Violation: Invalid character format in arguments.")

        unis = database.get_universities()
        results = []

        for uni in unis:
            country_match = (country.lower() == "any" or uni["country"].lower() == country.lower())
            field_match = (field.lower() == "any" or any(f.lower() == field.lower() for f in uni["fields"]))
            if country_match and field_match:
                results.append(uni)

        # Sort by rank
        results = sorted(results, key=lambda x: x["rank"])
        return f"Recommended Universities:\n" + json.dumps(results, indent=2)

    def handle_evaluate_resume_match(self, arguments):
        sch_id = arguments.get("scholarship_id", "").strip()
        gpa = float(arguments.get("gpa", 0.0))
        ielts = float(arguments.get("ielts", 0.0))
        resume_text = arguments.get("resume_text", "").strip()

        # SECURITY PARAMETER CHECKS (Safety Bounds)
        if not sch_id or not re.match(r"^SCH\-[A-Z\-]+$", sch_id):
            raise ValueError("Security Violation: Invalid scholarship ID format.")
        
        if gpa < 0.0 or gpa > 4.0:
            raise ValueError("Security Violation: GPA must be between 0.0 and 4.0.")
            
        if ielts < 0.0 or ielts > 9.0:
            raise ValueError("Security Violation: IELTS band score must be between 0.0 and 9.0.")

        scholarships = database.get_scholarships()
        target_sch = None
        for sch in scholarships:
            if sch["id"] == sch_id:
                target_sch = sch
                break

        if not target_sch:
            raise ValueError(f"Scholarship {sch_id} not found.")

        # Match Evaluation Logic
        score = 100
        gaps = []
        checks = []

        # Check GPA
        if gpa >= target_sch["min_gpa"]:
            checks.append({"criteria": "GPA Threshold", "status": "PASS", "required": target_sch["min_gpa"], "actual": gpa})
        else:
            checks.append({"criteria": "GPA Threshold", "status": "FAIL", "required": target_sch["min_gpa"], "actual": gpa})
            score -= 30
            gaps.append(f"Your GPA ({gpa}) is below the required {target_sch['min_gpa']} for this scholarship.")

        # Check IELTS
        if ielts >= target_sch["min_ielts"]:
            checks.append({"criteria": "IELTS Language Proficiency", "status": "PASS", "required": target_sch["min_ielts"], "actual": ielts})
        else:
            checks.append({"criteria": "IELTS Language Proficiency", "status": "FAIL", "required": target_sch["min_ielts"], "actual": ielts})
            score -= 20
            gaps.append(f"Your IELTS score ({ielts}) is below the recommended {target_sch['min_ielts']}.")

        # Check research publications / projects count (heuristic scan of resume)
        has_publications = "publication" in resume_text.lower() or "published" in resume_text.lower() or "journal" in resume_text.lower()
        if not has_publications:
            gaps.append("Resume gap: No scientific publications or journals detected. Adding a research paper could boost match probability for graduate awards.")
            score -= 10
        else:
            checks.append({"criteria": "Research publications detected", "status": "PASS"})

        # Final score bounding
        score = max(0, score)

        report = {
            "scholarship_name": target_sch["name"],
            "country": target_sch["country"],
            "match_percentage": score,
            "eligibility_checklist": checks,
            "profile_gaps": gaps,
            "suggested_enhancements": [
                "Consider preparing a strong portfolio of academic research projects.",
                "Ensure your recommendation letters focus heavily on research potential.",
                "Take a preparatory course if you need to retake language exams to exceed thresholds."
            ]
        }

        return f"Match Evaluation Report:\n" + json.dumps(report, indent=2)

    def handle_generate_sop_template(self, arguments):
        scholarship_name = arguments.get("scholarship_name", "").strip()
        target_major = arguments.get("target_major", "").strip()
        resume_text = arguments.get("resume_text", "").strip()

        # Sanitize parameters
        if not re.match(r"^[a-zA-Z0-9\s\-\(\)\&]+$", scholarship_name) or not re.match(r"^[a-zA-Z0-9\s\-]+$", target_major):
            raise ValueError("Security Violation: Invalid characters in inputs.")

        # Custom tailored outline structure
        sop_outline = f"""STATEMENT OF PURPOSE OUTLINE
Target Award: {scholarship_name}
Proposed Program: Master/PhD in {target_major}

[SECTION 1: Introduction & Hook]
- State clearly your target field of study: {target_major} and why you have selected {scholarship_name}.
- Anchor this section around a core scientific question or project referenced in your experience.

[SECTION 2: Academic Background]
- Summarize your relevant academic coursework.
- Connect your past achievements (GPA, key laboratory work) directly to the rigor of this scholarship.

[SECTION 3: Professional/Research Experience]
- Highlight key projects found in your profile.
- Detail methodology used, results, and what you learned from these experiences.
- (Heuristic reference: Tailor this to address your target major of {target_major}).

[SECTION 4: Future Goals & Motivation for Host Country]
- Explain why studying in this country (South Korea, Japan, Germany, Singapore, Taiwan) fits your academic trajectory.
- Connect the scholarship's funding values (e.g. international diplomacy, STEM innovation) to your post-graduate plans.
"""
        return sop_outline

    # JSON-RPC server event loop
    def run(self):
        log_debug("Scholarship MCP Server started.")
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                method = request.get("method")
                req_id = request.get("id")

                log_debug(f"Received request: {method}")

                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "global-scholar-mcp-server", "version": "1.0.0"}
                        }
                    }
                elif method == "tools/list":
                    tool_list = [
                        {
                            "name": info["name"],
                            "description": info["description"],
                            "inputSchema": info["inputSchema"]
                        } for info in self.tools.values()
                    ]
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"tools": tool_list}
                    }
                elif method == "tools/call":
                    params = request.get("params", {})
                    name = params.get("name")
                    arguments = params.get("arguments", {})

                    if name in self.tools:
                        handler = self.tools[name]["handler"]
                        try:
                            result_text = handler(arguments)
                            response = {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "result": {
                                    "content": [{"type": "text", "text": result_text}]
                                }
                            }
                        except Exception as e:
                            log_debug(f"Tool execution error: {str(e)}")
                            response = {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "error": {
                                    "code": -32000,
                                    "message": f"Execution error in tool {name}: {str(e)}"
                                }
                            }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "error": {"code": -32601, "message": f"Tool '{name}' not found."}
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": f"Method '{method}' not implemented."}
                    }

                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except Exception as e:
                log_debug(f"Global loop error: {str(e)}")
                break

if __name__ == "__main__":
    server = ScholarMCPServer()
    server.run()
