import os
import json

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SCHOLARSHIPS_FILE = os.path.join(DB_DIR, "scholarships.json")
UNIVERSITIES_FILE = os.path.join(DB_DIR, "universities.json")

def ensure_db_dir():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

def read_json_file(filepath, default_data):
    ensure_db_dir()
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4)
        return default_data
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return default_data

def write_json_file(filepath, data):
    ensure_db_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def initialize_dbs():
    ensure_db_dir()
    
    # 1. Target Scholarships Database
    default_scholarships = [
        # South Korea
        {
            "id": "SCH-GKS",
            "name": "Global Korea Scholarship (GKS)",
            "country": "South Korea",
            "provider": "Korean NIIED",
            "coverage": "Full Tuition, Monthly Allowance (1,000,000 KRW), Airfare, Health Insurance, 1-Year Language Course",
            "min_gpa": 3.2,
            "min_ielts": 6.0,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business", "Humanities"],
            "description": "The premier scholarship of South Korea designed to foster international exchange and friendship.",
            "required_documents": ["Resume/CV", "Statement of Purpose (SOP)", "Study Plan", "Two Recommendation Letters", "Bachelor's/Master's Graduation Certificate", "Transcripts", "Language Certificate (IELTS/TOPIK)"]
        },
        {
            "id": "SCH-KAIST",
            "name": "KAIST Graduate Scholarship",
            "country": "South Korea",
            "provider": "KAIST University",
            "coverage": "Full Tuition Waiver, Monthly Stipend (350,000 KRW for MS, 400,000 KRW for PhD), Health Insurance",
            "min_gpa": 3.3,
            "min_ielts": 6.5,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business"],
            "description": "Fully funded assistantships and university scholarships for top-tier STEM candidates at KAIST.",
            "required_documents": ["Resume/CV", "SOP", "Two Recommendation Letters", "Official Transcripts", "English Proficiency Report", "Consent Form for Background Check"]
        },
        {
            "id": "SCH-SPF",
            "name": "SNU President Fellowship (SPF)",
            "country": "South Korea",
            "provider": "Seoul National University",
            "coverage": "Full Tuition for 6 Semesters, Monthly Stipend (1,500,000 KRW) for 4 years, Round-trip Airfare, Korean Language Course",
            "min_gpa": 3.6,
            "min_ielts": 7.0,
            "degree_levels": ["PhD"],
            "eligible_fields": ["Engineering", "Science", "Business", "Humanities"],
            "description": "Prestigious fellowship for faculty members of major universities in developing countries pursuing a PhD at SNU.",
            "required_documents": ["Resume/CV", "SOP", "Research Proposal", "Proof of Faculty Employment", "Recommendation from President of Home University", "Transcripts"]
        },
        
        # Japan
        {
            "id": "SCH-MEXT",
            "name": "MEXT Research Scholarship",
            "country": "Japan",
            "provider": "Japanese Ministry of Education",
            "coverage": "Full Tuition Waiver, Monthly Stipend (143,000 JPY), Round-trip Airfare, Optional Japanese Training",
            "min_gpa": 3.3,
            "min_ielts": 6.5,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business", "Humanities"],
            "description": "Fully funded fellowship by the Japanese Government for international research students.",
            "required_documents": ["Resume/CV", "Placement Application Form", "Field of Study and Research Plan (SOP)", "Recommendation Letters", "Transcripts", "Medical Certificate"]
        },
        {
            "id": "SCH-HONJO",
            "name": "Honjo International Scholarship Foundation",
            "country": "Japan",
            "provider": "Honjo Foundation",
            "coverage": "Monthly Stipend of 150,000 to 200,000 JPY based on degree duration, Travel Expenses for Conferences",
            "min_gpa": 3.4,
            "min_ielts": 7.0,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business", "Humanities"],
            "description": "Scholarship awarded to outstanding students with leadership potential to study in Japan.",
            "required_documents": ["Resume/CV", "Academic Transcripts", "Research Proposal", "Recommendation Letter", "SOP detailing career vision"]
        },
        
        # Germany
        {
            "id": "SCH-DAAD",
            "name": "DAAD EPOS Postgraduate Scholarship",
            "country": "Germany",
            "provider": "German Academic Exchange Service",
            "coverage": "Full Tuition, Monthly Allowance (934 EUR to 1,200 EUR), Health Insurance, Travel Grant",
            "min_gpa": 3.0,
            "min_ielts": 6.0,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business"],
            "description": "Fully funded scholarships supporting young professionals from developing countries to study in Germany.",
            "required_documents": ["DAAD Application Form", "Hand-signed CV (Europass format)", "Hand-signed Letter of Motivation (SOP)", "Academic Recommendation Letters", "Professional Certificate of Employment"]
        },
        {
            "id": "SCH-GER-DEUT",
            "name": "Deutschlandstipendium National Scholarship",
            "country": "Germany",
            "provider": "German Federal Government & Private Sponsors",
            "coverage": "Monthly Stipend of 300 EUR, Networking Events, Mentorship Opportunities",
            "min_gpa": 3.2,
            "min_ielts": 6.5,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business", "Humanities"],
            "description": "Merit-based scholarship supporting high-achieving international and domestic students at German universities.",
            "required_documents": ["Resume/CV", "Letter of Motivation", "University Admission Letter", "Transcripts", "References"]
        },

        # Singapore
        {
            "id": "SCH-SINGA",
            "name": "Singapore International Graduate Award (SINGA)",
            "country": "Singapore",
            "provider": "A*STAR, NUS, NTU, SUTD",
            "coverage": "Full Tuition Coverage, Monthly Stipend ($2,200 - $2,700 SGD), Airfare Grant, Settling-in Allowance",
            "min_gpa": 3.5,
            "min_ielts": 6.5,
            "degree_levels": ["PhD"],
            "eligible_fields": ["Engineering", "Science"],
            "description": "A prestigious PhD scholarship targeting top international researchers to study at Singapore's leading labs.",
            "required_documents": ["Resume/CV", "Transcripts", "Degree Scroll", "Two Recommendation Letters", "Research Proposal", "English Test Report"]
        },
        {
            "id": "SCH-NUS-RES",
            "name": "NUS Graduate Research Scholarship",
            "country": "Singapore",
            "provider": "National University of Singapore",
            "coverage": "Full Tuition Waiver, Monthly Stipend ($2,000 SGD for MSc, $2,200 - $2,700 SGD for PhD), Research Grants",
            "min_gpa": 3.4,
            "min_ielts": 6.5,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business", "Humanities"],
            "description": "Fully funded assistantships at NUS to attract and support outstanding graduate research candidates.",
            "required_documents": ["Resume/CV", "SOP", "Transcripts", "Two Academic Referee Reports", "GRE/GMAT Scores (for some fields)", "TOEFL/IELTS Certificate"]
        },
        {
            "id": "SCH-NTU-RES",
            "name": "NTU Research Scholarship",
            "country": "Singapore",
            "provider": "Nanyang Technological University",
            "coverage": "Full Tuition Waiver, Monthly Stipend ($2,000 - $2,500 SGD), Research and Travel Support",
            "min_gpa": 3.4,
            "min_ielts": 6.5,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business"],
            "description": "Graduate research scholarships offered by NTU to outstanding local and international graduates.",
            "required_documents": ["Resume/CV", "SOP", "Official University Transcripts", "Two Recommendation Letters", "IELTS/TOEFL score sheet"]
        },

        # Taiwan
        {
            "id": "SCH-TAIWAN-MOE",
            "name": "Taiwan MOE Scholarship",
            "country": "Taiwan",
            "provider": "Taiwan Ministry of Education",
            "coverage": "Tuition support up to NTD 40,000 per semester, Monthly Stipend (NTD 20,000 for Graduates)",
            "min_gpa": 3.0,
            "min_ielts": 6.0,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business", "Humanities"],
            "description": "Government scholarship to encourage outstanding international students to pursue degrees in Taiwan.",
            "required_documents": ["Resume/CV", "Application Form", "Transcripts", "Study Plan (SOP)", "Two Recommendation Letters", "Language Proficiency Certificate"]
        },
        {
            "id": "SCH-TIGP",
            "name": "Academia Sinica TIGP Fellowship",
            "country": "Taiwan",
            "provider": "Academia Sinica",
            "coverage": "Full Tuition Waiver, Monthly Fellowship (NTD 34,000) for 3 years, Lab Research Support",
            "min_gpa": 3.4,
            "min_ielts": 6.5,
            "degree_levels": ["PhD"],
            "eligible_fields": ["Science", "Engineering"],
            "description": "Highly competitive PhD research programs in collaboration with top universities in Taiwan.",
            "required_documents": ["Resume/CV", "SOP", "Academic Transcripts", "Three Letters of Recommendation", "GRE score report (optional)", "IELTS/TOEFL score"]
        },
        {
            "id": "SCH-ICDF",
            "name": "Taiwan ICDF Scholarship",
            "country": "Taiwan",
            "provider": "Taiwan ICDF",
            "coverage": "Full Tuition Waiver, Monthly Allowance (NTD 15,000 for Masters, NTD 17,000 for PhD), Return Airfare, Housing",
            "min_gpa": 3.0,
            "min_ielts": 6.0,
            "degree_levels": ["Master", "PhD"],
            "eligible_fields": ["Engineering", "Science", "Business"],
            "description": "Fully funded scholarships for students from diplomatic allies and friendly developing countries.",
            "required_documents": ["Resume/CV", "Application Form", "Transcripts", "SOP", "Two Letters of Recommendation", "Medical Report"]
        }
    ]
    write_json_file(SCHOLARSHIPS_FILE, default_scholarships)

    # 2. Target Universities Database
    default_universities = [
        # South Korea (10 universities)
        {"id": "UNI-SNU", "name": "Seoul National University (SNU)", "country": "South Korea", "rank": 41, "fields": ["Engineering", "Science", "Business", "Humanities"]},
        {"id": "UNI-KAIST", "name": "Korea Advanced Institute of Science & Technology (KAIST)", "country": "South Korea", "rank": 53, "fields": ["Engineering", "Science"]},
        {"id": "UNI-POSTECH", "name": "Pohang University of Science and Technology (POSTECH)", "country": "South Korea", "rank": 100, "fields": ["Engineering", "Science"]},
        {"id": "UNI-YONSEI", "name": "Yonsei University", "country": "South Korea", "rank": 76, "fields": ["Engineering", "Science", "Business", "Humanities"]},
        {"id": "UNI-KOREA", "name": "Korea University", "country": "South Korea", "rank": 79, "fields": ["Engineering", "Science", "Business", "Humanities"]},
        {"id": "UNI-SKKU", "name": "Sungkyunkwan University (SKKU)", "country": "South Korea", "rank": 145, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-HANYANG", "name": "Hanyang University", "country": "South Korea", "rank": 164, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-GIST", "name": "Gwangju Institute of Science and Technology (GIST)", "country": "South Korea", "rank": 307, "fields": ["Engineering", "Science"]},
        {"id": "UNI-UNIST", "name": "Ulsan National Institute of Science and Technology (UNIST)", "country": "South Korea", "rank": 197, "fields": ["Engineering", "Science"]},
        {"id": "UNI-KHU", "name": "Kyung Hee University", "country": "South Korea", "rank": 332, "fields": ["Engineering", "Science", "Business", "Humanities"]},

        # Japan (10 universities)
        {"id": "UNI-UTOKYO", "name": "University of Tokyo", "country": "Japan", "rank": 28, "fields": ["Engineering", "Science", "Business", "Humanities"]},
        {"id": "UNI-KYOTO", "name": "Kyoto University", "country": "Japan", "rank": 46, "fields": ["Engineering", "Science", "Humanities"]},
        {"id": "UNI-TOKYOTECH", "name": "Tokyo Institute of Technology (Tokyo Tech)", "country": "Japan", "rank": 91, "fields": ["Engineering", "Science"]},
        {"id": "UNI-OSAKA", "name": "Osaka University", "country": "Japan", "rank": 80, "fields": ["Engineering", "Science", "Business", "Humanities"]},
        {"id": "UNI-TOHOKU", "name": "Tohoku University", "country": "Japan", "rank": 113, "fields": ["Engineering", "Science", "Humanities"]},
        {"id": "UNI-NAGOYA", "name": "Nagoya University", "country": "Japan", "rank": 152, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-KYUSHU", "name": "Kyushu University", "country": "Japan", "rank": 167, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-HOKKAIDO", "name": "Hokkaido University", "country": "Japan", "rank": 196, "fields": ["Engineering", "Science", "Humanities"]},
        {"id": "UNI-WASEDA", "name": "Waseda University", "country": "Japan", "rank": 199, "fields": ["Engineering", "Science", "Business", "Humanities"]},
        {"id": "UNI-KEIO", "name": "Keio University", "country": "Japan", "rank": 214, "fields": ["Engineering", "Science", "Business", "Humanities"]},

        # Germany (10 universities)
        {"id": "UNI-TUM", "name": "Technical University of Munich (TUM)", "country": "Germany", "rank": 37, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-LMU", "name": "LMU Munich", "country": "Germany", "rank": 54, "fields": ["Science", "Humanities"]},
        {"id": "UNI-HEIDELBERG", "name": "Heidelberg University", "country": "Germany", "rank": 87, "fields": ["Science", "Humanities"]},
        {"id": "UNI-HUMBOLDT", "name": "Humboldt University of Berlin", "country": "Germany", "rank": 120, "fields": ["Science", "Business", "Humanities"]},
        {"id": "UNI-FU-BERLIN", "name": "Free University of Berlin", "country": "Germany", "rank": 97, "fields": ["Science", "Humanities"]},
        {"id": "UNI-RWTH", "name": "RWTH Aachen University", "country": "Germany", "rank": 106, "fields": ["Engineering", "Science"]},
        {"id": "UNI-KIT", "name": "Karlsruhe Institute of Technology (KIT)", "country": "Germany", "rank": 119, "fields": ["Engineering", "Science"]},
        {"id": "UNI-TUBERLIN", "name": "TU Berlin", "country": "Germany", "rank": 154, "fields": ["Engineering", "Science"]},
        {"id": "UNI-FREIBURG", "name": "University of Freiburg", "country": "Germany", "rank": 189, "fields": ["Science", "Humanities"]},
        {"id": "UNI-STUTTGART", "name": "University of Stuttgart", "country": "Germany", "rank": 312, "fields": ["Engineering", "Science"]},

        # Singapore (6 universities)
        {"id": "UNI-NUS", "name": "National University of Singapore (NUS)", "country": "Singapore", "rank": 8, "fields": ["Engineering", "Science", "Business", "Humanities"]},
        {"id": "UNI-NTU", "name": "Nanyang Technological University (NTU)", "country": "Singapore", "rank": 26, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-SMU", "name": "Singapore Management University (SMU)", "country": "Singapore", "rank": 585, "fields": ["Business", "Humanities"]},
        {"id": "UNI-SUTD", "name": "Singapore University of Technology and Design (SUTD)", "country": "Singapore", "rank": 440, "fields": ["Engineering", "Science"]},
        {"id": "UNI-SIT", "name": "Singapore Institute of Technology (SIT)", "country": "Singapore", "rank": 800, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-SUSS", "name": "Singapore University of Social Sciences (SUSS)", "country": "Singapore", "rank": 900, "fields": ["Business", "Humanities"]},

        # Taiwan (10 universities)
        {"id": "UNI-NTU-TW", "name": "National Taiwan University (NTU)", "country": "Taiwan", "rank": 69, "fields": ["Engineering", "Science", "Business", "Humanities"]},
        {"id": "UNI-NTHU", "name": "National Tsing Hua University", "country": "Taiwan", "rank": 177, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-NYCU", "name": "National Yang Ming Chiao Tung University (NYCU)", "country": "Taiwan", "rank": 217, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-NCKU", "name": "National Cheng Kung University (NCKU)", "country": "Taiwan", "rank": 228, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-NTUST", "name": "National Taiwan University of Science and Technology (Taiwan Tech)", "country": "Taiwan", "rank": 387, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-NCU", "name": "National Central University (NCU)", "country": "Taiwan", "rank": 614, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-NSYSU", "name": "National Sun Yat-sen University (NSYSU)", "country": "Taiwan", "rank": 505, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-NCHU", "name": "National Chung Hsing University (NCHU)", "country": "Taiwan", "rank": 651, "fields": ["Engineering", "Science"]},
        {"id": "UNI-TAIPEITECH", "name": "National Taipei University of Technology", "country": "Taiwan", "rank": 431, "fields": ["Engineering", "Science", "Business"]},
        {"id": "UNI-TAMKANG", "name": "Tamkang University", "country": "Taiwan", "rank": 1001, "fields": ["Engineering", "Science", "Business", "Humanities"]}
    ]
    write_json_file(UNIVERSITIES_FILE, default_universities)

def get_scholarships():
    return read_json_file(SCHOLARSHIPS_FILE, [])

def get_universities():
    return read_json_file(UNIVERSITIES_FILE, [])

def add_scholarship(name, country, provider, coverage, min_gpa, min_ielts, degree_levels, eligible_fields, required_documents=None):
    scholarships = get_scholarships()
    new_id = f"SCH-NEW-{len(scholarships) + 1:02d}"
    sch = {
        "id": new_id,
        "name": name,
        "country": country,
        "provider": provider,
        "coverage": coverage,
        "min_gpa": float(min_gpa),
        "min_ielts": float(min_ielts),
        "degree_levels": degree_levels,
        "eligible_fields": eligible_fields,
        "description": "Custom verified scholarship program added to local index.",
        "required_documents": required_documents or ["Resume/CV", "SOP", "Transcripts", "Recommendation Letters"]
    }
    scholarships.append(sch)
    write_json_file(SCHOLARSHIPS_FILE, scholarships)
    return sch

def add_university(name, country, rank, fields):
    unis = get_universities()
    new_id = f"UNI-NEW-{len(unis) + 1:02d}"
    uni = {
        "id": new_id,
        "name": name,
        "country": country,
        "rank": int(rank),
        "fields": fields
    }
    unis.append(uni)
    write_json_file(UNIVERSITIES_FILE, unis)
    return uni

# Initialize tables
initialize_dbs()
