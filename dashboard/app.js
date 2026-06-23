/* -------------------------------------------------------------
   Global Scholar Portal Frontend Controller
   ------------------------------------------------------------- */

const API_BASE = "http://127.0.0.1:5000/api";

// DOM Elements
const elements = {
    valScholars: document.getElementById("val-scholarships"),
    valUnis: document.getElementById("val-unis"),
    
    profGpa: document.getElementById("prof-gpa"),
    profIelts: document.getElementById("prof-ielts"),
    profMajor: document.getElementById("prof-major"),
    profCountryMode: document.getElementById("prof-country-mode"),
    profResume: document.getElementById("prof-resume"),
    btnRunMatch: document.getElementById("btn-run-match"),
    
    matchesList: document.getElementById("matches-list"),
    
    chatTerminal: document.getElementById("chat-terminal"),
    chatMessages: document.getElementById("chat-messages"),
    chatInput: document.getElementById("chat-input"),
    btnSendChat: document.getElementById("btn-send-chat"),
    thinkingArea: document.getElementById("agent-thinking-area"),
    
    sopEmptyState: document.getElementById("sop-empty-state"),
    sopOutput: document.getElementById("sop-output")
};

let activeScholarships = [];
let activeUniversities = [];

// Initial Load
document.addEventListener("DOMContentLoaded", () => {
    fetchDashboardStats();
    setupEventListeners();
});

// Load stats for metrics cards
async function fetchDashboardStats() {
    try {
        const response = await fetch(`${API_BASE}/dashboard`);
        if (response.ok) {
            const data = await response.json();
            elements.valScholars.textContent = data.metrics.total_programs;
            elements.valUnis.textContent = data.metrics.total_universities;
            activeScholarships = data.scholarships;
            activeUniversities = data.universities;
        }
    } catch (e) {
        console.error("Failed to load statistics:", e);
    }
}

function setupEventListeners() {
    elements.btnRunMatch.addEventListener("click", runMatchPipeline);
    elements.btnSendChat.addEventListener("click", handleChatSend);
    elements.chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleChatSend();
    });

    // Country mode change listener
    const modeSelect = document.getElementById("prof-country-mode");
    if (modeSelect) {
        modeSelect.addEventListener("change", (e) => {
            const singleGroup = document.getElementById("group-single-country");
            const multiGroup = document.getElementById("group-multiple-countries");
            if (e.target.value === "single") {
                singleGroup.style.display = "block";
                multiGroup.style.display = "none";
            } else if (e.target.value === "multiple") {
                singleGroup.style.display = "none";
                multiGroup.style.display = "block";
            } else {
                singleGroup.style.display = "none";
                multiGroup.style.display = "none";
            }
        });
    }

    // Language selector change listener
    const langSelector = document.getElementById("prof-lang-type");
    langSelector.addEventListener("change", (e) => {
        const scoreGroup = document.getElementById("group-lang-score");
        const scoreInput = document.getElementById("prof-ielts");
        const lbl = document.getElementById("lbl-lang-score");
        
        if (e.target.value === "Exempt") {
            scoreGroup.style.opacity = "0.3";
            scoreInput.disabled = true;
            scoreInput.value = "9.0"; // Set to high score to pass simple filters
            lbl.innerText = "Exempt (English Medium)";
        } else if (e.target.value === "None") {
            scoreGroup.style.opacity = "0.3";
            scoreInput.disabled = true;
            scoreInput.value = "0.0"; // Set to 0 since test is not taken
            lbl.innerText = "No Language Test Taken";
        } else {
            scoreGroup.style.opacity = "1";
            scoreInput.disabled = false;
            scoreInput.value = "7.0";
            if (e.target.value === "Native") {
                lbl.innerText = "Language Score (TOPIK/JLPT/TestDaF)";
                scoreInput.max = "6.0"; // for level levels
                scoreInput.value = "5";
            } else if (e.target.value === "TOEFL") {
                lbl.innerText = "TOEFL Score (0-120)";
                scoreInput.max = "120";
                scoreInput.value = "95";
            } else {
                lbl.innerText = "IELTS Score (0-9.0)";
                scoreInput.max = "9.0";
                scoreInput.value = "7.0";
            }
        }
    });

    // Code snippets clicks
    document.querySelectorAll(".example-prompts code").forEach(code => {
        code.addEventListener("click", (e) => {
            elements.chatInput.value = e.target.innerText.replace(/"/g, '');
            elements.chatInput.focus();
        });
    });

    // Resume file upload listeners
    const fileInput = document.getElementById("resume-file");
    const uploadBtn = document.getElementById("btn-upload-resume");
    if (fileInput && uploadBtn) {
        uploadBtn.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            appendChatBubble("user", `Uploading and analyzing resume file: "${file.name}"`);
            elements.thinkingArea.style.display = "flex";
            elements.chatTerminal.scrollTop = elements.chatTerminal.scrollHeight;
            
            const formData = new FormData();
            formData.append("file", file);
            
            try {
                const response = await fetch(`${API_BASE}/upload-resume`, {
                    method: "POST",
                    body: formData
                });
                const data = await response.json();
                elements.thinkingArea.style.display = "none";
                
                if (response.ok && data.status === "Success") {
                    elements.profResume.value = data.text;
                    autoFillFromResume(data.text);
                } else {
                    appendChatBubble("agent", `⚠️ File Upload Error: ${data.error || "Failed to parse file."}`);
                }
            } catch (err) {
                elements.thinkingArea.style.display = "none";
                appendChatBubble("agent", "❌ Connection error during resume upload.");
            }
        });
    }
}

