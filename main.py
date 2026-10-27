"""
Societal Innovation Collaboration Platform - Main Backend Application
Built with FastAPI, Scikit-Learn, and SQLite.
"""

import os
import shutil
import json
from typing import Optional, List, Tuple
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.database import (
    init_db,
    insert_problem,
    get_all_problems,
    get_problem_by_id,
    update_problem_status,
    insert_solution,
    get_solutions_by_problem,
    get_all_solutions,
    insert_industry_support,
    get_all_industry_support,
    get_dashboard_analytics,
    get_db_connection
)
from app.ai_engine import ai_engine
from app.training_data import UNIVERSITIES, DOMAINS

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Nationwide Location Data & Validation Cache
LOCATIONS_PATH = os.path.join(BASE_DIR, "app", "india_locations.json")
ALL_LOCATIONS = []
STATE_DISTRICT_MAP = {}
STATE_CODES = {
    "Andhra Pradesh": "AP", "Arunachal Pradesh": "AR", "Assam": "AS", "Bihar": "BR",
    "Chhattisgarh": "CG", "Goa": "GA", "Gujarat": "GJ", "Haryana": "HR",
    "Himachal Pradesh": "HP", "Jharkhand": "JH", "Karnataka": "KA", "Kerala": "KL",
    "Madhya Pradesh": "MP", "Maharashtra": "MH", "Manipur": "MN", "Meghalaya": "ML",
    "Mizoram": "MZ", "Nagaland": "NL", "Odisha": "OD", "Punjab": "PB",
    "Rajasthan": "RJ", "Sikkim": "SK", "Tamil Nadu": "TN", "Telangana": "TG",
    "Tripura": "TR", "Uttar Pradesh": "UP", "Uttarakhand": "UK", "West Bengal": "WB",
    "Andaman and Nicobar Islands": "AN", "Chandigarh": "CH",
    "Dadra and Nagar Haveli and Daman and Diu": "DD", "Delhi": "DL",
    "Jammu and Kashmir": "JK", "Ladakh": "LA", "Lakshadweep": "LD", "Puducherry": "PY"
}

if os.path.exists(LOCATIONS_PATH):
    with open(LOCATIONS_PATH, "r", encoding="utf-8") as f:
        loc_data = json.load(f)
        ALL_LOCATIONS = loc_data.get("states", [])
        for s in ALL_LOCATIONS:
            STATE_DISTRICT_MAP[s["name"].lower()] = (s["name"], set(d.lower() for d in s.get("districts", [])))

def resolve_and_validate_location(state: Optional[str], district: Optional[str]) -> Tuple[str, str]:
    """Validate and normalize state & district with backward compatibility for legacy inputs."""
    state_in = (state or "").strip()
    dist_in = (district or "").strip()

    matched_state = None
    if state_in:
        for s_lower, (s_name, _) in STATE_DISTRICT_MAP.items():
            if state_in.lower() == s_lower:
                matched_state = s_name
                break

    # If state is omitted or not directly matched, infer from known district
    if not matched_state and dist_in:
        for s_lower, (s_name, dist_set) in STATE_DISTRICT_MAP.items():
            if dist_in.lower() in dist_set:
                matched_state = s_name
                break

    final_state = matched_state or state_in or "Jharkhand"
    final_district = dist_in or "General"
    return final_state, final_district

# Initialize database
init_db()

app = FastAPI(
    title="Societal Innovation Collaboration Platform",
    description="AI-driven demand matching and project lifecycle platform for societal challenges across India.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and uploads directories
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Pydantic Request Models
class AnalyzeRequest(BaseModel):
    title: str
    description: str
    state: Optional[str] = "Jharkhand"
    district: Optional[str] = ""
    urgency: Optional[str] = "Medium"
    impact: Optional[str] = "Community"


class ProblemCreateRequest(BaseModel):
    title: str
    description: str
    state: Optional[str] = "Jharkhand"
    district: str
    locality: Optional[str] = ""
    citizen_name: Optional[str] = "Anonymous Citizen"
    citizen_contact: Optional[str] = ""
    urgency: Optional[str] = "Medium"
    impact: Optional[str] = "Community"


class SolutionCreateRequest(BaseModel):
    problem_id: str
    university_id: str
    university_name: str
    lead_faculty: str
    student_team: str
    solution_title: str
    proposal_summary: str
    technical_approach: str
    estimated_budget: float
    timeline_months: int
    milestones: List[dict]


class IndustryPledgeRequest(BaseModel):
    problem_id: str
    solution_id: Optional[int] = None
    company_name: str
    support_type: str
    amount_pledged: float
    mentor_name: Optional[str] = ""


# HTML Root View
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"domains": DOMAINS, "universities": UNIVERSITIES, "locations": ALL_LOCATIONS}
    )


