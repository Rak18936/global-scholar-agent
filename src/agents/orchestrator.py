import asyncio
import sys
import os
import re
import json

import agents.coordinator as coordinator
import agents.researcher as researcher
import agents.evaluator as evaluator
import database

HAS_SDK = False
try:
    from google.antigravity import Agent
    HAS_SDK = True
except ImportError:
    pass

class ScholarAgentOrchestrator:
    def __init__(self):
        self.logs = []

    def add_log(self, agent_name, message):
        log_entry = f"[{agent_name}] {message}"
        self.logs.append(log_entry)
        try:
            print(log_entry)
        except UnicodeEncodeError:
            clean_log = log_entry.encode('ascii', errors='replace').decode('ascii')
            print(clean_log)

    async def execute_task(self, data):
        self.logs = []
        
        # Check if it is a general chat question (string) or a structured profile match (dict)
        is_chat_question = True
        prompt_str = ""
        
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
                if isinstance(parsed_data, dict):
                    data = parsed_data
                    is_chat_question = False
                else:
                    prompt_str = data
            except Exception:
                prompt_str = data
        elif isinstance(data, dict):
            if "resume_text" in data or "degree" in data:
                is_chat_question = False
            else:
                prompt_str = data.get("prompt", "")
                if not prompt_str:
                    # Fallback
                    prompt_str = str(data)

        if is_chat_question:
            self.add_log("System", f"Processing general query: '{prompt_str[:100]}...'")
            if HAS_SDK and os.environ.get("GEMINI_API_KEY"):
                return await self._run_sdk_orchestration(prompt_str)
            else:
                return await self._run_simulated_orchestration(prompt_str)
        else:
            self.add_log("System", "Initiating Global Scholar Multi-Agent pipeline...")
            return await self._run_structured_pipeline(data)

    async def _run_sdk_orchestration(self, prompt):
        self.add_log("System", "Running using active Google Antigravity SDK.")
        coord_config = coordinator.get_config()
        research_config = researcher.get_config()
        eval_config = evaluator.get_config()

        try:
            async with Agent(coord_config) as coord_agent:
                self.add_log("Coordinator", "Analyzing academic parameters and query criteria...")
                response = await coord_agent.chat(f"Triage and plan scholarship search: {prompt}")
                plan = "".join([t async for t in response])
                
                async with Agent(research_config) as research_agent:
                    self.add_log("Researcher", "Querying scholarship databases and university rankings...")
                    res_response = await research_agent.chat(f"Find scholarships and universities matching: {plan}")
                    raw_data = "".join([t async for t in res_response])
                    
                    async with Agent(eval_config) as eval_agent:
                        self.add_log("Evaluator", "Cross-referencing resume text and calculating GPA/IELTS alignments...")
                        eval_response = await eval_agent.chat(f"Evaluate candidate profile gaps and draft SOP format based on: {raw_data} and user prompt: {prompt}")
                        evaluation = "".join([t async for t in eval_response])
                
                final_response = await coord_agent.chat(f"Construct final encouraging summary report based on: {evaluation}")
                report = "".join([t async for t in final_response])
                self.add_log("Coordinator", "Consolidated scholar summary completed.")

                return {
                    "status": "Success",
                    "logs": self.logs,
                    "result": report
                }
        except Exception as e:
            self.add_log("System", f"SDK execution failed: {str(e)}. Triggering Local Simulator.")
            return await self._run_simulated_orchestration(prompt)

    async def _run_simulated_orchestration(self, prompt):
        self.add_log("System", "Running in high-fidelity Local Scholarship Simulator.")
        await asyncio.sleep(0.3)

        p_lower = prompt.lower()
        
        # Extrapolate mock profile from string prompt
        gpa = 3.4
        ielts = 6.5
        major = "Engineering"
        country = "Any"
        has_publications = False

        gpa_match = re.search(r"gpa\s*(?:is|of)?\s*:?\s*([0-9]\.[0-9]+)", p_lower)
        if gpa_match:
            gpa = float(gpa_match.group(1))

        if "no language" in p_lower or "no ielts" in p_lower or "without language" in p_lower or "none" in p_lower:
            ielts = 0.0
        else:
            ielts_match = re.search(r"(?:ielts|toefl|language)\s*(?:is|of|score)?\s*:?\s*([0-9](?:\.[0-9]+)?)", p_lower)
            if ielts_match:
                ielts = float(ielts_match.group(1))

        if "computer" in p_lower or "software" in p_lower or "engineering" in p_lower or "tech" in p_lower:
            major = "Engineering"
        elif "science" in p_lower or "bio" in p_lower or "physics" in p_lower or "chem" in p_lower:
            major = "Science"
        elif "business" in p_lower or "mba" in p_lower or "finance" in p_lower:
            major = "Business"
        elif "humanities" in p_lower or "arts" in p_lower or "history" in p_lower:
            major = "Humanities"

        # Check target countries
        if "korea" in p_lower:
            country = "South Korea"
        elif "japan" in p_lower:
            country = "Japan"
        elif "germany" in p_lower:
            country = "Germany"
        elif "singapore" in p_lower:
            country = "Singapore"
        elif "taiwan" in p_lower:
            country = "Taiwan"

        if "publication" in p_lower or "journal" in p_lower or "published" in p_lower:
            has_publications = True

        # Map to structured flow for consistency
        mock_data = {
            "resume_text": f"Candidate seeking graduate studies in {major} with GPA {gpa} and IELTS score {ielts}. " + ("Has published papers." if has_publications else "No papers."),
            "degree": "PhD" if "phd" in p_lower or "ph.d" in p_lower else "Master's",
            "country_mode": "single" if country != "Any" else "auto",
            "selected_countries": [country] if country != "Any" else [],
            "gpa": gpa,
            "gpa_scale": "4.0",
            "lang_type": "IELTS",
            "ielts": ielts,
            "major": major,
            "pub_status": "Published" if has_publications else "None"
        }
        
        return await self._run_structured_pipeline(mock_data)

    async def _run_structured_pipeline(self, data):
        resume_text = data.get("resume_text", "").strip() or "Candidate resume details not available."
        raw_degree = data.get("degree", "Master's")
        degree_pref = "Master" if "master" in raw_degree.lower() else "PhD"
        country_mode = data.get("country_mode", "auto")
        selected_countries = data.get("selected_countries", [])
        
        # Advanced overrides (from frontend form, if available)
        overrides = {}
        if "gpa" in data:
            overrides["gpa"] = data.get("gpa")
            overrides["gpa_scale"] = data.get("gpa_scale", "4.0")
        if "lang_type" in data:
            overrides["lang_type"] = data.get("lang_type")
            overrides["ielts"] = data.get("ielts", 0.0)
        if "major" in data:
            overrides["major"] = data.get("major")
        if "pub_status" in data:
            overrides["pub_status"] = data.get("pub_status")

        # Step 1: Resume Parser Agent
        self.add_log("System", "📄 Reading Resume...")
        await asyncio.sleep(0.2)
        self.add_log("Coordinator", "👤 Building Academic Profile...")
        parsed_profile = self._parse_resume_text(resume_text, degree_pref, overrides)
        await asyncio.sleep(0.2)

        # Extract normalized numerical parameters for evaluation
        gpa = self._extract_float_gpa(parsed_profile["CGPA or GPA"])
        ielts = self._extract_float_ielts(parsed_profile["Language Scores"])
        major = self._normalize_major(parsed_profile["Major"])
        has_publications = parsed_profile["Publications"] != "Not Available" and "none" not in parsed_profile["Publications"].lower()
        has_research = parsed_profile["Research Experience"] != "Not Available"

        # Step 2: Profile Intelligence Agent
        # Calculate scores 0-100
        acad_score, acad_reason = self._calc_academic_strength(gpa, parsed_profile["Awards"])
        res_score, res_reason = self._calc_research_strength(has_publications, has_research, parsed_profile["Projects"])
        lang_is_exempt = "exempt" in parsed_profile["Language Scores"].lower()
        lang_is_none = "none" in parsed_profile["Language Scores"].lower() or ielts == 0.0
        
        lang_readiness, lang_reason = self._calc_language_readiness(ielts, lang_is_exempt, lang_is_none)
        sch_score, sch_reason = self._calc_scholarship_readiness(acad_score, res_score, lang_readiness, lang_is_none)

        # Step 3: Country Selection Modes & Rankings
        self.add_log("Coordinator", "🌍 Finding Best-Fit Countries...")
        await asyncio.sleep(0.2)
        
        target_countries = []
        if country_mode == "single" and selected_countries:
            target_countries = [selected_countries[0]]
        elif country_mode == "multiple" and selected_countries:
            target_countries = [c for c in selected_countries if c in ["South Korea", "Japan", "Germany", "Singapore", "Taiwan"]]
            if not target_countries:
                target_countries = ["South Korea", "Japan", "Germany", "Singapore", "Taiwan"]
        else:
            target_countries = ["South Korea", "Japan", "Germany", "Singapore", "Taiwan"]

        ranked_countries = self._rank_countries(target_countries, major, gpa, ielts, lang_is_exempt, degree_pref)

        # Step 4: University Discovery Agent
        self.add_log("Researcher", "🏫 Discovering Universities...")
        await asyncio.sleep(0.2)
        
        all_unis = database.get_universities()
        all_scholarships = database.get_scholarships()
        
        # Pre-classify scholarships for lookup
        classified_all_scholarships = []
        for sch in all_scholarships:
            name_lower = sch["name"].lower()
            provider_lower = sch["provider"].lower()
            if "government" in name_lower or "government" in provider_lower or "ministry" in provider_lower or "niied" in provider_lower or "daad" in name_lower or "mext" in name_lower or "singa" in name_lower or "tigp" in name_lower or "moe" in name_lower:
                funding_type = "Fully Funded Government Scholarship"
                priority_group = 1
            else:
                funding_type = "University Graduate Scholarship"
                priority_group = 2
            sch_copied = dict(sch)
            sch_copied["funding_type"] = funding_type
            sch_copied["priority_group"] = priority_group
            classified_all_scholarships.append(sch_copied)
            
        matched_unis = []
        for uni in all_unis:
            if uni["country"] not in target_countries:
                continue
            if major not in uni["fields"]:
                continue
                
            # Assign realistic Department and Program based on candidates preferences
            dept, prog = self._assign_dept_program(uni, major, degree_pref)
            
            # Calculate Match Score factors
            score = self._calc_university_match_score(uni, gpa, ielts, lang_is_exempt, lang_is_none, degree_pref, has_publications)
            
            # Competitiveness Level
            comp_level = self._calc_university_competitiveness(uni, gpa, ielts, has_publications)
            
            # Scholarships in that country
            country_scholarships = [s for s in classified_all_scholarships if s["country"] == uni["country"] and major in s["eligible_fields"]]
            available_sch_names = [s["name"] for s in country_scholarships if degree_pref in s["degree_levels"]]
            
            funding_source = "Funding information unavailable"
            if available_sch_names:
                funding_source = ", ".join(available_sch_names)
            else:
                # Identify at least one alternative funding source for this university recommendation
                if uni["country"] == "Germany":
                    funding_source = "Deutschlandstipendium / DAAD EPOS alternative funding"
                elif uni["country"] == "Singapore":
                    funding_source = "NUS/NTU Research Fellowship / Graduate RA"
                elif uni["country"] == "South Korea":
                    funding_source = "KAIST/SNU Graduate Assistantship / Professor RA"
                elif uni["country"] == "Japan":
                    funding_source = "MEXT alternative university recommendation / RA"
                elif uni["country"] == "Taiwan":
                    funding_source = "TIGP / Academia Sinica lab research funding"
            
            # Research Alignment
            res_align = "High" if has_publications or has_research else "Medium" if parsed_profile["Projects"] != "Not Available" else "Low"
            
            # Reqs summary
            req_gpa = 3.2 if uni["rank"] < 50 else 3.0
            req_ielts = 6.5 if uni["rank"] < 100 else 6.0
            reqs_summary = f"Min GPA: {req_gpa}/4.0, English proficiency (IELTS {req_ielts} equivalent), SOP, Resume, 2 Letters of Recommendation."

            matched_unis.append({
                "name": uni["name"],
                "country": uni["country"],
                "department": dept,
                "program": prog,
                "match_score": score,
                "competitiveness": comp_level,
                "why_recommended": f"Strong alignment with {major} field. Matches department strengths at {uni['name']} with excellent funding potential.",
                "scholarships": funding_source,
                "research_alignment": res_align,
                "requirements": reqs_summary
            })

        # Rank universities by suitability
        matched_unis.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Enforce Minimum 10, Maximum 15 universities (or recommend all available if database has fewer than 10 total)
        final_recommendations = []
        if len(matched_unis) >= 10:
            final_recommendations = matched_unis[:min(15, len(matched_unis))]
        else:
            final_recommendations = matched_unis

        # Step 5: Scholarship Matching Agent
        self.add_log("Researcher", "💰 Matching Scholarships...")
        await asyncio.sleep(0.2)
        
        matched_scholarships = []
        for sch in classified_all_scholarships:
            if sch["country"] not in target_countries:
                continue
            if major not in sch["eligible_fields"]:
                continue
            if degree_pref not in sch["degree_levels"]:
                continue
                
            sch_match_score = 100
            explanation_parts = []
            
            # GPA Check
            if gpa >= sch["min_gpa"]:
                explanation_parts.append(f"GPA {gpa:.2f} satisfies the minimum of {sch['min_gpa']}.")
            else:
                sch_match_score -= 30
                explanation_parts.append(f"GPA {gpa:.2f} is below the recommended {sch['min_gpa']}.")
                
            # Language Check
            if lang_is_exempt:
                explanation_parts.append("Exempt from language scores due to English medium background.")
            elif lang_is_none:
                sch_match_score -= 25
                explanation_parts.append(f"Requires IELTS {sch['min_ielts']} but no test was uploaded.")
            elif ielts >= sch["min_ielts"]:
                explanation_parts.append(f"Language score IELTS {ielts:.1f} meets requirement of {sch['min_ielts']}.")
            else:
                sch_match_score -= 25
                explanation_parts.append(f"IELTS {ielts:.1f} is below target threshold of {sch['min_ielts']}.")
                
            # Research Factor
            if sch["id"] in ["SCH-SINGA", "SCH-TIGP", "SCH-SPF"]: # Research heavy PhDs
                if has_publications:
                    explanation_parts.append("Has scientific publications, which is optimal for research fellowships.")
                else:
                    sch_match_score -= 15
                    explanation_parts.append("Missing publications, which are highly recommended for this fellowship.")
            else:
                if has_publications:
                    explanation_parts.append("Publications provide an additional competitive edge.")
                    
            sch_match_score = max(0, sch_match_score)
            
            # Rank scholarships using: Eligibility Match (40%), Funding Amount (30%), Profile Fit (20%), Competitiveness (10%)
            elig_factor = sch_match_score
            funding_factor = 100 if sch["priority_group"] == 1 else 85
            fit_factor = 95 if (major in ["Engineering", "Science"] and sch["id"] in ["SCH-SINGA", "SCH-TIGP", "SCH-KAIST"]) else 80
            comp_factor = 90 if sch["priority_group"] == 1 else 75
            
            rank_score = int(elig_factor * 0.4 + funding_factor * 0.3 + fit_factor * 0.2 + (100 - comp_factor) * 0.1)
            
            # Priority Level
            priority = "Low Priority"
            if sch_match_score >= 85:
                priority = "High Priority"
            elif sch_match_score >= 60:
                priority = "Medium Priority"
                
            matched_scholarships.append({
                "name": sch["name"],
                "country": sch["country"],
                "funding_type": sch["funding_type"],
                "coverage": sch["coverage"],
                "match_score": sch_match_score,
                "rank_score": rank_score,
                "priority_group": sch["priority_group"],
                "explanation": " ".join(explanation_parts),
                "priority": priority,
                "documents": ", ".join(sch.get("required_documents", ["CV", "SOP", "Transcripts", "Recommendation Letters"]))
            })

        # Append alternative scholarships dynamically for target countries to ensure Priorities 3, 4, 5, 6 are covered
        for country in target_countries:
            # Priority 3: Department Scholarship
            dept_score = max(0, int(gpa / 4.0 * 90))
            dept_elig = f"Departmental review of GPA ({gpa:.2f}/4.0) satisfies merit parameters."
            matched_scholarships.append({
                "name": f"{country} Graduate Departmental Fellowship",
                "country": country,
                "funding_type": "Department Scholarship",
                "coverage": "Partial to Full Tuition Waiver from departmental funds",
                "match_score": dept_score,
                "rank_score": int(dept_score * 0.4 + 65 * 0.3 + 80 * 0.2 + 35 * 0.1),
                "priority_group": 3,
                "explanation": dept_elig,
                "priority": "High Priority" if dept_score >= 80 else "Medium Priority",
                "documents": "CV, Academic transcripts, Statement of Purpose"
            })
            
            # Priority 4: Research Assistantship (RA)
            ra_score = 90 if has_publications or has_research else 70
            ra_elig = "Strong fit due to documented research publications/projects." if (has_publications or has_research) else "Requires advisor outreach showing lab engineering skills."
            matched_scholarships.append({
                "name": f"Graduate Research Assistantship (GRA) - {country}",
                "country": country,
                "funding_type": "Research Assistantship (RA)",
                "coverage": "Full Tuition Waiver + Monthly Research Stipend (advisor funded)",
                "match_score": ra_score,
                "rank_score": int(ra_score * 0.4 + 75 * 0.3 + (95 if has_publications else 80) * 0.2 + 40 * 0.1),
                "priority_group": 4,
                "explanation": ra_elig,
                "priority": "High Priority" if ra_score >= 80 else "Medium Priority",
                "documents": "Research Proposal, Technical Portfolio, Resume/CV, Advisor Cover Letter"
            })
            
            # Priority 5: Teaching Assistantship (TA)
            ta_score = 80 if not lang_is_none else 50
            ta_elig = "Standard English test scores fit assistantship communication requirements." if not lang_is_none else "Standard English test score is required to run lecture/grading sessions."
            matched_scholarships.append({
                "name": f"Graduate Teaching Assistantship (GTA) - {country}",
                "country": country,
                "funding_type": "Teaching Assistantship (TA)",
                "coverage": "Full or Partial Tuition Waiver + Monthly Teaching Stipend",
                "match_score": ta_score,
                "rank_score": int(ta_score * 0.4 + 70 * 0.3 + 80 * 0.2 + 50 * 0.1),
                "priority_group": 5,
                "explanation": ta_elig,
                "priority": "High Priority" if ta_score >= 80 else "Medium Priority" if ta_score >= 60 else "Low Priority",
                "documents": "Language scores, Faculty reference letters, GTA application sheet"
            })
            
            # Priority 6: Partial Tuition Scholarship
            partial_score = 95
            partial_elig = "General international student fee reduction program."
            matched_scholarships.append({
                "name": f"International Student Tuition Reduction - {country}",
                "country": country,
                "funding_type": "Partial Tuition Scholarship",
                "coverage": "20% to 50% tuition fee waiver based on semester GPA",
                "match_score": partial_score,
                "rank_score": int(partial_score * 0.4 + 45 * 0.3 + 80 * 0.2 + 60 * 0.1),
                "priority_group": 6,
                "explanation": partial_elig,
                "priority": "High Priority",
                "documents": "University Admission Letter, Enrolled student transcript"
            })

        # Sort scholarships: Priority Group ascending (Priority 1 to 6), and then Rank Score descending
        matched_scholarships.sort(key=lambda x: (x["priority_group"], -x["rank_score"]))

        # Step 6: Eligibility Verification Agent
        # Classifications: Eligible, Partially Eligible, Not Eligible + evidence
        acad_elig, acad_ev = self._verify_eligibility_academic(gpa, all_scholarships, target_countries)
        lang_elig, lang_ev = self._verify_eligibility_language(ielts, lang_is_exempt, lang_is_none, all_scholarships, target_countries)
        res_elig, res_ev = self._verify_eligibility_research(has_publications, has_research, degree_pref)
        sch_elig, sch_ev = self._verify_eligibility_scholarship(gpa, ielts, lang_is_exempt, lang_is_none, all_scholarships, target_countries, degree_pref)

        # Step 7: Admission Competitiveness Agent
        self.add_log("Evaluator", "📊 Calculating Competitiveness...")
        await asyncio.sleep(0.2)
        
        overall_comp_score = int(acad_score * 0.4 + res_score * 0.3 + lang_readiness * 0.3)
        overall_comp_level = "Moderate"
        if overall_comp_score >= 85:
            overall_comp_level = "Highly Competitive"
        elif overall_comp_score >= 70:
            overall_comp_level = "Competitive"
        elif overall_comp_score >= 50:
            overall_comp_level = "Moderate"
        else:
            overall_comp_level = "Easy"

        # Step 8: Roadmap Planning Agent
        self.add_log("Evaluator", "📅 Creating Application Roadmap...")
        await asyncio.sleep(0.2)
        
        roadmap_milestones = self._generate_roadmap(lang_is_none, degree_pref, has_publications)

        # Step 9: Best Overall Opportunity Agent
        best_opp = self._determine_best_opportunity(final_recommendations, matched_scholarships)

        # Compile final markdown report with the EXACT 9 sections
        report = self._format_markdown_report(
            parsed_profile,
            ranked_countries,
            final_recommendations,
            matched_scholarships,
            (acad_elig, acad_ev, lang_elig, lang_ev, res_elig, res_ev, sch_elig, sch_ev),
            (overall_comp_score, overall_comp_level),
            (lang_is_none, degree_pref, has_publications),
            roadmap_milestones,
            best_opp,
            acad_score, acad_reason,
            res_score, res_reason,
            sch_score, sch_reason,
            lang_readiness, lang_reason
        )

        self.add_log("System", "✅ Your Personalized Study-Abroad Plan is Ready")
        
        return {
            "status": "Success",
            "logs": self.logs,
            "result": report
        }

    # --- HEURISTIC HELPERS ---
    
    def _parse_resume_text(self, resume_text, degree_pref, overrides):
        parsed = {
            "Degree": "Not Available",
            "Major": "Not Available",
            "CGPA or GPA": "Not Available",
            "Skills": "Not Available",
            "Programming Languages": "Not Available",
            "Projects": "Not Available",
            "Internships": "Not Available",
            "Work Experience": "Not Available",
            "Research Experience": "Not Available",
            "Publications": "Not Available",
            "Certifications": "Not Available",
            "Awards": "Not Available",
            "Leadership Activities": "Not Available",
            "Language Scores": "Not Available",
            "Career Interests": "Not Available"
        }
        
        text_lower = resume_text.lower()
        
        # 1. Degree
        parsed["Degree"] = degree_pref
        
        # 2. Major
        major_list = []
        if "computer science" in text_lower or "software engineering" in text_lower or "information technology" in text_lower or "programming" in text_lower or "developer" in text_lower:
            major_list.append("Engineering")
        elif "mechanical" in text_lower or "electrical" in text_lower or "civil" in text_lower or "chemical" in text_lower:
            major_list.append("Engineering")
        if "physics" in text_lower or "chemistry" in text_lower or "biology" in text_lower or "biotech" in text_lower or "mathematics" in text_lower or "science" in text_lower:
            major_list.append("Science")
        if "business" in text_lower or "mba" in text_lower or "finance" in text_lower or "economics" in text_lower or "accounting" in text_lower:
            major_list.append("Business")
        if "literature" in text_lower or "history" in text_lower or "arts" in text_lower or "linguistics" in text_lower or "philosophy" in text_lower:
            major_list.append("Humanities")
            
        if overrides.get("major"):
            parsed["Major"] = overrides.get("major")
        elif major_list:
            parsed["Major"] = major_list[0]
        else:
            parsed["Major"] = "Engineering" # default fallback
            
        # 3. CGPA or GPA
        gpa_found = None
        gpa_match = re.search(r"(?:gpa|cgpa)\s*[:=-]?\s*([0-9]\.[0-9]{1,2})\s*/\s*(4\.0|4|10\.0|10)", text_lower)
        if gpa_match:
            gpa_found = f"{gpa_match.group(1)} / {gpa_match.group(2)}"
        else:
            gpa_match2 = re.search(r"(?:gpa|cgpa)\s*[:=-]?\s*([0-9]\.[0-9]{1,2})", text_lower)
            if gpa_match2:
                val = float(gpa_match2.group(1))
                if val <= 4.0:
                    gpa_found = f"{val} / 4.0"
                elif val <= 10.0:
                    gpa_found = f"{val} / 10.0"
                    
        if not gpa_found:
            pct_match = re.search(r"([5-9][0-9](?:\.[0-9]+)?)\s*%", text_lower)
            if pct_match:
                gpa_found = f"{pct_match.group(1)}%"
                
        raw_gpa_val = 3.2
        raw_scale_val = "4.0"
        
        if overrides.get("gpa"):
            raw_gpa_val = float(overrides.get("gpa"))
            raw_scale_val = overrides.get("gpa_scale", "4.0")
        elif gpa_found:
            if "/" in gpa_found:
                p_parts = gpa_found.split("/")
                raw_gpa_val = float(p_parts[0].strip())
                raw_scale_val = p_parts[1].strip()
            elif "%" in gpa_found:
                raw_gpa_val = float(gpa_found.replace("%", "").strip())
                raw_scale_val = "100"
        
        # Calculate standard 4.0 GPA
        gpa_4_0 = raw_gpa_val
        if raw_scale_val == "10.0" or raw_scale_val == "10":
            gpa_4_0 = (raw_gpa_val / 10.0) * 4.0
            parsed["CGPA"] = f"{raw_gpa_val:.2f} / 10.0"
        elif raw_scale_val == "100" or raw_scale_val == "100.0":
            gpa_4_0 = (raw_gpa_val / 100.0) * 4.0
            parsed["CGPA"] = f"{raw_gpa_val:.1f}%"
        else:
            parsed["CGPA"] = "Not Available"
            
        parsed["Academic GPA (4.0 scale)"] = f"{gpa_4_0:.2f} / 4.0"
        parsed["CGPA or GPA"] = f"{raw_gpa_val} / {raw_scale_val}"

        # 4. Programming Languages
        langs = []
        for lang in ["python", "java", "c\\+\\+", "javascript", "c#", "go", "rust", "typescript", "html", "css", "sql", "matlab", " r "]:
            clean_l = lang.replace("\\", "")
            if re.search(r"\b" + lang + r"\b", text_lower):
                langs.append(clean_l.strip().upper())
        if langs:
            parsed["Programming Languages"] = ", ".join(langs)
            
        # 5. Skills
        skills = []
        skills_dict = {
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "data science": "Data Science",
            "project management": "Project Management",
            "software development": "Software Development",
            "algorithms": "Algorithms & Data Structures",
            "research methodology": "Research Methodology",
            "git": "Git/Version Control",
            "cad": "Computer-Aided Design (CAD)",
            "data analysis": "Data Analysis",
            "lab techniques": "Laboratory Techniques"
        }
        for k, v in skills_dict.items():
            if k in text_lower:
                skills.append(v)
        if skills:
            parsed["Skills"] = ", ".join(skills)
            
        # 6. Projects
        project_matches = re.findall(r"(?:project|developed|built|designed)\s*[:=-]?\s*([^\n\.\,]{10,80})", text_lower)
        if project_matches:
            parsed["Projects"] = "; ".join([p.strip().title() for p in project_matches[:3]])
            
        # 7. Internships
        intern_matches = re.findall(r"(?:intern|internship)\s*at\s*([^\n\.\,]{3,50})", text_lower)
        if intern_matches:
            parsed["Internships"] = ", ".join([i.strip().title() for i in intern_matches])
        elif "intern" in text_lower:
            parsed["Internships"] = "Technical Intern"
            
        # 8. Work Experience
        jobs = []
        job_titles = ["software engineer", "developer", "researcher", "analyst", "assistant", "manager", "engineer"]
        for title in job_titles:
            if title in text_lower:
                jobs.append(title.title())
        if jobs:
            parsed["Work Experience"] = ", ".join(set(jobs))
        elif "experience" in text_lower:
            parsed["Work Experience"] = "Graduate Assistant"

        # 9. Research Experience
        if "research assistant" in text_lower or "research intern" in text_lower or "lab assistant" in text_lower:
            parsed["Research Experience"] = "Research Assistant / Lab Experience"
        elif "research" in text_lower:
            parsed["Research Experience"] = "Academic Research Projects"
            
        # 10. Publications
        pub_matches = re.findall(r"(?:publication|published|journal|conference|paper)\s*[:=-]?\s*([^\n\.]{15,100})", text_lower)
        if overrides.get("pub_status") == "Published":
            parsed["Publications"] = "Published Paper (Conference/Journal)"
        elif pub_matches:
            parsed["Publications"] = "; ".join([p.strip() for p in pub_matches[:2]])
        elif "publication" in text_lower or "journal" in text_lower or "published" in text_lower:
            parsed["Publications"] = "Research Paper publication"

        # 11. Certifications
        certs = []
        for c in ["aws", "google", "coursera", "udemy", "azure", "cisco", "pmp"]:
            if c in text_lower:
                certs.append(c.upper())
        if certs:
            parsed["Certifications"] = ", ".join(certs)

        # 12. Awards
        awards = []
        for a in ["scholarship", "dean's list", "award", "honor", "medal", "fellowship"]:
            if a in text_lower:
                awards.append(a.title() + " recipient")
        if awards:
            parsed["Awards"] = ", ".join(set(awards[:3]))

        # 13. Leadership Activities
        leaders = []
        for l in ["president", "founder", "lead", "volunteer", "chairman", "club leader"]:
            if l in text_lower:
                leaders.append(l.title())
        if leaders:
            parsed["Leadership Activities"] = ", ".join(set(leaders))

        # 14. Language Scores
        lang_info = []
        ielts_match = re.search(r"ielts\s*[:=-]?\s*([4-9](?:\.[0-9])?)", text_lower)
        if ielts_match:
            lang_info.append(f"IELTS: {ielts_match.group(1)}")
        toefl_match = re.search(r"toefl\s*[:=-]?\s*([6-9][0-9]|1[0-1][0-9]|120)", text_lower)
        if toefl_match:
            lang_info.append(f"TOEFL: {toefl_match.group(1)}")
            
        if overrides.get("lang_type") and overrides.get("lang_type") not in ["None", "Exempt"]:
            parsed["Language Scores"] = f"{overrides.get('lang_type')}: {overrides.get('ielts')}"
        elif overrides.get("lang_type") == "Exempt":
            parsed["Language Scores"] = "Exempt (English Medium Instruction)"
        elif overrides.get("lang_type") == "None":
            parsed["Language Scores"] = "None"
        elif lang_info:
            parsed["Language Scores"] = ", ".join(lang_info)
        else:
            parsed["Language Scores"] = "None"

        # 15. Career Interests
        interests = []
        for interest in ["researcher", "professor", "data scientist", "software engineer", "machine learning engineer"]:
            if interest in text_lower:
                interests.append(interest.title())
        if interests:
            parsed["Career Interests"] = ", ".join(interests)

        return parsed

    def _extract_float_gpa(self, gpa_str):
        if not gpa_str or gpa_str == "Not Available":
            return 3.0
        try:
            parts = gpa_str.split("/")
            if len(parts) == 2:
                val = float(parts[0].strip())
                scale = float(parts[1].strip())
                if scale == 10.0:
                    return (val / 10.0) * 4.0
                elif scale == 100.0:
                    return (val / 100.0) * 4.0
                return val
            if "%" in gpa_str:
                val = float(gpa_str.replace("%", "").strip())
                return (val / 100.0) * 4.0
            return float(gpa_str.strip())
        except Exception:
            return 3.0

    def _extract_float_ielts(self, lang_str):
        if not lang_str or "none" in lang_str.lower() or lang_str == "Not Available":
            return 0.0
        if "exempt" in lang_str.lower():
            return 9.0
        try:
            match = re.search(r"ielts\s*[:=-]?\s*([0-9](?:\.[0-9])?)", lang_str.lower())
            if match:
                return float(match.group(1))
            match_toefl = re.search(r"toefl\s*[:=-]?\s*([0-9]+)", lang_str.lower())
            if match_toefl:
                val = float(match_toefl.group(1))
                if val >= 110: return 8.5
                elif val >= 100: return 7.5
                elif val >= 90: return 7.0
                elif val >= 80: return 6.5
                elif val >= 60: return 6.0
                return 5.0
            return 6.5
        except Exception:
            return 6.5

    def _normalize_major(self, major_str):
        if not major_str or major_str == "Not Available":
            return "Engineering"
        m_lower = major_str.lower()
        if "science" in m_lower or "physics" in m_lower or "chemistry" in m_lower or "biology" in m_lower or "biotech" in m_lower:
            return "Science"
        elif "business" in m_lower or "economics" in m_lower or "finance" in m_lower:
            return "Business"
        elif "humanities" in m_lower or "arts" in m_lower or "literature" in m_lower or "history" in m_lower:
            return "Humanities"
        return "Engineering"

    def _calc_academic_strength(self, gpa, awards_str):
        score = int((gpa / 4.0) * 100)
        score = min(100, max(0, score))
        
        bonus = 0
        if awards_str != "Not Available":
            bonus += 5
        score = min(100, score + bonus)
        
        reason = f"Based on a normalized GPA of {gpa:.2f}/4.0."
        if bonus > 0:
            reason += " Additional score credit applied for documented academic awards/honors."
        else:
            reason += " Relevant technical coursework supports basic academic strength."
        return score, reason

    def _calc_research_strength(self, has_pub, has_res, proj_str):
        if has_pub:
            score = 92
            reason = "Excellent research foundation demonstrated by peer-reviewed publications."
        elif has_res:
            score = 75
            reason = "Good academic research experience, such as a lab internship or senior thesis project."
        elif proj_str != "Not Available":
            score = 60
            reason = "Moderate research potential proved by practical coursework engineering projects."
        else:
            score = 35
            reason = "Limited scientific research history or project documentation in profile."
        return score, reason

    def _calc_language_readiness(self, ielts, is_exempt, is_none):
        if is_exempt:
            return 95, "Exempt from standardized test requirement. Candidate completed previous degree in English medium."
        elif is_none or ielts == 0.0:
            return 30, "No language proficiency scores detected. Standard English certifications are required for admission."
        elif ielts >= 7.5:
            return 98, f"Outstanding English proficiency (IELTS {ielts:.1f} equivalent). Meets and exceeds all threshold standards."
        elif ielts >= 6.5:
            return 85, f"Good English proficiency (IELTS {ielts:.1f} equivalent). Compatible with top-tier university expectations."
        elif ielts >= 6.0:
            return 70, f"Satisfactory English proficiency (IELTS {ielts:.1f}). Meets standard admission baselines, but may fall short for top fellowships."
        else:
            return 45, f"Lower IELTS score ({ielts:.1f}). Submitting higher test scores is recommended to secure funding."

    def _calc_scholarship_readiness(self, acad, res, lang, is_none):
        score = int(acad * 0.4 + res * 0.3 + lang * 0.3)
        if is_none:
            score = min(60, score)
            reason = "Readiness is limited by the absence of an English test score. Most fully funded international scholarships require language proof."
        else:
            reason = "High readiness stemming from solid academic foundation, language scores, and project records."
            if acad >= 85 and res >= 75:
                reason = "Highly ready for graduate fellowships due to excellent GPA and verified research alignment."
        return score, reason

    def _rank_countries(self, target_countries, major, gpa, ielts, is_exempt, degree_pref):
        rankings = []
        strengths = {
            "South Korea": {
                "score_base": 88,
                "reason": "Strong scholarship ecosystem (GKS covers all tuition, flight, and monthly allowance) and high-tech research opportunities."
            },
            "Japan": {
                "score_base": 85,
                "reason": "MEXT Research Fellowship offers full funding and monthly stipends. Excellent STEM and Humanities research facilities."
            },
            "Germany": {
                "score_base": 90,
                "reason": "Very low/no tuition fees at public universities, strong engineering programs, and solid DAAD scholarship coverage."
            },
            "Singapore": {
                "score_base": 80,
                "reason": "Home to world-class QS top-10 universities (NUS/NTU). SINGA offers full funding specifically for PhD tracks."
            },
            "Taiwan": {
                "score_base": 78,
                "reason": "Excellent technology research sector (semiconductors/STEM). Generous MOE and Academia Sinica TIGP fellowships."
            }
        }
        
        for country in target_countries:
            details = strengths[country]
            score = details["score_base"]
            
            if major in ["Engineering", "Science"] and country in ["South Korea", "Singapore", "Taiwan"]:
                score += 5
            if degree_pref == "PhD" and country == "Singapore":
                score += 8
            if degree_pref == "Master" and country == "Singapore":
                score -= 10
                
            if gpa >= 3.5:
                score += 2
            else:
                if country in ["Singapore"]:
                    score -= 8
                    
            score = min(100, max(0, score))
            rankings.append({
                "country": country,
                "score": score,
                "reason": details["reason"]
            })
            
        rankings.sort(key=lambda x: x["score"], reverse=True)
        return rankings

    def _assign_dept_program(self, uni, major, degree_pref):
        deg_abbr = "M.S." if degree_pref == "Master" else "Ph.D."
        
        if major == "Engineering":
            return "College of Engineering", f"{deg_abbr} in Computer Science & Engineering"
        elif major == "Science":
            return "Department of Natural Sciences", f"{deg_abbr} in Physics & Applied Sciences"
        elif major == "Business":
            return "Graduate School of Business", f"{deg_abbr} in Finance & Economics"
        else:
            return "Department of Humanities", f"{deg_abbr} in Applied Linguistics & Intercultural Studies"

    def _calc_university_match_score(self, uni, gpa, ielts, is_exempt, is_none, degree_pref, has_pub):
        score = 90
        rank = uni["rank"]
        if rank < 50:
            target_gpa = 3.6
            target_ielts = 7.0
        elif rank < 200:
            target_gpa = 3.3
            target_ielts = 6.5
        else:
            target_gpa = 3.0
            target_ielts = 6.0
            
        if gpa < target_gpa:
            diff = target_gpa - gpa
            score -= int(diff * 35)
            
        if not is_exempt:
            if is_none:
                score -= 15
            elif ielts < target_ielts:
                score -= 12
                
        if degree_pref == "PhD":
            if not has_pub:
                score -= 10
                
        return min(100, max(40, score))

    def _calc_university_competitiveness(self, uni, gpa, ielts, has_pub):
        rank = uni["rank"]
        if rank < 30:
            return "Highly Competitive"
        elif rank < 100:
            if gpa >= 3.6 and (ielts >= 7.0 or has_pub):
                return "Competitive"
            return "Highly Competitive"
        elif rank < 250:
            if gpa >= 3.3:
                return "Moderate"
            return "Competitive"
        else:
            return "Easy"

    def _verify_eligibility_academic(self, gpa, scholarships, countries):
        min_needed = 3.0
        for s in scholarships:
            if s["country"] in countries:
                min_needed = min(min_needed, s["min_gpa"])
                
        if gpa >= 3.4:
            return "Eligible", f"GPA of {gpa:.2f}/4.0 is comfortably above the standard admission cutoff of 3.0-3.2."
        elif gpa >= min_needed:
            return "Partially Eligible", f"GPA of {gpa:.2f}/4.0 meets the absolute minimum of {min_needed} for some programs, but is competitive only for mid-tier options."
        else:
            return "Not Eligible", f"GPA of {gpa:.2f}/4.0 is below the required baseline of {min_needed} for major fully-funded programs."

    def _verify_eligibility_language(self, ielts, is_exempt, is_none, scholarships, countries):
        # 1. Missing Language Scores Rule (Rule Check for no language test provided)
        if is_none or ielts == 0.0:
            return "Language Score Not Found in Resume.", "Language Score Not Found in Resume. Language requirements depend on the selected university, scholarship, and program. Further verification required using official admission requirements."

        # 2. Country-Specific Validation Rules
        eval_parts = []
        primary_status = "Requirement Information Unavailable"
        
        for country in countries:
            if country == "South Korea":
                # Do NOT assume IELTS or TOEFL is mandatory (various proofs like MOI are accepted)
                if is_exempt:
                    status = "✓ Alternative Proof Accepted"
                    desc = "Medium of Instruction Certificate (MOI) may be accepted by KAIST, SNU, Yonsei, or Korea University."
                else:
                    gks_ielts = 6.0
                    kaist_ielts = 6.5
                    if ielts >= kaist_ielts:
                        status = "✓ Requirement Satisfied"
                        desc = f"IELTS score of {ielts:.1f} meets verified thresholds for both GKS (6.0) and KAIST (6.5)."
                    elif ielts >= gks_ielts:
                        status = "✓ Program Specific Requirement"
                        desc = f"IELTS score of {ielts:.1f} meets GKS (6.0), but program-specific check is required for KAIST/SNU."
                    else:
                        status = "✓ Requirement Not Verified"
                        desc = f"IELTS score of {ielts:.1f} falls below GKS minimum. Verify directly with official admissions."
                primary_status = status
                eval_parts.append(f"South Korea: {status} ({desc})")

            elif country == "Japan":
                # Do NOT assume IELTS or TOEFL is mandatory (varies by MEXT, embassy, university recommend pathways)
                if is_exempt:
                    status = "✓ Program Specific Requirement"
                    desc = "Exemptions depend on university-specific recommendation tracks. Direct verification is required."
                else:
                    mext_ielts = 6.5
                    if ielts >= mext_ielts:
                        status = "✓ Language Requirement Met"
                        desc = f"IELTS score of {ielts:.1f} meets the standard MEXT Research Scholarship database baseline."
                    else:
                        status = "✓ University Verification Required"
                        desc = f"IELTS score of {ielts:.1f} is below standard MEXT threshold. Direct university recommendation checks required."
                primary_status = status
                eval_parts.append(f"Japan: {status} ({desc})")

            elif country == "Germany":
                # Do NOT assume IELTS is mandatory (varies by program language, public tuition waivers, MOI)
                if is_exempt:
                    status = "✓ English Requirement Satisfied"
                    desc = "English-medium degree/MOI exemption is accepted at most public engineering programs."
                else:
                    daad_ielts = 6.0
                    if ielts >= daad_ielts:
                        status = "✓ English Requirement Satisfied"
                        desc = f"IELTS score of {ielts:.1f} satisfies DAAD and standard public English track thresholds."
                    else:
                        status = "✓ German Requirement Needed"
                        desc = f"IELTS score of {ielts:.1f} is below English tracks. German language certificate (e.g. TestDaF) is required."
                primary_status = status
                eval_parts.append(f"Germany: {status} ({desc})")

            elif country == "Singapore":
                # Proof of English required, but MOI widely accepted for English-taught bachelor degrees
                if is_exempt:
                    status = "✓ MOI May Be Accepted"
                    desc = "NUS and NTU waive IELTS/TOEFL if evidence is provided that previous education was conducted in English."
                else:
                    singa_ielts = 6.5
                    if ielts >= singa_ielts:
                        status = "✓ Requirement Met"
                        desc = f"IELTS score of {ielts:.1f} satisfies the SINGA PhD and university graduate scholarship database threshold."
                    else:
                        status = "✓ University Verification Required"
                        desc = f"IELTS score of {ielts:.1f} is below 6.5. Direct verification required with official university source."
                primary_status = status
                eval_parts.append(f"Singapore: {status} ({desc})")

            elif country == "Taiwan":
                # Varies by university and scholarship (English track institutional certifications)
                if is_exempt:
                    status = "✓ Alternative Proof Accepted"
                    desc = "Institutional MOI certificate is accepted by several English-taught programs."
                else:
                    moe_ielts = 6.0
                    if ielts >= moe_ielts:
                        status = "✓ Requirement Met"
                        desc = f"IELTS score of {ielts:.1f} meets the Taiwan MOE and ICDF scholarship thresholds."
                    else:
                        status = "✓ Program Specific Requirement"
                        desc = f"IELTS score of {ielts:.1f} is below 6.0. Verify specific program exceptions."
                primary_status = status
                eval_parts.append(f"Taiwan: {status} ({desc})")

        if not eval_parts:
            return "Requirement Information Unavailable", "Requirement information unavailable. Please verify through official university or scholarship sources."

        if len(eval_parts) > 1:
            return "✓ Requirement Evaluated", " | ".join(eval_parts)
        else:
            return primary_status, eval_parts[0]

    def _verify_eligibility_research(self, has_pub, has_res, degree_pref):
        if degree_pref == "Master":
            if has_pub or has_res:
                return "Eligible", "Candidate possesses active research indicators which are highly favorable but not mandatory for Master's admissions."
            return "Eligible", "Research experience is optional for coursework-based Master's degree applications."
        else:
            if has_pub:
                return "Eligible", "Excellent. Peer-reviewed publication satisfies the highest standards for PhD candidate admissions."
            elif has_res:
                return "Partially Eligible", "Candidate has academic project research experience, but lacks journal publications which are highly expected by top advisors."
            else:
                return "Not Eligible", "Applying for a PhD without research projects or papers is highly restricted. Prior experience is required."

    def _verify_eligibility_scholarship(self, gpa, ielts, is_exempt, is_none, scholarships, countries, degree_pref):
        matched = []
        for s in scholarships:
            if s["country"] in countries and degree_pref in s["degree_levels"]:
                gpa_ok = gpa >= s["min_gpa"]
                lang_ok = is_exempt or (not is_none and ielts >= s["min_ielts"])
                if gpa_ok and lang_ok:
                    matched.append(s["name"])
                    
        if len(matched) >= 2:
            return "Eligible", f"Fully eligible for multiple major awards, including: {', '.join(matched[:3])}."
        elif len(matched) == 1:
            return "Partially Eligible", f"Eligible for {matched[0]}. High-selectivity limits other matches."
        else:
            return "Not Eligible", "No verified scholarship matches candidate's academic GPA and language scores."

    def _generate_roadmap(self, is_none, degree_pref, has_pub):
        milestones = []
        
        if is_none:
            milestones.append(("Month 1", "Register & Prepare for English Language Test (IELTS/TOEFL). Aim for IELTS 6.5+ equivalent."))
        else:
            milestones.append(("Month 1", "Resume Polish & Initial University Search. Map specific lab professors matching research interests."))
            
        milestones.append(("Month 2", "Draft Statement of Purpose (SOP) & Custom Study Plan tailored to target country guidelines (e.g. GKS study goals)."))
        
        if degree_pref == "PhD" or has_pub:
            milestones.append(("Month 3", "Professor Outreach. Contact potential advisors at selected universities with CV and research proposal draft."))
        else:
            milestones.append(("Month 3", "Request Academic Recommendation Letters. Secure commitments from 2 professors from bachelor institution."))
            
        if degree_pref == "PhD":
            milestones.append(("Month 4", "Secure Professor Acceptance Letters & Finalize Research Proposal. Request recommendation letters from faculty."))
        else:
            milestones.append(("Month 4", "Prepare Certified Academic Documents. Obtain apostilled graduation certificates and transcripts."))
            
        milestones.append(("Month 5", "Submit Scholarship Applications. Apply for Government funding tracks (Embassy/University GKS, MEXT, or DAAD portals)."))
        milestones.append(("Month 6", "Submit University Portal Applications. Prepare for university interviews and coordinate visa documentation."))
        
        return milestones

    def _determine_best_opportunity(self, recommendations, scholarships):
        if not recommendations:
            return {
                "university": "Insufficient Verified Data",
                "country": "Insufficient Verified Data",
                "program": "Insufficient Verified Data",
                "scholarship": "Insufficient Verified Data",
                "success_score": 0,
                "reasoning": "No suitable university matches found based on current criteria."
            }
            
        best_uni = recommendations[0]
        best_sch = "University Scholarships & Tuition Waivers"
        for s in scholarships:
            if s["country"] == best_uni["country"] and s["match_score"] >= 80:
                best_sch = s["name"]
                break
                
        success_val = int(best_uni["match_score"] * 0.9)
        
        return {
            "university": best_uni["name"],
            "country": best_uni["country"],
            "program": best_uni["program"],
            "scholarship": best_sch,
            "success_score": success_val,
            "reasoning": f"Excellent compatibility score of {best_uni['match_score']}% based on field alignment and GPA fit. Fully funded scholarship covers all expenses."
        }

    def _format_markdown_report(self, parsed, ranked_countries, recommendations, scholarships, eligibility, comp, roadmap_params, roadmap_milestones, best_opp, acad_score, acad_reason, res_score, res_reason, sch_score, sch_reason, lang_score, lang_reason):
        acad_elig, acad_ev, lang_elig, lang_ev, res_elig, res_ev, sch_elig, sch_ev = eligibility
        comp_score, comp_level = comp
        is_none, degree_pref, has_pub = roadmap_params

        markdown = f"""# ScholarAgent Recommendation Report

---

### SECTION 1: Student Profile Summary
* **Degree**: {parsed['Degree']}
* **Major**: {parsed['Major']}
* **Academic GPA (4.0 scale)**: {parsed.get('Academic GPA (4.0 scale)', 'Not Available')}
* **CGPA**: {parsed.get('CGPA', 'Not Available')}
* **Skills**: {parsed['Skills']}
* **Programming Languages**: {parsed['Programming Languages']}
* **Projects**: {parsed['Projects']}
* **Internships**: {parsed['Internships']}
* **Work Experience**: {parsed['Work Experience']}
* **Research Experience**: {parsed['Research Experience']}
* **Publications**: {parsed['Publications']}
* **Certifications**: {parsed['Certifications']}
* **Awards**: {parsed['Awards']}
* **Leadership Activities**: {parsed['Leadership Activities']}
* **Language Scores**: {parsed['Language Scores']}
* **Career Interests**: {parsed['Career Interests']}

---

### SECTION 2: Country Rankings
Here is the ranked suitability of supported destination countries based on study opportunities, degree level ({parsed['Degree']}), and scholarship availability:

"""
        for idx, rc in enumerate(ranked_countries, 1):
            markdown += f"{idx}. **{rc['country']}** (Suitability Score: {rc['score']}%)\n"
            markdown += f"   * *Reason*: {rc['reason']}\n\n"

        markdown += """---

### SECTION 3: Top University Matches
The following universities represent the best fit for your academic profile, based on verified rankings and department compatibility:

"""
        if not recommendations:
            markdown += "* **Insufficient Verified Data**: No university matched the target parameters.\n"
        else:
            for idx, uni in enumerate(recommendations, 1):
                markdown += f"#### {idx}. {uni['name']}\n"
                markdown += f"* **Country**: {uni['country']}\n"
                markdown += f"* **Department**: {uni['department']}\n"
                markdown += f"* **Program**: {uni['program']}\n"
                markdown += f"* **Match Score**: {uni['match_score']}%\n"
                markdown += f"* **Admission Competitiveness**: {uni['competitiveness']}\n"
                markdown += f"* **Why Recommended**: {uni['why_recommended']}\n"
                markdown += f"* **Scholarships Available**: {uni['scholarships']}\n"
                markdown += f"* **Research Alignment**: {uni['research_alignment']}\n"
                markdown += f"* **Requirements Summary**: {uni['requirements']}\n\n"

        # Check if there are matches in Priority 1 & 2 with Match Score >= 60
        has_high_priority_matches = any(s.get("priority_group", 6) <= 2 and s.get("match_score", 0) >= 60 for s in scholarships)
        use_alternative_header = not has_high_priority_matches

        markdown += """---

### SECTION 4: Scholarship Matches
"""
        if use_alternative_header:
            markdown += "**Alternative Funding Opportunities Found**\n\n"
        else:
            markdown += "These verified scholarship programs match your target destination and field. Ensure to check priority flags:\n\n"

        if not scholarships:
            markdown += "* **Insufficient Verified Data**: No verified scholarships match this specific profile configuration.\n"
        else:
            for idx, sch in enumerate(scholarships, 1):
                markdown += f"#### {idx}. {sch['name']}\n"
                markdown += f"* **Funding Type**: {sch['funding_type']}\n"
                markdown += f"* **Coverage**: {sch['coverage']}\n"
                markdown += f"* **Match Score**: {sch['match_score']}%\n"
                markdown += f"* **Reason for Recommendation**: {sch['explanation']}\n"
                markdown += f"* **Application Priority**: {sch['priority']} (Priority {sch['priority_group']})\n\n"

        markdown += f"""---

### SECTION 5: Eligibility Analysis
Verification analysis across primary eligibility domains:

* **Academic Eligibility**: **{acad_elig}**
  * *Evidence*: {acad_ev}
* **Language Eligibility**: **{lang_elig}**
  * *Evidence*: {lang_ev}
* **Research Eligibility**: **{res_elig}**
  * *Evidence*: {res_ev}
* **Scholarship Eligibility**: **{sch_elig}**
  * *Evidence*: {sch_ev}

---

### SECTION 6: Admission Competitiveness
Evaluation of admission profile strength for target graduate schools:

* **Admission Competitiveness Level**: {comp_level}
* **Estimated Admission Score**: {comp_score}/100
* *Important Note*: **Estimate only.**

---

### SECTION 7: Profile Improvement Suggestions
Prioritized recommendations to strengthen your application profile for fully funded grants:

"""
        # High Impact
        markdown += "#### High Impact Suggestions\n"
        if is_none:
            markdown += "* **Take English Proficiency Test**: Standard international programs require IELTS (6.5+) or TOEFL (85+) for admissions. Take this immediately.\n"
        if degree_pref == "PhD" and not has_pub:
            markdown += "* **Publish a Research Paper**: Submit a manuscript or write-up to a peer-reviewed journal or conference in your field to establish academic credibility.\n"
        markdown += "* **Gain Research Experience**: Assist a faculty professor in their laboratory to secure a strong academic recommendation letter detailing research skills.\n"

        # Medium Impact
        markdown += "\n#### Medium Impact Suggestions\n"
        markdown += "* **Secure Technical Internships**: Undertake practical projects at established engineering or technology firms to build engineering portfolios.\n"
        markdown += "* **Contribute to Open Source**: Build software tool repositories on GitHub to prove coding mastery to potential PhD advisors.\n"

        # Low Impact
        markdown += "\n#### Low Impact Suggestions\n"
        markdown += "* **Acquire Professional Certifications**: Enroll in specialized online specialization tracks (e.g. AWS Cloud, GCP ML) to supplement certifications.\n"

        markdown += """
---

### SECTION 8: Application Roadmap
Personalized month-by-month application milestones:

"""
        for m_id, milestone in roadmap_milestones:
            markdown += f"* **{m_id}**: {milestone}\n"

        markdown += f"""
---

### SECTION 9: Best Overall Opportunity
Based on our multi-agent evaluation, here is the most recommended program and funding route:

* **Best Overall Opportunity**
* **University**: {best_opp['university']}
* **Country**: {best_opp['country']}
* **Program**: {best_opp['program']}
* **Scholarship**: {best_opp['scholarship']}
* **Success Score**: {best_opp['success_score']}%
* **Reasoning**: {best_opp['reasoning']}
"""
        return markdown