// Pipeline: Submit academic profile, calculate matches, generate dashboard elements
async function runMatchPipeline() {
    const resumeRaw = elements.profResume.value.trim();
    if (!resumeRaw) {
        alert("Please upload a resume or paste your academic history first.");
        return;
    }

    const degree = document.getElementById("prof-degree").value;
    const countryMode = document.getElementById("prof-country-mode").value;
    
    let selectedCountries = [];
    if (countryMode === "single") {
        selectedCountries.push(document.getElementById("prof-single-country").value);
    } else if (countryMode === "multiple") {
        const checkedBoxes = document.querySelectorAll('input[name="multi-country"]:checked');
        checkedBoxes.forEach(cb => selectedCountries.push(cb.value));
        if (selectedCountries.length === 0) {
            alert("Please select at least one target country.");
            return;
        }
    } else {
        selectedCountries = ["South Korea", "Japan", "Germany", "Singapore", "Taiwan"];
    }

    // Read advanced overrides (if the user modified them)
    const gpaRaw = parseFloat(elements.profGpa.value);
    const gpaScale = document.getElementById("prof-gpa-scale").value;
    const ielts = parseFloat(elements.profIelts.value);
    const major = elements.profMajor.value;
    const langType = document.getElementById("prof-lang-type").value;
    const pubStatus = document.getElementById("prof-pub-status").value;

    const isExempt = langType === "Exempt";
    const isNone = langType === "None";

    // GPA validation based on selected scale
    let maxGpa = 4.0;
    if (gpaScale === "10.0") maxGpa = 10.0;
    if (gpaScale === "100") maxGpa = 100.0;

    if (isNaN(gpaRaw) || gpaRaw < 0 || gpaRaw > maxGpa || (!isExempt && !isNone && isNaN(ielts))) {
        alert(`Please verify advanced settings: Ensure valid GPA (0-${maxGpa}) and language score.`);
        return;
    }

    // Normalize GPA to 4.0 scale for server matches
    let gpa = gpaRaw;
    if (gpaScale === "10.0") {
        gpa = (gpaRaw / 10.0) * 4.0;
    } else if (gpaScale === "100") {
        gpa = (gpaRaw / 100.0) * 4.0;
    }

    // Set UI to loading
    elements.btnRunMatch.disabled = true;
    elements.btnRunMatch.innerText = "Running ScholarAgent Pipeline...";
    
    // Construct structured request payload
    const payload = {
        resume_text: resumeRaw,
        degree: degree,
        country_mode: countryMode,
        selected_countries: selectedCountries,
        // Passing advanced fields as overrides to the model:
        gpa: gpaRaw,
        gpa_scale: gpaScale,
        lang_type: langType,
        ielts: ielts,
        major: major,
        pub_status: pubStatus
    };
    
    // Add user question to terminal
    appendChatBubble("user", `Analyze my profile for a ${degree} degree. Mode: ${countryMode}. Target Countries: ${selectedCountries.join(', ')}.`);
    elements.thinkingArea.style.display = "flex";
    elements.chatTerminal.scrollTop = elements.chatTerminal.scrollHeight;

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        
        elements.thinkingArea.style.display = "none";
        elements.btnRunMatch.disabled = false;
        elements.btnRunMatch.innerText = "Analyze Profile & Match Programs";

        if (response.ok && data.status === "Success") {
            // 1. Render multi-agent typewriter logs
            await renderAgentLogs(data.logs);
            // 2. Append final report in chat bubble
            appendChatBubble("agent", data.result);
            // 3. Render matching list cards in UI
            renderMatches(gpa, ielts, major, countryMode, selectedCountries, resumeRaw, isExempt, isNone, degree);
        } else {
            appendChatBubble("agent", `⚠️ Workflow failed: ${data.error || "Execution error"}`);
        }
    } catch (e) {
        elements.thinkingArea.style.display = "none";
        elements.btnRunMatch.disabled = false;
        elements.btnRunMatch.innerText = "Analyze Profile & Match Programs";
        appendChatBubble("agent", "❌ Backend Server offline. Please verify app.py is running!");
    }
}

