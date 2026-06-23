---
name: global-scholar-agent
description: Search for fully funded scholarships and suggest top ranking universities in South Korea, Japan, Germany, Singapore, and Taiwan based on academic profile inputs.
---

# Global Scholar Agent Skill Instructions

Trigger this skill when a student requests university suggestions, scholarship matches, profile evaluations, or Statement of Purpose (SOP) structures.

1. **Information Extraction**:
   - Extract destination preferences (S. Korea, Japan, Germany, Singapore, Taiwan).
   - Extract academic parameters: GPA, major/field, publication count, and IELTS/TOEFL scores.
   
2. **Execution Workflows**:
   - Use the `search_scholarships` and `get_university_suggestions` tools to locate matching university programs.
   - Use `evaluate_resume_match` to calculate candidate eligibility and compile a checklist of gaps.
   - Use `generate_sop_template` to format an outline for the application.

3. **System Setup Commands**:
   - To start backend Flask server: Run `python src/app.py` in project root directory.
   - To start command line interactive loop: Run `python src/main.py`.
   - To open dashboard: Open `dashboard/index.html` in browser.
