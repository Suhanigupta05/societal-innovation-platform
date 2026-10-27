"""
SQLite Database Layer for Societal Innovation Collaboration Platform
Provides zero-setup persistent storage with automatic table initialization and seeding.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "societal_platform.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create all required tables for the platform."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Problems Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS problems (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        district TEXT NOT NULL,
        locality TEXT,
        citizen_name TEXT,
        citizen_contact TEXT,
        evidence_media TEXT,
        predicted_domain TEXT,
        ai_confidence REAL,
        priority_level TEXT,
        priority_score INTEGER,
        priority_factors TEXT,
        all_probabilities TEXT,
        matched_universities TEXT,
        duplicate_flags TEXT,
        status TEXT DEFAULT 'Submitted',
        assigned_university_id TEXT,
        assigned_university_name TEXT,
        created_at TEXT
    )
    """)

    # Solutions / University Projects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id TEXT NOT NULL,
        university_id TEXT NOT NULL,
        university_name TEXT NOT NULL,
        lead_faculty TEXT,
        student_team TEXT,
        solution_title TEXT NOT NULL,
        proposal_summary TEXT NOT NULL,
        technical_approach TEXT,
        estimated_budget REAL,
        timeline_months INTEGER,
        milestones TEXT,
        status TEXT DEFAULT 'Proposal_Submitted',
        created_at TEXT,
        FOREIGN KEY (problem_id) REFERENCES problems(id)
    )
    """)

    # Industry / CSR Sponsorships Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS industry_support (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id TEXT NOT NULL,
        solution_id INTEGER,
        company_name TEXT NOT NULL,
        support_type TEXT NOT NULL,
        amount_pledged REAL,
        mentor_name TEXT,
        status TEXT DEFAULT 'Pledged',
        created_at TEXT,
        FOREIGN KEY (problem_id) REFERENCES problems(id)
    )
    """)

    conn.commit()
    conn.close()

# Helper queries
def insert_problem(p: Dict[str, Any]) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO problems (
        id, title, description, district, locality, citizen_name, citizen_contact,
        evidence_media, predicted_domain, ai_confidence, priority_level, priority_score,
        priority_factors, all_probabilities, matched_universities, duplicate_flags,
        status, assigned_university_id, assigned_university_name, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p["id"],
        p["title"],
        p["description"],
        p.get("district", "General"),
        p.get("locality", ""),
        p.get("citizen_name", "Anonymous Citizen"),
        p.get("citizen_contact", ""),
        p.get("evidence_media", ""),
        p.get("predicted_domain", "General"),
        p.get("ai_confidence", 0.0),
        p.get("priority_level", "MEDIUM"),
        p.get("priority_score", 50),
        json.dumps(p.get("priority_factors", [])),
        json.dumps(p.get("all_probabilities", [])),
        json.dumps(p.get("matched_universities", [])),
        json.dumps(p.get("duplicate_flags", {})),
        p.get("status", "Submitted"),
        p.get("assigned_university_id", None),
        p.get("assigned_university_name", None),
        p.get("created_at", datetime.now().isoformat())
    ))

    conn.commit()
    conn.close()
    return p["id"]

def get_all_problems(domain: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM problems WHERE 1=1"
    params = []

    if domain and domain != "All":
        query += " AND predicted_domain = ?"
        params.append(domain)
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        item["priority_factors"] = json.loads(item["priority_factors"]) if item["priority_factors"] else []
        item["all_probabilities"] = json.loads(item["all_probabilities"]) if item["all_probabilities"] else []
        item["matched_universities"] = json.loads(item["matched_universities"]) if item["matched_universities"] else []
        item["duplicate_flags"] = json.loads(item["duplicate_flags"]) if item["duplicate_flags"] else {}
        result.append(item)
    return result

def get_problem_by_id(problem_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    item = dict(row)
    item["priority_factors"] = json.loads(item["priority_factors"]) if item["priority_factors"] else []
    item["all_probabilities"] = json.loads(item["all_probabilities"]) if item["all_probabilities"] else []
    item["matched_universities"] = json.loads(item["matched_universities"]) if item["matched_universities"] else []
    item["duplicate_flags"] = json.loads(item["duplicate_flags"]) if item["duplicate_flags"] else {}
    return item

def update_problem_status(problem_id: str, status: str, uni_id: Optional[str] = None, uni_name: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if uni_id and uni_name:
        cursor.execute("""
        UPDATE problems SET status = ?, assigned_university_id = ?, assigned_university_name = ?
        WHERE id = ?
        """, (status, uni_id, uni_name, problem_id))
    else:
        cursor.execute("UPDATE problems SET status = ? WHERE id = ?", (status, problem_id))

    conn.commit()
    conn.close()

def insert_solution(sol: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO solutions (
        problem_id, university_id, university_name, lead_faculty, student_team,
        solution_title, proposal_summary, technical_approach, estimated_budget,
        timeline_months, milestones, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sol["problem_id"],
        sol["university_id"],
        sol["university_name"],
        sol.get("lead_faculty", ""),
        sol.get("student_team", ""),
        sol["solution_title"],
        sol["proposal_summary"],
        sol.get("technical_approach", ""),
        sol.get("estimated_budget", 0.0),
        sol.get("timeline_months", 6),
        json.dumps(sol.get("milestones", [])),
        sol.get("status", "Proposal_Submitted"),
        datetime.now().isoformat()
    ))
    sol_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return sol_id

def get_solutions_by_problem(problem_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM solutions WHERE problem_id = ? ORDER BY id DESC", (problem_id,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        item["milestones"] = json.loads(item["milestones"]) if item["milestones"] else []
        result.append(item)
    return result

def get_all_solutions() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT s.*, p.title as problem_title, p.district, p.predicted_domain FROM solutions s JOIN problems p ON s.problem_id = p.id ORDER BY s.id DESC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        item["milestones"] = json.loads(item["milestones"]) if item["milestones"] else []
        result.append(item)
    return result

def insert_industry_support(ind: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO industry_support (
        problem_id, solution_id, company_name, support_type, amount_pledged, mentor_name, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ind["problem_id"],
        ind.get("solution_id"),
        ind["company_name"],
        ind["support_type"],
        ind.get("amount_pledged", 0.0),
        ind.get("mentor_name", ""),
        ind.get("status", "Pledged"),
        datetime.now().isoformat()
    ))
    ind_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ind_id

def get_all_industry_support() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM industry_support ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_dashboard_analytics() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM problems")
    total_problems = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM problems WHERE status = 'Resolved'")
    resolved_problems = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM solutions")
    total_solutions = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(amount_pledged), 0) FROM industry_support")
    total_csr_funds = cursor.fetchone()[0]

    # Domain breakdown
    cursor.execute("SELECT predicted_domain, COUNT(*) FROM problems GROUP BY predicted_domain ORDER BY COUNT(*) DESC")
    domain_counts = {r[0]: r[1] for r in cursor.fetchall()}

    # Priority breakdown
    cursor.execute("SELECT priority_level, COUNT(*) FROM problems GROUP BY priority_level")
    priority_counts = {r[0]: r[1] for r in cursor.fetchall()}

    # Status pipeline
    cursor.execute("SELECT status, COUNT(*) FROM problems GROUP BY status")
    status_counts = {r[0]: r[1] for r in cursor.fetchall()}

    conn.close()

    return {
        "total_problems": total_problems,
        "resolved_problems": resolved_problems,
        "total_solutions": total_solutions,
        "total_csr_funds": total_csr_funds,
        "domain_distribution": domain_counts,
        "priority_distribution": priority_counts,
        "status_distribution": status_counts
    }