// Render dynamic program cards
function renderMatches(gpa, ielts, major, countryMode, selectedCountries, resumeText, isExempt, isNone, degree) {
    elements.matchesList.innerHTML = "";
    
    // Filter matching scholarships locally to render matching cards (VERIFIED ONLY - Rule 1 & 5)
    const normalizedDegree = degree.includes("Master") ? "Master" : "PhD";
    let matches = activeScholarships.filter(s => {
        const countryOk = (countryMode === "auto" || selectedCountries.includes(s.country));
        const fieldOk = s.eligible_fields.includes(major);
        const degreeOk = s.degree_levels.includes(normalizedDegree);
        return countryOk && fieldOk && degreeOk;
    });

    let usedSchScores = new Set();
    const scoredMatches = matches.map(sch => {
        let score = 90;
        
        // GPA fit (Academic Fit - 30%)
        const gpaDiff = gpa - sch.min_gpa;
        score += Math.round(gpaDiff * 15);
        
        // Language fit (Language Readiness - 5%)
        if (!isExempt) {
            if (isNone) {
                // Do not reject scholarship (Rule 10), but adjust eligibility fit score
                score -= 10;
            } else {
                const langDiff = ielts - sch.min_ielts;
                score += Math.round(langDiff * 10);
            }
        } else {
            score += 5;
        }
        
        // Research fit (Research Fit - 20%)
        const hasPub = resumeText.toLowerCase().includes("publication") || resumeText.toLowerCase().includes("journal") || resumeText.toLowerCase().includes("published") || resumeText.toLowerCase().includes("paper");
        if (sch.id === "SCH-SINGA" || sch.id === "SCH-TIGP" || sch.id === "SCH-SPF") {
            score += hasPub ? 8 : -15;
        } else {
            if (hasPub) score += 3;
        }
        
        // Experience fit (Experience Fit - 15%)
        const hasIntern = resumeText.toLowerCase().includes("intern") || resumeText.toLowerCase().includes("work") || resumeText.toLowerCase().includes("experience") || resumeText.toLowerCase().includes("engineer");
        if (hasIntern) score += 5;
        
        // Bounding
        let finalScore = Math.min(99, Math.max(35, score));
        
        // Uniqueness resolver
        while (usedSchScores.has(finalScore)) {
            finalScore -= 1;
            if (finalScore < 10) finalScore = 99;
        }
        usedSchScores.add(finalScore);
        
        // Map fields (Rule 4)
        let fType = "Government Scholarship";
        if (sch.id.includes("KAIST") || sch.id.includes("NUS") || sch.id.includes("NTU") || sch.id.includes("HONJO") || sch.id.includes("SPF")) {
            fType = "University Scholarship";
        }
        
        return { 
            ...sch, 
            calculatedScore: finalScore,
            funding_type: fType,
            funding_coverage: sch.coverage,
            official_source: sch.provider
        };
    });

    // Rank scholarships by calculated match score descending (Rule 8)
    scoredMatches.sort((a, b) => b.calculatedScore - a.calculatedScore);

    // Limit to maximum Top 10 matches (Rule 7)
    const top10Scholarships = scoredMatches.slice(0, 10);

    if (top10Scholarships.length === 0) {
        elements.matchesList.innerHTML = `<p class="empty-state">Alternative funding opportunities identified</p>`;
    } else {
        top10Scholarships.forEach(sch => {
            const scoreClass = sch.calculatedScore >= 85 ? "high" : sch.calculatedScore >= 60 ? "medium" : "low";

            // Determine if language test score is missing (Rule 10)
            let langNotice = "";
            if (isNone) {
                langNotice = `<div class="conditional-match-notice" style="color: var(--accent-orange); font-size: 0.72rem; margin-top: 0.4rem; font-weight: 500;">⚠️ Conditional Match: IELTS/TOEFL score required before application.</div>`;
            }

            const card = document.createElement("div");
            card.className = "match-item";
            card.innerHTML = `
                <div class="match-header-row">
                    <span class="match-title">${sch.name}</span>
                    <span class="match-score-badge ${scoreClass}">${sch.calculatedScore}% Match</span>
                </div>
                <div class="match-details-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.25rem; margin-top: 0.4rem; font-size: 0.72rem; color: var(--text-muted);">
                    <span>Country: <strong>${sch.country}</strong></span>
                    <span>Type: <strong>${sch.funding_type}</strong></span>
                    <span>Source: <strong>${sch.official_source}</strong></span>
                    <span>Min GPA: <strong>${sch.min_gpa}</strong></span>
                </div>
                <div class="match-coverage-desc" style="margin-top: 0.4rem; font-size: 0.72rem; color: var(--text-muted);">Coverage: ${sch.funding_coverage}</div>
                ${langNotice}
            `;

            card.addEventListener("click", () => {
                document.querySelectorAll(".match-item").forEach(item => item.classList.remove("selected"));
                card.classList.add("selected");
                
                loadSopAssistant(sch, major, resumeText);
            });

            elements.matchesList.appendChild(card);
        });
    }

    // Render Matched Universities
    const unisListContainer = document.getElementById("unis-list");
    unisListContainer.innerHTML = "";

    let usedUniScores = new Set();
    const scoredUnis = activeUniversities.filter(u => {
        const countryOk = (countryMode === "auto" || selectedCountries.includes(u.country));
        const fieldOk = u.fields.includes(major);
        return countryOk && fieldOk;
    }).map(uni => {
        let score = 88;
        const rank = uni.rank;
        let targetGpa = 3.0;
        let targetIelts = 6.0;
        if (rank < 50) {
            targetGpa = 3.6;
            targetIelts = 7.0;
        } else if (rank < 200) {
            targetGpa = 3.3;
            targetIelts = 6.5;
        }
        
        // GPA fit
        const gpaDiff = gpa - targetGpa;
        score += Math.round(gpaDiff * 18);
        
        // Language fit
        if (!isExempt) {
            if (isNone) {
                score -= 15;
            } else {
                const langDiff = ielts - targetIelts;
                score += Math.round(langDiff * 8);
            }
        } else {
            score += 4;
        }
        
        // Research fit
        const hasPub = resumeText.toLowerCase().includes("publication") || resumeText.toLowerCase().includes("journal") || resumeText.toLowerCase().includes("published") || resumeText.toLowerCase().includes("paper");
        if (hasPub) {
            score += (rank < 100) ? 8 : 4;
        } else {
            if (rank < 100) score -= 12;
        }
        
        // Internship fit
        const hasIntern = resumeText.toLowerCase().includes("intern") || resumeText.toLowerCase().includes("work") || resumeText.toLowerCase().includes("experience") || resumeText.toLowerCase().includes("engineer");
        if (hasIntern) score += 5;
        
        // Bounding
        let finalScore = Math.min(99, Math.max(40, score));
        
        // Uniqueness resolver
        while (usedUniScores.has(finalScore)) {
            finalScore -= 1;
            if (finalScore < 20) finalScore = 99;
        }
        usedUniScores.add(finalScore);
        
        return { ...uni, calculatedScore: finalScore };
    });

    // Sort universities by match score descending
    scoredUnis.sort((a, b) => b.calculatedScore - a.calculatedScore);

    // Slice to top 10 universities
    const top10Unis = scoredUnis.slice(0, 10);

    if (top10Unis.length === 0) {
        unisListContainer.innerHTML = `<p class="empty-state">No matching universities found.</p>`;
    } else {
        top10Unis.forEach(uni => {
            const card = document.createElement("div");
            card.className = "uni-item";
            card.innerHTML = `
                <div class="uni-details">
                    <h4>${uni.name}</h4>
                    <p>Country: ${uni.country} | Match: <strong>${uni.calculatedScore}%</strong></p>
                </div>
                <span class="uni-rank-badge">QS Rank #${uni.rank}</span>
            `;
            unisListContainer.appendChild(card);
        });
    }
}