# API Endpoints
@app.get("/api/locations")
def list_locations():
    """Return all Indian states, UTs, and their official districts."""
    return {"states": ALL_LOCATIONS}


@app.get("/api/universities")
def list_universities():
    """Return all partnered universities and their expertise profiles."""
    return UNIVERSITIES


@app.get("/api/domains")
def list_domains():
    """Return recognized societal challenge domains."""
    return DOMAINS


@app.post("/api/ai/analyze")
def run_ai_analysis(payload: AnalyzeRequest):
    """
    Live AI inspection endpoint:
    Runs NLP classification, duplicate detection against existing DB,
    nationwide university matching, and priority calculation without saving.
    """
    state, district = resolve_and_validate_location(payload.state, payload.district)
    existing_problems = get_all_problems()
    result = ai_engine.full_problem_analysis(
        title=payload.title,
        description=payload.description,
        district=district,
        state=state,
        reported_urgency=payload.urgency or "Medium",
        population_impact=payload.impact or "Community",
        existing_problems=existing_problems
    )
    return result


@app.get("/api/problems")
def fetch_problems(domain: Optional[str] = None, status: Optional[str] = None, state: Optional[str] = None):
    """List all problems with optional filtering by domain, status, or state."""
    return get_all_problems(domain=domain, status=status, state=state)


