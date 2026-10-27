"""
Societal Innovation Collaboration Platform - Main Backend Application
Built with FastAPI, Scikit-Learn, and SQLite.
"""

import os
import shutil
import json
from typing import Optional, List
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

# Initialize database
init_db()

app = FastAPI(
    title="Societal Innovation Collaboration Platform",
    description="AI-driven demand matching and project lifecycle platform for societal challenges.",
    version="1.0.0"
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
    district: Optional[str] = ""
    urgency: Optional[str] = "Medium"
    impact: Optional[str] = "Community"


class ProblemCreateRequest(BaseModel):
    title: str
    description: str
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
        context={"domains": DOMAINS, "universities": UNIVERSITIES}
    )


# API Endpoints
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
    university matching, and priority calculation without saving.
    """
    existing_problems = get_all_problems()
    result = ai_engine.full_problem_analysis(
        title=payload.title,
        description=payload.description,
        district=payload.district or "",
        reported_urgency=payload.urgency or "Medium",
        population_impact=payload.impact or "Community",
        existing_problems=existing_problems
    )
    return result


@app.get("/api/problems")
def fetch_problems(domain: Optional[str] = None, status: Optional[str] = None):
    """List all problems with optional filtering."""
    return get_all_problems(domain=domain, status=status)


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
    """Submit a problem via JSON."""
    existing_problems = get_all_problems()

    # Generate sequential ID
    problem_number = len(existing_problems) + 1
    new_id = f"JH-2026-{problem_number:03d}"

    # Full AI Pipeline
    analysis = ai_engine.full_problem_analysis(
        title=payload.title,
        description=payload.description,
        district=payload.district,
        reported_urgency=payload.urgency,
        population_impact=payload.impact,
        existing_problems=existing_problems
    )

    top_uni = analysis["recommended_universities"][0] if analysis["recommended_universities"] else None

    p_data = {
        "id": new_id,
        "title": payload.title,
        "description": payload.description,
        "district": payload.district,
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
    locality: Optional[str] = Form(""),
    citizen_name: Optional[str] = Form("Anonymous Citizen"),
    citizen_contact: Optional[str] = Form(""),
    urgency: Optional[str] = Form("Medium"),
    impact: Optional[str] = Form("Community"),
    file: Optional[UploadFile] = File(None)
):
    """Submit problem with optional evidence photo/document file."""
    existing_problems = get_all_problems()
    problem_number = len(existing_problems) + 1
    new_id = f"JH-2026-{problem_number:03d}"

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
        district=district,
        reported_urgency=urgency,
        population_impact=impact,
        existing_problems=existing_problems
    )

    top_uni = analysis["recommended_universities"][0] if analysis["recommended_universities"] else None

    p_data = {
        "id": new_id,
        "title": title,
        "description": description,
        "district": district,
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