// Load SOPoutline & trigger evaluator via backend
async function loadSopAssistant(scholarship, major, resumeText) {
    elements.sopEmptyState.style.display = "none";
    elements.sopOutput.style.display = "block";
    elements.sopOutput.textContent = "Loading Statement of Purpose template outline...";

    try {
        const response = await fetch(`${API_BASE}/sop`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                scholarship_name: scholarship.name,
                target_major: major,
                resume_text: resumeText
            })
        });
        const data = await response.json();
        if (response.ok && data.status === "Success") {
            elements.sopOutput.textContent = data.sop_outline;
        } else {
            elements.sopOutput.textContent = `Error creating outline: ${data.error}`;
        }
    } catch (e) {
        elements.sopOutput.textContent = "Error communicating with server API.";
    }
}

// Chat Terminal dispatch
async function handleChatSend() {
    const prompt = elements.chatInput.value.trim();
    if (!prompt) return;

    appendChatBubble("user", prompt);
    elements.chatInput.value = "";
    
    elements.thinkingArea.style.display = "flex";
    elements.chatTerminal.scrollTop = elements.chatTerminal.scrollHeight;

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt })
        });
        const data = await response.json();
        
        elements.thinkingArea.style.display = "none";
        if (response.ok && data.status === "Success") {
            await renderAgentLogs(data.logs);
            appendChatBubble("agent", data.result);
        } else {
            appendChatBubble("agent", `⚠️ Error: ${data.error || "Failed execution"}`);
        }
    } catch (e) {
        elements.thinkingArea.style.display = "none";
        appendChatBubble("agent", "❌ Server offline. Verify python server is running!");
    }
}