@app.get("/api/problems/{problem_id}")
def fetch_problem_detail(problem_id: str):
    """Get single problem details, linked solutions, and sponsors."""
    problem = get_problem_by_id(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    solutions = get_solutions_by_problem(problem_id)
    return {
        "problem": problem,
        "solutions": solutions
    }


@app.post("/api/problems")
async def create_problem_json(payload: ProblemCreateRequest):
    """Submit a problem via JSON with nationwide support."""
    state, district = resolve_and_validate_location(payload.state, payload.district)
    existing_problems = get_all_problems()

    # Generate sequential ID with state prefix (JH for Jharkhand, JK for J&K, etc.)
    problem_number = len(existing_problems) + 1
    state_code = STATE_CODES.get(state, "JH" if state == "Jharkhand" else "IND")
    new_id = f"{state_code}-2026-{problem_number:03d}"

    # Full AI Pipeline with nationwide location awareness
    analysis = ai_engine.full_problem_analysis(
        title=payload.title,
        description=payload.description,
        district=district,
        state=state,
        reported_urgency=payload.urgency,
        population_impact=payload.impact,
        existing_problems=existing_problems
    )

    top_uni = analysis["recommended_universities"][0] if analysis["recommended_universities"] else None

    p_data = {
        "id": new_id,
        "title": payload.title,
        "description": payload.description,
        "state": state,
        "district": district,
        "locality": payload.locality,
        "citizen_name": payload.citizen_name or "Anonymous Citizen",
        "citizen_contact": payload.citizen_contact or "",
        "evidence_media": "",
        "predicted_domain": analysis["nlp_classification"]["predicted_domain"],
        "ai_confidence": analysis["nlp_classification"]["confidence"],
        "priority_level": analysis["priority"]["priority_level"],
        "priority_score": analysis["priority"]["priority_score"],
        "priority_factors": analysis["priority"]["factors"],
        "all_probabilities": analysis["nlp_classification"]["all_probabilities"],
        "matched_universities": analysis["recommended_universities"],
        "duplicate_flags": analysis["duplicate_detection"],
        "status": "AI_Screened",
        "assigned_university_id": top_uni["university_id"] if top_uni else None,
        "assigned_university_name": top_uni["name"] if top_uni else None
    }

    insert_problem(p_data)
    return {"success": True, "problem_id": new_id, "analysis": analysis}


@app.post("/api/problems/upload")
async def create_problem_with_upload(
    title: str = Form(...),
    description: str = Form(...),
    district: str = Form(...),
    state: Optional[str] = Form("Jharkhand"),
    locality: Optional[str] = Form(""),
    citizen_name: Optional[str] = Form("Anonymous Citizen"),
    citizen_contact: Optional[str] = Form(""),
    urgency: Optional[str] = Form("Medium"),
    impact: Optional[str] = Form("Community"),
    file: Optional[UploadFile] = File(None)
):
    """Submit problem with optional evidence photo/document file across India."""
    resolved_state, resolved_district = resolve_and_validate_location(state, district)
    existing_problems = get_all_problems()
    problem_number = len(existing_problems) + 1
    state_code = STATE_CODES.get(resolved_state, "JH" if resolved_state == "Jharkhand" else "IND")
    new_id = f"{state_code}-2026-{problem_number:03d}"

    saved_filename = ""
    if file and file.filename:
        filename = f"{new_id}_{file.filename}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_filename = filename

    analysis = ai_engine.full_problem_analysis(
        title=title,
        description=description,
        district=resolved_district,
        state=resolved_state,
        reported_urgency=urgency,
        population_impact=impact,
        existing_problems=existing_problems
    )

    top_uni = analysis["recommended_universities"][0] if analysis["recommended_universities"] else None

    p_data = {
        "id": new_id,
        "title": title,
        "description": description,
        "state": resolved_state,
        "district": resolved_district,
        "locality": locality,
        "citizen_name": citizen_name or "Anonymous Citizen",
        "citizen_contact": citizen_contact or "",
        "evidence_media": saved_filename,
        "predicted_domain": analysis["nlp_classification"]["predicted_domain"],
        "ai_confidence": analysis["nlp_classification"]["confidence"],
        "priority_level": analysis["priority"]["priority_level"],
        "priority_score": analysis["priority"]["priority_score"],
        "priority_factors": analysis["priority"]["factors"],
        "all_probabilities": analysis["nlp_classification"]["all_probabilities"],
        "matched_universities": analysis["recommended_universities"],
        "duplicate_flags": analysis["duplicate_detection"],
        "status": "AI_Screened",
        "assigned_university_id": top_uni["university_id"] if top_uni else None,
        "assigned_university_name": top_uni["name"] if top_uni else None
    }

    insert_problem(p_data)
    return {"success": True, "problem_id": new_id, "analysis": analysis}


@app.post("/api/problems/{problem_id}/assign")
def assign_university(problem_id: str, university_id: str = Form(...), university_name: str = Form(...)):
    """Assign or re-route a societal challenge to a university."""
    update_problem_status(problem_id, "Assigned_University", uni_id=university_id, uni_name=university_name)
    return {"success": True, "message": f"Problem {problem_id} assigned to {university_name}"}


@app.post("/api/solutions")
def submit_solution(payload: SolutionCreateRequest):
    """University research team submits an innovation proposal."""
    sol_id = insert_solution({
        "problem_id": payload.problem_id,
        "university_id": payload.university_id,
        "university_name": payload.university_name,
        "lead_faculty": payload.lead_faculty,
        "student_team": payload.student_team,
        "solution_title": payload.solution_title,
        "proposal_summary": payload.proposal_summary,
        "technical_approach": payload.technical_approach,
        "estimated_budget": payload.estimated_budget,
        "timeline_months": payload.timeline_months,
        "milestones": payload.milestones,
        "status": "Proposal_Submitted"
    })
    update_problem_status(payload.problem_id, "Solution_Proposed")
    return {"success": True, "solution_id": sol_id}


@app.get("/api/solutions")
def list_solutions():
    """List all university research proposals and projects."""
    return get_all_solutions()


@app.post("/api/solutions/{solution_id}/milestone")
def toggle_milestone(solution_id: int, milestone_index: int = Form(...), new_status: str = Form(...)):
    """Update milestone progress status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT milestones FROM solutions WHERE id = ?", (solution_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Solution not found")

    milestones = json.loads(row[0]) if row[0] else []
    if 0 <= milestone_index < len(milestones):
        milestones[milestone_index]["status"] = new_status

    cursor.execute("UPDATE solutions SET milestones = ? WHERE id = ?", (json.dumps(milestones), solution_id))
    conn.commit()
    conn.close()
    return {"success": True, "milestones": milestones}


@app.post("/api/industry")
def pledge_support(payload: IndustryPledgeRequest):
    """Industry/CSR partner pledges grant or mentorship."""
    ind_id = insert_industry_support({
        "problem_id": payload.problem_id,
        "solution_id": payload.solution_id,
        "company_name": payload.company_name,
        "support_type": payload.support_type,
        "amount_pledged": payload.amount_pledged,
        "mentor_name": payload.mentor_name,
        "status": "Committed"
    })
    update_problem_status(payload.problem_id, "Industry_Funded")
    return {"success": True, "sponsorship_id": ind_id}


@app.get("/api/industry")
def list_industry_support():
    """List all corporate & startup pledges."""
    return get_all_industry_support()


@app.get("/api/analytics")
def get_analytics():
    """Get aggregate platform analytics for government overview and charts."""
    return get_dashboard_analytics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
