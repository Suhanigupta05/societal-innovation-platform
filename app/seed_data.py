"""
Seed data generator for Societal Innovation Platform
Populates initial realistic problems, university assignments, and CSR pledges.
"""

from app.database import init_db, insert_problem, insert_solution, insert_industry_support, get_all_problems
from app.ai_engine import ai_engine

SAMPLE_PROBLEMS = [
    {
        "id": "JH-2026-001",
        "title": "Groundwater Fluoride Contamination in Palamu Rural Belt",
        "description": "Over 12 villages in Patan and Daltonganj blocks report high fluoride levels in borewell water (>3.5 mg/L). Children are showing signs of dental fluorosis and elderly villagers suffer crippling skeletal pain. Urgent low-cost community defluoridation filtration plant is needed.",
        "district": "Palamu",
        "locality": "Patan Block, Hamlets 4 & 5",
        "citizen_name": "Mukesh Mahto (Panchayat Samiti Member)",
        "citizen_contact": "mukesh.palamu@gmail.com",
        "urgency": "Critical",
        "impact": "Multiple Villages / Block",
        "status": "In_Progress",
        "assigned_university_id": "u2",
        "assigned_university_name": "IIT (Indian School of Mines), Dhanbad"
    },
    {
        "id": "JH-2026-002",
        "title": "Pest & Blast Disease Infestation in Bero Rice Paddy Fields",
        "description": "Fungal leaf blast spreading rapidly across 400 acres of paddy fields in Bero. Smallholder tribal farmers face near total harvest failure. Conventional chemical pesticides are unaffordable and causing runoff into the local stream.",
        "district": "Ranchi",
        "locality": "Bero Block, Khijri Belt",
        "citizen_name": "Sunita Linda (Kisan Mahila Samiti)",
        "citizen_contact": "sunita.linda@outlook.com",
        "urgency": "High",
        "impact": "Multiple Villages / Block",
        "status": "Solution_Proposed",
        "assigned_university_id": "u1",
        "assigned_university_name": "Birsa Agricultural University (BAU), Ranchi"
    },
    {
        "id": "JH-2026-003",
        "title": "Adolescent Tribal Girl School Dropouts due to Sanitation Deficit",
        "description": "In government Kasturba Gandhi Balika Vidyalaya in Torpa block, lack of regular running water supply and broken latrines has caused an alarming 40% absentee rate during menstrual cycles, leading to high school dropouts.",
        "district": "Khunti",
        "locality": "Torpa Block Girls High School",
        "citizen_name": "Sister Jacinta Dungdung",
        "citizen_contact": "jacinta.khunti@ngo.org",
        "urgency": "High",
        "impact": "Village / Town Ward",
        "status": "Assigned_University",
        "assigned_university_id": "u6",
        "assigned_university_name": "Central University of Jharkhand (CUJ), Ranchi"
    },
    {
        "id": "JH-2026-004",
        "title": "Sickle Cell Disease Diagnostic Lag in Santhal Pargana",
        "description": "Tribal children in remote villages of Deoghar and Dumka suffer chronic pain, anemia and early mortality due to delayed sickle cell screening. Nearest testing facility requires 45 km travel to district headquarters.",
        "district": "Deoghar",
        "locality": "Sarwan and Mohanpur blocks",
        "citizen_name": "Dr. Anand Soren (Rural Health Worker)",
        "citizen_contact": "anand.soren@health.jh.gov",
        "urgency": "Critical",
        "impact": "Entire District",
        "status": "Industry_Funded",
        "assigned_university_id": "u5",
        "assigned_university_name": "AIIMS Deoghar / RIMS Ranchi Medical Consortium"
    },
    {
        "id": "JH-2026-005",
        "title": "Thermal Fly Ash Runoff and Dust Pollution in Bokaro Periphery",
        "description": "Fly ash ponds near power generation units are overflowing into surrounding farmlands and breathing air. Heavy metals contaminating local drinking wells and damaging vegetable topsoil.",
        "district": "Bokaro",
        "locality": "Chandrapura Peripheral Area",
        "citizen_name": "Rajesh Kumar Sinha (Resident Welfare Association)",
        "citizen_contact": "rksinha.bokaro@gmail.com",
        "urgency": "High",
        "impact": "Multiple Villages / Block",
        "status": "AI_Screened",
        "assigned_university_id": None,
        "assigned_university_name": None
    },
    {
        "id": "JH-2026-006",
        "title": "Lack of Value Addition and Market Linkages for Lac and Mahua Collectors",
        "description": "Over 800 tribal households collect raw lac and forest mahua but sell to local middlemen at 20% of market value. Lack of local primary processing, solar drying units and quality certification.",
        "district": "Latehar",
        "locality": "Mahuadanr Forest Belt",
        "citizen_name": "Birsa Munda SHG Federation",
        "citizen_contact": "latehar.federation@shg.org",
        "urgency": "Medium",
        "impact": "Multiple Villages / Block",
        "status": "Submitted",
        "assigned_university_id": None,
        "assigned_university_name": None
    }
]