function appendChatBubble(sender, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-msg ${sender}-msg`;
    msgDiv.innerHTML = `<div class="bubble">${text}</div>`;
    elements.chatMessages.appendChild(msgDiv);
    elements.chatTerminal.scrollTop = elements.chatTerminal.scrollHeight;
}

// Render typewriter log stream
async function renderAgentLogs(logs) {
    if (!logs || logs.length === 0) return;
    
    const container = document.createElement("div");
    container.className = "log-output-container";
    elements.chatMessages.appendChild(container);
    
    for (const logLine of logs) {
        await new Promise(resolve => setTimeout(resolve, 200));
        
        const lineDiv = document.createElement("div");
        lineDiv.className = "agent-log-line";
        
        const match = logLine.match(/^\[(Coordinator|Researcher|Evaluator|System)\](.*)$/);
        if (match) {
            const tag = match[1];
            const text = match[2];
            lineDiv.innerHTML = `<span class="log-tag ${tag.toLowerCase()}">${tag}</span>${text}`;
        } else {
            lineDiv.textContent = logLine;
        }
        
        container.appendChild(lineDiv);
        elements.chatTerminal.scrollTop = elements.chatTerminal.scrollHeight;
    }
    
    await new Promise(resolve => setTimeout(resolve, 300));
}

// Auto-parse GPA, Language stats, and Publications status from CV/Resume content
function autoFillFromResume(text) {
    const textLower = text.toLowerCase();
    appendChatBubble("agent", "⏳ Analyzing resume keywords for profile matching...");
    
    // 1. GPA / CGPA scan
    let gpaFound = false;

    // Scan for CGPA (10.0 scale)
    const cgpaRegexes = [
        /cgpa\s*[:=-]?\s*([5-9]\.[0-9]{1,2}|10\.0)\s*\/?\s*10(?:\.0)?/i,
        /cgpa\s*[:=-]?\s*([5-9]\.[0-9]{1,2}|10\.0)/i,
        /([5-9]\.[0-9]{1,2}|10\.0)\s*\/?\s*10(?:\.0)?\s*cgpa/i
    ];
    for (const regex of cgpaRegexes) {
        const match = text.match(regex);
        if (match) {
            const val = parseFloat(match[1]);
            if (val >= 5.0 && val <= 10.0) {
                elements.profGpa.value = val;
                document.getElementById("prof-gpa-scale").value = "10.0";
                appendChatBubble("agent", `🔍 Resume Auto-Parser: Found CGPA ${val} on a 10.0 scale - Applied.`);
                gpaFound = true;
                break;
            }
        }
    }

    // Scan for Percentage (100% scale)
    if (!gpaFound) {
        const percentRegexes = [
            /([5-9][0-9](?:\.[0-9]{1,2})?)\s*%/i,
            /(?:percentage|aggregate)\s*[:=-]?\s*([5-9][0-9](?:\.[0-9]{1,2})?)/i
        ];
        for (const regex of percentRegexes) {
            const match = text.match(regex);
            if (match) {
                const val = parseFloat(match[1]);
                if (val >= 50.0 && val <= 100.0) {
                    elements.profGpa.value = val;
                    document.getElementById("prof-gpa-scale").value = "100";
                    appendChatBubble("agent", `🔍 Resume Auto-Parser: Found Percentage score ${val}% - Applied.`);
                    gpaFound = true;
                    break;
                }
            }
        }
    }

    // Scan for Standard GPA (4.0 scale)
    if (!gpaFound) {
        const gpaRegexes = [
            /gpa\s*[:=-]?\s*([0-3]\.[0-9]{1,2}|4\.0)/i,
            /([0-3]\.[0-9]{1,2}|4\.0)\s*\/?\s*4\.0\s*gpa/i,
            /([0-3]\.[0-9]{1,2}|4\.0)\s*gpa/i
        ];
        for (const regex of gpaRegexes) {
            const match = text.match(regex);
            if (match) {
                const val = parseFloat(match[1]);
                if (val >= 1.0 && val <= 4.0) {
                    elements.profGpa.value = val;
                    document.getElementById("prof-gpa-scale").value = "4.0";
                    appendChatBubble("agent", `🔍 Resume Auto-Parser: Found GPA ${val} on a 4.0 scale - Applied.`);
                    gpaFound = true;
                    break;
                }
            }
        }
    }
    
    if (!gpaFound) {
        elements.profGpa.value = "3.0"; // Default baseline
        document.getElementById("prof-gpa-scale").value = "4.0";
    }
    
    // 2. IELTS / TOEFL / Language scan
    let langFound = false;
    const ieltsRegex = /ielts\s*(?:band|score)?\s*[:=-]?\s*([4-9]\.[0-9]|[4-9])/i;
    const ieltsMatch = text.match(ieltsRegex);
    if (ieltsMatch) {
        const val = parseFloat(ieltsMatch[1]);
        if (val >= 4.0 && val <= 9.0) {
            document.getElementById("prof-lang-type").value = "IELTS";
            document.getElementById("prof-lang-type").dispatchEvent(new Event("change"));
            elements.profIelts.value = val;
            appendChatBubble("agent", `🔍 Resume Auto-Parser: Found IELTS score ${val} - Applied.`);
            langFound = true;
        }
    }
    
    if (!langFound) {
        const toeflRegex = /toefl\s*(?:score)?\s*[:=-]?\s*([6-9][0-9]|1[0-1][0-9]|120)/i;
        const toeflMatch = text.match(toeflRegex);
        if (toeflMatch) {
            const val = parseInt(toeflMatch[1]);
            document.getElementById("prof-lang-type").value = "TOEFL";
            document.getElementById("prof-lang-type").dispatchEvent(new Event("change"));
            elements.profIelts.value = val;
            appendChatBubble("agent", `🔍 Resume Auto-Parser: Found TOEFL score ${val} - Applied.`);
            langFound = true;
        }
    }

    if (!langFound) {
        // Default to None if not specified
        document.getElementById("prof-lang-type").value = "None";
        document.getElementById("prof-lang-type").dispatchEvent(new Event("change"));
        appendChatBubble("agent", "🔍 Resume Auto-Parser: No language test scores detected. Set Language to 'None/Not Taken'.");
    }
    
    // 3. Publications search
    const hasPubs = textLower.includes("publication") || textLower.includes("journal") || textLower.includes("published") || textLower.includes("conference") || textLower.includes("paper");
    if (hasPubs) {
        document.getElementById("prof-pub-status").value = "Published";
        appendChatBubble("agent", "🔍 Resume Auto-Parser: Found publications - Set Research status.");
    } else {
        document.getElementById("prof-pub-status").value = "None";
    }

    // 4. Target Major/Field Scan
    let major = "Engineering"; // Fallback default
    if (textLower.includes("computer science") || textLower.includes("software") || textLower.includes("developer") || textLower.includes("engineering") || textLower.includes("technical")) {
        major = "Engineering";
    } else if (textLower.includes("physics") || textLower.includes("chemistry") || textLower.includes("biology") || textLower.includes("researcher") || textLower.includes("science")) {
        major = "Science";
    } else if (textLower.includes("business") || textLower.includes("mba") || textLower.includes("finance") || textLower.includes("economics") || textLower.includes("marketing")) {
        major = "Business";
    } else if (textLower.includes("history") || textLower.includes("literature") || textLower.includes("philosophy") || textLower.includes("arts") || textLower.includes("social")) {
        major = "Humanities";
    }
    elements.profMajor.value = major;
    appendChatBubble("agent", `🔍 Resume Auto-Parser: Deduced major field: ${major}.`);

    // 5. Target Country / Degree Scan
    let degree = "Master's";
    if (textLower.includes("phd") || textLower.includes("ph.d") || textLower.includes("doctorate") || textLower.includes("doctor of philosophy")) {
        degree = "PhD";
    }
    document.getElementById("prof-degree").value = degree;
    appendChatBubble("agent", `🔍 Resume Auto-Parser: Deduced degree: ${degree === "PhD" ? "PhD / Doctorate" : "Master's"}.`);

    let country = "auto";
    let singleCountryVal = "South Korea";
    if (textLower.includes("korea") || textLower.includes("seoul")) {
        country = "single";
        singleCountryVal = "South Korea";
    } else if (textLower.includes("japan") || textLower.includes("tokyo") || textLower.includes("kyoto")) {
        country = "single";
        singleCountryVal = "Japan";
    } else if (textLower.includes("germany") || textLower.includes("munich") || textLower.includes("berlin")) {
        country = "single";
        singleCountryVal = "Germany";
    } else if (textLower.includes("singapore")) {
        country = "single";
        singleCountryVal = "Singapore";
    } else if (textLower.includes("taiwan") || textLower.includes("taipei")) {
        country = "single";
        singleCountryVal = "Taiwan";
    }

    const countryModeSelect = document.getElementById("prof-country-mode");
    countryModeSelect.value = country;
    countryModeSelect.dispatchEvent(new Event("change"));

    if (country === "single") {
        document.getElementById("prof-single-country").value = singleCountryVal;
        appendChatBubble("agent", `🔍 Resume Auto-Parser: Deduced target country: ${singleCountryVal}.`);
    } else {
        appendChatBubble("agent", "🔍 Resume Auto-Parser: No specific target country preference detected. Set to 'Auto Recommend'.");
    }

    // 6. IMMEDIATELY RUN THE MATCH PIPELINE autonomously!
    appendChatBubble("agent", "🚀 Running scholarship matching pipeline...");
    runMatchPipeline();
}
