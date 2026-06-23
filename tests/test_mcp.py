import subprocess
import json
import sys
import os

def test_scholarship_mcp():
    server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "mcp_server.py")
    
    process = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 1. Initialize Test
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()
    response = json.loads(process.stdout.readline())
    assert response["id"] == 1
    assert response["result"]["serverInfo"]["name"] == "global-scholar-mcp-server"
    print("Initialize Response OK.")

    # 2. Tools List Test
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    process.stdin.write(json.dumps(list_request) + "\n")
    process.stdin.flush()
    response = json.loads(process.stdout.readline())
    assert response["id"] == 2
    tools = response["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "search_scholarships" in tool_names
    assert "evaluate_resume_match" in tool_names
    print("Tools List OK. Found tools:", tool_names)

    # 3. Search Scholarships Test
    search_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_scholarships",
            "arguments": {
                "country": "Japan",
                "field": "Engineering"
            }
        }
    }
    process.stdin.write(json.dumps(search_request) + "\n")
    process.stdin.flush()
    response = json.loads(process.stdout.readline())
    assert response["id"] == 3
    assert "MEXT" in response["result"]["content"][0]["text"]
    print("Search Scholarships Tool OK.")

    # 4. Evaluate Match Test (Success)
    eval_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "evaluate_resume_match",
            "arguments": {
                "scholarship_id": "SCH-GKS",
                "gpa": 3.6,
                "ielts": 7.5,
                "resume_text": "Experienced software researcher. Developed computer vision engines. Academic publications in top journals."
            }
        }
    }
    process.stdin.write(json.dumps(eval_request) + "\n")
    process.stdin.flush()
    response = json.loads(process.stdout.readline())
    assert response["id"] == 4
    report_text = response["result"]["content"][0]["text"]
    assert "Match Evaluation Report" in report_text
    print("Evaluate Resume Match Tool OK.")

    # 5. Security Bounding check (Invalid GPA range)
    bad_gpa_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "evaluate_resume_match",
            "arguments": {
                "scholarship_id": "SCH-GKS",
                "gpa": 5.5,  # GPA out of range
                "ielts": 7.0,
                "resume_text": "Developer resume..."
            }
        }
    }
    process.stdin.write(json.dumps(bad_gpa_request) + "\n")
    process.stdin.flush()
    response = json.loads(process.stdout.readline())
    assert response["id"] == 5
    assert "error" in response
    assert "Security Violation" in response["error"]["message"]
    print("Security GPA Bounding Check OK.")

    # Terminate process
    process.terminate()
    process.wait()
    print("All Global Scholar MCP Server Tests Passed successfully!")

if __name__ == "__main__":
    test_scholarship_mcp()
