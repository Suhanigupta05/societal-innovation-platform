"""
Seed training dataset of realistic societal problems across 8 domains,
specifically tailored for societal innovation and regional challenges.
"""

TRAINING_DATA = [
    # Agriculture & Farming
    ("Pest infestation damaging paddy crops in Bero block causing heavy losses for small farmers", "Agriculture"),
    ("Lack of cold storage facilities causing tomato and vegetable harvest spoilage in Ranchi rural", "Agriculture"),
    ("Depleted soil fertility and excessive soil acidity reducing yield for millet and maize cultivators", "Agriculture"),
    ("Smallholder tribal farmers need affordable solar drip irrigation systems for multi-crop farming", "Agriculture"),
    ("Post-harvest loss of Lac and Mahua due to lack of local processing and drying units", "Agriculture"),
    ("Crop disease leaf blast affecting rice production in late monsoon harvest season", "Agriculture"),
    ("Unpredictable rainfall and lack of drought-resistant seeds impacting paddy seedlings", "Agriculture"),
    ("Need for low-cost soil moisture sensor to optimize water usage in potato farming", "Agriculture"),

    # Water Resource Management & Sanitation
    ("High fluoride contamination in groundwater causing fluorosis in Palamu and Garhwa villages", "Water Management"),
    ("Seasonal drying up of community open wells and tubewells leaving villagers without potable water", "Water Management"),
    ("Industrial discharge and coal mine runoff polluting the Subarnarekha and Damodar rivers", "Water Management"),
    ("Poor drainage and overflowing septic tanks contaminating drinking water pipelines in suburbs", "Water Management"),
    ("Rainwater harvesting systems required in rural primary schools facing dry season water shortage", "Water Management"),
    ("Arsenic contamination detected in shallow handpumps across Sahibganj riverine belt", "Water Management"),
    ("Defunct handpumps and broken chlorination units leading to contaminated village drinking supply", "Water Management"),
    ("Heavy siltation in check dams reducing water storage capacity for irrigation and livestock", "Water Management"),

    # Healthcare & Public Health
    ("High prevalence of sickle cell anemia and lack of early diagnostic testing in tribal hamlets", "Healthcare"),
    ("Maternal and child malnutrition in remote Anganwadi centers lacking supplementary nutrition monitoring", "Healthcare"),
    ("Shortage of specialized doctors at Community Health Centers requiring telemedicine support", "Healthcare"),
    ("Rising cases of malaria and vector-borne dengue following monsoon without rapid test kits", "Healthcare"),
    ("Lack of cold chain maintenance for vaccines in un-electrified health sub-centers", "Healthcare"),
    ("High incidence of tuberculosis in coal mining clusters with delayed sputum test results", "Healthcare"),
    ("Lack of mental health counseling and emergency ambulance transport in rural hilly areas", "Healthcare"),
    ("Need for portable point-of-care anemia screening device for adolescent girls and pregnant women", "Healthcare"),

    # Education & Skill Development
    ("High school dropout rates among girl students due to lack of functional toilets and sanitary pads", "Education"),
    ("Lack of digital literacy and interactive STEM laboratories in government higher secondary schools", "Education"),
    ("Shortage of bilingual teachers proficient in local tribal languages like Santhali and Mundari", "Education"),
    ("Unemployment among rural youth graduating without industry-relevant vocational skills", "Education"),
    ("Inadequate classroom infrastructure and lack of power backup in rural smart classrooms", "Education"),
    ("Need for low-cost digital learning tablets with offline curriculum for remote tribal schools", "Education"),
    ("Poor foundational numeracy and reading skills in primary classes requiring gamified learning tools", "Education"),
    ("Lack of career counseling and entrance exam coaching for students from economically weaker sections", "Education"),

    # Environment, Forestry & Clean Energy
    ("Forest degradation and rising human-elephant conflict near elephant corridors in East Singhbhum", "Environment"),
    ("Heavy fly ash pollution from thermal power plants affecting air quality and agricultural land", "Environment"),
    ("Illegal tree felling and loss of indigenous Sal and Teak forest cover in Saranda region", "Environment"),
    ("Need for decentralized solar micro-grids in off-grid forested villages", "Environment"),
    ("Open coal fires and biomass burning causing respiratory distress and soot accumulation", "Environment"),
    ("Electronic waste and plastic dumping in forest fringes endangering local wildlife", "Environment"),
    ("Forest fires during dry summer months threatening bio-reserves and non-timber forest produce", "Environment"),
    ("Need for biochar conversion units to recycle agricultural residue instead of open field burning", "Environment"),

    # Rural Livelihoods & Handicrafts
    ("Tribal bamboo artisans unable to reach national markets and earn fair value for handicrafts", "Rural Livelihoods"),
    ("Lack of modern looms and yarn dying technology for traditional silk and tussar weavers", "Rural Livelihoods"),
    ("Lack of micro-cold chain and branding for forest honey collectors in Latehar district", "Rural Livelihoods"),
    ("Seasonal distress migration of unskilled rural laborers due to lack of local off-season work", "Rural Livelihoods"),
    ("Women self-help groups struggling with packaging and market linkages for millets and spices", "Rural Livelihoods"),
    ("Need for low-cost machinery for processing sal leaves into biodegradable plates and bowls", "Rural Livelihoods"),
    ("Artisans producing Sohrai and Kohbar GI-tagged art need digital authentication and e-commerce portal", "Rural Livelihoods"),
    ("Fisherfolk facing fish fingerling mortality due to lack of oxygen testing kits in community ponds", "Rural Livelihoods"),

    # Urban Infrastructure & Waste Management
    ("Severe traffic congestion and absence of automated signals at major city intersections", "Urban Infrastructure"),
    ("Unsegregated municipal solid waste piling up in open landfills causing leachate leakage", "Urban Infrastructure"),
    ("Potholes and waterlogged roads causing severe commuting hazards and accidents during monsoon", "Urban Infrastructure"),
    ("Inadequate street lighting in peripheral town colonies leading to nighttime safety hazards", "Urban Infrastructure"),
    ("Lack of disabled-friendly ramps and accessible public transit stations in urban centers", "Urban Infrastructure"),
    ("Overflowing open garbage bins near market areas attracting stray animals and disease vectors", "Urban Infrastructure"),
    ("Rapid urban concrete sprawl causing severe depletion of urban groundwater aquifers", "Urban Infrastructure"),
    ("Unplanned construction and illegal encroachments blocking natural stormwater drainage channels", "Urban Infrastructure"),

    # Public Safety & Disaster Resilience
    ("Flash flood risks and lack of early warning sensors in vulnerable river catchment zones", "Public Safety"),
    ("Lightning strikes causing fatalities among rural agricultural workers during pre-monsoon storms", "Public Safety"),
    ("Abandoned open coal mine pits causing drowning accidents and ground subsidence", "Public Safety"),
    ("Fire safety non-compliance in congested commercial markets and older hospital buildings", "Public Safety"),
    ("Lack of rapid emergency SOS alert system for women commuting on isolated rural routes", "Public Safety"),
    ("Landslides along hilly ghat roads disrupting essential supplies during heavy rains", "Public Safety"),
]