def seed_database():
    init_db()
    existing = get_all_problems()
    if existing:
        print(f"Database already has {len(existing)} problems. Skipping seed.")
        return

    print("Seeding initial problems with AI analysis...")
    created_problems = []

    for item in SAMPLE_PROBLEMS:
        analysis = ai_engine.full_problem_analysis(
            title=item["title"],
            description=item["description"],
            district=item["district"],
            reported_urgency=item["urgency"],
            population_impact=item["impact"]
        )

        p_data = {
            "id": item["id"],
            "title": item["title"],
            "description": item["description"],
            "district": item["district"],
            "locality": item["locality"],
            "citizen_name": item["citizen_name"],
            "citizen_contact": item["citizen_contact"],
            "evidence_media": "",
            "predicted_domain": analysis["nlp_classification"]["predicted_domain"],
            "ai_confidence": analysis["nlp_classification"]["confidence"],
            "priority_level": analysis["priority"]["priority_level"],
            "priority_score": analysis["priority"]["priority_score"],
            "priority_factors": analysis["priority"]["factors"],
            "all_probabilities": analysis["nlp_classification"]["all_probabilities"],
            "matched_universities": analysis["recommended_universities"],
            "duplicate_flags": analysis["duplicate_detection"],
            "status": item["status"],
            "assigned_university_id": item["assigned_university_id"],
            "assigned_university_name": item["assigned_university_name"]
        }

        insert_problem(p_data)
        created_problems.append(p_data)

    print("Seeding University R&D Solutions...")
    # Solution 1: IIT ISM for Fluoride
    sol1_id = insert_solution({
        "problem_id": "JH-2026-001",
        "university_id": "u2",
        "university_name": "IIT (Indian School of Mines), Dhanbad",
        "lead_faculty": "Prof. A. K. Mishra (Dept of Environmental Tech)",
        "student_team": "Team Jal-Shuddhi (4 M.Tech & Ph.D Scholars)",
        "solution_title": "Nano-Activated Alumina Community Defluoridation Filtration Unit",
        "proposal_summary": "Design and deployment of gravity-fed continuous filtration plant using local low-cost activated alumina cartridges to reduce fluoride from 3.8 mg/L to WHO standard (<1.0 mg/L).",
        "technical_approach": "Adsorption column with zero electricity requirement, powered by gravity with solar backwash pump. Cartridge replacement cycle 6 months.",
        "estimated_budget": 350000.0,
        "timeline_months": 6,
        "milestones": [
            {"title": "Water Sample Analysis & Prototype Lab Testing", "status": "Completed", "date": "Month 1"},
            {"title": "Pilot Unit Fabrication & Installation in Patan", "status": "In Progress", "date": "Month 3"},
            {"title": "Community Training & Water Quality Verification", "status": "Upcoming", "date": "Month 6"}
        ],
        "status": "In_Progress"
    })

    # Solution 2: BAU Ranchi for Paddy blast
    insert_solution({
        "problem_id": "JH-2026-002",
        "university_id": "u1",
        "university_name": "Birsa Agricultural University (BAU), Ranchi",
        "lead_faculty": "Dr. Rameshwar Oraon (Plant Pathology)",
        "student_team": "Team Krishi-Kavach (3 B.Sc Ag + 2 PG Researchers)",
        "solution_title": "Bio-formulation of Trichoderma & Neem Extract Sprays for Organic Blast Control",
        "proposal_summary": "Indigenous bio-control formulation to arrest fungal mycelium growth without harmful pesticide residue, combined with SMS alert advisory for weather-triggered spore outbreaks.",
        "technical_approach": "Microbial antagonism testing + low-cost on-farm mother culture multiplication kits distributed to women farmers.",
        "estimated_budget": 180000.0,
        "timeline_months": 4,
        "milestones": [
            {"title": "Bio-culture Preparation & Field Trials", "status": "Completed", "date": "Month 1"},
            {"title": "Farmer Field School Demonstrations in Bero", "status": "In Progress", "date": "Month 2"},
            {"title": "Efficacy Evaluation & Distribution of 500 Bio-kits", "status": "Upcoming", "date": "Month 4"}
        ],
        "status": "Proposal_Submitted"
    })

    # Solution 3: AIIMS Deoghar for Sickle Cell
    sol3_id = insert_solution({
        "problem_id": "JH-2026-004",
        "university_id": "u5",
        "university_name": "AIIMS Deoghar / RIMS Ranchi Medical Consortium",
        "lead_faculty": "Dr. Sunita Murmu (Dept of Community Medicine)",
        "student_team": "Team Jeevan-Rekha (4 Resident Doctors & Med-Tech Interns)",
        "solution_title": "Mobile Paper-Microfluidics Point-of-Care Sickle Cell Diagnostic Kit",
        "proposal_summary": "Rapid 15-minute diagnostic test strip requiring only a single fingerprick blood drop, requiring no lab centrifuge, costing under ₹40 per test for field Anganwadi deployment.",
        "technical_approach": "Paper-based hemoglobin solubility assay coupled with a smartphone camera colorimetric analyzer app for instant digital health card generation.",
        "estimated_budget": 520000.0,
        "timeline_months": 8,
        "milestones": [
            {"title": "Assay Optimization & Clinical Validation", "status": "Completed", "date": "Month 2"},
            {"title": "Smartphone Detection App & Pilot Screening of 2000 Children", "status": "Completed", "date": "Month 4"},
            {"title": "District-wide Anganwadi Worker Training & Deployment", "status": "In Progress", "date": "Month 8"}
        ],
        "status": "Funded"
    })

    print("Seeding Industry CSR Sponsorships...")
    insert_industry_support({
        "problem_id": "JH-2026-001",
        "solution_id": sol1_id,
        "company_name": "Tata Steel Foundation (CSR Division)",
        "support_type": "CSR Grant & Fabrication Assistance",
        "amount_pledged": 350000.0,
        "mentor_name": "Amitava Roy (Head, CSR Water Initiatives)",
        "status": "Committed"
    })

    insert_industry_support({
        "problem_id": "JH-2026-004",
        "solution_id": sol3_id,
        "company_name": "Central Coalfields Limited (CCL) Health CSR",
        "support_type": "CSR Grant & Mobile Health Van Support",
        "amount_pledged": 520000.0,
        "mentor_name": "Dr. B. K. Singh (Chief Medical Officer, CSR)",
        "status": "Disbursed"
    })

    print("Database initialization and seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