DOMAINS = [
    "Agriculture",
    "Water Management",
    "Healthcare",
    "Education",
    "Environment",
    "Rural Livelihoods",
    "Urban Infrastructure",
    "Public Safety"
]

UNIVERSITIES = [
    {
        "id": "u1",
        "name": "Birsa Agricultural University (BAU), Ranchi",
        "primary_domains": ["Agriculture", "Water Management", "Rural Livelihoods"],
        "expertise_keywords": [
            "soil", "crop", "seeds", "irrigation", "farming", "pesticides",
            "horticulture", "veterinary", "dairy", "poultry", "millet", "lac", "tussar"
        ],
        "districts": ["Ranchi", "Khunti", "Gumla", "Lohardaga", "Ramgarh"],
        "departments": ["Agronomy", "Soil Science", "Water Management", "Plant Pathology", "Horticulture"],
        "faculty_lead": "Dr. Rameshwar Oraon (Director of Extension Education)"
    },
    {
        "id": "u2",
        "name": "IIT (Indian School of Mines), Dhanbad",
        "primary_domains": ["Water Management", "Environment", "Urban Infrastructure", "Public Safety"],
        "expertise_keywords": [
            "groundwater", "hydrology", "water contamination", "fluoride", "arsenic",
            "mine runoff", "fly ash", "subsidence", "renewable energy", "geotech", "sensors"
        ],
        "districts": ["Dhanbad", "Bokaro", "Giridih", "Palamu", "Garhwa"],
        "departments": ["Environmental Science & Engineering", "Applied Geology", "Civil Engineering", "Mining"],
        "faculty_lead": "Prof. A. K. Mishra (Head of Environmental Tech)"
    },
    {
        "id": "u3",
        "name": "Birla Institute of Technology (BIT) Mesra, Ranchi",
        "primary_domains": ["Urban Infrastructure", "Healthcare", "Education", "Public Safety"],
        "expertise_keywords": [
            "ai", "iot", "smart cities", "telemedicine", "traffic", "sensors",
            "embedded systems", "computer vision", "remote sensing", "gis", "software"
        ],
        "districts": ["Ranchi", "Hazaribagh", "Ramgarh", "East Singhbhum"],
        "departments": ["Computer Science & Engineering", "Civil & Environmental", "Bio-Engineering", "Remote Sensing"],
        "faculty_lead": "Dr. Sudip Mukherjee (Coordinator, Innovation & Incubation)"
    },
    {
        "id": "u4",
        "name": "National Institute of Technology (NIT) Jamshedpur",
        "primary_domains": ["Urban Infrastructure", "Environment", "Water Management"],
        "expertise_keywords": [
            "waste management", "water treatment", "concrete", "structural safety",
            "potholes", "drainage", "automation", "manufacturing", "clean energy"
        ],
        "districts": ["East Singhbhum", "West Singhbhum", "Seraikela-Kharsawan"],
        "departments": ["Civil Engineering", "Mechanical Engineering", "Chemical Engineering"],
        "faculty_lead": "Dr. Prabal Ghosh (Center for Rural Technology)"
    },
    {
        "id": "u5",
        "name": "AIIMS Deoghar / RIMS Ranchi Medical Consortium",
        "primary_domains": ["Healthcare", "Public Safety"],
        "expertise_keywords": [
            "malnutrition", "sickle cell", "anemia", "malaria", "tuberculosis",
            "telemedicine", "epidemic", "diagnostics", "rural clinics", "maternal health"
        ],
        "districts": ["Deoghar", "Dumka", "Godda", "Sahibganj", "Ranchi"],
        "departments": ["Community Medicine", "Pediatrics", "Hematology", "Preventive Healthcare"],
        "faculty_lead": "Dr. Sunita Murmu (Professor, Community & Family Medicine)"
    },
    {
        "id": "u6",
        "name": "Central University of Jharkhand (CUJ), Ranchi",
        "primary_domains": ["Environment", "Education", "Rural Livelihoods"],
        "expertise_keywords": [
            "forest", "wildlife", "climate", "solar microgrid", "tribal languages",
            "curriculum", "ecology", "biochar", "elephant corridors", "sustainable dev"
        ],
        "districts": ["Ranchi", "Simdega", "Latehar", "Khunti"],
        "departments": ["Environmental Sciences", "Energy Engineering", "Tribal Studies", "Education"],
        "faculty_lead": "Prof. Manoj Kumar (Dean, Natural Resource Management)"
    },
    {
        "id": "u7",
        "name": "Xavier Institute of Social Service (XISS), Ranchi",
        "primary_domains": ["Rural Livelihoods", "Education"],
        "expertise_keywords": [
            "shg", "handicrafts", "e-commerce", "migration", "market linkages",
            "financial literacy", "sohrai art", "bamboo", "weaving", "social impact"
        ],
        "districts": ["Ranchi", "Gumla", "Lohardaga", "Pakur"],
        "departments": ["Rural Management", "Financial Management", "Social Entrepreneurship"],
        "faculty_lead": "Dr. Anant Prasad (Rural Incubation Hub)"
    }
]
